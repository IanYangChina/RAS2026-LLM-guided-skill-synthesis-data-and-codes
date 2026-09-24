## Search State

- **Seed**: 5
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.2993 | 0.00 | ✅ accepted |
| 0 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.2993 | 0.00 | ✅ accepted |

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

## Current Skill (Q=-0.299) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
- id: pull_1
  type: pull
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    pull_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: release_2
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: release_3
  type: release
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  end_effector_action: open
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
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

- **Composite score**: -0.299
- **task_score** (E): 0.001
- **fitness_score**: 0.001  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| push_1 | 1.00 | 1.00 | 0.2044 |
| release_1 | 1.00 | 1.00 | 0.0099 |
| pull_1 | 1.00 | 1.00 | 0.1668 |
| release_2 | 1.00 | 1.00 | 0.2636 |
| release_3 | 1.00 | 1.00 | 0.0049 |
| grasp_1 | 1.00 | 1.00 | 0.0004 |
| retract_1 | 0.00 | 1.00 | 0.1084 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| push_1 | push | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.497, 0.099, 0.123) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.550 | 2.488 |
| release_1 | release | 1.00 / step_budget | (0.497, 0.099, 0.123)→(0.491, 0.098, 0.115) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.540 | 0.589 |
| pull_1 | pull | 1.00 / time_limit | (0.491, 0.098, 0.115)→(0.491, 0.049, 0.274) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.535 | 0.590 |
| release_2 | release | 1.00 / step_budget | (0.491, 0.049, 0.274)→(0.492, -0.073, 0.041) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.546 | 0.590 |
| release_3 | release | 1.00 / time_limit | (0.492, -0.073, 0.041)→(0.495, -0.075, 0.039) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 2.000 | 70.890 | 213.204 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, -0.075, 0.039)→(0.496, -0.075, 0.038) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 2.000 | 68.570 | 78.527 |
| retract_1 | retract | 0.00 / step_budget | (0.496, -0.075, 0.038)→(0.494, -0.043, 0.142) | (0.504, 0.095, 0.034)→(0.504, 0.094, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.541 | 77.633 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.002
- alignment_error: None
- force_efficiency: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.001
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: -0.300
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.483


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71204,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"pull_1.pull_distance":0.07389,"push_1.push_depth":0.04257,"retract_1.speed":0.07181},"optimized_scores":{"best_composite_score":-0.29964,"best_fitness_score":0.00036,"best_task_score":0.00036},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":460.0,"contact_point_centroid":[0.53654,-0.1,0.06497],"force_p95":201.35643,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":213.27472,"mean_force":138.74666,"phase_index":4.0,"phase_name":"release_3","phase_type":"release","tcp_position_centroid":[0.49373,-0.07413,0.03865]},{"body_a":"channel_base_body","body_b":"link7","contact_count":450.0,"contact_point_centroid":[0.53841,-0.1,0.06498],"force_p95":78.09783,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.51891,"mean_force":73.38508,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49571,-0.07434,0.03844]},{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53856,-0.1,0.06498],"force_p95":75.71489,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.59838,"mean_force":59.01919,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49587,-0.07426,0.03841]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50574,0.10468,0.00938],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.55797,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49727,0.14975,0.20233]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49941,0.19859,0.29738]},{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.50606,0.10435,0.00939],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57575,"mean_force":0.5463,"phase_index":1.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49258,0.10266,0.10943]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.5059,0.10465,0.00939],"force_p95":0.57565,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57571,"mean_force":0.54633,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.48866,0.09066,0.18513]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1024.0,"contact_point_centroid":[0.50585,0.10467,0.00939],"force_p95":0.57557,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57562,"mean_force":0.54633,"phase_index":3.0,"phase_name":"release_2","phase_type":"release","tcp_position_centroid":[0.49237,-0.01804,0.13867]},{"body_a":"peg","body_b":"channel_base_body","contact_count":489.0,"contact_point_centroid":[0.50578,0.10451,0.00939],"force_p95":0.57551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57553,"mean_force":0.54633,"phase_index":4.0,"phase_name":"release_3","phase_type":"release","tcp_position_centroid":[0.49359,-0.07407,0.03873]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50602,0.10464,0.00939],"force_p95":0.57547,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57549,"mean_force":0.54633,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49571,-0.07434,0.03844]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50586,0.10463,0.00939],"force_p95":0.5754,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57545,"mean_force":0.54633,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49339,-0.05649,0.09544]}],"total_contact_groups":11},"final_pose_error":0.15269,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50587,0.10452,0.03384],"final_tcp_position":[0.49459,-0.04023,0.1528],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":213.27472,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54104,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1005.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.49652,0.10362,0.11495],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08167,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50584,0.10459,0.03384],"object_pos_start":[0.50599,0.10464,0.03384],"object_to_goal_dist_end":0.18478,"object_to_goal_dist_start":0.18484,"object_z_max":0.03384,"peak_contact_force":0.55188,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":200.0,"raw_peak_contact_force":0.57575,"tcp_end":[0.49076,0.10231,0.10691],"tcp_start":[0.49652,0.10362,0.11495],"tcp_to_object_dist_end":0.07465,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50586,0.10456,0.03384],"object_pos_start":[0.50584,0.10459,0.03384],"object_to_goal_dist_end":0.18475,"object_to_goal_dist_start":0.18478,"object_z_max":0.03384,"peak_contact_force":0.55164,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.57571,"tcp_end":[0.49088,0.05588,0.26784],"tcp_start":[0.49076,0.10231,0.10691],"tcp_to_object_dist_end":0.23948,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":874.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.10458,0.03384],"object_pos_start":[0.50586,0.10456,0.03384],"object_to_goal_dist_end":0.18478,"object_to_goal_dist_start":0.18475,"object_z_max":0.03384,"peak_contact_force":0.53565,"phase_name":"release_2","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.57562,"tcp_end":[0.49158,-0.07285,0.04107],"tcp_start":[0.49088,0.05588,0.26784],"tcp_to_object_dist_end":0.17816,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.50586,0.10469,0.03384],"object_pos_start":[0.50596,0.10458,0.03384],"object_to_goal_dist_end":0.18489,"object_to_goal_dist_start":0.18478,"object_z_max":0.03384,"peak_contact_force":71.51306,"phase_name":"release_3","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":949.0,"raw_peak_contact_force":213.27472,"tcp_end":[0.4955,-0.07441,0.0385],"tcp_start":[0.49158,-0.07285,0.04107],"tcp_to_object_dist_end":0.17946,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50584,0.10454,0.03384],"object_pos_start":[0.50586,0.10469,0.03384],"object_to_goal_dist_end":0.18473,"object_to_goal_dist_start":0.18489,"object_z_max":0.03384,"peak_contact_force":68.56431,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":900.0,"raw_peak_contact_force":78.51891,"tcp_end":[0.49587,-0.07427,0.03841],"tcp_start":[0.4955,-0.07441,0.0385],"tcp_to_object_dist_end":0.17914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50587,0.10452,0.03384],"object_pos_start":[0.50584,0.10454,0.03384],"object_to_goal_dist_end":0.18472,"object_to_goal_dist_start":0.18473,"object_z_max":0.03384,"peak_contact_force":0.54427,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1003.0,"raw_peak_contact_force":77.59838,"tcp_end":[0.49459,-0.04023,0.1528],"tcp_start":[0.49587,-0.07427,0.03841],"tcp_to_object_dist_end":0.18771,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6178,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"pull_1.pull_distance":0.09828,"push_1.push_depth":0.06528,"retract_1.speed":0.06389},"optimized_scores":{"best_composite_score":-0.29976,"best_fitness_score":0.00024,"best_task_score":0.00024},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":421.0,"contact_point_centroid":[0.53646,-0.1,0.06498],"force_p95":207.9182,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":217.93277,"mean_force":137.53569,"phase_index":4.0,"phase_name":"release_3","phase_type":"release","tcp_position_centroid":[0.4936,-0.07546,0.03889]},{"body_a":"channel_base_body","body_b":"link7","contact_count":450.0,"contact_point_centroid":[0.53786,-0.1,0.06498],"force_p95":78.09836,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.57904,"mean_force":73.39358,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49508,-0.07545,0.03871]},{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53801,-0.1,0.06498],"force_p95":75.3019,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.75284,"mean_force":56.62424,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49525,-0.07537,0.03868]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50307,0.06748,0.00936],"force_p95":0.55225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55539,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49738,0.14054,0.21834]},{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.50311,0.06729,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55071,"mean_force":0.54666,"phase_index":1.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49306,0.08435,0.13969]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50304,0.06744,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55066,"mean_force":0.54665,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.48968,0.06864,0.21426]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1028.0,"contact_point_centroid":[0.50302,0.06746,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55057,"mean_force":0.54664,"phase_index":3.0,"phase_name":"release_2","phase_type":"release","tcp_position_centroid":[0.49311,-0.03075,0.15072]},{"body_a":"peg","body_b":"channel_base_body","contact_count":463.0,"contact_point_centroid":[0.50312,0.06754,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55055,"mean_force":0.54665,"phase_index":4.0,"phase_name":"release_3","phase_type":"release","tcp_position_centroid":[0.4934,-0.07538,0.03906]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50304,0.06746,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55055,"mean_force":0.54665,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49508,-0.07545,0.03871]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50305,0.06744,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55055,"mean_force":0.54665,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49275,-0.05901,0.0898]}],"total_contact_groups":10},"final_pose_error":0.16461,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50303,0.06742,0.0338],"final_tcp_position":[0.49393,-0.04411,0.14152],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":217.93277,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54571,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":984.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49671,0.08514,0.14515],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11293,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54743,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":200.0,"raw_peak_contact_force":0.55071,"tcp_end":[0.49134,0.08408,0.13719],"tcp_start":[0.49671,0.08514,0.14515],"tcp_to_object_dist_end":0.10537,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.503,0.06745,0.0338],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54669,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55066,"tcp_end":[0.49232,0.02734,0.29321],"tcp_start":[0.49134,0.08408,0.13719],"tcp_to_object_dist_end":0.26271,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":878.0,"n_steps_budget":1000.0,"object_pos_end":[0.50303,0.0675,0.0338],"object_pos_start":[0.503,0.06745,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14761,"object_z_max":0.0338,"peak_contact_force":0.54564,"phase_name":"release_2","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.55057,"tcp_end":[0.49168,-0.07409,0.04243],"tcp_start":[0.49232,0.02734,0.29321],"tcp_to_object_dist_end":0.1423,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":313.0,"n_steps_budget":600.0,"object_pos_end":[0.50306,0.06743,0.0338],"object_pos_start":[0.50303,0.0675,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":70.17803,"phase_name":"release_3","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":884.0,"raw_peak_contact_force":217.93277,"tcp_end":[0.49488,-0.07552,0.03877],"tcp_start":[0.49168,-0.07409,0.04243],"tcp_to_object_dist_end":0.14328,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50306,0.06743,0.0338],"object_pos_start":[0.50306,0.06743,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":68.5786,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":900.0,"raw_peak_contact_force":78.57904,"tcp_end":[0.49525,-0.07538,0.03868],"tcp_start":[0.49488,-0.07552,0.03877],"tcp_to_object_dist_end":0.14311,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50303,0.06742,0.0338],"object_pos_start":[0.50306,0.06743,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.5478,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1003.0,"raw_peak_contact_force":77.75284,"tcp_end":[0.49393,-0.04411,0.14152],"tcp_start":[0.49525,-0.07538,0.03868],"tcp_to_object_dist_end":0.15533,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51269,"average_solve_count":197.0,"average_success_count":197.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"pull_1.pull_distance":0.14542,"push_1.push_depth":0.03694,"retract_1.speed":0.05179},"optimized_scores":{"best_composite_score":-0.29859,"best_fitness_score":0.00141,"best_task_score":0.00141},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":465.0,"contact_point_centroid":[0.53659,-0.10001,0.06497],"force_p95":197.53172,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":208.40393,"mean_force":139.30273,"phase_index":4.0,"phase_name":"release_3","phase_type":"release","tcp_position_centroid":[0.49379,-0.07378,0.03858]},{"body_a":"channel_base_body","body_b":"link7","contact_count":450.0,"contact_point_centroid":[0.53841,-0.1,0.06498],"force_p95":78.07841,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.48397,"mean_force":73.38029,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49572,-0.074,0.03838]},{"body_a":"channel_base_body","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.53856,-0.1,0.06499],"force_p95":73.78485,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.5464,"mean_force":53.95493,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49588,-0.07392,0.03836]},{"body_a":"peg","body_b":"channel_base_body","contact_count":978.0,"contact_point_centroid":[0.50365,0.11171,0.00938],"force_p95":0.60969,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55293,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49726,0.15304,0.19971]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50366,0.11144,0.00942],"force_p95":0.5936,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64692,"mean_force":0.54307,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49315,-0.0591,0.08518]},{"body_a":"peg","body_b":"channel_base_body","contact_count":489.0,"contact_point_centroid":[0.50373,0.11161,0.00941],"force_p95":0.59914,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64603,"mean_force":0.54363,"phase_index":4.0,"phase_name":"release_3","phase_type":"release","tcp_position_centroid":[0.49367,-0.07374,0.03864]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1026.0,"contact_point_centroid":[0.50366,0.11156,0.00942],"force_p95":0.5995,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6452,"mean_force":0.543,"phase_index":3.0,"phase_name":"release_2","phase_type":"release","tcp_position_centroid":[0.49223,-0.01474,0.13563]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50371,0.11162,0.00941],"force_p95":0.60111,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64416,"mean_force":0.54396,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.48847,0.09694,0.17873]},{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.50356,0.11167,0.0094],"force_p95":0.59117,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64166,"mean_force":0.54505,"phase_index":1.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49249,0.10851,0.1033]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50375,0.11153,0.00941],"force_p95":0.58646,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63255,"mean_force":0.54402,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49572,-0.074,0.03838]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49965,0.19926,0.29909]}],"total_contact_groups":11},"final_pose_error":0.1737,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50372,0.11154,0.03383],"final_tcp_position":[0.49409,-0.04573,0.13254],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":208.40393,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5037,0.1117,0.03384],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19184,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.56382,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":994.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.49648,0.10951,0.10886],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0754,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,0.11174,0.03383],"object_pos_start":[0.5037,0.1117,0.03384],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19184,"object_z_max":0.03386,"peak_contact_force":0.52075,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":200.0,"raw_peak_contact_force":0.64166,"tcp_end":[0.49064,0.10813,0.10077],"tcp_start":[0.49648,0.10951,0.10886],"tcp_to_object_dist_end":0.0683,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11172,0.03389],"object_pos_start":[0.50368,0.11174,0.03383],"object_to_goal_dist_end":0.19185,"object_to_goal_dist_start":0.19187,"object_z_max":0.034,"peak_contact_force":0.5075,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.64416,"tcp_end":[0.49059,0.06346,0.26163],"tcp_start":[0.49064,0.10813,0.10077],"tcp_to_object_dist_end":0.23317,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":876.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11164,0.03382],"object_pos_start":[0.50372,0.11172,0.03389],"object_to_goal_dist_end":0.19178,"object_to_goal_dist_start":0.19185,"object_z_max":0.03399,"peak_contact_force":0.55737,"phase_name":"release_2","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.6452,"tcp_end":[0.49156,-0.07262,0.04059],"tcp_start":[0.49059,0.06346,0.26163],"tcp_to_object_dist_end":0.18479,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.50375,0.11162,0.03385],"object_pos_start":[0.50375,0.11164,0.03382],"object_to_goal_dist_end":0.19175,"object_to_goal_dist_start":0.19178,"object_z_max":0.034,"peak_contact_force":70.97874,"phase_name":"release_3","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":954.0,"raw_peak_contact_force":208.40393,"tcp_end":[0.49551,-0.07407,0.03844],"tcp_start":[0.49156,-0.07262,0.04059],"tcp_to_object_dist_end":0.18592,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50372,0.11162,0.03391],"object_pos_start":[0.50375,0.11162,0.03385],"object_to_goal_dist_end":0.19176,"object_to_goal_dist_start":0.19175,"object_z_max":0.03399,"peak_contact_force":68.56586,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":900.0,"raw_peak_contact_force":78.48397,"tcp_end":[0.49588,-0.07393,0.03835],"tcp_start":[0.49551,-0.07407,0.03844],"tcp_to_object_dist_end":0.18577,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11154,0.03383],"object_pos_start":[0.50372,0.11162,0.03391],"object_to_goal_dist_end":0.19167,"object_to_goal_dist_start":0.19176,"object_z_max":0.03402,"peak_contact_force":0.53017,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1004.0,"raw_peak_contact_force":77.5464,"tcp_end":[0.49409,-0.04573,0.13254],"tcp_start":[0.49588,-0.07393,0.03835],"tcp_to_object_dist_end":0.18592,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```