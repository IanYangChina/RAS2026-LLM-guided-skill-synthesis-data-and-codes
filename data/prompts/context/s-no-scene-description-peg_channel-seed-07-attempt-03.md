## Search State

- **Seed**: 7
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | force_exceeded | 6 | 0.0319 | 0.02 | ❌ rejected |
| 2 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1314 | 0.26 | ✅ accepted |
| 1 | approach → descend → grasp → align → push → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | admittance_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | force_exceeded | pose_tolerance | 5 | -0.0266 | 0.22 | ❌ rejected |
| 0 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1315 | 0.26 | ✅ accepted |

**Proposal policy**: task_score is 0.02 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.032) — your mutation base

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

- **Composite score**: 0.032
- **task_score** (E): 0.016
- **fitness_score**: 0.142  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1764 |
| descend_1 | 1.00 | 1.00 | 0.0884 |
| align_1 | 1.00 | 1.00 | 0.0180 |
| insert_1 | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.503, 0.109, 0.151) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.536 | 2.732 |
| descend_1 | descend | 1.00 / force_exceeded | (0.503, 0.109, 0.151)→(0.498, 0.100, 0.063) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 2.000 | 21.045 | 21.045 |
| align_1 | align | 1.00 / step_budget | (0.498, 0.100, 0.063)→(0.507, 0.095, 0.050) | (0.502, 0.098, 0.034)→(0.501, 0.094, 0.028) | 0.178→0.175 | 1.00 / 3.000 | 223.568 | 285.992 |
| insert_1 | insert | 0.00 / guard_failure | (0.507, 0.095, 0.050)→(0.507, 0.095, 0.050) | (0.501, 0.094, 0.028)→(0.501, 0.094, 0.028) | 0.175→0.175 | 1.00 / 3.000 | 132.164 | 132.164 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.026
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.024
- phase_score: 0.272
- phase_breakdown.approach_target_score: 0.906
- phase_breakdown.insertion_progress_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.173
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.024
- **Median Q (composite search score)**: 0.060
- **K-run variance**: 0.0017
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.413


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.625,"average_solve_count":88.0,"average_success_count":88.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.0093,"align_1.lateral_offset_y":-0.0079,"approach_1.speed":0.0768,"descend_1.descent_force":6.21937,"insert_1.insertion_depth":0.07326,"insert_1.insertion_force":37.83171},"optimized_scores":{"best_composite_score":0.06259,"best_fitness_score":0.17259,"best_task_score":0.02356},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":517.0,"contact_point_centroid":[0.51098,0.10804,0.00662],"force_p95":222.25334,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":252.71382,"mean_force":132.0806,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50148,0.10909,0.05329]},{"body_a":"attachment","body_b":"peg","contact_count":517.0,"contact_point_centroid":[0.51247,0.10924,0.05086],"force_p95":226.07496,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":252.45545,"mean_force":132.01372,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50148,0.10909,0.05329]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50909,0.09084,0.00468],"force_p95":125.78737,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":125.78737,"mean_force":125.78737,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50437,0.10644,0.04602]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51538,0.10664,0.04532],"force_p95":124.81308,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":124.81308,"mean_force":124.81308,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50437,0.10644,0.04602]},{"body_a":"peg","body_b":"channel_base_body","contact_count":369.0,"contact_point_centroid":[0.50355,0.11162,0.00941],"force_p95":0.59636,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.66365,"mean_force":0.59869,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50237,0.11303,0.10163]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5117,0.1121,0.05876],"force_p95":20.23144,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.23144,"mean_force":20.23144,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5007,0.1119,0.0635]},{"body_a":"peg","body_b":"world","contact_count":65.0,"contact_point_centroid":[0.51368,0.10695,-0.0002],"force_p95":10.94213,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.38506,"mean_force":4.54292,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50387,0.10676,0.04676]},{"body_a":"peg","body_b":"channel_base_body","contact_count":897.0,"contact_point_centroid":[0.50361,0.11172,0.00938],"force_p95":0.60971,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55371,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50233,0.15571,0.21643]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49967,0.19931,0.29927]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.50942,0.09095,-0.00032],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50437,0.10644,0.04602]}],"total_contact_groups":10},"final_pose_error":0.07325,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50287,0.10758,0.02446],"final_tcp_position":[0.50441,0.10642,0.04603],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":252.71382,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":919.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11181,0.03389],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19194,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.53634,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":913.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach_target","tcp_end":[0.50631,0.11468,0.14144],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10762,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":369.0,"n_steps_budget":690.0,"object_pos_end":[0.50373,0.11171,0.03379],"object_pos_start":[0.50372,0.11181,0.03389],"object_to_goal_dist_end":0.19185,"object_to_goal_dist_start":0.19194,"object_z_max":0.03398,"peak_contact_force":20.66365,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":370.0,"raw_peak_contact_force":20.66365,"tcp_end":[0.5007,0.1119,0.06331],"tcp_start":[0.50631,0.11468,0.14144],"tcp_to_object_dist_end":0.02967,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":517.0,"n_steps_budget":600.0,"object_pos_end":[0.50285,0.10759,0.02445],"object_pos_start":[0.50373,0.11171,0.03379],"object_to_goal_dist_end":0.18826,"object_to_goal_dist_start":0.19185,"object_z_max":0.03379,"peak_contact_force":219.04975,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1099.0,"raw_peak_contact_force":252.71382,"tcp_end":[0.50437,0.10644,0.04602],"tcp_start":[0.5007,0.1119,0.06331],"tcp_to_object_dist_end":0.02165,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50287,0.10758,0.02446],"object_pos_start":[0.50285,0.10759,0.02445],"object_to_goal_dist_end":0.18825,"object_to_goal_dist_start":0.18826,"object_z_max":0.02445,"peak_contact_force":125.78737,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":125.78737,"subtask_id":"insertion_progress","tcp_end":[0.50441,0.10642,0.04603],"tcp_start":[0.50437,0.10644,0.04602],"tcp_to_object_dist_end":0.02166,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04403,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00606,"align_1.lateral_offset_y":-0.0099,"approach_1.speed":0.02999,"descend_1.descent_force":12.15452,"insert_1.insertion_depth":0.11839,"insert_1.insertion_force":27.84251},"optimized_scores":{"best_composite_score":0.06032,"best_fitness_score":0.17032,"best_task_score":0.01758},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":78.0,"contact_point_centroid":[0.52512,0.11378,0.05995],"force_p95":303.18767,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":305.0096,"mean_force":195.12651,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50808,0.11375,0.05003]},{"body_a":"peg","body_b":"channel_base_body","contact_count":542.0,"contact_point_centroid":[0.50705,0.11563,0.00725],"force_p95":213.72922,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":220.80158,"mean_force":128.76568,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49776,0.11609,0.05444]},{"body_a":"attachment","body_b":"peg","contact_count":542.0,"contact_point_centroid":[0.50835,0.1165,0.05215],"force_p95":213.26179,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":220.29473,"mean_force":128.25037,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49776,0.11609,0.05444]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51209,0.11928,0.00702],"force_p95":128.34321,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":128.34321,"mean_force":128.34321,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50786,0.11377,0.04999]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51144,0.11576,0.05148],"force_p95":127.90406,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":127.90406,"mean_force":127.90406,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50786,0.11377,0.04999]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52505,0.11381,0.05998],"force_p95":29.82294,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":29.82294,"mean_force":29.82294,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50786,0.11377,0.04999]},{"body_a":"peg","body_b":"channel_base_body","contact_count":432.0,"contact_point_centroid":[0.49602,0.11923,0.00941],"force_p95":0.60366,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.0323,"mean_force":0.5951,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48472,0.12039,0.1015]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49914,0.11964,0.05897],"force_p95":22.56078,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.56078,"mean_force":22.56078,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48825,0.11935,0.06401]},{"body_a":"peg","body_b":"channel_base_body","contact_count":900.0,"contact_point_centroid":[0.49617,0.11917,0.00943],"force_p95":0.60642,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.54874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49074,0.15982,0.21778]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49944,0.19915,0.29868]}],"total_contact_groups":10},"final_pose_error":0.11839,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49436,0.11568,0.02909],"final_tcp_position":[0.50786,0.11377,0.05],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":305.0096,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":925.0,"n_steps_budget":1000.0,"object_pos_end":[0.49605,0.11935,0.03384],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19949,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52402,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":924.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_target","tcp_end":[0.48363,0.12206,0.14281],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1097,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":432.0,"n_steps_budget":690.0,"object_pos_end":[0.49595,0.11901,0.03395],"object_pos_start":[0.49605,0.11935,0.03384],"object_to_goal_dist_end":0.19914,"object_to_goal_dist_start":0.19949,"object_z_max":0.03398,"peak_contact_force":23.0323,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":433.0,"raw_peak_contact_force":23.0323,"tcp_end":[0.48829,0.11935,0.06382],"tcp_start":[0.48363,0.12206,0.14281],"tcp_to_object_dist_end":0.03084,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49449,0.11569,0.02905],"object_pos_start":[0.49595,0.11901,0.03395],"object_to_goal_dist_end":0.19607,"object_to_goal_dist_start":0.19914,"object_z_max":0.03402,"peak_contact_force":276.17047,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1162.0,"raw_peak_contact_force":305.0096,"tcp_end":[0.50786,0.11377,0.04999],"tcp_start":[0.48829,0.11935,0.06382],"tcp_to_object_dist_end":0.02491,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":750.0,"object_pos_end":[0.49436,0.11568,0.02909],"object_pos_start":[0.49449,0.11569,0.02905],"object_to_goal_dist_end":0.19607,"object_to_goal_dist_start":0.19607,"object_z_max":0.02905,"peak_contact_force":128.34321,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":128.34321,"subtask_id":"insertion_progress","tcp_end":[0.50786,0.11377,0.05],"tcp_start":[0.50786,0.11377,0.04999],"tcp_to_object_dist_end":0.02496,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60976,"average_solve_count":82.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":5e-05,"align_1.lateral_offset_y":-0.00387,"approach_1.speed":0.09977,"descend_1.descent_force":10.17357,"insert_1.insertion_depth":0.14311,"insert_1.insertion_force":39.07228},"optimized_scores":{"best_composite_score":-0.02707,"best_fitness_score":0.08293,"best_task_score":0.00704},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":282.0,"contact_point_centroid":[0.52505,0.06586,0.05998],"force_p95":276.74655,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":300.25204,"mean_force":187.27774,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50934,0.06585,0.05405]},{"body_a":"peg","body_b":"channel_base_body","contact_count":522.0,"contact_point_centroid":[0.51841,0.06599,0.00782],"force_p95":166.68087,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":169.76257,"mean_force":123.5864,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50823,0.0667,0.05586]},{"body_a":"attachment","body_b":"peg","contact_count":522.0,"contact_point_centroid":[0.51921,0.06667,0.05333],"force_p95":166.19363,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":169.27395,"mean_force":123.07106,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50823,0.0667,0.05586]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52209,0.06677,0.00739],"force_p95":142.36142,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":142.36142,"mean_force":142.36142,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50898,0.06575,0.05365]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51988,0.0658,0.0517],"force_p95":141.77391,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":141.77391,"mean_force":141.77391,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50898,0.06575,0.05365]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52505,0.06577,0.05998],"force_p95":35.3303,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.3303,"mean_force":35.3303,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50898,0.06575,0.05365]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":51.0,"contact_point_centroid":[0.52503,0.06117,0.05237],"force_p95":22.86825,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.62841,"mean_force":5.7043,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50905,0.06622,0.05504]},{"body_a":"peg","body_b":"channel_base_body","contact_count":477.0,"contact_point_centroid":[0.50592,0.06297,0.00938],"force_p95":0.55275,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.4396,"mean_force":0.58619,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51202,0.08021,0.11484]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51678,0.06959,0.05879],"force_p95":19.03154,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.03154,"mean_force":19.03154,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50579,0.06964,0.06355]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50586,0.06296,0.00937],"force_p95":0.55508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56049,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50962,0.1428,0.22923]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49967,0.19817,0.29748]}],"total_contact_groups":11},"final_pose_error":0.14311,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50549,0.06001,0.02984],"final_tcp_position":[0.50898,0.06575,0.05366],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":300.25204,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54709,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1006.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach_target","tcp_end":[0.52038,0.09077,0.16791],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13771,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":477.0,"n_steps_budget":870.0,"object_pos_end":[0.50592,0.06302,0.03381],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14323,"object_z_max":0.03381,"peak_contact_force":19.4396,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":478.0,"raw_peak_contact_force":19.4396,"tcp_end":[0.50577,0.0696,0.06335],"tcp_start":[0.52038,0.09077,0.16791],"tcp_to_object_dist_end":0.03026,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":522.0,"n_steps_budget":600.0,"object_pos_end":[0.5055,0.06001,0.02984],"object_pos_start":[0.50592,0.06302,0.03381],"object_to_goal_dist_end":0.14049,"object_to_goal_dist_start":0.14328,"object_z_max":0.03384,"peak_contact_force":175.48237,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1377.0,"raw_peak_contact_force":300.25204,"tcp_end":[0.50898,0.06575,0.05365],"tcp_start":[0.50577,0.0696,0.06335],"tcp_to_object_dist_end":0.02473,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":900.0,"object_pos_end":[0.50549,0.06001,0.02984],"object_pos_start":[0.5055,0.06001,0.02984],"object_to_goal_dist_end":0.14049,"object_to_goal_dist_start":0.14049,"object_z_max":0.02984,"peak_contact_force":142.36142,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":142.36142,"subtask_id":"insertion_progress","tcp_end":[0.50898,0.06575,0.05366],"tcp_start":[0.50898,0.06575,0.05365],"tcp_to_object_dist_end":0.02474,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```