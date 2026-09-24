## Search State

- **Seed**: 1
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2817 | 0.84 | ❌ rejected |
| 11 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.7475 | 0.96 | ❌ rejected |
| 10 | approach → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | impedance_control | force_exceeded | pose_tolerance | force_exceeded | 8 | 0.6544 | 0.84 | ❌ rejected |
| 9 | approach → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 8 | 0.4942 | 0.85 | ❌ rejected |
| 8 | approach → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.2720 | 0.76 | ❌ rejected |

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

## Current Skill (Q=0.282) — your mutation base

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

- **Composite score**: 0.282
- **task_score** (E): 0.837
- **fitness_score**: 0.512  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.33 | 1.00 | 0.1575 |
| align_1 | 1.00 | 0.00 | 0.0296 |
| insert_1 | 0.00 | 0.00 | 0.0003 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.460, 0.005, 0.150) | (0.504, -0.000, 0.340)→(0.497, 0.004, 0.135) | 0.260→0.058 | 1.00 / 1.000 | 309.535 | 1184.377 |
| align_1 | align | 1.00 / step_budget | (0.460, 0.005, 0.150)→(0.485, 0.009, 0.139) | (0.497, 0.004, 0.135)→(0.522, 0.010, 0.125) | 0.058→0.056 | 0.00 / 0.000 | 0.000 | 341.299 |
| insert_1 | insert | 0.00 / guard_failure | (0.485, 0.009, 0.139)→(0.485, 0.009, 0.139) | (0.522, 0.010, 0.125)→(0.522, 0.010, 0.125) | 0.056→0.056 | 0.00 / 0.000 | 0.000 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.835
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.835
- phase_score: 0.378
- phase_breakdown.insert_into_goal_score: 0.386
- phase_breakdown.reach_above_goal_score: 0.359

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.561
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.842
- **Median Q (composite search score)**: 0.294
- **K-run variance**: 0.0021
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.392


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":2.0,"average_failure_rate":0.04651,"average_mean_iterations":16.16279,"average_solve_count":43.0,"average_success_count":41.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.0007,"align_1.lateral_offset_y":0.00426,"approach_1.approach_z_offset":0.12272,"insert_1.push_distance":0.13822},"optimized_scores":{"best_composite_score":0.22037,"best_fitness_score":0.45037,"best_task_score":0.84226},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.45588,0.00481,0.07882],"force_p95":1007.67866,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1061.39491,"mean_force":243.48949,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45141,0.00476,0.09194]},{"body_a":"peg_socket","body_b":"link7","contact_count":213.0,"contact_point_centroid":[0.55849,0.01349,0.07953],"force_p95":408.55778,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":814.64154,"mean_force":294.38807,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45295,0.00964,0.15332]},{"body_a":"peg_socket","body_b":"link7","contact_count":229.0,"contact_point_centroid":[0.5609,0.03594,0.07992],"force_p95":370.84725,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":461.17042,"mean_force":215.31438,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48152,0.03223,0.1813]},{"body_a":"peg_socket","body_b":"link6","contact_count":274.0,"contact_point_centroid":[0.56087,0.02011,0.07985],"force_p95":319.48809,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":328.68855,"mean_force":291.55737,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45358,0.02061,0.18584]},{"body_a":"peg_socket","body_b":"link6","contact_count":169.0,"contact_point_centroid":[0.5609,0.02677,0.07991],"force_p95":160.33566,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":251.90889,"mean_force":137.70892,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45887,0.02734,0.18943]}],"total_contact_groups":5},"final_pose_error":0.22815,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.49744,0.04435,0.16975],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":1061.39491,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":602.0,"n_steps_budget":660.0,"object_pos_end":[0.48467,0.0264,0.17138],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09635,"object_to_goal_dist_start":0.26034,"object_z_max":0.3444,"peak_contact_force":278.21035,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":499.0,"raw_peak_contact_force":1061.39491,"subtask_id":"reach_above_goal","tcp_end":[0.44951,0.02586,0.19045],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":482.0,"n_steps_budget":600.0,"object_pos_end":[0.53323,0.04746,0.15234],"object_pos_start":[0.48467,0.0264,0.17138],"object_to_goal_dist_end":0.09269,"object_to_goal_dist_start":0.09635,"object_z_max":0.17148,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":398.0,"raw_peak_contact_force":461.17042,"tcp_end":[0.49723,0.04425,0.16947],"tcp_start":[0.44951,0.02586,0.19045],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.53346,0.04753,0.15265],"object_pos_start":[0.53323,0.04746,0.15234],"object_to_goal_dist_end":0.09304,"object_to_goal_dist_start":0.09269,"object_z_max":0.15234,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_into_goal","tcp_end":[0.49744,0.04435,0.16975],"tcp_start":[0.49723,0.04425,0.16947],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a0b26c055417598cbe086e53f7823e257fb75222f78e6d5a64925f365f02417e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.34146,"average_solve_count":41.0,"average_success_count":41.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00939,"align_1.lateral_offset_y":0.00997,"approach_1.approach_z_offset":0.13145,"insert_1.push_distance":0.11363},"optimized_scores":{"best_composite_score":0.33081,"best_fitness_score":0.56081,"best_task_score":0.83515},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":451.0,"contact_point_centroid":[0.54059,-0.00738,0.07969],"force_p95":316.21365,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1429.03334,"mean_force":301.91682,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46286,-0.00347,0.13054]},{"body_a":"attachment","body_b":"peg_socket","contact_count":15.0,"contact_point_centroid":[0.44396,-0.00505,0.07788],"force_p95":814.65562,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":853.61729,"mean_force":161.7032,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44039,-0.00271,0.08926]},{"body_a":"peg_socket","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.5409,-0.00871,0.07999],"force_p95":64.54048,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.42395,"mean_force":37.32709,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47028,-0.00438,0.13742]}],"total_contact_groups":3},"final_pose_error":0.15901,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.48576,-0.00618,0.125],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":1429.03334,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.50761,-0.00486,0.12828],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.04911,"object_to_goal_dist_start":0.26034,"object_z_max":0.34436,"peak_contact_force":315.47373,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":466.0,"raw_peak_contact_force":1429.03334,"subtask_id":"reach_above_goal","tcp_end":[0.46917,-0.00418,0.13933],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":424.0,"n_steps_budget":600.0,"object_pos_end":[0.52389,-0.00671,0.11347],"object_pos_start":[0.50761,-0.00486,0.12828],"object_to_goal_dist_end":0.04167,"object_to_goal_dist_start":0.04911,"object_z_max":0.12828,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":23.0,"raw_peak_contact_force":71.42395,"tcp_end":[0.48561,-0.00603,0.12505],"tcp_start":[0.46917,-0.00418,0.13933],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":990.0,"object_pos_end":[0.52404,-0.00687,0.11343],"object_pos_start":[0.52389,-0.00671,0.11347],"object_to_goal_dist_end":0.04175,"object_to_goal_dist_start":0.04167,"object_z_max":0.11347,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_into_goal","tcp_end":[0.48576,-0.00618,0.125],"tcp_start":[0.48561,-0.00603,0.12505],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d263ae29be72790e561c8447b0a7b2ba7baa0aae40b60396cc4b2e04f6cc146d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.62,"average_solve_count":50.0,"average_success_count":50.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00993,"align_1.lateral_offset_y":0.00974,"approach_1.approach_z_offset":0.08615,"insert_1.push_distance":0.15994},"optimized_scores":{"best_composite_score":0.29387,"best_fitness_score":0.52387,"best_task_score":0.83455},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":718.0,"contact_point_centroid":[0.52662,-0.00934,0.06698],"force_p95":338.13901,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1062.70418,"mean_force":308.74911,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45624,-0.00602,0.11429]},{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.44206,0.00927,0.0798],"force_p95":609.15233,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":615.50295,"mean_force":345.63392,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44008,-0.00347,0.08651]},{"body_a":"world","body_b":"link6","contact_count":255.0,"contact_point_centroid":[0.68312,-0.01325,-1e-05],"force_p95":135.47532,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":491.30368,"mean_force":66.73961,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46678,-0.00842,0.1219]},{"body_a":"peg_socket","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.52678,-0.01192,0.06383],"force_p95":282.89294,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":293.30798,"mean_force":135.06419,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46203,-0.00697,0.12006]},{"body_a":"world","body_b":"link6","contact_count":63.0,"contact_point_centroid":[0.67915,-0.00976,-4e-05],"force_p95":122.8364,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":145.85265,"mean_force":40.33042,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4621,-0.00681,0.12066]},{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.43627,0.00732,0.07988],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4345,-0.00596,0.08651]}],"total_contact_groups":6},"final_pose_error":0.20374,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.47254,-0.01088,0.12347],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":1062.70418,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":812.0,"n_steps_budget":870.0,"object_pos_end":[0.49955,-0.00814,0.10633],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02757,"object_to_goal_dist_start":0.26034,"object_z_max":0.34435,"peak_contact_force":334.92239,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":798.0,"raw_peak_contact_force":1062.70418,"subtask_id":"reach_above_goal","tcp_end":[0.46199,-0.00693,0.12005],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":382.0,"n_steps_budget":600.0,"object_pos_end":[0.50973,-0.012,0.10927],"object_pos_start":[0.49955,-0.00814,0.10633],"object_to_goal_dist_end":0.03309,"object_to_goal_dist_start":0.02757,"object_z_max":0.10926,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":263.0,"raw_peak_contact_force":491.30368,"tcp_end":[0.47237,-0.0108,0.12349],"tcp_start":[0.46199,-0.00693,0.12005],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50991,-0.01209,0.10925],"object_pos_start":[0.50973,-0.012,0.10927],"object_to_goal_dist_end":0.03317,"object_to_goal_dist_start":0.03309,"object_z_max":0.10927,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_into_goal","tcp_end":[0.47254,-0.01088,0.12347],"tcp_start":[0.47237,-0.0108,0.12349],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```