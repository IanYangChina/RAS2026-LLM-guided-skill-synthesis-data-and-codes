## Search State

- **Seed**: 4
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → contact → grasp → insert → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | grasp_success | force_exceeded | pose_tolerance | 8 | 0.2346 | 0.18 | ❌ rejected |
| 0 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3038 | 0.61 | ✅ accepted |

**Proposal policy**: task_score is 0.18 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.235) — your mutation base

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

- **Composite score**: 0.235
- **task_score** (E): 0.183
- **fitness_score**: 0.458  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.267
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1751 |
| align_contact | 1.00 | 1.00 | 0.0869 |
| grasp_peg | 1.00 | 1.00 | 0.0001 |
| push_insert | 0.33 | 1.00 | 0.0101 |
| retract | 0.33 | 1.00 | 0.0561 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.517, 0.092, 0.165) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.544 | 3.242 |
| align_contact | contact | 1.00 / force_exceeded | (0.517, 0.092, 0.165)→(0.501, 0.095, 0.079) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 2.000 | 34.565 | 34.565 |
| grasp_peg | grasp | 1.00 / step_budget | (0.499, 0.095, 0.076)→(0.499, 0.095, 0.076) | (0.505, 0.084, 0.034)→(0.505, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.667 | 34.162 | 74.975 |
| push_insert | insert | 0.33 / guard_failure | (0.499, 0.095, 0.076)→(0.499, 0.085, 0.074) | (0.505, 0.081, 0.034)→(0.505, 0.074, 0.036) | 0.162→0.154 | 1.00 / 2.333 | 42.117 | 42.117 |
| retract | retract | 0.33 / step_budget | (0.499, 0.085, 0.074)→(0.507, 0.046, 0.075) | (0.505, 0.074, 0.036)→(0.503, 0.050, 0.033) | 0.154→0.130 | 1.00 / 3.000 | 42.231 | 322.195 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.320
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.165
- phase_score: 0.647
- phase_breakdown.insertion_depth_score: 0.249
- phase_breakdown.contact_peg_score: 1.000
- phase_breakdown.reach_above_peg_score: 0.823

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.564
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.360
- **Median Q (composite search score)**: 0.274
- **K-run variance**: 0.0155
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.359


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60526,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_contact.align_offset_x":0.01048,"align_contact.align_offset_y":0.01995,"align_contact.contact_force":12.92324,"approach_peg.approach_speed":0.07655,"push_insert.insertion_force":8.8526,"push_insert.push_distance":0.14225,"push_insert.push_speed":0.03922,"retract.retract_speed":0.05402},"optimized_scores":{"best_composite_score":0.06619,"best_fitness_score":0.35619,"best_task_score":0.02297},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":508.0,"contact_point_centroid":[0.525,0.11994,0.05783],"force_p95":206.69251,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":334.7077,"mean_force":123.16173,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51381,0.07838,0.06813]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":594.0,"contact_point_centroid":[0.47499,0.11998,0.05999],"force_p95":293.16536,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":314.17362,"mean_force":192.53473,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51506,0.07666,0.06593]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":684.0,"contact_point_centroid":[0.52504,0.07964,0.05998],"force_p95":194.14064,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":220.76195,"mean_force":142.73355,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51506,0.07689,0.06599]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":532.0,"contact_point_centroid":[0.52501,0.12,0.05999],"force_p95":66.72538,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":67.293,"mean_force":63.05894,"phase_index":2.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.51661,0.095,0.06883]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,0.12,0.05999],"force_p95":45.43812,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.43812,"mean_force":45.43812,"phase_index":3.0,"phase_name":"push_insert","phase_type":"insert","tcp_position_centroid":[0.51609,0.09489,0.06833]},{"body_a":"peg","body_b":"channel_base_body","contact_count":550.0,"contact_point_centroid":[0.50199,0.07468,0.0095],"force_p95":23.44002,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.93781,"mean_force":3.18425,"phase_index":2.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.51664,0.09501,0.06886]},{"body_a":"attachment","body_b":"peg","contact_count":185.0,"contact_point_centroid":[0.51072,0.09504,0.05918],"force_p95":30.46842,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.47881,"mean_force":7.96837,"phase_index":2.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.5169,0.09507,0.06909]},{"body_a":"peg","body_b":"channel_base_body","contact_count":469.0,"contact_point_centroid":[0.50598,0.08091,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.82213,"mean_force":0.60066,"phase_index":1.0,"phase_name":"align_contact","phase_type":"contact","tcp_position_centroid":[0.51911,0.09191,0.10628]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51679,0.09529,0.05872],"force_p95":25.31759,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.31759,"mean_force":25.31759,"phase_index":1.0,"phase_name":"align_contact","phase_type":"contact","tcp_position_centroid":[0.51786,0.09536,0.07064]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1150.0,"contact_point_centroid":[0.49921,0.05779,0.00996],"force_p95":2.22735,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.23478,"mean_force":1.13143,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51444,0.07822,0.06711]},{"body_a":"attachment","body_b":"peg","contact_count":995.0,"contact_point_centroid":[0.50428,0.07737,0.06125],"force_p95":1.94868,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.86572,"mean_force":0.79107,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51453,0.07777,0.06691]},{"body_a":"peg","body_b":"channel_base_body","contact_count":599.0,"contact_point_centroid":[0.5057,0.08086,0.00936],"force_p95":0.55706,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57224,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51471,0.14171,0.22746]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50003,0.19756,0.29666]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50209,0.05949,0.00938],"force_p95":0.5442,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5442,"mean_force":0.5442,"phase_index":3.0,"phase_name":"push_insert","phase_type":"insert","tcp_position_centroid":[0.51609,0.09489,0.06833]}],"total_contact_groups":14},"final_pose_error":0.17365,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50102,0.06491,0.03959],"final_tcp_position":[0.51519,0.07626,0.06581],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":334.7077,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":628.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54527,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":635.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_above_peg","tcp_end":[0.53011,0.08823,0.16388],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13253,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":469.0,"n_steps_budget":840.0,"object_pos_end":[0.50599,0.0809,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":25.82213,"phase_name":"align_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":470.0,"raw_peak_contact_force":25.82213,"subtask_id":"contact_peg","tcp_end":[0.51785,0.09538,0.07042],"tcp_start":[0.53011,0.08823,0.16388],"tcp_to_object_dist_end":0.04115,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50397,0.07737,0.0342],"object_pos_start":[0.50599,0.0809,0.03378],"object_to_goal_dist_end":0.15753,"object_to_goal_dist_start":0.16113,"object_z_max":0.03492,"peak_contact_force":63.43474,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1267.0,"raw_peak_contact_force":67.293,"subtask_id":"contact_peg","tcp_end":[0.51609,0.09489,0.06833],"tcp_start":[0.51618,0.09491,0.06843],"tcp_to_object_dist_end":0.04023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50397,0.07735,0.03378],"object_pos_start":[0.50397,0.07734,0.03378],"object_to_goal_dist_end":0.15752,"object_to_goal_dist_start":0.15751,"object_z_max":0.03378,"peak_contact_force":45.43812,"phase_name":"push_insert","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":45.43812,"subtask_id":"insertion_depth","tcp_end":[0.51609,0.09489,0.06832],"tcp_start":[0.51609,0.09489,0.06833],"tcp_to_object_dist_end":0.0406,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50102,0.06491,0.03959],"object_pos_start":[0.50397,0.07735,0.03378],"object_to_goal_dist_end":0.14491,"object_to_goal_dist_start":0.15752,"object_z_max":0.03963,"peak_contact_force":52.39875,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3931.0,"raw_peak_contact_force":334.7077,"subtask_id":"insertion_depth","tcp_end":[0.51508,0.07634,0.06584],"tcp_start":[0.51609,0.09489,0.06832],"tcp_to_object_dist_end":0.0319,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `54762c1e743ba455eff3c9979c2b42f5642abe1893e28eae37dc231d7efcd4e4`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83784,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_contact.align_offset_x":-0.01988,"align_contact.align_offset_y":0.01987,"align_contact.contact_force":14.84773,"approach_peg.approach_speed":0.09903,"push_insert.insertion_force":19.40263,"push_insert.push_distance":0.16541,"push_insert.push_speed":0.03707,"retract.retract_speed":0.09768},"optimized_scores":{"best_composite_score":0.36397,"best_fitness_score":0.45397,"best_task_score":0.16514},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":140.0,"contact_point_centroid":[0.52509,0.10303,0.04282],"force_p95":338.56524,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":415.15583,"mean_force":104.2755,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51385,0.10042,0.03988]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1079.0,"contact_point_centroid":[0.46346,0.11994,0.05932],"force_p95":235.68443,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":407.96312,"mean_force":179.68031,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50029,0.08953,0.04891]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":52.0,"contact_point_centroid":[0.47497,0.11989,0.0588],"force_p95":304.95037,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":322.24145,"mean_force":104.51148,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48725,0.08252,0.05957]},{"body_a":"attachment","body_b":"peg","contact_count":973.0,"contact_point_centroid":[0.5023,0.08675,0.04911],"force_p95":8.97047,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.6018,"mean_force":3.55296,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49915,0.08879,0.04998]},{"body_a":"peg","body_b":"channel_base_body","contact_count":550.0,"contact_point_centroid":[0.50639,0.096,0.00951],"force_p95":32.51738,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.00481,"mean_force":5.03541,"phase_index":2.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.49043,0.11695,0.06531]},{"body_a":"attachment","body_b":"peg","contact_count":268.0,"contact_point_centroid":[0.49949,0.11732,0.05904],"force_p95":36.52143,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.54496,"mean_force":9.30766,"phase_index":2.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.49101,0.11734,0.06621]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1130.0,"contact_point_centroid":[0.50642,0.06401,0.00993],"force_p95":6.77038,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.3174,"mean_force":2.69516,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49989,0.08939,0.04923]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":858.0,"contact_point_centroid":[0.52511,0.07346,0.03546],"force_p95":5.85826,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.11814,"mean_force":2.27662,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49719,0.08727,0.05131]},{"body_a":"attachment","body_b":"peg","contact_count":316.0,"contact_point_centroid":[0.49848,0.10038,0.05521],"force_p95":17.20025,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.85958,"mean_force":11.18762,"phase_index":3.0,"phase_name":"push_insert","phase_type":"insert","tcp_position_centroid":[0.48746,0.10029,0.0595]},{"body_a":"peg","body_b":"channel_base_body","contact_count":472.0,"contact_point_centroid":[0.50599,0.10455,0.00939],"force_p95":0.57569,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.17527,"mean_force":0.59847,"phase_index":1.0,"phase_name":"align_contact","phase_type":"contact","tcp_position_centroid":[0.50316,0.11573,0.1075]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49479,0.11863,0.05884],"force_p95":24.82585,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.82585,"mean_force":24.82585,"phase_index":1.0,"phase_name":"align_contact","phase_type":"contact","tcp_position_centroid":[0.49384,0.1187,0.07076]},{"body_a":"peg","body_b":"channel_base_body","contact_count":330.0,"contact_point_centroid":[0.50792,0.07632,0.00984],"force_p95":12.49493,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.74401,"mean_force":7.62428,"phase_index":3.0,"phase_name":"push_insert","phase_type":"insert","tcp_position_centroid":[0.48754,0.10092,0.05966]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":312.0,"contact_point_centroid":[0.52517,0.08574,0.05031],"force_p95":11.31343,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.72409,"mean_force":6.80601,"phase_index":3.0,"phase_name":"push_insert","phase_type":"insert","tcp_position_centroid":[0.48744,0.10012,0.05946]},{"body_a":"peg","body_b":"channel_base_body","contact_count":505.0,"contact_point_centroid":[0.5056,0.10471,0.00937],"force_p95":0.57748,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56875,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50937,0.15373,0.22847]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49996,0.19792,0.29673]}],"total_contact_groups":15},"final_pose_error":0.20615,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50487,0.07406,0.03527],"final_tcp_position":[0.51495,0.09992,0.0405],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":415.15583,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":532.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.5424,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":537.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_above_peg","tcp_end":[0.51968,0.11123,0.16543],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13247,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":472.0,"n_steps_budget":870.0,"object_pos_end":[0.50588,0.10456,0.03382],"object_pos_start":[0.506,0.10464,0.03384],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18484,"object_z_max":0.03384,"peak_contact_force":25.17527,"phase_name":"align_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":473.0,"raw_peak_contact_force":25.17527,"subtask_id":"contact_peg","tcp_end":[0.4938,0.11873,0.07055],"tcp_start":[0.51968,0.11123,0.16543],"tcp_to_object_dist_end":0.04118,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50662,0.09946,0.03378],"object_pos_start":[0.50588,0.10456,0.03382],"object_to_goal_dist_end":0.17969,"object_to_goal_dist_start":0.18476,"object_z_max":0.03489,"peak_contact_force":0.02543,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":818.0,"raw_peak_contact_force":39.00481,"subtask_id":"contact_peg","tcp_end":[0.48982,0.1165,0.06435],"tcp_start":[0.48982,0.1165,0.06435],"tcp_to_object_dist_end":0.03882,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":330.0,"n_steps_budget":1000.0,"object_pos_end":[0.50765,0.0769,0.03978],"object_pos_start":[0.50663,0.09949,0.03378],"object_to_goal_dist_end":0.15708,"object_to_goal_dist_start":0.17972,"object_z_max":0.03978,"peak_contact_force":30.85958,"phase_name":"push_insert","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":958.0,"raw_peak_contact_force":30.85958,"subtask_id":"insertion_depth","tcp_end":[0.48731,0.08697,0.05815],"tcp_start":[0.48982,0.1165,0.06435],"tcp_to_object_dist_end":0.0292,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50487,0.07406,0.03527],"object_pos_start":[0.50765,0.0769,0.03978],"object_to_goal_dist_end":0.1542,"object_to_goal_dist_start":0.15708,"object_z_max":0.04075,"peak_contact_force":73.66978,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4232.0,"raw_peak_contact_force":415.15583,"subtask_id":"insertion_depth","tcp_end":[0.51368,0.10066,0.03966],"tcp_start":[0.48731,0.08697,0.05815],"tcp_to_object_dist_end":0.02837,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b230a5798f38c3fb8968a6bc74f96ee85fe7026f3170cf8216fc868a1c5c570f`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52336,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_contact.align_offset_x":-0.0129,"align_contact.align_offset_y":0.00286,"align_contact.contact_force":6.21938,"approach_peg.approach_speed":0.09471,"push_insert.insertion_force":17.27356,"push_insert.push_distance":0.12087,"push_insert.push_speed":0.02742,"retract.retract_speed":0.05365},"optimized_scores":{"best_composite_score":0.27378,"best_fitness_score":0.56378,"best_task_score":0.36033},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":559.0,"contact_point_centroid":[0.47499,0.11997,0.05998],"force_p95":212.0051,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":216.72065,"mean_force":160.24566,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49651,0.07106,0.09263]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":546.0,"contact_point_centroid":[0.475,0.11999,0.05999],"force_p95":52.27719,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":118.62846,"mean_force":43.89882,"phase_index":2.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.49232,0.07337,0.09579]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47499,0.11997,0.05998],"force_p95":52.69642,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":52.69642,"mean_force":52.69642,"phase_index":1.0,"phase_name":"align_contact","phase_type":"contact","tcp_position_centroid":[0.49241,0.07191,0.09763]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.475,0.11999,0.06],"force_p95":50.05197,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":50.05197,"mean_force":50.05197,"phase_index":3.0,"phase_name":"push_insert","phase_type":"insert","tcp_position_centroid":[0.49226,0.07371,0.09531]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1142.0,"contact_point_centroid":[0.50379,0.0499,0.00933],"force_p95":25.52634,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.45962,"mean_force":3.98638,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49585,0.03073,0.10358]},{"body_a":"peg","body_b":"link7","contact_count":222.0,"contact_point_centroid":[0.49936,0.06161,0.06545],"force_p95":39.28567,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.07739,"mean_force":17.76028,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49498,0.00901,0.11033]},{"body_a":"peg","body_b":"channel_base_body","contact_count":602.0,"contact_point_centroid":[0.50302,0.06743,0.00934],"force_p95":0.55514,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56093,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49921,0.13656,0.2292]},{"body_a":"peg","body_b":"channel_base_body","contact_count":345.0,"contact_point_centroid":[0.5031,0.06758,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55089,"mean_force":0.54665,"phase_index":1.0,"phase_name":"align_contact","phase_type":"contact","tcp_position_centroid":[0.48861,0.07723,0.11567]},{"body_a":"peg","body_b":"channel_base_body","contact_count":550.0,"contact_point_centroid":[0.50309,0.06745,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55071,"mean_force":0.54664,"phase_index":2.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.49232,0.07337,0.09579]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.5145,0.05358,0.00938],"force_p95":0.54779,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54779,"mean_force":0.54779,"phase_index":3.0,"phase_name":"push_insert","phase_type":"insert","tcp_position_centroid":[0.49226,0.07371,0.09531]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,0.01049,0.05572],"force_p95":0.43543,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43543,"mean_force":0.43543,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49495,-0.02793,0.1209]}],"total_contact_groups":11},"final_pose_error":0.04553,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5039,0.00981,0.02442],"final_tcp_position":[0.49544,-0.03771,0.12376],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":216.72065,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":618.0,"n_steps_budget":1000.0,"object_pos_end":[0.50304,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54574,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":602.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_above_peg","tcp_end":[0.49995,0.07566,0.16435],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13084,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":345.0,"n_steps_budget":840.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50304,0.0675,0.0338],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":52.69642,"phase_name":"align_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":346.0,"raw_peak_contact_force":52.69642,"subtask_id":"contact_peg","tcp_end":[0.4924,0.07191,0.09746],"tcp_start":[0.49995,0.07566,0.16435],"tcp_to_object_dist_end":0.0647,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14762,"object_z_max":0.0338,"peak_contact_force":39.02653,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1096.0,"raw_peak_contact_force":118.62846,"subtask_id":"contact_peg","tcp_end":[0.49226,0.07371,0.09531],"tcp_start":[0.49228,0.07368,0.09536],"tcp_to_object_dist_end":0.06277,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50307,0.06743,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":50.05197,"phase_name":"push_insert","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":50.05197,"subtask_id":"insertion_depth","tcp_end":[0.49226,0.07372,0.09531],"tcp_start":[0.49226,0.07371,0.09531],"tcp_to_object_dist_end":0.06277,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5039,0.00981,0.02442],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.09123,"object_to_goal_dist_start":0.14758,"object_z_max":0.04079,"peak_contact_force":0.62552,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1924.0,"raw_peak_contact_force":216.72065,"subtask_id":"insertion_depth","tcp_end":[0.49303,-0.03824,0.12016],"tcp_start":[0.49226,0.07372,0.09531],"tcp_to_object_dist_end":0.10767,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```