## Search State

- **Seed**: 1
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → align → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 7 | 0.4765 | 0.89 | ❌ rejected |
| 12 | approach → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2817 | 0.84 | ❌ rejected |
| 11 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.7475 | 0.96 | ❌ rejected |
| 10 | approach → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | impedance_control | force_exceeded | pose_tolerance | force_exceeded | 8 | 0.6544 | 0.84 | ❌ rejected |
| 9 | approach → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 8 | 0.4942 | 0.85 | ❌ rejected |

**Proposal policy**: task_score is 0.89 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.477) — your mutation base

```yaml
skill: peg_insert
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

- **Composite score**: 0.477
- **task_score** (E): 0.887
- **fitness_score**: 0.637  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 0.00 | 0.0721 |
| align_to_goal | 1.00 | 0.00 | 0.1251 |
| descend_to_rim | 0.00 | 0.00 | 0.0439 |
| insert_into_hole | 1.00 | 1.00 | 0.0167 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.486, -0.000, 0.233) | (0.504, -0.000, 0.340)→(0.490, -0.000, 0.273) | 0.260→0.194 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_to_goal | align | 1.00 / step_budget | (0.486, -0.000, 0.233)→(0.494, 0.001, 0.109) | (0.490, -0.000, 0.273)→(0.499, 0.001, 0.148) | 0.194→0.070 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_rim | push | 0.00 / step_budget | (0.494, 0.001, 0.109)→(0.481, 0.000, 0.069) | (0.499, 0.001, 0.148)→(0.487, 0.000, 0.108) | 0.070→0.041 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_into_hole | push | 1.00 / force_exceeded | (0.481, 0.000, 0.069)→(0.479, 0.000, 0.052) | (0.487, 0.000, 0.108)→(0.484, 0.000, 0.092) | 0.041→0.033 | 1.00 / 1.000 | 58.661 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.914
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.914
- phase_score: 0.521
- phase_breakdown.insert_into_goal_score: 0.459
- phase_breakdown.reach_above_goal_score: 0.665

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.678
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.914
- **Median Q (composite search score)**: 0.476
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.348


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `45273c8d1228632fd57317b0a02550505db6d7cbf023a115124b89e828802a94`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `70dcb1d9cf130ce66aaa294bb82afc0ceb52288177fb1bbf0b6209922022fad5`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56944,"average_solve_count":72.0,"average_success_count":72.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_goal.lateral_offset_x":0.00966,"align_to_goal.lateral_offset_y":-0.01901,"approach_above.approach_z_offset":0.13451,"descend_to_rim.descend_distance":0.04171,"descend_to_rim.force_threshold_descend":25.40945,"insert_into_hole.force_threshold_push":30.22413,"insert_into_hole.push_distance":0.19153},"optimized_scores":{"best_composite_score":0.4757,"best_fitness_score":0.6357,"best_task_score":0.88728},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.14362,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.49567,0.03323,0.05196],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":58.10716,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":146.0,"n_steps_budget":600.0,"object_pos_end":[0.50325,0.02665,0.27162],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.19349,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_goal","tcp_end":[0.4987,0.02662,0.23188],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":396.0,"n_steps_budget":840.0,"object_pos_end":[0.51092,0.0179,0.14837],"object_pos_start":[0.50325,0.02665,0.27162],"object_to_goal_dist_end":0.07151,"object_to_goal_dist_start":0.19349,"object_z_max":0.27162,"peak_contact_force":0.0,"phase_name":"align_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.5059,0.01785,0.10868],"tcp_start":[0.4987,0.02662,0.23188],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":291.0,"n_steps_budget":600.0,"object_pos_end":[0.50316,0.03328,0.10027],"object_pos_start":[0.51092,0.0179,0.14837],"object_to_goal_dist_end":0.03909,"object_to_goal_dist_start":0.07151,"object_z_max":0.14837,"peak_contact_force":0.0,"phase_name":"descend_to_rim","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49768,0.0332,0.06064],"tcp_start":[0.5059,0.01785,0.10868],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":40.0,"n_steps_budget":960.0,"object_pos_end":[0.5014,0.03332,0.09155],"object_pos_start":[0.50316,0.03328,0.10027],"object_to_goal_dist_end":0.03529,"object_to_goal_dist_start":0.03909,"object_z_max":0.10027,"peak_contact_force":58.10716,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_into_goal","tcp_end":[0.49567,0.03323,0.05196],"tcp_start":[0.49768,0.0332,0.06064],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a0b26c055417598cbe086e53f7823e257fb75222f78e6d5a64925f365f02417e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58667,"average_solve_count":75.0,"average_success_count":75.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_goal.lateral_offset_x":0.0191,"align_to_goal.lateral_offset_y":0.00963,"approach_above.approach_z_offset":0.13762,"descend_to_rim.descend_distance":0.03406,"descend_to_rim.force_threshold_descend":27.57712,"insert_into_hole.force_threshold_push":31.97821,"insert_into_hole.push_distance":0.21004},"optimized_scores":{"best_composite_score":0.51802,"best_fitness_score":0.67802,"best_task_score":0.91387},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.16216,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.477,-0.01432,0.05206],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":57.4609,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":130.0,"n_steps_budget":600.0,"object_pos_end":[0.48903,-0.01154,0.27639],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.19703,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_goal","tcp_end":[0.4845,-0.01154,0.23665],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":420.0,"n_steps_budget":870.0,"object_pos_end":[0.50007,-0.00698,0.14829],"object_pos_start":[0.48903,-0.01154,0.27639],"object_to_goal_dist_end":0.06864,"object_to_goal_dist_start":0.19703,"object_z_max":0.27639,"peak_contact_force":0.0,"phase_name":"align_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49508,-0.00698,0.1086],"tcp_start":[0.4845,-0.01154,0.23665],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":202.0,"n_steps_budget":600.0,"object_pos_end":[0.48557,-0.01419,0.11006],"object_pos_start":[0.50007,-0.00698,0.14829],"object_to_goal_dist_end":0.03624,"object_to_goal_dist_start":0.06864,"object_z_max":0.14829,"peak_contact_force":0.0,"phase_name":"descend_to_rim","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.48013,-0.01418,0.07044],"tcp_start":[0.49508,-0.00698,0.1086],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":89.0,"n_steps_budget":1000.0,"object_pos_end":[0.48281,-0.01434,0.09164],"object_pos_start":[0.48557,-0.01419,0.11006],"object_to_goal_dist_end":0.02523,"object_to_goal_dist_start":0.03624,"object_z_max":0.11006,"peak_contact_force":57.4609,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_into_goal","tcp_end":[0.477,-0.01432,0.05206],"tcp_start":[0.48013,-0.01418,0.07044],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d263ae29be72790e561c8447b0a7b2ba7baa0aae40b60396cc4b2e04f6cc146d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59211,"average_solve_count":76.0,"average_success_count":76.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_goal.lateral_offset_x":0.01983,"align_to_goal.lateral_offset_y":0.01462,"approach_above.approach_z_offset":0.13346,"descend_to_rim.descend_distance":0.0294,"descend_to_rim.force_threshold_descend":26.36613,"insert_into_hole.force_threshold_push":34.14525,"insert_into_hole.push_distance":0.15999},"optimized_scores":{"best_composite_score":0.43589,"best_fitness_score":0.59589,"best_task_score":0.8593},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.11219,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46315,-0.01846,0.05211],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":60.41567,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":147.0,"n_steps_budget":630.0,"object_pos_end":[0.4779,-0.01573,0.27082],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.19274,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_goal","tcp_end":[0.47337,-0.01572,0.23108],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":406.0,"n_steps_budget":840.0,"object_pos_end":[0.48696,-0.00735,0.14824],"object_pos_start":[0.4779,-0.01573,0.27082],"object_to_goal_dist_end":0.06986,"object_to_goal_dist_start":0.19274,"object_z_max":0.27082,"peak_contact_force":0.0,"phase_name":"align_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.48197,-0.00735,0.10855],"tcp_start":[0.47337,-0.01572,0.23108],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":196.0,"n_steps_budget":600.0,"object_pos_end":[0.47185,-0.01811,0.11411],"object_pos_start":[0.48696,-0.00735,0.14824],"object_to_goal_dist_end":0.04779,"object_to_goal_dist_start":0.06986,"object_z_max":0.14824,"peak_contact_force":0.0,"phase_name":"descend_to_rim","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.46643,-0.0181,0.07448],"tcp_start":[0.48197,-0.00735,0.10855],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":113.0,"n_steps_budget":840.0,"object_pos_end":[0.46895,-0.01848,0.09168],"object_pos_start":[0.47185,-0.01811,0.11411],"object_to_goal_dist_end":0.03797,"object_to_goal_dist_start":0.04779,"object_z_max":0.11411,"peak_contact_force":60.41567,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_into_goal","tcp_end":[0.46315,-0.01846,0.05211],"tcp_start":[0.46643,-0.0181,0.07448],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```