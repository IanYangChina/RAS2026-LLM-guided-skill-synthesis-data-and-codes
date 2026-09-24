## Search State

- **Seed**: 5
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.2993 | 0.00 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → insert → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | -0.5799 | 0.00 | ❌ rejected |
| 4 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.2994 | 0.00 | ❌ rejected |
| 3 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.2993 | 0.00 | ✅ accepted |
| 2 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.2993 | 0.00 | ✅ accepted |

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
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

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
| push_1 | 1.00 | 1.00 | 0.2025 |
| release_1 | 1.00 | 1.00 | 0.0098 |
| pull_1 | 1.00 | 1.00 | 0.1667 |
| release_2 | 1.00 | 1.00 | 0.2644 |
| release_3 | 1.00 | 1.00 | 0.0050 |
| grasp_1 | 1.00 | 1.00 | 0.0004 |
| retract_1 | 0.00 | 1.00 | 0.1133 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| push_1 | push | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.497, 0.096, 0.127) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.544 | 2.488 |
| release_1 | release | 1.00 / step_budget | (0.497, 0.096, 0.127)→(0.491, 0.095, 0.119) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.550 | 0.585 |
| pull_1 | pull | 1.00 / time_limit | (0.491, 0.095, 0.119)→(0.491, 0.045, 0.278) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.550 | 0.591 |
| release_2 | release | 1.00 / step_budget | (0.491, 0.045, 0.278)→(0.492, -0.073, 0.042) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.531 | 0.589 |
| release_3 | release | 1.00 / time_limit | (0.492, -0.073, 0.042)→(0.495, -0.075, 0.039) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 2.000 | 70.703 | 215.667 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, -0.075, 0.039)→(0.496, -0.075, 0.039) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 2.000 | 68.569 | 78.567 |
| retract_1 | retract | 0.00 / step_budget | (0.496, -0.075, 0.039)→(0.494, -0.042, 0.147) | (0.504, 0.095, 0.034)→(0.504, 0.094, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.539 | 77.659 |

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
- **Final σ (mean)**: 0.341


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9b36d26f861d7a613dfb3d8c86d70470e42095a430c2befa4bd6e530468a8a7e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2af86d8f59685db6584febc0596b9044223ae39cea3120c112c665a54a1c4732`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50754,"average_solve_count":199.0,"average_success_count":199.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"pull_1.pull_distance":0.03322,"push_1.push_depth":0.04117,"retract_1.speed":0.05016},"optimized_scores":{"best_composite_score":-0.29964,"best_fitness_score":0.00036,"best_task_score":0.00036},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":459.0,"contact_point_centroid":[0.53654,-0.10001,0.06497],"force_p95":201.16084,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":213.46806,"mean_force":139.09663,"phase_index":4.0,"phase_name":"release_3","phase_type":"release","tcp_position_centroid":[0.49372,-0.07412,0.03865]},{"body_a":"channel_base_body","body_b":"link7","contact_count":450.0,"contact_point_centroid":[0.5384,-0.1,0.06498],"force_p95":78.09716,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.51323,"mean_force":73.38538,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4957,-0.07433,0.03845]},{"body_a":"channel_base_body","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.53855,-0.1,0.06498],"force_p95":73.75193,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.59729,"mean_force":53.65891,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49586,-0.07425,0.03842]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50574,0.10468,0.00938],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.55797,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49727,0.15007,0.20199]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49941,0.1986,0.29738]},{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.50606,0.10435,0.00939],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57575,"mean_force":0.5463,"phase_index":1.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49256,0.10327,0.10875]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.5059,0.10465,0.00939],"force_p95":0.57565,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57571,"mean_force":0.54633,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.48864,0.0912,0.18469]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1024.0,"contact_point_centroid":[0.50585,0.10467,0.00939],"force_p95":0.57557,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57562,"mean_force":0.54633,"phase_index":3.0,"phase_name":"release_2","phase_type":"release","tcp_position_centroid":[0.49237,-0.01784,0.13858]},{"body_a":"peg","body_b":"channel_base_body","contact_count":489.0,"contact_point_centroid":[0.50578,0.10451,0.00939],"force_p95":0.57551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57553,"mean_force":0.54633,"phase_index":4.0,"phase_name":"release_3","phase_type":"release","tcp_position_centroid":[0.49358,-0.07407,0.03873]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50602,0.10464,0.00939],"force_p95":0.57547,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57549,"mean_force":0.54633,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4957,-0.07433,0.03845]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50586,0.10463,0.00939],"force_p95":0.5754,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57545,"mean_force":0.54633,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49313,-0.05936,0.08526]}],"total_contact_groups":11},"final_pose_error":0.17367,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50587,0.10452,0.03384],"final_tcp_position":[0.49405,-0.04592,0.13262],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":213.46806,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54104,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1005.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.4965,0.10421,0.11425],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08097,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50584,0.10459,0.03384],"object_pos_start":[0.50599,0.10464,0.03384],"object_to_goal_dist_end":0.18478,"object_to_goal_dist_start":0.18484,"object_z_max":0.03384,"peak_contact_force":0.55188,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":200.0,"raw_peak_contact_force":0.57575,"tcp_end":[0.49073,0.10291,0.10622],"tcp_start":[0.4965,0.10421,0.11425],"tcp_to_object_dist_end":0.07397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50586,0.10456,0.03384],"object_pos_start":[0.50584,0.10459,0.03384],"object_to_goal_dist_end":0.18475,"object_to_goal_dist_start":0.18478,"object_z_max":0.03384,"peak_contact_force":0.55164,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.57571,"tcp_end":[0.49086,0.0563,0.26764],"tcp_start":[0.49073,0.10291,0.10622],"tcp_to_object_dist_end":0.2392,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":874.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.10458,0.03384],"object_pos_start":[0.50586,0.10456,0.03384],"object_to_goal_dist_end":0.18478,"object_to_goal_dist_start":0.18475,"object_z_max":0.03384,"peak_contact_force":0.53565,"phase_name":"release_2","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.57562,"tcp_end":[0.49158,-0.07282,0.04109],"tcp_start":[0.49086,0.0563,0.26764],"tcp_to_object_dist_end":0.17812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.50586,0.10469,0.03384],"object_pos_start":[0.50596,0.10458,0.03384],"object_to_goal_dist_end":0.18489,"object_to_goal_dist_start":0.18478,"object_z_max":0.03384,"peak_contact_force":71.58779,"phase_name":"release_3","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":948.0,"raw_peak_contact_force":213.46806,"tcp_end":[0.49549,-0.0744,0.03851],"tcp_start":[0.49158,-0.07282,0.04109],"tcp_to_object_dist_end":0.17946,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50584,0.10454,0.03384],"object_pos_start":[0.50586,0.10469,0.03384],"object_to_goal_dist_end":0.18473,"object_to_goal_dist_start":0.18489,"object_z_max":0.03384,"peak_contact_force":68.5651,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":900.0,"raw_peak_contact_force":78.51323,"tcp_end":[0.49586,-0.07426,0.03841],"tcp_start":[0.49549,-0.0744,0.03851],"tcp_to_object_dist_end":0.17914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50587,0.10452,0.03384],"object_pos_start":[0.50584,0.10454,0.03384],"object_to_goal_dist_end":0.18472,"object_to_goal_dist_start":0.18473,"object_z_max":0.03384,"peak_contact_force":0.54427,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1004.0,"raw_peak_contact_force":77.59729,"tcp_end":[0.49405,-0.04592,0.13262],"tcp_start":[0.49586,-0.07426,0.03841],"tcp_to_object_dist_end":0.18037,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50761,"average_solve_count":197.0,"average_success_count":197.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"pull_1.pull_distance":0.17643,"push_1.push_depth":0.06345,"retract_1.speed":0.05104},"optimized_scores":{"best_composite_score":-0.29976,"best_fitness_score":0.00024,"best_task_score":0.00024},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":422.0,"contact_point_centroid":[0.53646,-0.1,0.06498],"force_p95":207.83357,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":217.91419,"mean_force":137.224,"phase_index":4.0,"phase_name":"release_3","phase_type":"release","tcp_position_centroid":[0.4936,-0.07543,0.03889]},{"body_a":"channel_base_body","body_b":"link7","contact_count":450.0,"contact_point_centroid":[0.53786,-0.1,0.06498],"force_p95":78.09749,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.57771,"mean_force":73.39348,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49509,-0.07543,0.0387]},{"body_a":"channel_base_body","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.53801,-0.1,0.06498],"force_p95":73.90211,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.7495,"mean_force":53.81551,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49525,-0.07535,0.03868]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50307,0.06748,0.00936],"force_p95":0.55225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55539,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49738,0.14079,0.21795]},{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.50311,0.06729,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55071,"mean_force":0.54666,"phase_index":1.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49303,0.08475,0.13881]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50304,0.06744,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55066,"mean_force":0.54665,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.48964,0.06905,0.21368]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1028.0,"contact_point_centroid":[0.50302,0.06746,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55057,"mean_force":0.54664,"phase_index":3.0,"phase_name":"release_2","phase_type":"release","tcp_position_centroid":[0.4931,-0.0306,0.1506]},{"body_a":"peg","body_b":"channel_base_body","contact_count":463.0,"contact_point_centroid":[0.50312,0.06754,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55055,"mean_force":0.54665,"phase_index":4.0,"phase_name":"release_3","phase_type":"release","tcp_position_centroid":[0.49341,-0.07535,0.03906]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50304,0.06746,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55055,"mean_force":0.54665,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49509,-0.07543,0.0387]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50305,0.06744,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55055,"mean_force":0.54665,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49265,-0.06018,0.08564]}],"total_contact_groups":10},"final_pose_error":0.17337,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50303,0.06742,0.0338],"final_tcp_position":[0.49367,-0.04651,0.13311],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":217.91419,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54571,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":984.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49668,0.08552,0.14425],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11211,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54743,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":200.0,"raw_peak_contact_force":0.55071,"tcp_end":[0.49131,0.08447,0.13631],"tcp_start":[0.49668,0.08552,0.14425],"tcp_to_object_dist_end":0.10458,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.503,0.06745,0.0338],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54669,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55066,"tcp_end":[0.49229,0.02767,0.29294],"tcp_start":[0.49131,0.08447,0.13631],"tcp_to_object_dist_end":0.26239,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":878.0,"n_steps_budget":1000.0,"object_pos_end":[0.50303,0.0675,0.0338],"object_pos_start":[0.503,0.06745,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14761,"object_z_max":0.0338,"peak_contact_force":0.54564,"phase_name":"release_2","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.55057,"tcp_end":[0.49168,-0.07407,0.04241],"tcp_start":[0.49229,0.02767,0.29294],"tcp_to_object_dist_end":0.14229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":313.0,"n_steps_budget":600.0,"object_pos_end":[0.50306,0.06743,0.0338],"object_pos_start":[0.50303,0.0675,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":70.18154,"phase_name":"release_3","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":885.0,"raw_peak_contact_force":217.91419,"tcp_end":[0.49488,-0.0755,0.03876],"tcp_start":[0.49168,-0.07407,0.04241],"tcp_to_object_dist_end":0.14325,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50306,0.06743,0.0338],"object_pos_start":[0.50306,0.06743,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":68.57878,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":900.0,"raw_peak_contact_force":78.57771,"tcp_end":[0.49525,-0.07535,0.03867],"tcp_start":[0.49488,-0.0755,0.03876],"tcp_to_object_dist_end":0.14308,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50303,0.06742,0.0338],"object_pos_start":[0.50306,0.06743,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.5478,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1004.0,"raw_peak_contact_force":77.7495,"tcp_end":[0.49367,-0.04651,0.13311],"tcp_start":[0.49525,-0.07535,0.03867],"tcp_to_object_dist_end":0.15143,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71728,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"pull_1.pull_distance":0.11919,"push_1.push_depth":0.06224,"retract_1.speed":0.08655},"optimized_scores":{"best_composite_score":-0.29851,"best_fitness_score":0.00149,"best_task_score":0.00149},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":457.0,"contact_point_centroid":[0.53651,-0.1,0.06497],"force_p95":205.03631,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":215.61796,"mean_force":138.32689,"phase_index":4.0,"phase_name":"release_3","phase_type":"release","tcp_position_centroid":[0.49369,-0.07437,0.0387]},{"body_a":"channel_base_body","body_b":"link7","contact_count":450.0,"contact_point_centroid":[0.53836,-0.1,0.06498],"force_p95":78.10074,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.60958,"mean_force":73.38716,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49565,-0.07456,0.03849]},{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53851,-0.1,0.06498],"force_p95":75.82837,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.63121,"mean_force":61.65242,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49581,-0.07448,0.03846]},{"body_a":"peg","body_b":"channel_base_body","contact_count":978.0,"contact_point_centroid":[0.50361,0.1117,0.00938],"force_p95":0.60828,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55297,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4973,0.14745,0.20608]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50369,0.11161,0.00942],"force_p95":0.60579,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64698,"mean_force":0.5427,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.48885,0.08566,0.19087]},{"body_a":"peg","body_b":"channel_base_body","contact_count":489.0,"contact_point_centroid":[0.50372,0.11152,0.00942],"force_p95":0.59809,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64599,"mean_force":0.54319,"phase_index":4.0,"phase_name":"release_3","phase_type":"release","tcp_position_centroid":[0.49354,-0.07431,0.03879]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1021.0,"contact_point_centroid":[0.50366,0.11158,0.00941],"force_p95":0.59763,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63995,"mean_force":0.54377,"phase_index":3.0,"phase_name":"release_2","phase_type":"release","tcp_position_centroid":[0.49249,-0.02046,0.14073]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50367,0.11152,0.00941],"force_p95":0.59602,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63634,"mean_force":0.54398,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49362,-0.05369,0.10598]},{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.50363,0.11164,0.00942],"force_p95":0.59111,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62846,"mean_force":0.54292,"phase_index":1.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49269,0.09793,0.11616]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50368,0.11146,0.00941],"force_p95":0.59399,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62482,"mean_force":0.54351,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49565,-0.07456,0.03849]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49964,0.19921,0.29913]}],"total_contact_groups":11},"final_pose_error":0.12942,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5037,0.11152,0.03387],"final_tcp_position":[0.49506,-0.03401,0.17522],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":215.61796,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11177,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.54493,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":994.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.49657,0.09884,0.12167],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0891,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,0.11174,0.03392],"object_pos_start":[0.50371,0.11177,0.0338],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19191,"object_z_max":0.03398,"peak_contact_force":0.55193,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":200.0,"raw_peak_contact_force":0.62846,"tcp_end":[0.49089,0.0976,0.11365],"tcp_start":[0.49657,0.09884,0.12167],"tcp_to_object_dist_end":0.08199,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50367,0.11173,0.03391],"object_pos_start":[0.50374,0.11174,0.03392],"object_to_goal_dist_end":0.19186,"object_to_goal_dist_start":0.19187,"object_z_max":0.034,"peak_contact_force":0.5502,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.64698,"tcp_end":[0.49111,0.05046,0.27227],"tcp_start":[0.49089,0.0976,0.11365],"tcp_to_object_dist_end":0.24643,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":871.0,"n_steps_budget":1000.0,"object_pos_end":[0.5037,0.11163,0.03381],"object_pos_start":[0.50367,0.11173,0.03391],"object_to_goal_dist_end":0.19177,"object_to_goal_dist_start":0.19186,"object_z_max":0.034,"peak_contact_force":0.51189,"phase_name":"release_2","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.63995,"tcp_end":[0.4916,-0.07307,0.04134],"tcp_start":[0.49111,0.05046,0.27227],"tcp_to_object_dist_end":0.18524,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.50372,0.11172,0.03387],"object_pos_start":[0.5037,0.11163,0.03381],"object_to_goal_dist_end":0.19186,"object_to_goal_dist_start":0.19177,"object_z_max":0.03407,"peak_contact_force":70.33866,"phase_name":"release_3","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":946.0,"raw_peak_contact_force":215.61796,"tcp_end":[0.49544,-0.07463,0.03855],"tcp_start":[0.4916,-0.07307,0.04134],"tcp_to_object_dist_end":0.1866,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,0.11163,0.03383],"object_pos_start":[0.50372,0.11172,0.03387],"object_to_goal_dist_end":0.19176,"object_to_goal_dist_start":0.19186,"object_z_max":0.034,"peak_contact_force":68.56326,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":900.0,"raw_peak_contact_force":78.60958,"tcp_end":[0.49581,-0.07449,0.03846],"tcp_start":[0.49544,-0.07463,0.03855],"tcp_to_object_dist_end":0.18634,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5037,0.11152,0.03387],"object_pos_start":[0.50368,0.11163,0.03383],"object_to_goal_dist_end":0.19166,"object_to_goal_dist_start":0.19176,"object_z_max":0.03396,"peak_contact_force":0.52481,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1003.0,"raw_peak_contact_force":77.63121,"tcp_end":[0.49506,-0.03401,0.17522],"tcp_start":[0.49581,-0.07449,0.03846],"tcp_to_object_dist_end":0.20307,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```