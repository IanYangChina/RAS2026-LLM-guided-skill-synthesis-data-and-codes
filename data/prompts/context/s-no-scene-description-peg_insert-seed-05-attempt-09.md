## Search State

- **Seed**: 5
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.8963 | 0.94 | ❌ rejected |
| 8 | grasp → approach → insert → release → retract | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | grasp_success | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.2855 | 0.86 | ❌ rejected |
| 7 | approach → insert → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.4161 | 0.89 | ❌ rejected |
| 6 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | 0.6642 | 0.96 | ❌ rejected |
| 5 | approach → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.4773 | 0.86 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.94). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

- Task name: peg_insert
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

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

## Current Skill (Q=0.896) — your mutation base

```yaml
skill: peg_insert
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

- **Composite score**: 0.896
- **task_score** (E): 0.938
- **fitness_score**: 0.893  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.00 | 0.0619 |
| insert_1 | 1.00 | 1.00 | 0.1877 |
| retract_1 | 0.00 | 0.00 | 0.0930 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.502, 0.006, 0.239) | (0.504, -0.000, 0.340)→(0.506, 0.006, 0.279) | 0.260→0.199 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_1 | insert | 1.00 / force_exceeded | (0.502, 0.006, 0.239)→(0.504, 0.011, 0.052) | (0.506, 0.006, 0.279)→(0.509, 0.011, 0.091) | 0.199→0.022 | 1.00 / 1.000 | 64.233 | 0.000 |
| retract_1 | retract | 0.00 / step_budget | (0.504, 0.011, 0.052)→(0.505, 0.013, 0.145) | (0.509, 0.011, 0.091)→(0.511, 0.013, 0.184) | 0.022→0.107 | 0.00 / 0.000 | 0.000 | 73.762 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.985
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.985
- phase_score: 0.898
- phase_breakdown.insertion_progress_score: 0.936
- phase_breakdown.reach_above_hole_score: 0.810

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.933
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.985
- **Median Q (composite search score)**: 0.879
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.360


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `5e5af3f51d5f63e3a348998ea00f94a7255959965642a40069d0a7b5ef8ede34`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `cc7f64fba434a86728ba6288ab9746a03660fc43702ba486c544717f06e4937d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.61233,"average_solve_count":227.0,"average_success_count":227.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_x":-0.018,"approach_1.lateral_y":-0.01872,"approach_1.speed":0.07269,"insert_1.force_threshold":35.97253,"insert_1.insertion_depth":0.12914,"retract_1.speed":0.05865},"optimized_scores":{"best_composite_score":0.87891,"best_fitness_score":0.87558,"best_task_score":0.9169},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.52731,0.01717,0.04995],"force_p95":64.56882,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.87204,"mean_force":49.92796,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51243,0.01712,0.05179]}],"total_contact_groups":1},"final_pose_error":0.09036,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.51521,0.02088,0.14019],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":69.87204,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":229.0,"n_steps_budget":1000.0,"object_pos_end":[0.50719,0.0047,0.2788],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.19898,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.50262,0.00469,0.23906],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":988.0,"n_steps_budget":1000.0,"object_pos_end":[0.51739,0.01714,0.09152],"object_pos_start":[0.50719,0.0047,0.2788],"object_to_goal_dist_end":0.027,"object_to_goal_dist_start":0.19898,"object_z_max":0.2788,"peak_contact_force":65.55185,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_progress","tcp_end":[0.51235,0.01711,0.05184],"tcp_start":[0.50262,0.00469,0.23906],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52072,0.02093,0.17981],"object_pos_start":[0.51739,0.01714,0.09152],"object_to_goal_dist_end":0.10406,"object_to_goal_dist_start":0.027,"object_z_max":0.17972,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":6.0,"raw_peak_contact_force":69.87204,"tcp_end":[0.51521,0.02088,0.14019],"tcp_start":[0.51235,0.01711,0.05184],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `619899a8ac3451ebc6b92c72992387b20e095386c555898a9ee2a3180ddd0ca3`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.62069,"average_solve_count":232.0,"average_success_count":232.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_x":0.00274,"approach_1.lateral_y":0.01887,"approach_1.speed":0.07144,"insert_1.force_threshold":21.03569,"insert_1.insertion_depth":0.17958,"retract_1.speed":0.01457},"optimized_scores":{"best_composite_score":0.93636,"best_fitness_score":0.93303,"best_task_score":0.98537},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.51354,-0.00442,0.04986],"force_p95":65.00449,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.28854,"mean_force":36.77149,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49866,-0.00452,0.05161]}],"total_contact_groups":1},"final_pose_error":0.08222,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.49785,-0.00904,0.14802],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":74.28854,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":229.0,"n_steps_budget":1000.0,"object_pos_end":[0.50672,0.00505,0.27871],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.19888,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.50214,0.00503,0.23897],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":927.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,-0.00447,0.09138],"object_pos_start":[0.50672,0.00505,0.27871],"object_to_goal_dist_end":0.01279,"object_to_goal_dist_start":0.19888,"object_z_max":0.27871,"peak_contact_force":63.10282,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_progress","tcp_end":[0.49875,-0.00448,0.05169],"tcp_start":[0.50214,0.00503,0.23897],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50333,-0.00903,0.18764],"object_pos_start":[0.50377,-0.00447,0.09138],"object_to_goal_dist_end":0.10807,"object_to_goal_dist_start":0.01279,"object_z_max":0.18754,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":10.0,"raw_peak_contact_force":74.28854,"tcp_end":[0.49785,-0.00904,0.14802],"tcp_start":[0.49875,-0.00448,0.05169],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `09a021eaed2a28b8f97b40a956e668b0df532c8dfcbc8d48b91f00ceefb0c83a`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.61739,"average_solve_count":230.0,"average_success_count":230.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_x":-0.00682,"approach_1.lateral_y":-0.01999,"approach_1.speed":0.08186,"insert_1.force_threshold":19.36661,"insert_1.insertion_depth":0.17416,"retract_1.speed":0.01262},"optimized_scores":{"best_composite_score":0.8735,"best_fitness_score":0.87016,"best_task_score":0.91131},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.51645,0.02152,0.0499],"force_p95":67.8925,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.12584,"mean_force":41.97043,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50157,0.02145,0.05168]}],"total_contact_groups":1},"final_pose_error":0.08478,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.5029,0.02696,0.14566],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":77.12584,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.50463,0.00942,0.27866],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.19893,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.50006,0.0094,0.23892],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":952.0,"n_steps_budget":1000.0,"object_pos_end":[0.50662,0.02148,0.09145],"object_pos_start":[0.50463,0.00942,0.27866],"object_to_goal_dist_end":0.02522,"object_to_goal_dist_start":0.19893,"object_z_max":0.27866,"peak_contact_force":64.04583,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_progress","tcp_end":[0.5016,0.02144,0.05177],"tcp_start":[0.50006,0.0094,0.23892],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50838,0.02702,0.18528],"object_pos_start":[0.50662,0.02148,0.09145],"object_to_goal_dist_end":0.10901,"object_to_goal_dist_start":0.02522,"object_z_max":0.18519,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":9.0,"raw_peak_contact_force":77.12584,"tcp_end":[0.5029,0.02696,0.14566],"tcp_start":[0.5016,0.02144,0.05177],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```