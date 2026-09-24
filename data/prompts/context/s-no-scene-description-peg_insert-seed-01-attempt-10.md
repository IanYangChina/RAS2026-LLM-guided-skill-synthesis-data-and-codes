## Search State

- **Seed**: 1
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | impedance_control | force_exceeded | pose_tolerance | force_exceeded | 8 | 0.6544 | 0.84 | ❌ rejected |
| 9 | approach → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 8 | 0.4942 | 0.85 | ❌ rejected |
| 8 | approach → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.2720 | 0.76 | ❌ rejected |
| 7 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.7475 | 0.96 | ❌ rejected |
| 6 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.7475 | 0.96 | ❌ rejected |

**Proposal policy**: task_score is 0.84 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.654) — your mutation base

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

- **Composite score**: 0.654
- **task_score** (E): 0.838
- **fitness_score**: 0.418  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.667
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_hole | 1.00 | 1.00 | 0.2181 |
| align_hole | 0.00 | 0.67 | 0.0681 |
| insert_peg | 1.00 | 1.00 | 0.0010 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_hole | approach | 1.00 / force_exceeded | (0.500, -0.000, 0.301)→(0.448, -0.000, 0.089) | (0.504, -0.000, 0.340)→(0.486, -0.000, 0.101) | 0.260→0.027 | 1.00 / 1.333 | 967.105 | 967.105 |
| align_hole | align | 0.00 / step_budget | (0.448, -0.000, 0.089)→(0.483, -0.005, 0.146) | (0.486, -0.000, 0.101)→(0.519, -0.005, 0.129) | 0.027→0.054 | 0.67 / 1.000 | 127.032 | 1691.256 |
| insert_peg | insert | 1.00 / force_exceeded | (0.483, -0.005, 0.146)→(0.483, -0.006, 0.146) | (0.519, -0.005, 0.129)→(0.519, -0.005, 0.129) | 0.054→0.054 | 1.00 / 1.667 | 468.015 | 468.015 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.834
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.834
- phase_score: 0.151
- phase_breakdown.approach_hole_score: 0.112
- phase_breakdown.insert_peg_score: 0.000
- phase_breakdown.align_hole_score: 0.293

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.424
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.842
- **Median Q (composite search score)**: 0.653
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.299


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":1.0,"average_failure_rate":0.03704,"average_mean_iterations":19.55556,"average_solve_count":27.0,"average_success_count":26.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_tolerance":0.01155,"align_hole.lateral_offset_x":-0.01321,"align_hole.lateral_offset_y":-0.00099,"approach_hole.approach_speed":0.23225,"approach_hole.force_threshold":19.14048,"insert_peg.force_threshold":34.81186,"insert_peg.insertion_depth":0.0757,"insert_peg.insertion_speed":0.05626},"optimized_scores":{"best_composite_score":0.64936,"best_fitness_score":0.4127,"best_task_score":0.84226},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.46472,0.00361,0.07977],"force_p95":964.9951,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":964.9951,"mean_force":964.9951,"phase_index":0.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.45912,0.0036,0.09345]},{"body_a":"peg_socket","body_b":"link7","contact_count":420.0,"contact_point_centroid":[0.56015,0.01267,0.07967],"force_p95":460.63307,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":916.38057,"mean_force":310.47088,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.48037,0.01103,0.17231]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.56085,0.00754,0.07996],"force_p95":765.14355,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":765.14355,"mean_force":765.14355,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.49957,-0.01124,0.15881]},{"body_a":"attachment","body_b":"peg_socket","contact_count":8.0,"contact_point_centroid":[0.45652,0.00359,0.07863],"force_p95":622.84368,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":684.7272,"mean_force":149.08054,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.4521,0.00354,0.09158]}],"total_contact_groups":4},"final_pose_error":0.1615,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.49963,-0.01185,0.15853],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":964.9951,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":89.0,"n_steps_budget":600.0,"object_pos_end":[0.49385,0.0037,0.10633],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02729,"object_to_goal_dist_start":0.26034,"object_z_max":0.34437,"peak_contact_force":964.9951,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1.0,"raw_peak_contact_force":964.9951,"subtask_id":"approach_hole","tcp_end":[0.45648,0.00361,0.09207],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":483.0,"n_steps_budget":600.0,"object_pos_end":[0.5348,-0.00107,0.14306],"object_pos_start":[0.49385,0.0037,0.10633],"object_to_goal_dist_end":0.07204,"object_to_goal_dist_start":0.02729,"object_z_max":0.16992,"peak_contact_force":0.0,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":428.0,"raw_peak_contact_force":916.38057,"subtask_id":"align_hole","tcp_end":[0.49942,-0.00993,0.1595],"tcp_start":[0.45648,0.00361,0.09207],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.53487,-0.00269,0.14197],"object_pos_start":[0.5348,-0.00107,0.14306],"object_to_goal_dist_end":0.07116,"object_to_goal_dist_start":0.07204,"object_z_max":0.14306,"peak_contact_force":765.14355,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":765.14355,"subtask_id":"insert_peg","tcp_end":[0.49963,-0.01185,0.15853],"tcp_start":[0.49942,-0.00993,0.1595],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a0b26c055417598cbe086e53f7823e257fb75222f78e6d5a64925f365f02417e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.53571,"average_solve_count":28.0,"average_success_count":28.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_tolerance":0.00976,"align_hole.lateral_offset_x":0.00458,"align_hole.lateral_offset_y":0.00185,"approach_hole.approach_speed":0.20736,"approach_hole.force_threshold":18.06253,"insert_peg.force_threshold":34.93153,"insert_peg.insertion_depth":0.10337,"insert_peg.insertion_speed":0.059},"optimized_scores":{"best_composite_score":0.6532,"best_fitness_score":0.41653,"best_task_score":0.83762},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":29.0,"contact_point_centroid":[0.67865,-0.0179,-0.00071],"force_p95":1681.96263,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1728.80238,"mean_force":732.42484,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.48586,-0.01016,0.15494]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54073,-0.00571,0.07972],"force_p95":1383.25773,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1383.25773,"mean_force":1383.25773,"phase_index":0.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.44728,-0.00178,0.0883]},{"body_a":"peg_socket","body_b":"link7","contact_count":454.0,"contact_point_centroid":[0.54053,-0.01013,0.07969],"force_p95":537.18849,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1356.68653,"mean_force":359.94233,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.47728,-0.00497,0.15842]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.45052,-0.01357,0.07986],"force_p95":747.07593,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":747.07593,"mean_force":747.07593,"phase_index":0.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.44728,-0.00178,0.0883]},{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.4456,-0.00597,0.07826],"force_p95":509.54866,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":559.92317,"mean_force":146.63164,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.44179,-0.00203,0.08916]},{"body_a":"peg_socket","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54087,-0.02849,0.07999],"force_p95":397.86912,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":411.67775,"mean_force":273.59148,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.4864,0.00134,0.14937]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.68751,-0.03457,-7e-05],"force_p95":210.7094,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":210.7094,"mean_force":210.7094,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.48642,0.00142,0.149]}],"total_contact_groups":7},"final_pose_error":0.17317,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.48639,0.00137,0.14883],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":1728.80238,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":92.0,"n_steps_budget":600.0,"object_pos_end":[0.48297,-0.00188,0.09925],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02577,"object_to_goal_dist_start":0.26034,"object_z_max":0.34435,"peak_contact_force":1383.25773,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2.0,"raw_peak_contact_force":1383.25773,"subtask_id":"approach_hole","tcp_end":[0.44479,-0.00183,0.08734],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.5208,-0.00646,0.13088],"object_pos_start":[0.48297,-0.00188,0.09925],"object_to_goal_dist_end":0.05535,"object_to_goal_dist_start":0.02577,"object_z_max":0.15508,"peak_contact_force":207.92229,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":492.0,"raw_peak_contact_force":1728.80238,"subtask_id":"align_hole","tcp_end":[0.48638,0.00125,0.14973],"tcp_start":[0.44479,-0.00183,0.08734],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.52084,-0.00625,0.12998],"object_pos_start":[0.5208,-0.00646,0.13088],"object_to_goal_dist_end":0.05451,"object_to_goal_dist_start":0.05535,"object_z_max":0.13088,"peak_contact_force":411.67775,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":411.67775,"subtask_id":"insert_peg","tcp_end":[0.48639,0.00137,0.14883],"tcp_start":[0.48638,0.00125,0.14973],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d263ae29be72790e561c8447b0a7b2ba7baa0aae40b60396cc4b2e04f6cc146d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.11538,"average_solve_count":26.0,"average_success_count":26.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.align_tolerance":0.00892,"align_hole.lateral_offset_x":-0.01497,"align_hole.lateral_offset_y":0.01316,"approach_hole.approach_speed":0.20718,"approach_hole.force_threshold":11.65052,"insert_peg.force_threshold":30.31603,"insert_peg.insertion_depth":0.07822,"insert_peg.insertion_speed":0.02322},"optimized_scores":{"best_composite_score":0.66061,"best_fitness_score":0.42394,"best_task_score":0.8338},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":256.0,"contact_point_centroid":[0.676,-0.00595,-9e-05],"force_p95":549.11872,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2428.58415,"mean_force":149.00772,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.46444,-0.00648,0.12996]},{"body_a":"peg_socket","body_b":"link7","contact_count":454.0,"contact_point_centroid":[0.52656,-0.00949,0.0712],"force_p95":427.87622,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1784.20907,"mean_force":354.7241,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.46226,-0.00624,0.12695]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.44817,0.00929,0.07973],"force_p95":553.06289,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":553.06289,"mean_force":553.06289,"phase_index":0.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.4453,-0.0023,0.08809]},{"body_a":"attachment","body_b":"peg_socket","contact_count":5.0,"contact_point_centroid":[0.4406,0.0094,0.07975],"force_p95":378.84172,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":449.07447,"mean_force":148.62732,"phase_index":1.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.4389,-0.00358,0.08586]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52679,-0.01096,0.07061],"force_p95":227.22278,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":227.22278,"mean_force":227.22278,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.46438,-0.00746,0.12953]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.67627,-0.00577,-4e-05],"force_p95":209.88807,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":209.88807,"mean_force":209.88807,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.46438,-0.00746,0.12953]}],"total_contact_groups":6},"final_pose_error":0.12849,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46438,-0.00742,0.12952],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":2428.58415,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":92.0,"n_steps_budget":600.0,"object_pos_end":[0.48068,-0.00261,0.09868],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.027,"object_to_goal_dist_start":0.26034,"object_z_max":0.34429,"peak_contact_force":553.06289,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1.0,"raw_peak_contact_force":553.06289,"subtask_id":"approach_hole","tcp_end":[0.44244,-0.00254,0.08692],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.50131,-0.00715,0.11416],"object_pos_start":[0.48068,-0.00261,0.09868],"object_to_goal_dist_end":0.03493,"object_to_goal_dist_start":0.027,"object_z_max":0.11556,"peak_contact_force":173.1744,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":715.0,"raw_peak_contact_force":2428.58415,"subtask_id":"align_hole","tcp_end":[0.46438,-0.00746,0.12953],"tcp_start":[0.44244,-0.00254,0.08692],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50131,-0.00712,0.11416],"object_pos_start":[0.50131,-0.00715,0.11416],"object_to_goal_dist_end":0.03492,"object_to_goal_dist_start":0.03493,"object_z_max":0.11416,"peak_contact_force":227.22278,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":227.22278,"subtask_id":"insert_peg","tcp_end":[0.46438,-0.00742,0.12952],"tcp_start":[0.46438,-0.00746,0.12953],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```