## Search State

- **Seed**: 5
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → grasp → lift → push → retract | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2552 | 0.00 | ❌ rejected |
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

## Current Skill (Q=-0.255) — your mutation base

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

- **Composite score**: -0.255
- **task_score** (E): 0.000
- **fitness_score**: 0.135  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1676 |
| grasp_peg | 1.00 | 1.00 | 0.0000 |
| lift_peg | 1.00 | 1.00 | 0.0235 |
| insert_peg | 0.33 | 1.00 | 0.1165 |
| retract_peg | 1.00 | 1.00 | 0.0900 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.111, 0.159) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.333 | 75.396 | 76.834 |
| grasp_peg | grasp | 1.00 / step_budget | (0.505, 0.111, 0.154)→(0.505, 0.111, 0.154) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.333 | 26.286 | 44.143 |
| lift_peg | lift | 1.00 / step_budget | (0.505, 0.111, 0.154)→(0.503, 0.111, 0.177) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.553 | 22.523 |
| insert_peg | push | 0.33 / step_budget | (0.503, 0.111, 0.177)→(0.503, 0.227, 0.168) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.553 | 0.590 |
| retract_peg | retract | 1.00 / step_budget | (0.503, 0.227, 0.168)→(0.501, 0.227, 0.258) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.533 | 0.587 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.001
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.001
- phase_score: 0.266
- phase_breakdown.grasp_peg_score: 1.000
- phase_breakdown.reach_peg_score: 0.828
- phase_breakdown.insert_peg_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.160
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: -0.255
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: approach_peg.approach_speed
- **Final σ (mean)**: 0.447


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12707,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.07895,"insert_peg.insert_distance":0.171,"insert_peg.insert_speed":0.00879,"lift_peg.lift_height":0.028,"lift_peg.lift_speed":0.02177,"retract_peg.retract_speed":0.07869},"optimized_scores":{"best_composite_score":-0.25541,"best_fitness_score":0.13459,"best_task_score":0.00029},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50574,0.10468,0.00938],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.55797,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5021,0.15647,0.22152]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49073,0.18149,0.2783]},{"body_a":"peg","body_b":"channel_base_body","contact_count":550.0,"contact_point_centroid":[0.50597,0.10456,0.00939],"force_p95":0.5757,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57575,"mean_force":0.54631,"phase_index":1.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.51413,0.11848,0.15128]},{"body_a":"peg","body_b":"channel_base_body","contact_count":665.0,"contact_point_centroid":[0.50585,0.10459,0.00939],"force_p95":0.57564,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57568,"mean_force":0.54635,"phase_index":2.0,"phase_name":"lift_peg","phase_type":"lift","tcp_position_centroid":[0.51106,0.11855,0.15968]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50589,0.10463,0.00939],"force_p95":0.57557,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57562,"mean_force":0.54633,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"push","tcp_position_centroid":[0.51034,0.17706,0.16476]},{"body_a":"peg","body_b":"channel_base_body","contact_count":712.0,"contact_point_centroid":[0.50587,0.10469,0.00939],"force_p95":0.5755,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57554,"mean_force":0.54632,"phase_index":4.0,"phase_name":"retract_peg","phase_type":"retract","tcp_position_centroid":[0.50986,0.22993,0.20669]}],"total_contact_groups":6},"final_pose_error":0.0104,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50592,0.10455,0.03384],"final_tcp_position":[0.51007,0.22993,0.25225],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":3.33087,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54104,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1005.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_peg","tcp_end":[0.51814,0.11853,0.15844],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12596,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50584,0.10469,0.03384],"object_pos_start":[0.50599,0.10464,0.03384],"object_to_goal_dist_end":0.18489,"object_to_goal_dist_start":0.18484,"object_z_max":0.03384,"peak_contact_force":0.55164,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":550.0,"raw_peak_contact_force":0.57575,"subtask_id":"grasp_peg","tcp_end":[0.51356,0.1185,0.15028],"tcp_start":[0.51356,0.1185,0.15028],"tcp_to_object_dist_end":0.11751,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":665.0,"n_steps_budget":810.0,"object_pos_end":[0.50581,0.10461,0.03384],"object_pos_start":[0.50586,0.10456,0.03384],"object_to_goal_dist_end":0.18481,"object_to_goal_dist_start":0.18476,"object_z_max":0.03384,"peak_contact_force":0.55005,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":665.0,"raw_peak_contact_force":0.57568,"tcp_end":[0.51096,0.11855,0.17145],"tcp_start":[0.51356,0.1185,0.15028],"tcp_to_object_dist_end":0.13841,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50582,0.10457,0.03384],"object_pos_start":[0.50581,0.10461,0.03384],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18481,"object_z_max":0.03384,"peak_contact_force":0.55184,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.57562,"subtask_id":"insert_peg","tcp_end":[0.51191,0.2304,0.16248],"tcp_start":[0.51096,0.11855,0.17145],"tcp_to_object_dist_end":0.18006,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":712.0,"n_steps_budget":810.0,"object_pos_end":[0.50592,0.10455,0.03384],"object_pos_start":[0.50582,0.10457,0.03384],"object_to_goal_dist_end":0.18474,"object_to_goal_dist_start":0.18477,"object_z_max":0.03384,"peak_contact_force":0.54218,"phase_name":"retract_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":712.0,"raw_peak_contact_force":0.57554,"tcp_end":[0.51007,0.22993,0.25225],"tcp_start":[0.51191,0.2304,0.16248],"tcp_to_object_dist_end":0.25188,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.88384,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.08,"insert_peg.insert_distance":0.16473,"insert_peg.insert_speed":0.02324,"lift_peg.lift_height":0.01805,"lift_peg.lift_speed":0.02559,"retract_peg.retract_speed":0.04858},"optimized_scores":{"best_composite_score":-0.28003,"best_fitness_score":0.10997,"best_task_score":0.00019},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50307,0.06748,0.00936],"force_p95":0.55225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55539,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49293,0.14478,0.22667]},{"body_a":"peg","body_b":"channel_base_body","contact_count":550.0,"contact_point_centroid":[0.50308,0.06743,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55071,"mean_force":0.54665,"phase_index":1.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.49603,0.0977,0.16516]},{"body_a":"peg","body_b":"channel_base_body","contact_count":426.0,"contact_point_centroid":[0.50298,0.06737,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55062,"mean_force":0.54664,"phase_index":2.0,"phase_name":"lift_peg","phase_type":"lift","tcp_position_centroid":[0.49322,0.0979,0.16919]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50303,0.06746,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55058,"mean_force":0.54665,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"push","tcp_position_centroid":[0.49185,0.15987,0.16877]},{"body_a":"peg","body_b":"channel_base_body","contact_count":841.0,"contact_point_centroid":[0.50309,0.06751,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55055,"mean_force":0.54665,"phase_index":4.0,"phase_name":"retract_peg","phase_type":"retract","tcp_position_centroid":[0.49087,0.21703,0.2106]}],"total_contact_groups":5},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50306,0.06743,0.0338],"final_tcp_position":[0.49107,0.21703,0.25608],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":2.06903,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54571,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":984.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_peg","tcp_end":[0.49979,0.09757,0.17176],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50307,0.06743,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54784,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":550.0,"raw_peak_contact_force":0.55071,"subtask_id":"grasp_peg","tcp_end":[0.49549,0.09775,0.16423],"tcp_start":[0.49549,0.09775,0.16423],"tcp_to_object_dist_end":0.13412,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.50301,0.06748,0.0338],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":0.54526,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":426.0,"raw_peak_contact_force":0.55062,"tcp_end":[0.49298,0.09792,0.17573],"tcp_start":[0.49549,0.09775,0.16423],"tcp_to_object_dist_end":0.1455,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50303,0.0675,0.0338],"object_pos_start":[0.50301,0.06748,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14764,"object_z_max":0.0338,"peak_contact_force":0.54564,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55058,"subtask_id":"insert_peg","tcp_end":[0.4929,0.21744,0.1659],"tcp_start":[0.49298,0.09792,0.17573],"tcp_to_object_dist_end":0.20008,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":841.0,"n_steps_budget":1000.0,"object_pos_end":[0.50306,0.06743,0.0338],"object_pos_start":[0.50303,0.0675,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":0.54558,"phase_name":"retract_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":841.0,"raw_peak_contact_force":0.55055,"tcp_end":[0.49107,0.21703,0.25608],"tcp_start":[0.4929,0.21744,0.1659],"tcp_to_object_dist_end":0.2682,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2663,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.07834,"insert_peg.insert_distance":0.17564,"insert_peg.insert_speed":0.01248,"lift_peg.lift_height":0.04489,"lift_peg.lift_speed":0.03789,"retract_peg.retract_speed":0.07978},"optimized_scores":{"best_composite_score":-0.23025,"best_fitness_score":0.15975,"best_task_score":0.00078},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.5251,0.05556,0.05973],"force_p95":221.97337,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":225.10142,"mean_force":158.32114,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50667,0.11799,0.14677]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":550.0,"contact_point_centroid":[0.52501,0.05548,0.05996],"force_p95":119.72368,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":131.30136,"mean_force":80.26319,"phase_index":1.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.50689,0.11732,0.14775]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.52501,0.05557,0.05998],"force_p95":62.64711,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":66.44376,"mean_force":46.21814,"phase_index":2.0,"phase_name":"lift_peg","phase_type":"lift","tcp_position_centroid":[0.50678,0.11737,0.14778]},{"body_a":"peg","body_b":"channel_base_body","contact_count":978.0,"contact_point_centroid":[0.50359,0.11168,0.00938],"force_p95":0.61965,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55269,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49636,0.15552,0.21453]},{"body_a":"peg","body_b":"channel_base_body","contact_count":550.0,"contact_point_centroid":[0.50375,0.11171,0.00939],"force_p95":0.64051,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64414,"mean_force":0.54518,"phase_index":1.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.50689,0.11732,0.14775]},{"body_a":"peg","body_b":"channel_base_body","contact_count":663.0,"contact_point_centroid":[0.50371,0.11168,0.00938],"force_p95":0.64134,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64283,"mean_force":0.54505,"phase_index":2.0,"phase_name":"lift_peg","phase_type":"lift","tcp_position_centroid":[0.50437,0.11744,0.16479]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50369,0.11162,0.00941],"force_p95":0.59839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6427,"mean_force":0.54383,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"push","tcp_position_centroid":[0.50317,0.17833,0.17858]},{"body_a":"peg","body_b":"channel_base_body","contact_count":711.0,"contact_point_centroid":[0.50364,0.11162,0.00941],"force_p95":0.5982,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63358,"mean_force":0.54344,"phase_index":4.0,"phase_name":"retract_peg","phase_type":"retract","tcp_position_centroid":[0.50221,0.23391,0.22067]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49675,0.19421,0.2927]}],"total_contact_groups":9},"final_pose_error":0.01027,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50369,0.11164,0.03384],"final_tcp_position":[0.50242,0.2339,0.26618],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":225.10142,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.11176,0.03376],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":225.10142,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1008.0,"raw_peak_contact_force":225.10142,"subtask_id":"reach_peg","tcp_end":[0.50677,0.11765,0.14668],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11311,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,0.11174,0.03376],"object_pos_start":[0.50377,0.11176,0.03376],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.1919,"object_z_max":0.03397,"peak_contact_force":77.75836,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1100.0,"raw_peak_contact_force":131.30136,"subtask_id":"grasp_peg","tcp_end":[0.50678,0.11738,0.14778],"tcp_start":[0.5068,0.11737,0.14779],"tcp_to_object_dist_end":0.1142,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.50371,0.11178,0.03384],"object_pos_start":[0.50364,0.11174,0.03376],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.19187,"object_z_max":0.03399,"peak_contact_force":0.56304,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":667.0,"raw_peak_contact_force":66.44376,"tcp_end":[0.50433,0.11744,0.18514],"tcp_start":[0.50678,0.11738,0.14778],"tcp_to_object_dist_end":0.1514,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.11172,0.03384],"object_pos_start":[0.50371,0.11178,0.03384],"object_to_goal_dist_end":0.19186,"object_to_goal_dist_start":0.19192,"object_z_max":0.03399,"peak_contact_force":0.56013,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.6427,"subtask_id":"insert_peg","tcp_end":[0.50414,0.23438,0.17628],"tcp_start":[0.50433,0.11744,0.18514],"tcp_to_object_dist_end":0.18797,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":711.0,"n_steps_budget":810.0,"object_pos_end":[0.50369,0.11164,0.03384],"object_pos_start":[0.50377,0.11172,0.03384],"object_to_goal_dist_end":0.19178,"object_to_goal_dist_start":0.19186,"object_z_max":0.03403,"peak_contact_force":0.51231,"phase_name":"retract_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":711.0,"raw_peak_contact_force":0.63358,"tcp_end":[0.50242,0.2339,0.26618],"tcp_start":[0.50414,0.23438,0.17628],"tcp_to_object_dist_end":0.26254,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```