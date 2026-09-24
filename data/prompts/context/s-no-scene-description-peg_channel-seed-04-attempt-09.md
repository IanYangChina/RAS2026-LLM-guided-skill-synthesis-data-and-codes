## Search State

- **Seed**: 4
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | -0.3000 | 0.00 | ❌ rejected |
| 8 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3046 | 0.61 | ❌ rejected |
| 7 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3046 | 0.60 | ❌ rejected |
| 6 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3035 | 0.61 | ✅ accepted |
| 5 | approach → grasp → lift → align → insert → release → retract | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_motion | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.4052 | 0.00 | ❌ rejected |

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

## Current Skill (Q=-0.300) — your mutation base

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

- **Composite score**: -0.300
- **task_score** (E): 0.000
- **fitness_score**: 0.010  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0955 |
| descend_1 | 1.00 | 1.00 | 0.1609 |
| push_channel | 0.00 | 1.00 | 0.1359 |
| retract_1 | 1.00 | 1.00 | 0.2010 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.515, 0.208, 0.208) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.541 | 3.242 |
| descend_1 | descend | 1.00 / step_budget | (0.515, 0.208, 0.208)→(0.502, 0.112, 0.080) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 1.000 | 0.546 | 0.565 |
| push_channel | push | 0.00 / step_budget | (0.502, 0.112, 0.080)→(0.499, 0.248, 0.074) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 1.000 | 0.548 | 0.559 |
| retract_1 | retract | 1.00 / step_budget | (0.499, 0.248, 0.074)→(0.499, 0.412, 0.190) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.164 | 1.00 / 1.000 | 0.547 | 0.559 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.959
- terminal_score: 0.000
- phase_score: 0.017
- phase_breakdown.reach_peg_score: 0.056
- phase_breakdown.push_channel_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.010
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.300
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.304


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `424e8a040c59c1e1e42822c1022320b6050001458f7b9b4937cb9238911ce80b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `72d2436204c0f1ee3bbdbdfe3e5489661153a48f95d8f0dc3b73e6ce1e1e081b`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91613,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.1392,"descend_1.descend_speed":0.09611,"push_channel.push_distance":0.12384,"push_channel.push_force":26.05422,"retract_1.retract_speed":0.0708},"optimized_scores":{"best_composite_score":-0.30039,"best_fitness_score":0.00961,"best_task_score":8e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":162.0,"contact_point_centroid":[0.50496,0.08095,0.0093],"force_p95":0.8652,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.64096,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51403,0.20743,0.24767]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50168,0.20152,0.29357]},{"body_a":"peg","body_b":"channel_base_body","contact_count":497.0,"contact_point_centroid":[0.50598,0.08084,0.00938],"force_p95":0.55008,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55176,"mean_force":0.54676,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51434,0.15719,0.1416]},{"body_a":"peg","body_b":"channel_base_body","contact_count":742.0,"contact_point_centroid":[0.50602,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55007,"mean_force":0.54677,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50093,0.16392,0.07489]},{"body_a":"peg","body_b":"channel_base_body","contact_count":234.0,"contact_point_centroid":[0.50597,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49991,0.30289,0.12847]}],"total_contact_groups":5},"final_pose_error":0.04916,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50595,0.08086,0.03378],"final_tcp_position":[0.50039,0.38857,0.19055],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":4.32595,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":191.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54794,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":198.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.52617,0.20526,0.20674],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.21399,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":497.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54527,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":497.0,"raw_peak_contact_force":0.55176,"subtask_id":"reach_peg","tcp_end":[0.50426,0.10869,0.07973],"tcp_start":[0.52617,0.20526,0.20674],"tcp_to_object_dist_end":0.05374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":742.0,"n_steps_budget":780.0,"object_pos_end":[0.50595,0.08087,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":0.54819,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":742.0,"raw_peak_contact_force":0.55007,"subtask_id":"push_channel","tcp_end":[0.50071,0.22439,0.07421],"tcp_start":[0.50426,0.10869,0.07973],"tcp_to_object_dist_end":0.14921,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":234.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.08086,0.03378],"object_pos_start":[0.50595,0.08087,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":0.54819,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":234.0,"raw_peak_contact_force":0.55006,"tcp_end":[0.50039,0.38857,0.19055],"tcp_start":[0.50071,0.22439,0.07421],"tcp_to_object_dist_end":0.34539,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `54762c1e743ba455eff3c9979c2b42f5642abe1893e28eae37dc231d7efcd4e4`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84106,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.11603,"descend_1.descend_speed":0.07002,"push_channel.push_distance":0.16221,"push_channel.push_force":17.87333,"retract_1.retract_speed":0.10967},"optimized_scores":{"best_composite_score":-0.2999,"best_fitness_score":0.0101,"best_task_score":0.00027},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":164.0,"contact_point_centroid":[0.50474,0.10461,0.00933],"force_p95":0.79501,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.61522,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50871,0.21727,0.25015]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50089,0.20214,0.29499]},{"body_a":"peg","body_b":"channel_base_body","contact_count":505.0,"contact_point_centroid":[0.50594,0.1046,0.00939],"force_p95":0.57543,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58307,"mean_force":0.54636,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5093,0.17823,0.14255]},{"body_a":"peg","body_b":"channel_base_body","contact_count":986.0,"contact_point_centroid":[0.50593,0.10464,0.00939],"force_p95":0.57569,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57597,"mean_force":0.54633,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50005,0.2058,0.07466]},{"body_a":"peg","body_b":"channel_base_body","contact_count":231.0,"contact_point_centroid":[0.50599,0.10482,0.00939],"force_p95":0.57566,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57567,"mean_force":0.54627,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49906,0.36482,0.12796]}],"total_contact_groups":5},"final_pose_error":0.04983,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5059,0.10455,0.03384],"final_tcp_position":[0.49958,0.44984,0.18917],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":3.33087,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":191.0,"n_steps_budget":630.0,"object_pos_end":[0.50594,0.10473,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18493,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.53325,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":196.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_peg","tcp_end":[0.51711,0.22397,0.20827],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.21159,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":505.0,"n_steps_budget":1000.0,"object_pos_end":[0.50585,0.1047,0.03384],"object_pos_start":[0.50594,0.10473,0.03383],"object_to_goal_dist_end":0.18489,"object_to_goal_dist_start":0.18493,"object_z_max":0.03384,"peak_contact_force":0.54329,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":505.0,"raw_peak_contact_force":0.58307,"subtask_id":"reach_peg","tcp_end":[0.50339,0.13198,0.07984],"tcp_start":[0.51711,0.22397,0.20827],"tcp_to_object_dist_end":0.05354,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":986.0,"n_steps_budget":1000.0,"object_pos_end":[0.50582,0.10462,0.03384],"object_pos_start":[0.50585,0.1047,0.03384],"object_to_goal_dist_end":0.18481,"object_to_goal_dist_start":0.18489,"object_z_max":0.03384,"peak_contact_force":0.55006,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":986.0,"raw_peak_contact_force":0.57597,"subtask_id":"push_channel","tcp_end":[0.49991,0.28569,0.07378],"tcp_start":[0.50339,0.13198,0.07984],"tcp_to_object_dist_end":0.18552,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":231.0,"n_steps_budget":1000.0,"object_pos_end":[0.5059,0.10455,0.03384],"object_pos_start":[0.50582,0.10462,0.03384],"object_to_goal_dist_end":0.18475,"object_to_goal_dist_start":0.18481,"object_z_max":0.03384,"peak_contact_force":0.5442,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":231.0,"raw_peak_contact_force":0.57567,"tcp_end":[0.49958,0.44984,0.18917],"tcp_start":[0.49991,0.28569,0.07378],"tcp_to_object_dist_end":0.37867,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b230a5798f38c3fb8968a6bc74f96ee85fe7026f3170cf8216fc868a1c5c570f`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63253,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.09202,"descend_1.descend_speed":0.0444,"push_channel.push_distance":0.14576,"push_channel.push_force":15.91492,"retract_1.retract_speed":0.17482},"optimized_scores":{"best_composite_score":-0.29971,"best_fitness_score":0.01029,"best_task_score":0.00026},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":164.0,"contact_point_centroid":[0.50319,0.0674,0.00924],"force_p95":0.94488,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.59912,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49992,0.20119,0.25136]},{"body_a":"peg","body_b":"channel_base_body","contact_count":583.0,"contact_point_centroid":[0.50297,0.06747,0.00938],"force_p95":0.55132,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56003,"mean_force":0.54664,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49882,0.14482,0.14189]},{"body_a":"peg","body_b":"channel_base_body","contact_count":885.0,"contact_point_centroid":[0.5031,0.06748,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55079,"mean_force":0.54664,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49602,0.16158,0.07428]},{"body_a":"peg","body_b":"channel_base_body","contact_count":217.0,"contact_point_centroid":[0.50311,0.06739,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5506,"mean_force":0.54665,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49525,0.31243,0.12886]}],"total_contact_groups":4},"final_pose_error":0.04926,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50304,0.06742,0.0338],"final_tcp_position":[0.4957,0.39668,0.18978],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":2.06903,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":180.0,"n_steps_budget":780.0,"object_pos_end":[0.50303,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54129,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":164.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_peg","tcp_end":[0.50042,0.19465,0.20795],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.21569,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":583.0,"n_steps_budget":1000.0,"object_pos_end":[0.50306,0.0675,0.0338],"object_pos_start":[0.50303,0.06743,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.55081,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":583.0,"raw_peak_contact_force":0.56003,"subtask_id":"reach_peg","tcp_end":[0.49936,0.09482,0.07908],"tcp_start":[0.50042,0.19465,0.20795],"tcp_to_object_dist_end":0.05302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":885.0,"n_steps_budget":930.0,"object_pos_end":[0.50307,0.06743,0.0338],"object_pos_start":[0.50306,0.0675,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":0.54557,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":885.0,"raw_peak_contact_force":0.55079,"subtask_id":"push_channel","tcp_end":[0.49584,0.23251,0.07358],"tcp_start":[0.49936,0.09482,0.07908],"tcp_to_object_dist_end":0.16996,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":217.0,"n_steps_budget":900.0,"object_pos_end":[0.50304,0.06742,0.0338],"object_pos_start":[0.50307,0.06743,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54778,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":217.0,"raw_peak_contact_force":0.5506,"tcp_end":[0.4957,0.39668,0.18978],"tcp_start":[0.49584,0.23251,0.07358],"tcp_to_object_dist_end":0.36441,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```