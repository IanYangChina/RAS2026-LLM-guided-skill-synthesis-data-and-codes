## Search State

- **Seed**: 1
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → align → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0556 | 0.78 | ❌ rejected |
| 13 | approach → align → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 7 | 0.4765 | 0.89 | ❌ rejected |
| 12 | approach → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2817 | 0.84 | ❌ rejected |
| 11 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.7475 | 0.96 | ❌ rejected |
| 10 | approach → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | impedance_control | force_exceeded | pose_tolerance | force_exceeded | 8 | 0.6544 | 0.84 | ❌ rejected |

**Proposal policy**: task_score is 0.78 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.056) — your mutation base

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

- **Composite score**: 0.056
- **task_score** (E): 0.781
- **fitness_score**: 0.416  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 0.00 | 0.0730 |
| align_to_goal | 1.00 | 0.00 | 0.0505 |
| descend_to_rim | 0.00 | 0.00 | 0.0752 |
| insert_into_hole | 1.00 | 0.00 | 0.0301 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.484, -0.000, 0.233) | (0.504, -0.000, 0.340)→(0.493, -0.000, 0.272) | 0.260→0.193 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_to_goal | align | 1.00 / step_budget | (0.484, -0.000, 0.233)→(0.477, -0.002, 0.186) | (0.493, -0.000, 0.272)→(0.478, -0.002, 0.226) | 0.193→0.151 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_rim | descend | 0.00 / step_budget | (0.477, -0.002, 0.186)→(0.479, -0.001, 0.113) | (0.478, -0.002, 0.226)→(0.483, -0.001, 0.153) | 0.151→0.080 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_into_hole | insert | 1.00 / step_budget | (0.479, -0.001, 0.113)→(0.479, -0.000, 0.143) | (0.483, -0.001, 0.153)→(0.480, -0.000, 0.183) | 0.080→0.109 | 0.00 / 0.000 | 0.000 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.799
- alignment_error: None
- force_efficiency: 1.000
- terminal_score: 0.799
- phase_score: 0.192
- phase_breakdown.insert_into_goal_score: 0.000
- phase_breakdown.reach_above_goal_score: 0.640

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.435
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.799
- **Median Q (composite search score)**: 0.056
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at lower bound**: descend_to_rim.descend_distance
- **Final σ (mean)**: 0.357


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5875,"average_solve_count":80.0,"average_success_count":80.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_goal.lateral_offset_x":-0.02477,"align_to_goal.lateral_offset_y":0.00293,"approach_above.approach_z_offset":0.14433,"descend_to_rim.descend_distance":0.03,"descend_to_rim.force_threshold_descend":6.60578,"insert_into_hole.push_distance":0.07737},"optimized_scores":{"best_composite_score":0.05594,"best_fitness_score":0.41594,"best_task_score":0.78615},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.01497,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.49676,0.03575,0.143],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":174.0,"n_steps_budget":600.0,"object_pos_end":[0.50606,0.02798,0.27572],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.19781,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_goal","tcp_end":[0.49842,0.02787,0.23646],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":173.0,"n_steps_budget":600.0,"object_pos_end":[0.47881,0.03645,0.22732],"object_pos_start":[0.50606,0.02798,0.27572],"object_to_goal_dist_end":0.15323,"object_to_goal_dist_start":0.19781,"object_z_max":0.27572,"peak_contact_force":0.0,"phase_name":"align_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.47809,0.0364,0.18733],"tcp_start":[0.49842,0.02787,0.23646],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":522.0,"n_steps_budget":600.0,"object_pos_end":[0.49884,0.0357,0.15073],"object_pos_start":[0.47881,0.03645,0.22732],"object_to_goal_dist_end":0.07924,"object_to_goal_dist_start":0.15323,"object_z_max":0.22732,"peak_contact_force":0.0,"phase_name":"descend_to_rim","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49576,0.03579,0.11085],"tcp_start":[0.47809,0.0364,0.18733],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":167.0,"n_steps_budget":600.0,"object_pos_end":[0.4973,0.03577,0.18299],"object_pos_start":[0.49884,0.0357,0.15073],"object_to_goal_dist_end":0.10906,"object_to_goal_dist_start":0.07924,"object_z_max":0.1828,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49676,0.03575,0.143],"tcp_start":[0.49576,0.03579,0.11085],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a0b26c055417598cbe086e53f7823e257fb75222f78e6d5a64925f365f02417e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5875,"average_solve_count":80.0,"average_success_count":80.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_goal.lateral_offset_x":0.00741,"align_to_goal.lateral_offset_y":-0.02371,"approach_above.approach_z_offset":0.12991,"descend_to_rim.descend_distance":0.03058,"descend_to_rim.force_threshold_descend":7.56066,"insert_into_hole.push_distance":0.09406},"optimized_scores":{"best_composite_score":0.0748,"best_fitness_score":0.4348,"best_task_score":0.79919},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.01489,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.47731,-0.01635,0.15962],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":186.0,"n_steps_budget":600.0,"object_pos_end":[0.49207,-0.01281,0.26311],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.18373,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_goal","tcp_end":[0.48255,-0.01272,0.22426],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":205.0,"n_steps_budget":600.0,"object_pos_end":[0.48487,-0.0344,0.22393],"object_pos_start":[0.49207,-0.01281,0.26311],"object_to_goal_dist_end":0.14876,"object_to_goal_dist_start":0.18373,"object_z_max":0.26311,"peak_contact_force":0.0,"phase_name":"align_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.48424,-0.03436,0.18394],"tcp_start":[0.48255,-0.01272,0.22426],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":372.0,"n_steps_budget":600.0,"object_pos_end":[0.48225,-0.01807,0.15364],"object_pos_start":[0.48487,-0.0344,0.22393],"object_to_goal_dist_end":0.07787,"object_to_goal_dist_start":0.14876,"object_z_max":0.22393,"peak_contact_force":0.0,"phase_name":"descend_to_rim","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.4778,-0.01794,0.11389],"tcp_start":[0.48424,-0.03436,0.18394],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":219.0,"n_steps_budget":600.0,"object_pos_end":[0.47782,-0.01636,0.19962],"object_pos_start":[0.48225,-0.01807,0.15364],"object_to_goal_dist_end":0.12275,"object_to_goal_dist_start":0.07787,"object_z_max":0.19941,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.47731,-0.01635,0.15962],"tcp_start":[0.4778,-0.01794,0.11389],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d263ae29be72790e561c8447b0a7b2ba7baa0aae40b60396cc4b2e04f6cc146d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5,"average_solve_count":80.0,"average_success_count":80.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_goal.lateral_offset_x":0.00491,"align_to_goal.lateral_offset_y":0.01615,"approach_above.approach_z_offset":0.14535,"descend_to_rim.descend_distance":0.03007,"descend_to_rim.force_threshold_descend":17.68387,"insert_into_hole.push_distance":0.06005},"optimized_scores":{"best_composite_score":0.0362,"best_fitness_score":0.3962,"best_task_score":0.7585},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.0148,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46261,-0.02035,0.12589],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":166.0,"n_steps_budget":600.0,"object_pos_end":[0.48193,-0.01632,0.27704],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.19854,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_goal","tcp_end":[0.47228,-0.01618,0.23822],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":187.0,"n_steps_budget":600.0,"object_pos_end":[0.46967,-0.00713,0.22711],"object_pos_start":[0.48193,-0.01632,0.27704],"object_to_goal_dist_end":0.15038,"object_to_goal_dist_start":0.19854,"object_z_max":0.27704,"peak_contact_force":0.0,"phase_name":"align_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.46897,-0.00713,0.18712],"tcp_start":[0.47228,-0.01618,0.23822],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":393.0,"n_steps_budget":600.0,"object_pos_end":[0.46833,-0.01956,0.15334],"object_pos_start":[0.46967,-0.00713,0.22711],"object_to_goal_dist_end":0.08225,"object_to_goal_dist_start":0.15038,"object_z_max":0.22711,"peak_contact_force":0.0,"phase_name":"descend_to_rim","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.46365,-0.01959,0.11362],"tcp_start":[0.46897,-0.00713,0.18712],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":76.0,"n_steps_budget":600.0,"object_pos_end":[0.46405,-0.02037,0.16586],"object_pos_start":[0.46833,-0.01956,0.15334],"object_to_goal_dist_end":0.09529,"object_to_goal_dist_start":0.08225,"object_z_max":0.16566,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.46261,-0.02035,0.12589],"tcp_start":[0.46365,-0.01959,0.11362],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```