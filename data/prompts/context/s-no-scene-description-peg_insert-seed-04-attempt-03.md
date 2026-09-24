## Search State

- **Seed**: 4
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | push → align → release → insert | impedance_motion | linear_cartesian | — | impedance_motion | impedance_control | position_control | position_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.6859 | 0.95 | ❌ rejected |
| 2 | grasp → approach → align → descend → insert | — | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 8 | 0.0843 | 0.92 | ❌ rejected |
| 1 | grasp → approach → align → descend → insert → release | — | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | admittance_control | position_control | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7 | 0.1090 | 0.93 | ❌ rejected |
| 0 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.1391 | 0.96 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.95). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.686) — your mutation base

```yaml
skill: peg_insert
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

- **Composite score**: 0.686
- **task_score** (E): 0.946
- **fitness_score**: 0.713  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| push_1 | 1.00 | 0.00 | 0.0685 |
| align_1 | 1.00 | 0.00 | 0.0989 |
| release_1 | 1.00 | 0.00 | 0.0096 |
| insert_1 | 1.00 | 1.00 | 0.0521 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| push_1 | push | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.517, 0.004, 0.237) | (0.504, -0.000, 0.340)→(0.517, 0.004, 0.277) | 0.260→0.198 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_1 | align | 1.00 / step_budget | (0.517, 0.004, 0.237)→(0.505, 0.003, 0.140) | (0.517, 0.004, 0.277)→(0.505, 0.003, 0.179) | 0.198→0.100 | 0.00 / 0.000 | 0.000 | 0.000 |
| release_1 | release | 1.00 / step_budget | (0.505, 0.003, 0.140)→(0.499, 0.002, 0.132) | (0.505, 0.003, 0.179)→(0.500, 0.002, 0.172) | 0.100→0.092 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_1 | insert | 1.00 / force_exceeded | (0.499, 0.002, 0.132)→(0.501, 0.003, 0.080) | (0.500, 0.002, 0.172)→(0.501, 0.003, 0.120) | 0.092→0.042 | 1.00 / 1.000 | 3905.455 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.950
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.950
- phase_score: 0.566
- phase_breakdown.finish_insertion_score: 0.801
- phase_breakdown.reach_approach_score: 0.019

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.720
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.950
- **Median Q (composite search score)**: 0.685
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.444


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `1c06d48834291abac995c6cc1d2cd84f840e8dd85a042a042b29bb3e8b43f340`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a5dd99a2832e295b96a2d483dc6e44525a65c5240d3c756ec4d63dfbfe5237b3`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30928,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.0192,"align_1.lateral_offset_y":-0.00556,"insert_1.insertion_depth":0.14844,"insert_1.insertion_force":4.60877,"push_1.push_distance":0.13132,"push_1.push_speed":0.03039},"optimized_scores":{"best_composite_score":0.6798,"best_fitness_score":0.70647,"best_task_score":0.94358},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.15012,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.51218,-0.00268,0.07983],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":3905.45451,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":691.0,"n_steps_budget":1000.0,"object_pos_end":[0.53094,0.00082,0.25125],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.17402,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_approach","tcp_end":[0.53046,0.00082,0.21125],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":220.0,"n_steps_budget":600.0,"object_pos_end":[0.51616,-0.00367,0.17977],"object_pos_start":[0.53094,0.00082,0.25125],"object_to_goal_dist_end":0.10114,"object_to_goal_dist_start":0.17402,"object_z_max":0.25125,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"finish_insertion","tcp_end":[0.51569,-0.00368,0.13978],"tcp_start":[0.53046,0.00082,0.21125],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5112,-0.00373,0.17169],"object_pos_start":[0.51616,-0.00367,0.17977],"object_to_goal_dist_end":0.09244,"object_to_goal_dist_start":0.10114,"object_z_max":0.17977,"peak_contact_force":0.0,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50996,-0.00373,0.13171],"tcp_start":[0.51569,-0.00368,0.13978],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":282.0,"n_steps_budget":1000.0,"object_pos_end":[0.51265,-0.00268,0.11983],"object_pos_start":[0.5112,-0.00373,0.17169],"object_to_goal_dist_end":0.04187,"object_to_goal_dist_start":0.09244,"object_z_max":0.17169,"peak_contact_force":3905.45451,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"finish_insertion","tcp_end":[0.51218,-0.00268,0.07983],"tcp_start":[0.50996,-0.00373,0.13171],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `82356f74d11e1888d903e80aabfa97b50f0a1f9374ab8997097863e47a04dcc6`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.01657,"align_1.lateral_offset_y":-0.01997,"insert_1.insertion_depth":0.14534,"insert_1.insertion_force":5.48209,"push_1.push_distance":0.16663,"push_1.push_speed":0.02513},"optimized_scores":{"best_composite_score":0.69304,"best_fitness_score":0.71971,"best_task_score":0.94986},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.1475,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.50253,0.01083,0.07987],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":3905.45451,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":560.0,"n_steps_budget":1000.0,"object_pos_end":[0.52044,0.02272,0.28541],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.20767,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_approach","tcp_end":[0.51998,0.0227,0.24541],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":328.0,"n_steps_budget":750.0,"object_pos_end":[0.50662,0.00683,0.17941],"object_pos_start":[0.52044,0.02272,0.28541],"object_to_goal_dist_end":0.09987,"object_to_goal_dist_start":0.20767,"object_z_max":0.28541,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"finish_insertion","tcp_end":[0.50615,0.00682,0.13942],"tcp_start":[0.51998,0.0227,0.24541],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50173,0.00666,0.17162],"object_pos_start":[0.50662,0.00683,0.17941],"object_to_goal_dist_end":0.09188,"object_to_goal_dist_start":0.09987,"object_z_max":0.17941,"peak_contact_force":0.0,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.5005,0.00664,0.13164],"tcp_start":[0.50615,0.00682,0.13942],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.50299,0.01084,0.11987],"object_pos_start":[0.50173,0.00666,0.17162],"object_to_goal_dist_end":0.04142,"object_to_goal_dist_start":0.09188,"object_z_max":0.17162,"peak_contact_force":3905.45451,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"finish_insertion","tcp_end":[0.50253,0.01083,0.07987],"tcp_start":[0.5005,0.00664,0.13164],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `4fedbe547233117d2a5522e0e6da389f32d172824e1a5c898bb2e8c1e5f99b78`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64407,"average_solve_count":59.0,"average_success_count":59.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00803,"align_1.lateral_offset_y":0.01895,"insert_1.insertion_depth":0.12117,"insert_1.insertion_force":10.32418,"push_1.push_distance":0.17026,"push_1.push_speed":0.06203},"optimized_scores":{"best_composite_score":0.68487,"best_fitness_score":0.71154,"best_task_score":0.94484},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.12254,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.48785,-0.00033,0.07981],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":3905.45451,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":255.0,"n_steps_budget":600.0,"object_pos_end":[0.50048,-0.01046,0.29355],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.2138,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_approach","tcp_end":[0.49999,-0.01046,0.25355],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":360.0,"n_steps_budget":780.0,"object_pos_end":[0.49297,0.00447,0.17931],"object_pos_start":[0.50048,-0.01046,0.29355],"object_to_goal_dist_end":0.09966,"object_to_goal_dist_start":0.2138,"object_z_max":0.29355,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"finish_insertion","tcp_end":[0.49254,0.00446,0.13931],"tcp_start":[0.49999,-0.01046,0.25355],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48815,0.00442,0.17192],"object_pos_start":[0.49297,0.00447,0.17931],"object_to_goal_dist_end":0.09279,"object_to_goal_dist_start":0.09966,"object_z_max":0.17931,"peak_contact_force":0.0,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.48698,0.0044,0.13194],"tcp_start":[0.49254,0.00446,0.13931],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.48828,-0.00032,0.11981],"object_pos_start":[0.48815,0.00442,0.17192],"object_to_goal_dist_end":0.0415,"object_to_goal_dist_start":0.09279,"object_z_max":0.17192,"peak_contact_force":3905.45451,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"finish_insertion","tcp_end":[0.48785,-0.00033,0.07981],"tcp_start":[0.48698,0.0044,0.13194],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```