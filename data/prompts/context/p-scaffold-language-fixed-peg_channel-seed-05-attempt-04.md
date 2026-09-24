## Search State

- **Seed**: 5
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.3806 | 0.14 | ❌ rejected |
| 3 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.0695 | 0.63 | ❌ rejected |
| 2 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.0561 | 0.61 | ❌ rejected |
| 1 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.0697 | 0.63 | ✅ accepted |
| 0 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.0676 | 0.62 | ✅ accepted |

**Proposal policy**: task_score is 0.14 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`
- Frozen object start: [0.5244002338996304, 0.1046352631789195, 0.04]
- Frozen task target: [0.5244002338996304, -0.05536473682108051, 0.04]
- Goal object position: (0.5244002338996304, -0.05536473682108051, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5244002338996304, 0.1046352631789195, 0.04)
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
  frozen_object_start: [0.5244, 0.1046, 0.04]
  frozen_task_target: [0.5244, -0.0554, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5244002338996304, 0.1046352631789195, 0.04]}
  frozen_targets: {'channel_exit': [0.5244002338996304, -0.05536473682108051, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e

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

## Current Skill (Q=-0.381) — your mutation base

```yaml
skill: peg_channel
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
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
  generator: linear_cartesian
  control: admittance_control
  termination: contact_detected
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
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

