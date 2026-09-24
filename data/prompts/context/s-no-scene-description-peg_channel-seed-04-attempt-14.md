## Search State

- **Seed**: 4
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → align → insert | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_motion | position_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | force_exceeded | 9 | -0.4437 | 0.01 | ❌ rejected |
| 13 | approach → descend → grasp → align → push | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_motion | position_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | force_exceeded | 9 | -0.3341 | 0.00 | ❌ rejected |
| 12 | approach → push | linear_cartesian | impedance_motion | position_control | admittance_control | pose_tolerance | force_exceeded | 6 | -0.1434 | 0.00 | ❌ rejected |
| 11 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3041 | 0.61 | ❌ rejected |
| 10 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3049 | 0.61 | ❌ rejected |

**Proposal policy**: task_score is 0.01 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.444) — your mutation base

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

- **Composite score**: -0.444
- **task_score** (E): 0.008
- **fitness_score**: 0.096  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

**⚠ Warning**: CMA-ES stagnated + low fitness_score → structure may be fundamentally incompatible with task

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1907 |
| descend_1 | 1.00 | 1.00 | 0.0880 |
| grasp_1 | 1.00 | 1.00 | 0.0007 |
| align_1 | 1.00 | 1.00 | 0.0142 |
| insert_1 | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.091, 0.145) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.548 | 3.242 |
| descend_1 | descend | 1.00 / step_budget | (0.516, 0.091, 0.145)→(0.504, 0.085, 0.059) | (0.505, 0.084, 0.034)→(0.506, 0.084, 0.032) | 0.165→0.165 | 1.00 / 2.000 | 81.387 | 91.017 |
| grasp_1 | grasp | 1.00 / step_budget | (0.504, 0.085, 0.059)→(0.505, 0.085, 0.059) | (0.506, 0.084, 0.032)→(0.505, 0.084, 0.032) | 0.165→0.164 | 1.00 / 2.000 | 65.387 | 81.172 |
| align_1 | align | 1.00 / step_budget | (0.505, 0.085, 0.059)→(0.508, 0.083, 0.051) | (0.505, 0.084, 0.032)→(0.505, 0.083, 0.029) | 0.164→0.163 | 1.00 / 3.000 | 204.301 | 211.409 |
| insert_1 | insert | 0.00 / guard_failure | (0.508, 0.083, 0.051)→(0.508, 0.083, 0.051) | (0.505, 0.083, 0.029)→(0.505, 0.083, 0.029) | 0.163→0.163 | 1.00 / 3.000 | 157.724 | 157.724 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.170
- phase_breakdown.approach_peg_score: 0.820
- phase_breakdown.insert_through_channel_score: 0.000
- phase_breakdown.align_to_channel_score: 0.041
- phase_breakdown.descend_peg_score: 0.952

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.102
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.022
- **Median Q (composite search score)**: -0.441
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.274


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44578,"average_solve_count":83.0,"average_success_count":83.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.06478,"align_1.align_tol":0.01279,"approach_1.approach_speed":0.10554,"approach_1.approach_tol":0.04316,"descend_1.descend_speed":0.0514,"descend_1.descend_tol":0.01076,"insert_1.insert_depth":0.13958,"insert_1.insert_force":24.81203,"insert_1.insert_speed":0.05026},"optimized_scores":{"best_composite_score":-0.45255,"best_fitness_score":0.08745,"best_task_score":0.00183},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":425.0,"contact_point_centroid":[0.51751,0.08114,0.00686],"force_p95":201.06635,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":216.87674,"mean_force":136.22721,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50741,0.08118,0.05352]},{"body_a":"attachment","body_b":"peg","contact_count":425.0,"contact_point_centroid":[0.51841,0.08123,0.05123],"force_p95":200.60782,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":216.34677,"mean_force":135.68677,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50741,0.08118,0.05352]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":62.0,"contact_point_centroid":[0.52501,0.08134,0.06],"force_p95":134.45777,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":165.48949,"mean_force":55.25706,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50772,0.08133,0.05038]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52347,0.08157,0.00622],"force_p95":164.76683,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":164.76683,"mean_force":164.76683,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50757,0.0817,0.05002]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51857,0.08172,0.04883],"force_p95":164.13863,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":164.13863,"mean_force":164.13863,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50757,0.0817,0.05002]},{"body_a":"peg","body_b":"channel_base_body","contact_count":375.0,"contact_point_centroid":[0.50681,0.08091,0.00935],"force_p95":71.22383,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.90381,"mean_force":6.32144,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51638,0.0842,0.10032]},{"body_a":"attachment","body_b":"peg","contact_count":31.0,"contact_point_centroid":[0.51692,0.08131,0.05719],"force_p95":84.50313,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.3625,"mean_force":69.91733,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50592,0.08125,0.06108]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.517,0.081,0.00834],"force_p95":74.20396,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.83338,"mean_force":66.29874,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50657,0.08117,0.05893]},{"body_a":"attachment","body_b":"peg","contact_count":450.0,"contact_point_centroid":[0.51758,0.08116,0.05542],"force_p95":73.68703,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":78.27951,"mean_force":65.7798,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50657,0.08117,0.05893]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,0.0817,0.05999],"force_p95":20.1866,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":20.1866,"mean_force":20.1866,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50757,0.0817,0.05002]},{"body_a":"peg","body_b":"channel_base_body","contact_count":621.0,"contact_point_centroid":[0.50576,0.08087,0.00936],"force_p95":0.55683,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57134,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51466,0.14156,0.21758]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50001,0.19752,0.29626]}],"total_contact_groups":12},"final_pose_error":0.14184,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50562,0.07989,0.02753],"final_tcp_position":[0.50758,0.0817,0.05004],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":216.87674,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":650.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54819,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":657.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach_peg","tcp_end":[0.52999,0.08783,0.1446],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11362,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":375.0,"n_steps_budget":600.0,"object_pos_end":[0.50619,0.08084,0.03204],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.16116,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":68.80473,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":406.0,"raw_peak_contact_force":87.90381,"subtask_id":"descend_peg","tcp_end":[0.50612,0.08119,0.05918],"tcp_start":[0.52999,0.08783,0.1446],"tcp_to_object_dist_end":0.02714,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50625,0.08037,0.03169],"object_pos_start":[0.50619,0.08084,0.03204],"object_to_goal_dist_end":0.1607,"object_to_goal_dist_start":0.16116,"object_z_max":0.03204,"peak_contact_force":59.23709,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":900.0,"raw_peak_contact_force":78.83338,"tcp_end":[0.50669,0.08117,0.05892],"tcp_start":[0.50612,0.08119,0.05918],"tcp_to_object_dist_end":0.02725,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":425.0,"n_steps_budget":600.0,"object_pos_end":[0.50563,0.07989,0.0275],"object_pos_start":[0.50625,0.08037,0.03169],"object_to_goal_dist_end":0.16048,"object_to_goal_dist_start":0.1607,"object_z_max":0.03174,"peak_contact_force":215.82613,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":912.0,"raw_peak_contact_force":216.87674,"subtask_id":"align_to_channel","tcp_end":[0.50757,0.0817,0.05002],"tcp_start":[0.50669,0.08117,0.05892],"tcp_to_object_dist_end":0.02267,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":900.0,"object_pos_end":[0.50562,0.07989,0.02753],"object_pos_start":[0.50563,0.07989,0.0275],"object_to_goal_dist_end":0.16048,"object_to_goal_dist_start":0.16048,"object_z_max":0.0275,"peak_contact_force":164.76683,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":164.76683,"subtask_id":"insert_through_channel","tcp_end":[0.50758,0.0817,0.05004],"tcp_start":[0.50757,0.0817,0.05002],"tcp_to_object_dist_end":0.02267,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `54762c1e743ba455eff3c9979c2b42f5642abe1893e28eae37dc231d7efcd4e4`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6,"average_solve_count":80.0,"average_success_count":80.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.04532,"align_1.align_tol":0.0107,"approach_1.approach_speed":0.10994,"approach_1.approach_tol":0.02693,"descend_1.descend_speed":0.04537,"descend_1.descend_tol":0.0092,"insert_1.insert_depth":0.14251,"insert_1.insert_force":25.67098,"insert_1.insert_speed":0.05688},"optimized_scores":{"best_composite_score":-0.44053,"best_fitness_score":0.09947,"best_task_score":0.02163},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":483.0,"contact_point_centroid":[0.51747,0.09331,0.00734],"force_p95":190.23762,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":193.28692,"mean_force":138.21343,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5072,0.09468,0.05432]},{"body_a":"attachment","body_b":"peg","contact_count":483.0,"contact_point_centroid":[0.51824,0.09496,0.05215],"force_p95":189.5402,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":189.78205,"mean_force":137.49632,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5072,0.09468,0.05432]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":92.0,"contact_point_centroid":[0.52501,0.08786,0.06],"force_p95":89.96881,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":173.1673,"mean_force":66.47927,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50857,0.08784,0.05212]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51858,0.08897,0.00745],"force_p95":153.84224,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":153.84224,"mean_force":153.84224,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50855,0.08776,0.05204]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51971,0.08865,0.05111],"force_p95":153.27846,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":153.27846,"mean_force":153.27846,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50855,0.08776,0.05204]},{"body_a":"peg","body_b":"channel_base_body","contact_count":394.0,"contact_point_centroid":[0.50674,0.1046,0.00935],"force_p95":73.39012,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":92.44389,"mean_force":6.2498,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51035,0.10734,0.10065]},{"body_a":"attachment","body_b":"peg","contact_count":33.0,"contact_point_centroid":[0.51548,0.10491,0.05716],"force_p95":87.51541,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.88718,"mean_force":68.14702,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50445,0.10481,0.06103]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.51535,0.10482,0.00831],"force_p95":77.91799,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.04456,"mean_force":66.3922,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50548,0.10488,0.0588]},{"body_a":"attachment","body_b":"peg","contact_count":450.0,"contact_point_centroid":[0.51651,0.1049,0.05536],"force_p95":77.39902,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.50633,"mean_force":65.87522,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50548,0.10488,0.0588]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52502,0.08778,0.05999],"force_p95":43.1957,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":43.1957,"mean_force":43.1957,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50855,0.08776,0.05204]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":24.0,"contact_point_centroid":[0.52529,0.09527,0.05331],"force_p95":13.47802,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.66341,"mean_force":7.3968,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50857,0.08785,0.05215]},{"body_a":"peg","body_b":"channel_base_body","contact_count":550.0,"contact_point_centroid":[0.50566,0.10458,0.00937],"force_p95":0.57703,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56691,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50921,0.15363,0.21875]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49986,0.19805,0.2966]}],"total_contact_groups":13},"final_pose_error":0.15099,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50403,0.09717,0.03081],"final_tcp_position":[0.50856,0.08776,0.05206],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":193.28692,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":577.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.10463,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18483,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55005,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":582.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach_peg","tcp_end":[0.5195,0.11074,0.14607],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11323,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":394.0,"n_steps_budget":600.0,"object_pos_end":[0.50622,0.10458,0.03196],"object_pos_start":[0.50583,0.10463,0.03384],"object_to_goal_dist_end":0.18486,"object_to_goal_dist_start":0.18483,"object_z_max":0.03384,"peak_contact_force":86.17377,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":427.0,"raw_peak_contact_force":92.44389,"subtask_id":"descend_peg","tcp_end":[0.50499,0.10483,0.05905],"tcp_start":[0.5195,0.11074,0.14607],"tcp_to_object_dist_end":0.02711,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50562,0.10415,0.03165],"object_pos_start":[0.50622,0.10458,0.03196],"object_to_goal_dist_end":0.18443,"object_to_goal_dist_start":0.18486,"object_z_max":0.03196,"peak_contact_force":72.16414,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":900.0,"raw_peak_contact_force":80.04456,"tcp_end":[0.5056,0.1049,0.05881],"tcp_start":[0.50499,0.10483,0.05905],"tcp_to_object_dist_end":0.02717,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":483.0,"n_steps_budget":600.0,"object_pos_end":[0.50405,0.09716,0.0308],"object_pos_start":[0.50562,0.10415,0.03165],"object_to_goal_dist_end":0.17744,"object_to_goal_dist_start":0.18443,"object_z_max":0.03166,"peak_contact_force":190.27545,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1082.0,"raw_peak_contact_force":193.28692,"subtask_id":"align_to_channel","tcp_end":[0.50855,0.08776,0.05204],"tcp_start":[0.5056,0.1049,0.05881],"tcp_to_object_dist_end":0.02366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":960.0,"object_pos_end":[0.50403,0.09717,0.03081],"object_pos_start":[0.50405,0.09716,0.0308],"object_to_goal_dist_end":0.17745,"object_to_goal_dist_start":0.17744,"object_z_max":0.0308,"peak_contact_force":153.84224,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":153.84224,"subtask_id":"insert_through_channel","tcp_end":[0.50856,0.08776,0.05206],"tcp_start":[0.50855,0.08776,0.05204],"tcp_to_object_dist_end":0.02368,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b230a5798f38c3fb8968a6bc74f96ee85fe7026f3170cf8216fc868a1c5c570f`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5119,"average_solve_count":84.0,"average_success_count":84.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.03962,"align_1.align_tol":0.01182,"approach_1.approach_speed":0.12643,"approach_1.approach_tol":0.02866,"descend_1.descend_speed":0.05676,"descend_1.descend_tol":0.00471,"insert_1.insert_depth":0.12887,"insert_1.insert_force":18.89458,"insert_1.insert_speed":0.06336},"optimized_scores":{"best_composite_score":-0.43816,"best_fitness_score":0.10184,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":47.0,"contact_point_centroid":[0.52502,0.07878,0.05999],"force_p95":155.66953,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":224.06308,"mean_force":64.03199,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5081,0.07877,0.05107]},{"body_a":"peg","body_b":"channel_base_body","contact_count":431.0,"contact_point_centroid":[0.51582,0.075,0.00703],"force_p95":202.8338,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":207.25067,"mean_force":142.8533,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50535,0.0741,0.05361]},{"body_a":"attachment","body_b":"peg","contact_count":431.0,"contact_point_centroid":[0.51634,0.0741,0.05142],"force_p95":202.33233,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":206.72933,"mean_force":142.32121,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50535,0.0741,0.05361]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52162,0.07888,0.00677],"force_p95":154.56269,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":154.56269,"mean_force":154.56269,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50811,0.0791,0.05079]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51913,0.07896,0.04979],"force_p95":153.92163,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":153.92163,"mean_force":153.92163,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50811,0.0791,0.05079]},{"body_a":"peg","body_b":"channel_base_body","contact_count":456.0,"contact_point_centroid":[0.50408,0.06741,0.00934],"force_p95":68.75536,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":92.70188,"mean_force":7.0908,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49809,0.07119,0.09911]},{"body_a":"attachment","body_b":"peg","contact_count":44.0,"contact_point_centroid":[0.51062,0.06814,0.05694],"force_p95":90.11474,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":92.15647,"mean_force":67.86899,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4997,0.06805,0.06097]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.51153,0.06793,0.00809],"force_p95":80.84102,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.63838,"mean_force":68.38896,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50162,0.06787,0.0585]},{"body_a":"attachment","body_b":"peg","contact_count":450.0,"contact_point_centroid":[0.51256,0.06799,0.05487],"force_p95":80.3305,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.11969,"mean_force":67.86421,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50162,0.06787,0.0585]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52508,0.07911,0.05997],"force_p95":19.79751,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":19.79751,"mean_force":19.79751,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50811,0.0791,0.05079]},{"body_a":"peg","body_b":"channel_base_body","contact_count":635.0,"contact_point_centroid":[0.50309,0.06744,0.00935],"force_p95":0.555,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56019,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49902,0.13642,0.21952]}],"total_contact_groups":11},"final_pose_error":0.1287,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50549,0.07111,0.02864],"final_tcp_position":[0.50813,0.07911,0.05081],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":224.06308,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":651.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54702,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":635.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_peg","tcp_end":[0.49972,0.07527,0.1451],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11162,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":456.0,"n_steps_budget":600.0,"object_pos_end":[0.50411,0.06727,0.03155],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14756,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":89.18338,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":500.0,"raw_peak_contact_force":92.70188,"subtask_id":"descend_peg","tcp_end":[0.50106,0.06795,0.05864],"tcp_start":[0.49972,0.07527,0.1451],"tcp_to_object_dist_end":0.02726,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50367,0.06646,0.0312],"object_pos_start":[0.50411,0.06727,0.03155],"object_to_goal_dist_end":0.14677,"object_to_goal_dist_start":0.14756,"object_z_max":0.03155,"peak_contact_force":64.76083,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":900.0,"raw_peak_contact_force":84.63838,"tcp_end":[0.50178,0.06783,0.05852],"tcp_start":[0.50106,0.06795,0.05864],"tcp_to_object_dist_end":0.02742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":431.0,"n_steps_budget":600.0,"object_pos_end":[0.5055,0.07111,0.02862],"object_pos_start":[0.50367,0.06646,0.0312],"object_to_goal_dist_end":0.15164,"object_to_goal_dist_start":0.14677,"object_z_max":0.03133,"peak_contact_force":206.80241,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":909.0,"raw_peak_contact_force":224.06308,"subtask_id":"align_to_channel","tcp_end":[0.50811,0.0791,0.05079],"tcp_start":[0.50178,0.06783,0.05852],"tcp_to_object_dist_end":0.02372,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":810.0,"object_pos_end":[0.50549,0.07111,0.02864],"object_pos_start":[0.5055,0.07111,0.02862],"object_to_goal_dist_end":0.15164,"object_to_goal_dist_start":0.15164,"object_z_max":0.02862,"peak_contact_force":154.56269,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":154.56269,"subtask_id":"insert_through_channel","tcp_end":[0.50813,0.07911,0.05081],"tcp_start":[0.50811,0.0791,0.05079],"tcp_to_object_dist_end":0.02372,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```