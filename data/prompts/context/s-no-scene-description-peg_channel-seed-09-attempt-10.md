## Search State

- **Seed**: 9
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2612 | 0.04 | ❌ rejected |
| 9 | approach → grasp → lift → approach → push | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 6 | -0.1790 | 0.00 | ❌ rejected |
| 8 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2555 | 0.03 | ❌ rejected |
| 7 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2555 | 0.05 | ❌ rejected |
| 6 | approach → grasp → lift → push | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | admittance_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 3 | 0.0260 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.04 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.261) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: rotate_1
  type: rotate
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
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
- id: push_1
  type: push
  generator: impedance_motion
  control: position_control
  termination: time_limit
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
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  parameters:
    grip_force:
      type: scalar
      range:
      - 5.0
      - 30.0

```

## Design Metrics

- **Composite score**: -0.261
- **task_score** (E): 0.045
- **fitness_score**: 0.109  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_1 | 1.00 | 1.00 | 0.1691 |
| pull_1 | 1.00 | 1.00 | 0.1295 |
| push_1 | 1.00 | 1.00 | 0.2026 |
| descend_1 | 1.00 | 1.00 | 0.1632 |
| descend_2 | 1.00 | 1.00 | 0.0207 |
| grasp_1 | 1.00 | 1.00 | 0.0011 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.499, 0.051, 0.380) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.549 | 4.034 |
| pull_1 | pull | 1.00 / time_limit | (0.499, 0.051, 0.380)→(0.498, -0.075, 0.351) | (0.502, 0.067, 0.034)→(0.502, 0.066, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.546 | 0.552 |
| push_1 | push | 1.00 / time_limit | (0.498, -0.075, 0.351)→(0.496, -0.028, 0.154) | (0.502, 0.066, 0.034)→(0.502, 0.066, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.545 | 0.552 |
| descend_1 | descend | 1.00 / step_budget | (0.496, -0.028, 0.154)→(0.507, 0.097, 0.051) | (0.502, 0.066, 0.034)→(0.499, 0.074, 0.032) | 0.147→0.155 | 1.00 / 2.333 | 185.506 | 312.977 |
| descend_2 | descend | 1.00 / step_budget | (0.507, 0.097, 0.051)→(0.501, 0.109, 0.037) | (0.499, 0.074, 0.032)→(0.499, 0.045, 0.028) | 0.155→0.126 | 1.00 / 2.667 | 138.162 | 268.854 |
| grasp_1 | grasp | 1.00 / step_budget | (0.501, 0.109, 0.037)→(0.500, 0.109, 0.036) | (0.499, 0.045, 0.028)→(0.498, 0.046, 0.027) | 0.126→0.127 | 1.00 / 3.000 | 69.100 | 93.238 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.259
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.066
- phase_score: 0.157
- phase_breakdown.approach_score: 0.555
- phase_breakdown.contact_score: 0.000
- phase_breakdown.push_score: 0.077

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.121
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.068
- **Median Q (composite search score)**: -0.260
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.401


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `bf8103833c1e96f48e87b3ce39b3b3bf17e268470bd7b5c037546fb78b5150b8`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `98954a34ee744fa939070f7dadee8a411de43cdcfeddcf3b4bfc5c3a4c536020`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75581,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"grasp_1.grip_force":11.89746,"pull_1.pull_distance":0.12247,"push_1.push_depth":0.04822,"push_1.push_distance":0.06919,"push_1.push_speed":0.0814},"optimized_scores":{"best_composite_score":-0.24944,"best_fitness_score":0.12056,"best_task_score":0.06588},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":86.0,"contact_point_centroid":[0.52508,0.08728,0.05996],"force_p95":300.96988,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":346.90029,"mean_force":231.80573,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50919,0.08726,0.05331]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":123.0,"contact_point_centroid":[0.54544,0.09836,0.0599],"force_p95":268.78718,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":272.10635,"mean_force":223.73201,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50035,0.09742,0.03693]},{"body_a":"attachment","body_b":"peg","contact_count":226.0,"contact_point_centroid":[0.51588,0.07754,0.05426],"force_p95":168.74347,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":200.6938,"mean_force":128.52639,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50625,0.08075,0.05606]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":35.0,"contact_point_centroid":[0.52504,0.09734,0.05998],"force_p95":194.15713,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":194.52097,"mean_force":158.23313,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50116,0.09716,0.03782]},{"body_a":"peg","body_b":"channel_base_body","contact_count":692.0,"contact_point_centroid":[0.50882,0.06877,0.00902],"force_p95":161.47366,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":182.02794,"mean_force":41.66343,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49969,0.04211,0.0902]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":450.0,"contact_point_centroid":[0.54577,0.09859,0.05998],"force_p95":72.9334,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.46661,"mean_force":68.63524,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50069,0.09764,0.03705]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":450.0,"contact_point_centroid":[0.52501,0.09783,0.06],"force_p95":63.07342,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.64035,"mean_force":28.04475,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50069,0.09764,0.03705]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":131.0,"contact_point_centroid":[0.52531,0.06833,0.05646],"force_p95":29.20042,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.89518,"mean_force":14.65215,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50575,0.07899,0.0566]},{"body_a":"peg","body_b":"channel_base_body","contact_count":208.0,"contact_point_centroid":[0.49928,0.03689,0.00903],"force_p95":1.12149,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.41369,"mean_force":0.71377,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5018,0.09559,0.0401]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50485,0.07965,0.05326],"force_p95":22.25414,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.81667,"mean_force":17.19133,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50803,0.09026,0.0516]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.49605,0.021,0.00807],"force_p95":0.68823,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.39826,"mean_force":0.65425,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50069,0.09764,0.03705]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47497,0.04481,0.02435],"force_p95":8.00712,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.04656,"mean_force":2.40666,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50074,0.09763,0.03703]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50586,0.06296,0.00937],"force_p95":0.55508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56049,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49843,0.13187,0.34825]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.4993,0.19877,0.29989]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47474,0.04652,0.0596],"force_p95":1.17364,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.28235,"mean_force":0.57017,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50622,0.09123,0.04882]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52516,0.023,0.0545],"force_p95":0.61129,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65347,"mean_force":0.36728,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50064,0.09592,0.03862]}],"total_contact_groups":18},"final_pose_error":0.00927,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49722,0.02146,0.02413],"final_tcp_position":[0.50078,0.09762,0.03698],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":346.90029,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54709,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1006.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.49865,0.0507,0.38034],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.34683,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":787.0,"n_steps_budget":840.0,"object_pos_end":[0.50593,0.06291,0.03384],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.14317,"object_to_goal_dist_start":0.14323,"object_z_max":0.03384,"peak_contact_force":0.54314,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":787.0,"raw_peak_contact_force":0.55532,"tcp_end":[0.4984,-0.07534,0.3508],"tcp_start":[0.49865,0.0507,0.38034],"tcp_to_object_dist_end":0.34588,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.06288,0.03386],"object_pos_start":[0.50593,0.06291,0.03384],"object_to_goal_dist_end":0.14313,"object_to_goal_dist_start":0.14317,"object_z_max":0.03386,"peak_contact_force":0.5494,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55442,"tcp_end":[0.49622,-0.01939,0.15301],"tcp_start":[0.4984,-0.07534,0.3508],"tcp_to_object_dist_end":0.14512,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":692.0,"n_steps_budget":1000.0,"object_pos_end":[0.49892,0.06475,0.03134],"object_pos_start":[0.50594,0.06288,0.03386],"object_to_goal_dist_end":0.14501,"object_to_goal_dist_start":0.14313,"object_z_max":0.03387,"peak_contact_force":346.90029,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1135.0,"raw_peak_contact_force":346.90029,"tcp_end":[0.5081,0.09019,0.0517],"tcp_start":[0.49622,-0.01939,0.15301],"tcp_to_object_dist_end":0.03385,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":219.0,"n_steps_budget":600.0,"object_pos_end":[0.49597,0.02089,0.02406],"object_pos_start":[0.49892,0.06475,0.03134],"object_to_goal_dist_end":0.10222,"object_to_goal_dist_start":0.14501,"object_z_max":0.04077,"peak_contact_force":194.52097,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":387.0,"raw_peak_contact_force":272.10635,"tcp_end":[0.50078,0.09762,0.03698],"tcp_start":[0.5081,0.09019,0.0517],"tcp_to_object_dist_end":0.07796,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49722,0.02146,0.02413],"object_pos_start":[0.49597,0.02089,0.02406],"object_to_goal_dist_end":0.10273,"object_to_goal_dist_start":0.10222,"object_z_max":0.02477,"peak_contact_force":67.99389,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1361.0,"raw_peak_contact_force":90.46661,"tcp_end":[0.50069,0.09766,0.03705],"tcp_start":[0.50078,0.09762,0.03698],"tcp_to_object_dist_end":0.07737,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `cae0d95026bac46aa2e5d95cffd531753a79751757c4f25fa56c1ec6e19c2175`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40306,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"grasp_1.grip_force":17.06023,"pull_1.pull_distance":0.1266,"push_1.push_depth":0.0591,"push_1.push_distance":0.14334,"push_1.push_speed":0.02411},"optimized_scores":{"best_composite_score":-0.2602,"best_fitness_score":0.1098,"best_task_score":0.06804},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":88.0,"contact_point_centroid":[0.52511,0.08156,0.05995],"force_p95":352.07752,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":371.96823,"mean_force":242.25877,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50931,0.08154,0.05347]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":95.0,"contact_point_centroid":[0.54567,0.09211,0.05987],"force_p95":254.60468,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":260.40985,"mean_force":224.54565,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50053,0.09147,0.03696]},{"body_a":"attachment","body_b":"peg","contact_count":219.0,"contact_point_centroid":[0.51589,0.07182,0.05439],"force_p95":164.35305,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":196.45795,"mean_force":125.3091,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50654,0.07548,0.05612]},{"body_a":"peg","body_b":"channel_base_body","contact_count":736.0,"contact_point_centroid":[0.50848,0.06162,0.00907],"force_p95":155.34373,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":177.59633,"mean_force":37.04381,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49966,0.0325,0.09611]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":74.0,"contact_point_centroid":[0.52502,0.0917,0.05999],"force_p95":144.55948,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":148.42099,"mean_force":123.23952,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5006,0.09152,0.03701]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":450.0,"contact_point_centroid":[0.54579,0.09226,0.05998],"force_p95":85.63412,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.69032,"mean_force":70.37493,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50065,0.0916,0.03718]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":130.0,"contact_point_centroid":[0.5253,0.06161,0.05706],"force_p95":30.95079,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.3133,"mean_force":15.75009,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50598,0.07365,0.05674]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":450.0,"contact_point_centroid":[0.52501,0.09178,0.06],"force_p95":37.4245,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":58.18663,"mean_force":24.3014,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50065,0.0916,0.03718]},{"body_a":"peg","body_b":"channel_base_body","contact_count":180.0,"contact_point_centroid":[0.5013,0.03229,0.00908],"force_p95":1.44291,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.55285,"mean_force":0.83883,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50226,0.08951,0.04084]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50523,0.0734,0.05315],"force_p95":15.15187,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.15187,"mean_force":15.15187,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50799,0.08491,0.05182]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52505,-0.00949,0.02397],"force_p95":10.2181,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.31014,"mean_force":3.84405,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50064,0.09157,0.03709]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.506,0.05661,0.00937],"force_p95":0.59948,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56302,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49843,0.1318,0.3483]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49926,0.19868,0.29987]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50583,0.01488,0.00807],"force_p95":0.68477,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.7676,"mean_force":0.60429,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50065,0.0916,0.03718]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47487,0.035,0.0596],"force_p95":0.7171,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.75817,"mean_force":0.42856,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5053,0.08636,0.04737]},{"body_a":"peg","body_b":"channel_base_body","contact_count":787.0,"contact_point_centroid":[0.50611,0.0566,0.00938],"force_p95":0.55015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55021,"mean_force":0.54674,"phase_index":1.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49812,-0.01441,0.37954]}],"total_contact_groups":18},"final_pose_error":0.00803,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50466,0.01499,0.02413],"final_tcp_position":[0.50066,0.09158,0.0371],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":371.96823,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.0566,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54967,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1008.0,"raw_peak_contact_force":4.44541,"tcp_end":[0.49865,0.0507,0.38034],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.3467,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":787.0,"n_steps_budget":840.0,"object_pos_end":[0.50611,0.05662,0.03378],"object_pos_start":[0.50611,0.0566,0.03378],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.13688,"object_z_max":0.03378,"peak_contact_force":0.54553,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":787.0,"raw_peak_contact_force":0.55021,"tcp_end":[0.4984,-0.07534,0.3508],"tcp_start":[0.49865,0.0507,0.38034],"tcp_to_object_dist_end":0.34348,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05659,0.03378],"object_pos_start":[0.50611,0.05662,0.03378],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.1369,"object_z_max":0.03378,"peak_contact_force":0.54501,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55015,"tcp_end":[0.49624,-0.03298,0.16581],"tcp_start":[0.4984,-0.07534,0.3508],"tcp_to_object_dist_end":0.15985,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":736.0,"n_steps_budget":1000.0,"object_pos_end":[0.50006,0.05775,0.03199],"object_pos_start":[0.50613,0.05659,0.03378],"object_to_goal_dist_end":0.13798,"object_to_goal_dist_start":0.13687,"object_z_max":0.03384,"peak_contact_force":0.98517,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1173.0,"raw_peak_contact_force":371.96823,"tcp_end":[0.50799,0.08491,0.05182],"tcp_start":[0.49624,-0.03298,0.16581],"tcp_to_object_dist_end":0.03455,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":190.0,"n_steps_budget":600.0,"object_pos_end":[0.50681,0.01498,0.02447],"object_pos_start":[0.50006,0.05775,0.03199],"object_to_goal_dist_end":0.09648,"object_to_goal_dist_start":0.13798,"object_z_max":0.04078,"peak_contact_force":216.72102,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":368.0,"raw_peak_contact_force":260.40985,"tcp_end":[0.50066,0.09158,0.0371],"tcp_start":[0.50799,0.08491,0.05182],"tcp_to_object_dist_end":0.07788,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50466,0.01499,0.02413],"object_pos_start":[0.50681,0.01498,0.02447],"object_to_goal_dist_end":0.09642,"object_to_goal_dist_start":0.09648,"object_z_max":0.02465,"peak_contact_force":67.90968,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1351.0,"raw_peak_contact_force":92.69032,"tcp_end":[0.50065,0.09162,0.03718],"tcp_start":[0.50066,0.09158,0.0371],"tcp_to_object_dist_end":0.07784,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fd7ada9a67242f1adcdb6e23860d1223cdc8a17daf859e94e1687ff0564d9575`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79412,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"grasp_1.grip_force":5.27587,"pull_1.pull_distance":0.10301,"push_1.push_depth":0.08962,"push_1.push_distance":0.13578,"push_1.push_speed":0.09349},"optimized_scores":{"best_composite_score":-0.27383,"best_fitness_score":0.09617,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":217.0,"contact_point_centroid":[0.52506,0.11938,0.05997],"force_p95":265.98383,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":274.04506,"mean_force":205.55735,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50863,0.11956,0.05144]},{"body_a":"peg","body_b":"channel_base_body","contact_count":789.0,"contact_point_centroid":[0.4993,0.08672,0.0088],"force_p95":212.66333,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":220.06146,"mean_force":53.9735,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49423,0.04597,0.08468]},{"body_a":"attachment","body_b":"peg","contact_count":285.0,"contact_point_centroid":[0.50872,0.0926,0.05288],"force_p95":215.36656,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":219.63384,"mean_force":147.95513,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49781,0.09319,0.05511]},{"body_a":"attachment","body_b":"peg","contact_count":368.0,"contact_point_centroid":[0.51207,0.11371,0.0495],"force_p95":148.90601,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":152.74012,"mean_force":117.75403,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50741,0.12391,0.04892]},{"body_a":"peg","body_b":"channel_base_body","contact_count":361.0,"contact_point_centroid":[0.50171,0.1003,0.00836],"force_p95":147.31291,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":151.0099,"mean_force":117.51221,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50753,0.12363,0.04914]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":423.0,"contact_point_centroid":[0.54806,0.12,0.05997],"force_p95":90.68257,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":96.55671,"mean_force":76.78546,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49858,0.13805,0.03449]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":348.0,"contact_point_centroid":[0.47435,0.09059,0.01916],"force_p95":44.31004,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.06033,"mean_force":36.24148,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50752,0.12408,0.04901]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.49397,0.07995,0.00937],"force_p95":0.57014,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.55973,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49843,0.13187,0.34825]},{"body_a":"peg","body_b":"channel_base_body","contact_count":441.0,"contact_point_centroid":[0.4933,0.08054,0.00998],"force_p95":0.54179,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.11281,"mean_force":0.47032,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49862,0.13805,0.03453]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49929,0.19874,0.29988]},{"body_a":"attachment","body_b":"peg","contact_count":417.0,"contact_point_centroid":[0.49963,0.12612,0.03407],"force_p95":0.30632,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.57137,"mean_force":0.27256,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49862,0.13805,0.03453]},{"body_a":"peg","body_b":"channel_base_body","contact_count":787.0,"contact_point_centroid":[0.49382,0.07993,0.00938],"force_p95":0.55022,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55037,"mean_force":0.54669,"phase_index":1.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49812,-0.01441,0.37954]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49382,0.07998,0.00938],"force_p95":0.55021,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55021,"mean_force":0.54668,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49661,-0.05376,0.24478]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47495,0.10799,0.03731],"force_p95":0.34806,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36563,"mean_force":0.22094,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49849,0.13799,0.03445]}],"total_contact_groups":14},"final_pose_error":0.00483,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49323,0.10107,0.03233],"final_tcp_position":[0.50052,0.13836,0.03691],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":274.04506,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49382,0.07993,0.03378],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16017,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.55002,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1007.0,"raw_peak_contact_force":3.77147,"tcp_end":[0.49865,0.0507,0.38034],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.34783,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":787.0,"n_steps_budget":840.0,"object_pos_end":[0.49382,0.07994,0.03378],"object_pos_start":[0.49382,0.07993,0.03378],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.16017,"object_z_max":0.03378,"peak_contact_force":0.54922,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":787.0,"raw_peak_contact_force":0.55037,"tcp_end":[0.4984,-0.07534,0.3508],"tcp_start":[0.49865,0.0507,0.38034],"tcp_to_object_dist_end":0.35304,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49379,0.07995,0.03378],"object_pos_start":[0.49382,0.07994,0.03378],"object_to_goal_dist_end":0.16019,"object_to_goal_dist_start":0.16018,"object_z_max":0.03378,"peak_contact_force":0.54143,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55021,"tcp_end":[0.49623,-0.03231,0.14289],"tcp_start":[0.4984,-0.07534,0.3508],"tcp_to_object_dist_end":0.15656,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":789.0,"n_steps_budget":1000.0,"object_pos_end":[0.49889,0.10076,0.03305],"object_pos_start":[0.49379,0.07995,0.03378],"object_to_goal_dist_end":0.18089,"object_to_goal_dist_start":0.16019,"object_z_max":0.03378,"peak_contact_force":208.63181,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1074.0,"raw_peak_contact_force":220.06146,"tcp_end":[0.50587,0.11581,0.04938],"tcp_start":[0.49623,-0.03231,0.14289],"tcp_to_object_dist_end":0.02328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":368.0,"n_steps_budget":600.0,"object_pos_end":[0.49496,0.09967,0.03685],"object_pos_start":[0.49889,0.10076,0.03305],"object_to_goal_dist_end":0.17977,"object_to_goal_dist_start":0.18089,"object_z_max":0.03832,"peak_contact_force":3.24272,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1294.0,"raw_peak_contact_force":274.04506,"tcp_end":[0.50052,0.13836,0.03691],"tcp_start":[0.50587,0.11581,0.04938],"tcp_to_object_dist_end":0.03908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49323,0.10107,0.03233],"object_pos_start":[0.49496,0.09967,0.03685],"object_to_goal_dist_end":0.18136,"object_to_goal_dist_start":0.17977,"object_z_max":0.03685,"peak_contact_force":71.39618,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1292.0,"raw_peak_contact_force":96.55671,"tcp_end":[0.49878,0.13812,0.03448],"tcp_start":[0.50052,0.13836,0.03691],"tcp_to_object_dist_end":0.03752,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```