- **Composite score**: -0.381
- **task_score** (E): 0.141
- **fitness_score**: 0.109  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 0.00 | 1.00 | 0.2852 |
| approach_1 | 0.67 | 1.00 | 0.1862 |
| contact_1 | 0.33 | 1.00 | 0.0263 |
| push_1 | 0.00 | 1.00 | 0.0000 |
| retract_1 | 0.33 | 1.00 | 0.1350 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 0.00 / step_budget | (0.500, 0.200, 0.300)→(0.675, 0.277, 0.089) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 2.000 | 313.311 | 1377.732 |
| approach_1 | approach | 0.67 / step_budget | (0.675, 0.277, 0.089)→(0.532, 0.161, 0.109) | (0.504, 0.095, 0.034)→(0.501, 0.093, 0.034) | 0.175→0.173 | 1.00 / 1.000 | 0.539 | 226.654 |
| contact_1 | contact | 0.33 / step_budget | (0.532, 0.161, 0.109)→(0.517, 0.142, 0.112) | (0.501, 0.093, 0.034)→(0.498, 0.082, 0.034) | 0.173→0.162 | 1.00 / 3.000 | 280.674 | 315.014 |
| push_1 | push | 0.00 / guard_failure | (0.517, 0.142, 0.112)→(0.517, 0.142, 0.112) | (0.498, 0.082, 0.034)→(0.498, 0.082, 0.034) | 0.162→0.162 | 1.00 / 3.000 | 85.020 | 86.679 |
| retract_1 | retract | 0.33 / step_budget | (0.517, 0.142, 0.112)→(0.498, 0.010, 0.129) | (0.498, 0.082, 0.034)→(0.499, 0.069, 0.034) | 0.162→0.149 | 1.00 / 1.667 | 166.462 | 253.810 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.457
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.404
- phase_score: 0.084
- phase_breakdown.push_score: 0.014
- phase_breakdown.contact_score: 0.223
- phase_breakdown.approach_score: 0.157

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.212
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.404
- **Median Q (composite search score)**: -0.432
- **K-run variance**: 0.0053
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.315


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9b36d26f861d7a613dfb3d8c86d70470e42095a430c2befa4bd6e530468a8a7e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2af86d8f59685db6584febc0596b9044223ae39cea3120c112c665a54a1c4732`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14847,"average_solve_count":229.0,"average_success_count":229.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.12095,"approach_1.approach_height":0.08897,"approach_1.speed":0.06057,"contact_1.speed":0.0282,"push_1.impedance_stiffness":323.32136,"push_1.push_distance":0.13269,"retract_1.retract_height":0.14986,"retract_1.speed":0.05212},"optimized_scores":{"best_composite_score":-0.43157,"best_fitness_score":0.05843,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link6","contact_count":911.0,"contact_point_centroid":[0.54279,0.11922,0.05978],"force_p95":492.64467,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1368.11216,"mean_force":390.57982,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.6272,0.27168,0.15444]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":601.0,"contact_point_centroid":[0.47499,0.07987,0.05991],"force_p95":419.40254,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":422.54702,"mean_force":319.61333,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5167,0.14775,0.10385]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":129.0,"contact_point_centroid":[0.445,0.06111,0.05996],"force_p95":333.86821,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":345.02854,"mean_force":251.08883,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5167,0.14611,0.10798]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":246.0,"contact_point_centroid":[0.54624,0.11999,0.05997],"force_p95":149.37061,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":242.86005,"mean_force":78.50807,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.66091,0.25622,0.08851]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":19.0,"contact_point_centroid":[0.445,0.05987,0.05998],"force_p95":80.7375,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.25234,"mean_force":54.56553,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51608,0.14506,0.10827]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.445,0.06077,0.05993],"force_p95":83.99874,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.97645,"mean_force":74.33952,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51655,0.14619,0.10815]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":29.0,"contact_point_centroid":[0.475,0.07172,0.06],"force_p95":49.9204,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":55.63838,"mean_force":34.3187,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51499,0.14093,0.10828]},{"body_a":"peg","body_b":"channel_base_body","contact_count":676.0,"contact_point_centroid":[0.50849,0.10459,0.00968],"force_p95":12.69959,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.78447,"mean_force":3.07734,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51729,0.14862,0.10416]},{"body_a":"peg","body_b":"link7","contact_count":398.0,"contact_point_centroid":[0.4937,0.09362,0.05952],"force_p95":15.6729,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.21538,"mean_force":4.89392,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51669,0.14856,0.10187]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.475,0.07657,0.05998],"force_p95":34.81745,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":37.17819,"mean_force":16.91633,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51655,0.14619,0.10815]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50526,0.10515,0.0094],"force_p95":0.67404,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.73881,"mean_force":0.65816,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.6164,0.26796,0.15479]},{"body_a":"peg","body_b":"link6","contact_count":42.0,"contact_point_centroid":[0.51991,0.11507,0.05669],"force_p95":13.43854,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.31618,"mean_force":2.41751,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.43646,0.27458,0.14867]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":392.0,"contact_point_centroid":[0.52512,0.10576,0.0406],"force_p95":2.54343,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.96399,"mean_force":1.45886,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51661,0.14789,0.10368]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50071,0.19544,0.28298]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50669,0.10613,0.00939],"force_p95":0.57811,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6069,"mean_force":0.54577,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50816,0.06315,0.11988]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49639,0.09171,0.0094],"force_p95":0.57833,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58185,"mean_force":0.54825,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51655,0.14619,0.10815]}],"total_contact_groups":18},"final_pose_error":0.06311,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50696,0.10599,0.03381],"final_tcp_position":[0.50209,-0.01877,0.13471],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":1368.11216,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50549,0.10465,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":305.49766,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1958.0,"raw_peak_contact_force":1368.11216,"tcp_end":[0.68681,0.27242,0.08304],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.25188,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50546,0.10461,0.03384],"object_pos_start":[0.50549,0.10465,0.03384],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18484,"object_z_max":0.03384,"peak_contact_force":0.54311,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1246.0,"raw_peak_contact_force":242.86005,"subtask_id":"approach","tcp_end":[0.52556,0.16015,0.11335],"tcp_start":[0.68681,0.27242,0.08304],"tcp_to_object_dist_end":0.09905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":676.0,"n_steps_budget":1000.0,"object_pos_end":[0.50697,0.10598,0.03382],"object_pos_start":[0.50546,0.10461,0.03384],"object_to_goal_dist_end":0.18621,"object_to_goal_dist_start":0.1848,"object_z_max":0.03485,"peak_contact_force":335.94147,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2196.0,"raw_peak_contact_force":422.54702,"subtask_id":"contact","tcp_end":[0.51655,0.1462,0.10815],"tcp_start":[0.52556,0.16015,0.11335],"tcp_to_object_dist_end":0.08505,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50696,0.10596,0.03383],"object_pos_start":[0.50697,0.10598,0.03382],"object_to_goal_dist_end":0.1862,"object_to_goal_dist_start":0.18621,"object_z_max":0.03383,"peak_contact_force":84.97645,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":84.97645,"subtask_id":"push","tcp_end":[0.51656,0.14618,0.10815],"tcp_start":[0.51656,0.14619,0.10815],"tcp_to_object_dist_end":0.08505,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50696,0.10599,0.03381],"object_pos_start":[0.50698,0.10599,0.03383],"object_to_goal_dist_end":0.18622,"object_to_goal_dist_start":0.18622,"object_z_max":0.03388,"peak_contact_force":0.53302,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1385.0,"raw_peak_contact_force":86.25234,"tcp_end":[0.50209,-0.01877,0.13471],"tcp_start":[0.51656,0.14618,0.10815],"tcp_to_object_dist_end":0.16053,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18605,"average_solve_count":215.0,"average_success_count":215.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.14814,"approach_1.approach_height":0.0875,"approach_1.speed":0.06354,"contact_1.speed":0.01801,"push_1.impedance_stiffness":119.24531,"push_1.push_distance":0.1025,"retract_1.retract_height":0.1085,"retract_1.speed":0.09992},"optimized_scores":{"best_composite_score":-0.27783,"best_fitness_score":0.21217,"best_task_score":0.40384},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link6","contact_count":870.0,"contact_point_centroid":[0.53487,0.11828,0.05977],"force_p95":626.26604,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1415.49645,"mean_force":433.19437,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.61296,0.27363,0.14881]},{"body_a":"channel_base_body","body_b":"link6","contact_count":300.0,"contact_point_centroid":[0.43118,-0.10008,0.06499],"force_p95":219.64074,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":257.97997,"mean_force":142.06597,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50929,0.00879,0.10725]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":375.0,"contact_point_centroid":[0.53812,0.12,0.05998],"force_p95":115.4714,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":238.75918,"mean_force":67.16681,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.63827,0.24746,0.08001]},{"body_a":"channel_base_body","body_b":"link7","contact_count":91.0,"contact_point_centroid":[0.46722,-0.10002,0.06493],"force_p95":134.32089,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":140.78788,"mean_force":114.91854,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50512,-0.02506,0.11053]},{"body_a":"peg","body_b":"link7","contact_count":946.0,"contact_point_centroid":[0.50208,0.05854,0.05664],"force_p95":84.82496,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":109.17909,"mean_force":56.41242,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53009,0.12701,0.09626]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":767.0,"contact_point_centroid":[0.475,0.05971,0.05998],"force_p95":99.94977,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":106.47545,"mean_force":74.90994,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52858,0.12433,0.09688]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49734,0.05104,0.00887],"force_p95":80.31718,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":92.96929,"mean_force":52.42533,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53104,0.12848,0.09641]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":119.0,"contact_point_centroid":[0.475,0.01494,0.05999],"force_p95":79.59672,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":87.73483,"mean_force":57.36345,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5206,0.08644,0.10407]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.475,0.04843,0.05997],"force_p95":86.60368,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.93737,"mean_force":84.26157,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52609,0.12124,0.10301]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":193.0,"contact_point_centroid":[0.54848,0.11926,0.05998],"force_p95":71.63729,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.51145,"mean_force":52.1023,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.58195,0.1929,0.09534]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.52502,0.08561,0.05998],"force_p95":68.72198,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.1813,"mean_force":54.50501,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54538,0.15169,0.09721]},{"body_a":"peg","body_b":"link7","contact_count":591.0,"contact_point_centroid":[0.49344,0.01388,0.05907],"force_p95":54.96772,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.94011,"mean_force":39.43094,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51897,0.07367,0.10441]},{"body_a":"peg","body_b":"channel_base_body","contact_count":999.0,"contact_point_centroid":[0.49386,-0.00545,0.0094],"force_p95":54.26276,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.86462,"mean_force":22.79082,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51447,0.04299,0.10601]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":814.0,"contact_point_centroid":[0.47456,0.04142,0.02683],"force_p95":22.84059,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.64033,"mean_force":10.77565,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52877,0.12467,0.09663]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49152,0.04,0.00958],"force_p95":24.12899,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.78928,"mean_force":19.91297,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52609,0.12124,0.10301]},{"body_a":"peg","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.49475,0.05104,0.05874],"force_p95":23.7788,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.44859,"mean_force":19.04345,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52609,0.12124,0.10301]}],"total_contact_groups":21},"final_pose_error":0.04964,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49559,-0.0056,0.03397],"final_tcp_position":[0.50449,-0.03086,0.11392],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":1415.49645,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":958.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06725,0.03391],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14741,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":301.49222,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1823.0,"raw_peak_contact_force":1415.49645,"tcp_end":[0.6715,0.27637,0.07191],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.2712,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50314,0.06741,0.03379],"object_pos_start":[0.50305,0.06725,0.03391],"object_to_goal_dist_end":0.14757,"object_to_goal_dist_start":0.14741,"object_z_max":0.03391,"peak_contact_force":0.54218,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1568.0,"raw_peak_contact_force":238.75918,"subtask_id":"approach","tcp_end":[0.55062,0.15747,0.10191],"tcp_start":[0.6715,0.27637,0.07191],"tcp_to_object_dist_end":0.1225,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49277,0.0333,0.03416],"object_pos_start":[0.50314,0.06741,0.03379],"object_to_goal_dist_end":0.11368,"object_to_goal_dist_start":0.14757,"object_z_max":0.03416,"peak_contact_force":101.36519,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3533.0,"raw_peak_contact_force":109.17909,"subtask_id":"contact","tcp_end":[0.5261,0.12125,0.10302],"tcp_start":[0.55062,0.15747,0.10191],"tcp_to_object_dist_end":0.11658,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49277,0.03328,0.03416],"object_pos_start":[0.49277,0.0333,0.03416],"object_to_goal_dist_end":0.11366,"object_to_goal_dist_start":0.11368,"object_z_max":0.03416,"peak_contact_force":82.24688,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":86.93737,"subtask_id":"push","tcp_end":[0.52607,0.12121,0.103],"tcp_start":[0.52608,0.12123,0.103],"tcp_to_object_dist_end":0.11653,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49559,-0.0056,0.03397],"object_pos_start":[0.49277,0.03326,0.03416],"object_to_goal_dist_end":0.07477,"object_to_goal_dist_start":0.11364,"object_z_max":0.03796,"peak_contact_force":95.25291,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2686.0,"raw_peak_contact_force":257.97997,"tcp_end":[0.50449,-0.03086,0.11392],"tcp_start":[0.52607,0.12121,0.103],"tcp_to_object_dist_end":0.08432,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40201,"average_solve_count":199.0,"average_success_count":199.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.09562,"approach_1.approach_height":0.08327,"approach_1.speed":0.06602,"contact_1.speed":0.02917,"push_1.impedance_stiffness":259.42296,"push_1.push_distance":0.11261,"retract_1.retract_height":0.14048,"retract_1.speed":0.06599},"optimized_scores":{"best_composite_score":-0.43229,"best_fitness_score":0.05771,"best_task_score":0.02064},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link6","contact_count":914.0,"contact_point_centroid":[0.54072,0.11829,0.05979],"force_p95":479.48259,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1349.58888,"mean_force":397.06459,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.61571,0.27188,0.16735]},{"body_a":"channel_base_body","body_b":"link6","contact_count":499.0,"contact_point_centroid":[0.42003,-0.10003,0.06494],"force_p95":401.20858,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":417.19812,"mean_force":305.55368,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4948,0.07917,0.13206]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":991.0,"contact_point_centroid":[0.44502,0.04521,0.05992],"force_p95":408.73536,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":413.31669,"mean_force":370.97319,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51208,0.1626,0.11873]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":343.0,"contact_point_centroid":[0.53981,0.11789,0.05998],"force_p95":123.49156,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":198.34301,"mean_force":87.48519,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.63691,0.26194,0.11473]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":138.0,"contact_point_centroid":[0.445,0.02621,0.05999],"force_p95":111.06923,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":120.35819,"mean_force":76.1574,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50491,0.15027,0.12486]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":196.0,"contact_point_centroid":[0.46465,0.06264,0.05999],"force_p95":96.17099,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":114.0566,"mean_force":69.42491,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.56246,0.20141,0.11459]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.44502,0.03375,0.05993],"force_p95":88.09549,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.12422,"mean_force":87.80467,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50753,0.15964,0.12506]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49779,0.10582,0.00946],"force_p95":40.62523,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.86385,"mean_force":5.97299,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.59684,0.22928,0.11433]},{"body_a":"peg","body_b":"link6","contact_count":179.0,"contact_point_centroid":[0.50771,0.10157,0.06003],"force_p95":46.24674,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.48443,"mean_force":30.9965,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.59335,0.22585,0.11335]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":156.0,"contact_point_centroid":[0.47487,0.10435,0.05045],"force_p95":16.46512,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.57023,"mean_force":3.28844,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.57514,0.21135,0.11413]},{"body_a":"peg","body_b":"channel_base_body","contact_count":978.0,"contact_point_centroid":[0.50308,0.11202,0.0094],"force_p95":0.65127,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.84899,"mean_force":0.67309,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.60517,0.26778,0.16754]},{"body_a":"peg","body_b":"link6","contact_count":39.0,"contact_point_centroid":[0.51935,0.11841,0.0563],"force_p95":19.30395,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.49188,"mean_force":3.1083,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.43068,0.27302,0.14013]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49311,0.10575,0.00939],"force_p95":0.597,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61473,"mean_force":0.54553,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49937,0.10162,0.12837]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49315,0.10572,0.0094],"force_p95":0.57283,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61442,"mean_force":0.54511,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51213,0.16263,0.11867]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.48621,0.10439,0.0094],"force_p95":0.59653,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60036,"mean_force":0.55585,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50753,0.15964,0.12506]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50132,0.19857,0.29678]}],"total_contact_groups":17},"final_pose_error":0.15997,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49307,0.10578,0.03382],"final_tcp_position":[0.4881,0.0795,0.13747],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":1349.58888,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50327,0.11177,0.03386],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":332.94197,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1947.0,"raw_peak_contact_force":1349.58888,"tcp_end":[0.66538,0.28229,0.11218],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.24798,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49311,0.10578,0.03381],"object_pos_start":[0.50327,0.11177,0.03386],"object_to_goal_dist_end":0.18601,"object_to_goal_dist_start":0.1919,"object_z_max":0.03588,"peak_contact_force":0.53049,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1874.0,"raw_peak_contact_force":198.34301,"subtask_id":"approach","tcp_end":[0.51838,0.16563,0.1124],"tcp_start":[0.66538,0.28229,0.11218],"tcp_to_object_dist_end":0.10197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49312,0.10578,0.03382],"object_pos_start":[0.49311,0.10578,0.03381],"object_to_goal_dist_end":0.18602,"object_to_goal_dist_start":0.18601,"object_z_max":0.03395,"peak_contact_force":404.71438,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2005.0,"raw_peak_contact_force":413.31669,"subtask_id":"contact","tcp_end":[0.50753,0.15963,0.12506],"tcp_start":[0.51838,0.16563,0.1124],"tcp_to_object_dist_end":0.10692,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49308,0.1058,0.03381],"object_pos_start":[0.49312,0.10578,0.03382],"object_to_goal_dist_end":0.18603,"object_to_goal_dist_start":0.18602,"object_z_max":0.03382,"peak_contact_force":87.83699,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":88.12422,"subtask_id":"push","tcp_end":[0.50753,0.15965,0.12507],"tcp_start":[0.50753,0.15964,0.12507],"tcp_to_object_dist_end":0.10695,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49307,0.10578,0.03382],"object_pos_start":[0.49307,0.10581,0.03381],"object_to_goal_dist_end":0.18601,"object_to_goal_dist_start":0.18604,"object_z_max":0.03387,"peak_contact_force":403.59878,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1637.0,"raw_peak_contact_force":417.19812,"tcp_end":[0.4881,0.0795,0.13747],"tcp_start":[0.50753,0.15965,0.12507],"tcp_to_object_dist_end":0.10705,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```