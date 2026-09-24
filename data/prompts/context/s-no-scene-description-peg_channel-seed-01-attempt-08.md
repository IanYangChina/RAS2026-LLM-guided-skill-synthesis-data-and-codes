## Search State

- **Seed**: 1
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → rotate → contact → push | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | position_control | impedance_control | force_threshold_switch | admittance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.0551 | 0.00 | ❌ rejected |
| 7 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1659 | 0.40 | ❌ rejected |
| 6 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1659 | 0.40 | ❌ rejected |
| 5 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1614 | 0.09 | ❌ rejected |
| 4 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1680 | 0.40 | ❌ rejected |

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

## Current Skill (Q=0.055) — your mutation base

```yaml
skill: peg_channel
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
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
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: align_2
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

```

## Design Metrics

- **Composite score**: 0.055
- **task_score** (E): 0.001
- **fitness_score**: 0.115  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2042 |
| rotate_1 | 1.00 | 1.00 | 0.0307 |
| contact_1 | 1.00 | 1.00 | 0.0499 |
| push_1 | 0.00 | 1.00 | 0.0006 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.482, 0.089, 0.131) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.534 | 2.857 |
| rotate_1 | rotate | 1.00 / step_budget | (0.482, 0.089, 0.131)→(0.498, 0.087, 0.105) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.554 | 0.570 |
| contact_1 | contact | 1.00 / force_exceeded | (0.498, 0.087, 0.105)→(0.476, 0.096, 0.062) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 2.333 | 165.626 | 140.481 |
| push_1 | push | 0.00 / guard_failure | (0.476, 0.095, 0.060)→(0.475, 0.095, 0.060) | (0.497, 0.080, 0.034)→(0.497, 0.079, 0.034) | 0.160→0.160 | 1.00 / 2.333 | 131.215 | 228.623 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.002
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.002
- phase_score: 0.198
- phase_breakdown.reach_peg_score: 0.657
- phase_breakdown.traverse_channel_score: 0.001

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.119
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.002
- **Median Q (composite search score)**: 0.056
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.412


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a904e23429ae963dd2788b3e8d0575d9ce341e1daddfe013fbb1224c3e0c850e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6bee39a4c127c6d39ee1365e3969a50bb09484f7e2580b1a3dc4d8c4ae20213b`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43636,"average_solve_count":55.0,"average_success_count":55.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.14846,"contact_1.contact_force":8.90425,"push_1.push_distance":0.1439,"push_1.push_speed":0.141,"rotate_1.rotate_speed":0.24113},"optimized_scores":{"best_composite_score":0.05921,"best_fitness_score":0.11921,"best_task_score":0.00165},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50265,0.13374,0.05753],"force_p95":108.87956,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":109.55812,"mean_force":100.69326,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4921,0.12915,0.05991]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50697,0.11484,0.00932],"force_p95":108.80335,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":109.42658,"mean_force":100.8481,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4921,0.12915,0.05991]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50387,0.13376,0.05864],"force_p95":96.72963,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":96.72963,"mean_force":96.72963,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49306,0.12984,0.06188]},{"body_a":"peg","body_b":"channel_base_body","contact_count":25.0,"contact_point_centroid":[0.50218,0.1161,0.0094],"force_p95":0.62003,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":96.72767,"mean_force":4.38912,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50389,0.12939,0.08164]},{"body_a":"peg","body_b":"channel_base_body","contact_count":395.0,"contact_point_centroid":[0.50097,0.11609,0.00936],"force_p95":0.63861,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.5646,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49844,0.16081,0.21326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.4993,0.11623,0.00941],"force_p95":0.5936,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60895,"mean_force":0.54372,"phase_index":1.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.50742,0.11993,0.12352]}],"total_contact_groups":6},"final_pose_error":0.35287,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5007,0.11577,0.03339],"final_tcp_position":[0.49121,0.12869,0.05829],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":109.55812,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":411.0,"n_steps_budget":840.0,"object_pos_end":[0.50094,0.11605,0.03386],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.50688,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":395.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_peg","tcp_end":[0.49809,0.12341,0.13255],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09901,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50103,0.11602,0.03385],"object_pos_start":[0.50094,0.11605,0.03386],"object_to_goal_dist_end":0.19612,"object_to_goal_dist_start":0.19615,"object_z_max":0.03387,"peak_contact_force":0.56703,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":20.0,"raw_peak_contact_force":0.60895,"subtask_id":"reach_peg","tcp_end":[0.51583,0.12134,0.10622],"tcp_start":[0.49809,0.12341,0.13255],"tcp_to_object_dist_end":0.07405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":25.0,"n_steps_budget":600.0,"object_pos_end":[0.50088,0.11598,0.03378],"object_pos_start":[0.50103,0.11602,0.03385],"object_to_goal_dist_end":0.19608,"object_to_goal_dist_start":0.19612,"object_z_max":0.03385,"peak_contact_force":96.72963,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":26.0,"raw_peak_contact_force":96.72963,"tcp_end":[0.49256,0.12944,0.06081],"tcp_start":[0.51583,0.12134,0.10622],"tcp_to_object_dist_end":0.03133,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50088,0.11587,0.0337],"object_pos_start":[0.50088,0.11598,0.03378],"object_to_goal_dist_end":0.19598,"object_to_goal_dist_start":0.19608,"object_z_max":0.03378,"peak_contact_force":103.19427,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":109.55812,"subtask_id":"traverse_channel","tcp_end":[0.49121,0.12869,0.05829],"tcp_start":[0.49164,0.12887,0.05903],"tcp_to_object_dist_end":0.02937,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8416ac3bebb4dbec2abbf751596843a33db171fd8d70765023f3b940d846bd0c`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42029,"average_solve_count":69.0,"average_success_count":69.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.1111,"contact_1.contact_force":12.25048,"push_1.push_distance":0.16871,"push_1.push_speed":0.13725,"rotate_1.rotate_speed":0.10305},"optimized_scores":{"best_composite_score":0.05569,"best_fitness_score":0.11569,"best_task_score":0.00088},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47485,0.09192,0.05939],"force_p95":307.337,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":317.48869,"mean_force":229.21523,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47336,0.08021,0.061]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.48123,0.05276,0.0094],"force_p95":12.31478,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.6706,"mean_force":8.66677,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47336,0.08021,0.061]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.48477,0.07841,0.05853],"force_p95":11.82607,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.18765,"mean_force":8.12323,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47336,0.08021,0.061]},{"body_a":"peg","body_b":"channel_base_body","contact_count":480.0,"contact_point_centroid":[0.49557,0.06394,0.00937],"force_p95":0.59628,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56324,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48877,0.1347,0.21019]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49926,0.19759,0.29667]},{"body_a":"peg","body_b":"channel_base_body","contact_count":25.0,"contact_point_centroid":[0.49226,0.06514,0.0094],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55112,"mean_force":0.5459,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48449,0.08,0.08126]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.49513,0.0638,0.0094],"force_p95":0.54919,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54987,"mean_force":0.54575,"phase_index":1.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.48788,0.0704,0.12174]}],"total_contact_groups":7},"final_pose_error":0.33022,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49496,0.06366,0.03398],"final_tcp_position":[0.4727,0.07983,0.05986],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":317.48869,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":507.0,"n_steps_budget":1000.0,"object_pos_end":[0.49498,0.06404,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14425,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54425,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":508.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_peg","tcp_end":[0.47968,0.07453,0.13029],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.49499,0.06404,0.03394],"object_pos_start":[0.49498,0.06404,0.03394],"object_to_goal_dist_end":0.14425,"object_to_goal_dist_start":0.14425,"object_z_max":0.03394,"peak_contact_force":0.5438,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":20.0,"raw_peak_contact_force":0.54987,"subtask_id":"reach_peg","tcp_end":[0.49542,0.07158,0.10488],"tcp_start":[0.47968,0.07453,0.13029],"tcp_to_object_dist_end":0.07134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":25.0,"n_steps_budget":600.0,"object_pos_end":[0.49491,0.06378,0.03394],"object_pos_start":[0.49499,0.06404,0.03394],"object_to_goal_dist_end":0.144,"object_to_goal_dist_start":0.14425,"object_z_max":0.03394,"peak_contact_force":75.98549,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":25.0,"raw_peak_contact_force":0.55112,"tcp_end":[0.47379,0.08043,0.06173],"tcp_start":[0.49542,0.07158,0.10488],"tcp_to_object_dist_end":0.03867,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49493,0.06373,0.03395],"object_pos_start":[0.49491,0.06378,0.03394],"object_to_goal_dist_end":0.14395,"object_to_goal_dist_start":0.144,"object_z_max":0.03397,"peak_contact_force":154.1852,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":317.48869,"subtask_id":"traverse_channel","tcp_end":[0.4727,0.07983,0.05986],"tcp_start":[0.47297,0.07999,0.06032],"tcp_to_object_dist_end":0.03775,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0188121de1b8142d5ff7a7406b62c43adf6da5520b986a997e46ef53b7d11bf9`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88235,"average_solve_count":51.0,"average_success_count":51.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.19425,"contact_1.contact_force":10.60829,"push_1.push_distance":0.07773,"push_1.push_speed":0.13819,"rotate_1.rotate_speed":0.20987},"optimized_scores":{"best_composite_score":0.05048,"best_fitness_score":0.11048,"best_task_score":0.00022},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47318,0.08372,0.05964],"force_p95":324.1615,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":324.1615,"mean_force":324.1615,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46314,0.07824,0.06293]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47238,0.08314,0.05898],"force_p95":252.10014,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":258.82164,"mean_force":195.56424,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46233,0.0777,0.06162]},{"body_a":"peg","body_b":"channel_base_body","contact_count":441.0,"contact_point_centroid":[0.49439,0.05905,0.00935],"force_p95":0.59218,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57939,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48208,0.1317,0.20942]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4987,0.1964,0.295]},{"body_a":"peg","body_b":"channel_base_body","contact_count":26.0,"contact_point_centroid":[0.49449,0.0619,0.00939],"force_p95":0.55015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55113,"mean_force":0.54658,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47357,0.07786,0.08138]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.49383,0.05526,0.00939],"force_p95":0.54968,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54999,"mean_force":0.546,"phase_index":1.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.4751,0.06637,0.12182]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.48486,0.04452,0.00939],"force_p95":0.54617,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54625,"mean_force":0.5443,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46233,0.0777,0.06162]}],"total_contact_groups":7},"final_pose_error":0.23925,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49415,0.05884,0.03387],"final_tcp_position":[0.46175,0.07738,0.06081],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":324.1615,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":470.0,"n_steps_budget":750.0,"object_pos_end":[0.49404,0.05888,0.03386],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54978,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":476.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_peg","tcp_end":[0.46687,0.06986,0.13028],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10077,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.49423,0.05891,0.03386],"object_pos_start":[0.49404,0.05888,0.03386],"object_to_goal_dist_end":0.13917,"object_to_goal_dist_start":0.13914,"object_z_max":0.03386,"peak_contact_force":0.54999,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":20.0,"raw_peak_contact_force":0.54999,"subtask_id":"reach_peg","tcp_end":[0.48382,0.06874,0.10531],"tcp_start":[0.46687,0.06986,0.13028],"tcp_to_object_dist_end":0.07287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":26.0,"n_steps_budget":600.0,"object_pos_end":[0.49402,0.05889,0.03387],"object_pos_start":[0.49423,0.05891,0.03386],"object_to_goal_dist_end":0.13915,"object_to_goal_dist_start":0.13917,"object_z_max":0.03387,"peak_contact_force":324.1615,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":27.0,"raw_peak_contact_force":324.1615,"tcp_end":[0.46271,0.07788,0.06217],"tcp_start":[0.48382,0.06874,0.10531],"tcp_to_object_dist_end":0.04629,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49406,0.05885,0.03387],"object_pos_start":[0.49402,0.05889,0.03387],"object_to_goal_dist_end":0.13912,"object_to_goal_dist_start":0.13915,"object_z_max":0.03387,"peak_contact_force":136.26444,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":258.82164,"subtask_id":"traverse_channel","tcp_end":[0.46175,0.07738,0.06081],"tcp_start":[0.46199,0.07752,0.06113],"tcp_to_object_dist_end":0.04597,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```