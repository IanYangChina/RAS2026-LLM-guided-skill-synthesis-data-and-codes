## Search State

- **Seed**: 7
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | -0.0423 | 0.01 | ❌ rejected |
| 10 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1314 | 0.26 | ❌ rejected |
| 9 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | -0.2871 | 0.00 | ❌ rejected |
| 8 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1314 | 0.26 | ❌ rejected |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.2220 | 0.00 | ❌ rejected |

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

## Current Skill (Q=-0.042) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: insert_1
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: pose_tolerance
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
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
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

```

## Design Metrics

- **Composite score**: -0.042
- **task_score** (E): 0.006
- **fitness_score**: 0.151  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.037
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_to_peg | 1.00 | 1.00 | 0.2176 |
| push_through_channel | 0.33 | 1.00 | 0.0151 |
| retract_after_push | 1.00 | 1.00 | 0.0409 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_to_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.103, 0.107) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.532 | 2.732 |
| push_through_channel | push | 0.33 / guard_failure | (0.495, 0.104, 0.076)→(0.492, 0.101, 0.062) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 2.333 | 291.734 | 293.785 |
| retract_after_push | retract | 1.00 / step_budget | (0.492, 0.101, 0.062)→(0.488, 0.100, 0.103) | (0.502, 0.098, 0.033)→(0.503, 0.110, 0.027) | 0.178→0.191 | 1.00 / 1.000 | 0.515 | 489.150 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.008
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.003
- phase_score: 0.247
- phase_breakdown.approach_peg_score: 0.822
- phase_breakdown.push_through_channel_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.154
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.016
- **Median Q (composite search score)**: -0.076
- **K-run variance**: 0.0026
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.339


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.55249,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_peg.descend_speed":0.05638,"push_through_channel.insertion_depth":0.14337,"push_through_channel.insertion_force":12.09119,"retract_after_push.retract_speed":0.0106},"optimized_scores":{"best_composite_score":-0.07599,"best_fitness_score":0.15401,"best_task_score":0.01587},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":609.0,"contact_point_centroid":[0.50258,0.11044,0.00933],"force_p95":62.42728,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":321.79744,"mean_force":13.57742,"phase_index":2.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.48891,0.11768,0.07808]},{"body_a":"attachment","body_b":"peg","contact_count":169.0,"contact_point_centroid":[0.49486,0.1294,0.05634],"force_p95":75.9476,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":320.26598,"mean_force":47.1049,"phase_index":2.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.48592,0.12609,0.06174]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50416,0.12022,0.0575],"force_p95":256.84241,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":260.32488,"mean_force":223.02736,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49584,0.11465,0.06288]},{"body_a":"peg","body_b":"channel_base_body","contact_count":35.0,"contact_point_centroid":[0.50242,0.11184,0.00939],"force_p95":195.20148,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":260.24598,"mean_force":19.57371,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50774,0.11139,0.08714]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47488,0.11994,0.05788],"force_p95":18.78246,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.93391,"mean_force":16.33703,"phase_index":2.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.47903,0.12919,0.05798]},{"body_a":"peg","body_b":"channel_base_body","contact_count":686.0,"contact_point_centroid":[0.50364,0.11174,0.00937],"force_p95":0.61237,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55665,"phase_index":0.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.50214,0.15727,0.20043]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.4997,0.1993,0.2991]}],"total_contact_groups":7},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50455,0.10918,0.0338],"final_tcp_position":[0.49016,0.11425,0.10166],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":321.79744,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":708.0,"n_steps_budget":1000.0,"object_pos_end":[0.5037,0.11176,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.5071,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":702.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach_peg","tcp_end":[0.50593,0.11662,0.10762],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07402,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":35.0,"n_steps_budget":1000.0,"object_pos_end":[0.50357,0.11186,0.03379],"object_pos_start":[0.5037,0.11176,0.0338],"object_to_goal_dist_end":0.19199,"object_to_goal_dist_start":0.19189,"object_z_max":0.03381,"peak_contact_force":225.50012,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":38.0,"raw_peak_contact_force":260.32488,"subtask_id":"push_through_channel","tcp_end":[0.49368,0.11539,0.06093],"tcp_start":[0.4948,0.11502,0.06189],"tcp_to_object_dist_end":0.0291,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":609.0,"n_steps_budget":1000.0,"object_pos_end":[0.50455,0.10918,0.0338],"object_pos_start":[0.50328,0.11196,0.03335],"object_to_goal_dist_end":0.18934,"object_to_goal_dist_start":0.19211,"object_z_max":0.03692,"peak_contact_force":0.56377,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":782.0,"raw_peak_contact_force":321.79744,"tcp_end":[0.49016,0.11425,0.10166],"tcp_start":[0.49368,0.11539,0.06093],"tcp_to_object_dist_end":0.06955,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14563,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_peg.descend_speed":0.05883,"push_through_channel.insertion_depth":0.12845,"push_through_channel.insertion_force":18.1771,"retract_after_push.retract_speed":0.04998},"optimized_scores":{"best_composite_score":-0.08109,"best_fitness_score":0.14891,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47492,0.11994,0.05987],"force_p95":620.47855,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":620.47855,"mean_force":620.47855,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4661,0.1272,0.06187]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.4722,0.11976,0.05978],"force_p95":400.31981,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":413.4282,"mean_force":286.00505,"phase_index":2.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.4638,0.12799,0.06051]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.47941,0.12655,0.05828],"force_p95":53.42994,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.15591,"mean_force":28.89622,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4695,0.1267,0.06415]},{"body_a":"peg","body_b":"channel_base_body","contact_count":38.0,"contact_point_centroid":[0.4952,0.11981,0.0094],"force_p95":1.59911,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.5563,"mean_force":1.99989,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48334,0.12136,0.08654]},{"body_a":"peg","body_b":"world","contact_count":365.0,"contact_point_centroid":[0.49867,0.15738,-0.0019],"force_p95":0.83372,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.04443,"mean_force":0.6217,"phase_index":2.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.46134,0.12647,0.08377]},{"body_a":"peg","body_b":"channel_base_body","contact_count":656.0,"contact_point_centroid":[0.49618,0.1191,0.00944],"force_p95":0.61368,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55126,"phase_index":0.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.49087,0.16059,0.2004]},{"body_a":"peg","body_b":"channel_base_body","contact_count":89.0,"contact_point_centroid":[0.4986,0.11355,0.00934],"force_p95":0.87864,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.57391,"mean_force":0.5065,"phase_index":2.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.45479,0.13645,0.06095]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.49943,0.19897,0.29799]}],"total_contact_groups":8},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50233,0.15967,0.01398],"final_tcp_position":[0.46189,0.12595,0.10188],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":620.47855,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":681.0,"n_steps_budget":1000.0,"object_pos_end":[0.496,0.11959,0.03388],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19972,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.54575,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":680.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_peg","tcp_end":[0.48372,0.12347,0.10834],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":38.0,"n_steps_budget":960.0,"object_pos_end":[0.49612,0.11915,0.03353],"object_pos_start":[0.496,0.11959,0.03388],"object_to_goal_dist_end":0.1993,"object_to_goal_dist_start":0.19972,"object_z_max":0.03388,"peak_contact_force":620.47855,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":41.0,"raw_peak_contact_force":620.47855,"subtask_id":"push_through_channel","tcp_end":[0.46524,0.1272,0.06117],"tcp_start":[0.4661,0.1272,0.06187],"tcp_to_object_dist_end":0.04222,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":459.0,"n_steps_budget":660.0,"object_pos_end":[0.50233,0.15967,0.01398],"object_pos_start":[0.49649,0.11844,0.03313],"object_to_goal_dist_end":0.24109,"object_to_goal_dist_start":0.19859,"object_z_max":0.03461,"peak_contact_force":0.43648,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":458.0,"raw_peak_contact_force":413.4282,"tcp_end":[0.46189,0.12595,0.10188],"tcp_start":[0.46524,0.1272,0.06117],"tcp_to_object_dist_end":0.10246,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.56962,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_peg.descend_speed":0.0601,"push_through_channel.insertion_depth":0.05661,"push_through_channel.insertion_force":6.34784,"retract_after_push.retract_speed":0.01417},"optimized_scores":{"best_composite_score":0.03014,"best_fitness_score":0.14903,"best_task_score":0.00261},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52527,0.06264,0.0596],"force_p95":681.05409,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":732.22553,"mean_force":365.59377,"phase_index":2.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.51444,0.06073,0.06328]},{"body_a":"attachment","body_b":"peg","contact_count":110.0,"contact_point_centroid":[0.51733,0.07148,0.05771],"force_p95":138.41253,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":318.06135,"mean_force":42.27992,"phase_index":2.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50972,0.0648,0.06286]},{"body_a":"peg","body_b":"channel_base_body","contact_count":633.0,"contact_point_centroid":[0.50465,0.06301,0.00939],"force_p95":49.77591,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":317.86722,"mean_force":7.87462,"phase_index":2.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.51148,0.06055,0.08189]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":44.0,"contact_point_centroid":[0.52502,0.06239,0.05842],"force_p95":12.3293,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.57065,"mean_force":5.98765,"phase_index":2.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.51076,0.064,0.06377]},{"body_a":"peg","body_b":"channel_base_body","contact_count":818.0,"contact_point_centroid":[0.50582,0.06302,0.00937],"force_p95":0.55612,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56311,"phase_index":0.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.51168,0.1326,0.19786]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.49973,0.19806,0.2969]},{"body_a":"peg","body_b":"channel_base_body","contact_count":29.0,"contact_point_centroid":[0.50557,0.06281,0.00939],"force_p95":0.55082,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5515,"mean_force":0.54654,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.52632,0.06107,0.08945]}],"total_contact_groups":7},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50177,0.06234,0.03427],"final_tcp_position":[0.51202,0.05956,0.10512],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":732.22553,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":846.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.06298,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.5441,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":852.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach_peg","tcp_end":[0.5245,0.06957,0.10507],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":29.0,"n_steps_budget":630.0,"object_pos_end":[0.50603,0.063,0.03381],"object_pos_start":[0.50603,0.06298,0.03381],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14324,"object_z_max":0.03381,"peak_contact_force":29.22299,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":29.0,"raw_peak_contact_force":0.5515,"subtask_id":"push_through_channel","tcp_end":[0.51564,0.06026,0.06439],"tcp_start":[0.5245,0.06957,0.10507],"tcp_to_object_dist_end":0.03217,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":633.0,"n_steps_budget":1000.0,"object_pos_end":[0.50177,0.06234,0.03427],"object_pos_start":[0.50603,0.063,0.03381],"object_to_goal_dist_end":0.14247,"object_to_goal_dist_start":0.14326,"object_z_max":0.03657,"peak_contact_force":0.54579,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":790.0,"raw_peak_contact_force":732.22553,"tcp_end":[0.51202,0.05956,0.10512],"tcp_start":[0.51564,0.06026,0.06439],"tcp_to_object_dist_end":0.07163,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```