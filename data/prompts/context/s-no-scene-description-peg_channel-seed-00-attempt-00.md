## Search State

- **Seed**: 0
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1857 | 0.74 | ✅ accepted |

**Proposal policy**: task_score is 0.74 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.186) — your mutation base

```yaml
skill: peg_channel
phases:
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
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
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: arc_cartesian
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
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: insert_2
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: force_exceeded

```

## Design Metrics

- **Composite score**: 0.186
- **task_score** (E): 0.745
- **fitness_score**: 0.556  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| insert_1 | 0.00 | 1.00 | 0.1730 |
| approach_1 | 1.00 | 1.00 | 0.1465 |
| push_1 | 0.33 | 1.00 | 0.1512 |
| retract_1 | 0.00 | 1.00 | 0.1042 |
| lift_1 | 0.00 | 1.00 | 0.1648 |
| insert_2 | 0.00 | 1.00 | 0.1656 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| insert_1 | insert | 0.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.075, 0.180) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.575 | 2.179 |
| approach_1 | approach | 1.00 / step_budget | (0.497, 0.075, 0.180)→(0.497, 0.119, 0.043) | (0.500, 0.080, 0.034)→(0.500, 0.084, 0.033) | 0.161→0.165 | 1.00 / 1.667 | 34.686 | 43.877 |
| push_1 | push | 0.33 / step_budget | (0.497, 0.119, 0.043)→(0.494, -0.032, 0.038) | (0.500, 0.084, 0.033)→(0.505, -0.059, 0.032) | 0.165→0.029 | 1.00 / 2.667 | 41.148 | 161.757 |
| retract_1 | retract | 0.00 / step_budget | (0.494, -0.032, 0.038)→(0.493, 0.005, 0.134) | (0.505, -0.059, 0.032)→(0.501, -0.056, 0.031) | 0.029→0.029 | 1.00 / 1.000 | 0.544 | 96.928 |
| lift_1 | lift | 0.00 / step_budget | (0.493, 0.005, 0.134)→(0.404, -0.048, 0.262) | (0.501, -0.056, 0.031)→(0.501, -0.056, 0.031) | 0.029→0.029 | 1.00 / 1.000 | 0.595 | 0.654 |
| insert_2 | insert | 0.00 / step_budget | (0.404, -0.048, 0.262)→(0.465, -0.069, 0.109) | (0.501, -0.056, 0.031)→(0.500, -0.056, 0.031) | 0.029→0.030 | 1.00 / 1.000 | 0.563 | 0.597 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.884
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.872
- phase_score: 0.515
- phase_breakdown.approach_score: 0.783
- phase_breakdown.contact_score: 0.000
- phase_breakdown.push_score: 0.597

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.658
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.872
- **Median Q (composite search score)**: 0.138
- **K-run variance**: 0.0052
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.297


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6915c31707ac435a9367b840736087e39a7a48adfeb36a4f94b6b3ae57cce94`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `19172182883d287409b73cab43749e937e65f1ca1d4501d52b4a913a881aad36`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57708,"average_solve_count":253.0,"average_success_count":253.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.06771,"push_1.push_distance":0.17593,"push_1.push_speed":0.07006,"retract_1.retract_height":0.15649,"retract_1.speed":0.03231},"optimized_scores":{"best_composite_score":0.28796,"best_fitness_score":0.65796,"best_task_score":0.87246},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":327.0,"contact_point_centroid":[0.54138,-0.00802,0.06],"force_p95":58.88607,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.59092,"mean_force":44.5684,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49655,-0.00587,0.03702]},{"body_a":"attachment","body_b":"peg","contact_count":744.0,"contact_point_centroid":[0.50236,-0.00188,0.0424],"force_p95":24.71732,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.29786,"mean_force":7.04428,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49639,0.00953,0.0371]},{"body_a":"peg","body_b":"channel_base_body","contact_count":66.0,"contact_point_centroid":[0.50691,-0.10042,0.06038],"force_p95":44.50208,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.85534,"mean_force":25.59761,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4972,-0.05286,0.03674]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54213,-0.05071,0.05999],"force_p95":51.77117,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":52.1054,"mean_force":49.28036,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49746,-0.05461,0.03669]},{"body_a":"peg","body_b":"channel_base_body","contact_count":603.0,"contact_point_centroid":[0.50582,-0.0223,0.00983],"force_p95":14.94689,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.71656,"mean_force":5.96762,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49642,0.02011,0.03733]},{"body_a":"peg","body_b":"channel_base_body","contact_count":35.0,"contact_point_centroid":[0.50625,-0.10045,0.05824],"force_p95":8.17202,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.52104,"mean_force":1.58049,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49652,-0.05332,0.03766]},{"body_a":"attachment","body_b":"peg","contact_count":43.0,"contact_point_centroid":[0.50565,-0.06446,0.05692],"force_p95":1.34648,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.75447,"mean_force":1.16891,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49619,-0.05262,0.03825]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":369.0,"contact_point_centroid":[0.52507,-0.00675,0.02397],"force_p95":6.18947,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.45853,"mean_force":1.87687,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49626,0.01969,0.0371]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52505,-0.08334,0.06],"force_p95":4.63242,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.00453,"mean_force":2.07731,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49746,-0.0546,0.0367]},{"body_a":"peg","body_b":"channel_base_body","contact_count":977.0,"contact_point_centroid":[0.50366,0.06159,0.00935],"force_p95":0.6416,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55484,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49748,0.13519,0.23593]},{"body_a":"peg","body_b":"channel_base_body","contact_count":961.0,"contact_point_centroid":[0.50567,-0.08008,0.00939],"force_p95":0.55756,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.02386,"mean_force":0.54801,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49427,-0.02739,0.08206]},{"body_a":"peg","body_b":"channel_base_body","contact_count":454.0,"contact_point_centroid":[0.50368,0.06157,0.00936],"force_p95":0.64141,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64379,"mean_force":0.54631,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49703,0.08639,0.11069]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49956,0.19884,0.29897]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50568,-0.07991,0.00938],"force_p95":0.55287,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55362,"mean_force":0.54673,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45038,-0.02963,0.18707]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50572,-0.07988,0.00938],"force_p95":0.55272,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55279,"mean_force":0.54673,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.43765,-0.06014,0.17485]}],"total_contact_groups":15},"final_pose_error":0.06713,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50569,-0.07989,0.03378],"final_tcp_position":[0.46928,-0.07068,0.09895],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":71.59092,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50384,0.06159,0.03376],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.59321,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":996.0,"raw_peak_contact_force":2.17216,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14707,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":454.0,"n_steps_budget":930.0,"object_pos_end":[0.5038,0.06158,0.03376],"object_pos_start":[0.50384,0.06159,0.03376],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14178,"object_z_max":0.03377,"peak_contact_force":0.47825,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":454.0,"raw_peak_contact_force":0.64379,"tcp_end":[0.49926,0.09848,0.04185],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50676,-0.08324,0.03638],"object_pos_start":[0.5038,0.06158,0.03376],"object_to_goal_dist_end":0.00832,"object_to_goal_dist_start":0.14177,"object_z_max":0.03813,"peak_contact_force":0.00538,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2109.0,"raw_peak_contact_force":71.59092,"tcp_end":[0.49748,-0.05457,0.03671],"tcp_start":[0.49926,0.09848,0.04185],"tcp_to_object_dist_end":0.03013,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50571,-0.07988,0.03378],"object_pos_start":[0.50676,-0.08324,0.03638],"object_to_goal_dist_end":0.00844,"object_to_goal_dist_start":0.00832,"object_z_max":0.03684,"peak_contact_force":0.54319,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1047.0,"raw_peak_contact_force":52.1054,"tcp_end":[0.49494,-0.0093,0.12632],"tcp_start":[0.49748,-0.05457,0.03671],"tcp_to_object_dist_end":0.11689,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5057,-0.07986,0.03378],"object_pos_start":[0.50571,-0.07988,0.03378],"object_to_goal_dist_end":0.00844,"object_to_goal_dist_start":0.00844,"object_z_max":0.03378,"peak_contact_force":0.5528,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55362,"tcp_end":[0.40876,-0.05002,0.25217],"tcp_start":[0.49494,-0.0093,0.12632],"tcp_to_object_dist_end":0.24079,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50569,-0.07989,0.03378],"object_pos_start":[0.5057,-0.07986,0.03378],"object_to_goal_dist_end":0.00843,"object_to_goal_dist_start":0.00844,"object_z_max":0.03378,"peak_contact_force":0.54376,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55279,"tcp_end":[0.46928,-0.07068,0.09895],"tcp_start":[0.40876,-0.05002,0.25217],"tcp_to_object_dist_end":0.07522,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83691,"average_solve_count":233.0,"average_success_count":233.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.09607,"push_1.push_distance":0.14973,"push_1.push_speed":0.07108,"retract_1.retract_height":0.08621,"retract_1.speed":0.06696},"optimized_scores":{"best_composite_score":0.13815,"best_fitness_score":0.50815,"best_task_score":0.84776},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":832.0,"contact_point_centroid":[0.50046,0.06758,0.00838],"force_p95":185.41364,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":188.75268,"mean_force":71.91156,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50093,0.09901,0.04348]},{"body_a":"attachment","body_b":"peg","contact_count":716.0,"contact_point_centroid":[0.50459,0.10056,0.04518],"force_p95":185.49558,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":188.3008,"mean_force":88.40406,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50168,0.11005,0.04459]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.50657,0.13982,0.05102],"force_p95":119.53343,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.43451,"mean_force":83.80714,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49846,0.14657,0.05326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":563.0,"contact_point_centroid":[0.50214,0.1166,0.00925],"force_p95":94.17839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.99062,"mean_force":15.43742,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49609,0.11288,0.10781]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":290.0,"contact_point_centroid":[0.47407,0.05936,0.04058],"force_p95":65.48139,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.04268,"mean_force":16.7657,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50028,0.08633,0.0413]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":133.0,"contact_point_centroid":[0.54181,0.03103,0.06],"force_p95":57.75258,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.83463,"mean_force":43.91076,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49681,0.03365,0.0371]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54218,0.00692,0.06],"force_p95":57.79255,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":58.63079,"mean_force":50.24841,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49726,0.0108,0.0371]},{"body_a":"peg","body_b":"world","contact_count":132.0,"contact_point_centroid":[0.50192,0.12548,-0.00017],"force_p95":19.28294,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.74864,"mean_force":13.64565,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50029,0.155,0.04486]},{"body_a":"peg","body_b":"world","contact_count":28.0,"contact_point_centroid":[0.50222,0.12719,-0.0003],"force_p95":37.33342,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.90411,"mean_force":28.00895,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49992,0.15488,0.04587]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,-0.00718,0.05822],"force_p95":8.64143,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.64143,"mean_force":8.64143,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49704,0.0222,0.03713]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50098,0.11602,0.0094],"force_p95":0.60736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55146,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49749,0.13563,0.23636]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49909,-0.01979,0.00943],"force_p95":0.55429,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66295,"mean_force":0.54455,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4944,0.0249,0.0919]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49893,-0.01974,0.0094],"force_p95":0.5519,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55775,"mean_force":0.54543,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44465,-0.00536,0.2112]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.499,-0.01958,0.00939],"force_p95":0.55082,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55623,"mean_force":0.54633,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.42589,-0.05367,0.2017]}],"total_contact_groups":14},"final_pose_error":0.09696,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4989,-0.0196,0.03385],"final_tcp_position":[0.4577,-0.06543,0.12602],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":188.75268,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11601,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.58045,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":984.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15182,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.50228,0.12805,0.02979],"object_pos_start":[0.50092,0.11601,0.03383],"object_to_goal_dist_end":0.20832,"object_to_goal_dist_start":0.19611,"object_z_max":0.0342,"peak_contact_force":103.03901,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":700.0,"raw_peak_contact_force":130.43451,"tcp_end":[0.50029,0.1577,0.04359],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49847,-0.01948,0.03465],"object_pos_start":[0.50228,0.12805,0.02979],"object_to_goal_dist_end":0.06078,"object_to_goal_dist_start":0.20832,"object_z_max":0.03844,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2104.0,"raw_peak_contact_force":188.75268,"tcp_end":[0.49726,0.01094,0.03711],"tcp_start":[0.50029,0.1577,0.04359],"tcp_to_object_dist_end":0.03054,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4988,-0.01939,0.03405],"object_pos_start":[0.49847,-0.01948,0.03465],"object_to_goal_dist_end":0.06092,"object_to_goal_dist_start":0.06078,"object_z_max":0.03472,"peak_contact_force":0.54284,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1002.0,"raw_peak_contact_force":58.63079,"tcp_end":[0.49524,0.03161,0.14828],"tcp_start":[0.49726,0.01094,0.03711],"tcp_to_object_dist_end":0.12515,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49913,-0.01959,0.03391],"object_pos_start":[0.4988,-0.01939,0.03405],"object_to_goal_dist_end":0.06072,"object_to_goal_dist_start":0.06092,"object_z_max":0.03405,"peak_contact_force":0.54985,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55775,"tcp_end":[0.39667,-0.04232,0.27869],"tcp_start":[0.49524,0.03161,0.14828],"tcp_to_object_dist_end":0.26632,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4989,-0.0196,0.03385],"object_pos_start":[0.49913,-0.01959,0.03391],"object_to_goal_dist_end":0.06072,"object_to_goal_dist_start":0.06072,"object_z_max":0.03391,"peak_contact_force":0.54419,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55623,"tcp_end":[0.4577,-0.06543,0.12602],"tcp_start":[0.39667,-0.04232,0.27869],"tcp_to_object_dist_end":0.11087,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6214,"average_solve_count":243.0,"average_success_count":243.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.06692,"push_1.push_distance":0.18387,"push_1.push_speed":0.09747,"retract_1.retract_height":0.12932,"retract_1.speed":0.03952},"optimized_scores":{"best_composite_score":0.13109,"best_fitness_score":0.50109,"best_task_score":0.51446},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":369.0,"contact_point_centroid":[0.53503,-0.01462,0.05999],"force_p95":175.07409,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":224.92841,"mean_force":101.64321,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48972,-0.01034,0.03814]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":137.0,"contact_point_centroid":[0.47498,-0.04698,0.05206],"force_p95":172.29612,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":180.04647,"mean_force":86.67657,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48548,-0.0469,0.0463]},{"body_a":"attachment","body_b":"peg","contact_count":919.0,"contact_point_centroid":[0.49762,0.00774,0.03568],"force_p95":124.82061,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":142.52948,"mean_force":72.88424,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48958,0.0136,0.03805]},{"body_a":"peg","body_b":"channel_base_body","contact_count":968.0,"contact_point_centroid":[0.50838,-0.00636,0.00953],"force_p95":88.39149,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":109.48218,"mean_force":41.53659,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48957,0.01771,0.03816]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":843.0,"contact_point_centroid":[0.52618,-0.00565,0.02712],"force_p95":96.27426,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":102.95814,"mean_force":59.68727,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48967,0.00784,0.03803]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.53353,-0.0496,0.05997],"force_p95":73.92078,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.28867,"mean_force":57.69024,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4877,-0.05335,0.039]},{"body_a":"attachment","body_b":"peg","contact_count":129.0,"contact_point_centroid":[0.49563,-0.05043,0.03766],"force_p95":65.07149,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.64775,"mean_force":38.80164,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48576,-0.0499,0.04297]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":135.0,"contact_point_centroid":[0.52607,-0.05528,0.02716],"force_p95":64.92906,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.88911,"mean_force":37.36809,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48575,-0.0497,0.04319]},{"body_a":"peg","body_b":"channel_base_body","contact_count":980.0,"contact_point_centroid":[0.49981,-0.06758,0.00825],"force_p95":25.15695,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.79708,"mean_force":2.99479,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48654,-0.02756,0.08222]},{"body_a":"peg","body_b":"link7","contact_count":369.0,"contact_point_centroid":[0.51997,0.01098,0.06787],"force_p95":23.04521,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.44862,"mean_force":11.33212,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48949,0.03594,0.03789]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":16.0,"contact_point_centroid":[0.47486,-0.09249,0.02461],"force_p95":8.63109,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.20852,"mean_force":2.19747,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48551,-0.04024,0.05464]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.49527,0.06395,0.00938],"force_p95":0.55699,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55424,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49748,0.13493,0.23568]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49942,0.19831,0.29814]},{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.49974,-0.10009,0.01263],"force_p95":0.8838,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.09383,"mean_force":0.32118,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48748,-0.05356,0.03922]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49627,-0.06963,0.00805],"force_p95":0.68341,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.85108,"mean_force":0.60599,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44553,-0.02939,0.18876]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49664,-0.0697,0.00804],"force_p95":0.68341,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68341,"mean_force":0.60589,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.43468,-0.06005,0.17776]}],"total_contact_groups":18},"final_pose_error":0.07159,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49559,-0.06958,0.02413],"final_tcp_position":[0.46686,-0.07031,0.10271],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":224.92841,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06382,0.03401],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55002,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1001.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14649,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":447.0,"n_steps_budget":930.0,"object_pos_end":[0.49519,0.06359,0.03403],"object_pos_start":[0.49482,0.06382,0.03401],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14404,"object_z_max":0.03403,"peak_contact_force":0.54085,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":447.0,"raw_peak_contact_force":0.55403,"tcp_end":[0.4911,0.10042,0.04259],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51094,-0.07444,0.02547],"object_pos_start":[0.49519,0.06359,0.03403],"object_to_goal_dist_end":0.01902,"object_to_goal_dist_start":0.14379,"object_z_max":0.03995,"peak_contact_force":123.43713,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3468.0,"raw_peak_contact_force":224.92841,"tcp_end":[0.48776,-0.05306,0.03898],"tcp_start":[0.4911,0.10042,0.04259],"tcp_to_object_dist_end":0.03431,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49856,-0.06988,0.02414],"object_pos_start":[0.51094,-0.07444,0.02547],"object_to_goal_dist_end":0.01887,"object_to_goal_dist_start":0.01902,"object_z_max":0.03117,"peak_contact_force":0.54626,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1411.0,"raw_peak_contact_force":180.04647,"tcp_end":[0.48871,-0.00863,0.12766],"tcp_start":[0.48776,-0.05306,0.03898],"tcp_to_object_dist_end":0.12069,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49684,-0.06975,0.02413],"object_pos_start":[0.49856,-0.06988,0.02414],"object_to_goal_dist_end":0.01916,"object_to_goal_dist_start":0.01887,"object_z_max":0.0242,"peak_contact_force":0.68341,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1001.0,"raw_peak_contact_force":0.85108,"tcp_end":[0.40524,-0.05021,0.25423],"tcp_start":[0.48871,-0.00863,0.12766],"tcp_to_object_dist_end":0.24843,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49559,-0.06958,0.02413],"object_pos_start":[0.49684,-0.06975,0.02413],"object_to_goal_dist_end":0.01949,"object_to_goal_dist_start":0.01916,"object_z_max":0.02413,"peak_contact_force":0.60163,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.68341,"tcp_end":[0.46686,-0.07031,0.10271],"tcp_start":[0.40524,-0.05021,0.25423],"tcp_to_object_dist_end":0.08367,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```