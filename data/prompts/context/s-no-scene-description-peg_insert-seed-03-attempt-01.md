## Search State

- **Seed**: 3
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → align → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.4537 | 0.91 | ❌ rejected |
| 0 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7464 | 0.96 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.91). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.454) — your mutation base

```yaml
skill: peg_insert
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: position_control
  termination: pose_tolerance
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
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
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

```

## Design Metrics

- **Composite score**: 0.454
- **task_score** (E): 0.915
- **fitness_score**: 0.514  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.00 | 0.0666 |
| align_1 | 0.00 | 1.00 | 0.1109 |
| contact_descend_1 | 1.00 | 1.00 | 0.0002 |
| insert_1 | 0.00 | 0.33 | 0.0352 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.504, 0.006, 0.242) | (0.504, -0.000, 0.340)→(0.510, 0.006, 0.281) | 0.260→0.203 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_1 | align | 0.00 / step_budget | (0.504, 0.006, 0.242)→(0.506, 0.028, 0.147) | (0.510, 0.006, 0.281)→(0.543, 0.025, 0.138) | 0.203→0.092 | 1.00 / 1.333 | 335.308 | 1423.065 |
| contact_descend_1 | descend | 1.00 / force_exceeded | (0.506, 0.028, 0.147)→(0.506, 0.028, 0.147) | (0.543, 0.025, 0.138)→(0.543, 0.025, 0.138) | 0.092→0.092 | 1.00 / 1.333 | 327.575 | 327.575 |
| insert_1 | push | 0.00 / step_budget | (0.506, 0.028, 0.147)→(0.520, 0.036, 0.160) | (0.543, 0.025, 0.138)→(0.557, 0.034, 0.157) | 0.092→0.113 | 0.33 / 0.333 | 86.089 | 466.220 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.944
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.944
- phase_score: 0.434
- phase_breakdown.insert_sub_score: 0.573
- phase_breakdown.approach_sub_score: 0.110

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.638
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.962
- **Median Q (composite search score)**: 0.420
- **K-run variance**: 0.0082
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.429


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2fc05e51a25fc23cdfa051e1c0c9cb8327fc4318047dd2c0794162fe696d964b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `78de15924f40c9df864f10a8c33fe438e6928bbf6063e6b2cf47f87609839b79`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.17391,"average_solve_count":69.0,"average_success_count":69.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_tolerance":0.01044,"approach_1.approach_height":0.10679,"approach_1.arc_height":0.05252,"contact_descend_1.contact_force":7.62797,"insert_1.insert_depth":0.0638},"optimized_scores":{"best_composite_score":0.57782,"best_fitness_score":0.63782,"best_task_score":0.94352},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":518.0,"contact_point_centroid":[0.52626,-0.01725,0.07972],"force_p95":350.23514,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1600.63129,"mean_force":307.71038,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52465,-0.00588,0.08328]},{"body_a":"attachment","body_b":"peg_socket","contact_count":454.0,"contact_point_centroid":[0.52666,-0.023,0.07994],"force_p95":296.46251,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":349.04617,"mean_force":275.80731,"phase_index":3.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.52607,-0.00824,0.0825]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.52682,-0.02286,0.07999],"force_p95":329.55198,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":329.55198,"mean_force":329.55198,"phase_index":2.0,"phase_name":"contact_descend_1","phase_type":"descend","tcp_position_centroid":[0.52663,-0.00819,0.08307]}],"total_contact_groups":3},"final_pose_error":0.08974,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.52629,-0.0089,0.08232],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":1600.63129,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":283.0,"n_steps_budget":780.0,"object_pos_end":[0.47872,-0.00127,0.22758],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.14911,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_sub","tcp_end":[0.46636,-0.00127,0.18954],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.56565,-0.00958,0.09178],"object_pos_start":[0.47872,-0.00127,0.22758],"object_to_goal_dist_end":0.06738,"object_to_goal_dist_start":0.14911,"object_z_max":0.22758,"peak_contact_force":301.8454,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":518.0,"raw_peak_contact_force":1600.63129,"subtask_id":"approach_sub","tcp_end":[0.52663,-0.00819,0.08307],"tcp_start":[0.46636,-0.00127,0.18954],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.56566,-0.00956,0.09179],"object_pos_start":[0.56565,-0.00958,0.09178],"object_to_goal_dist_end":0.0674,"object_to_goal_dist_start":0.06738,"object_z_max":0.09178,"peak_contact_force":329.55198,"phase_name":"contact_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":329.55198,"subtask_id":"insert_sub","tcp_end":[0.52665,-0.00816,0.08307],"tcp_start":[0.52663,-0.00819,0.08307],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.56255,-0.01069,0.0991],"object_pos_start":[0.56566,-0.00956,0.09179],"object_to_goal_dist_end":0.06627,"object_to_goal_dist_start":0.0674,"object_z_max":0.09909,"peak_contact_force":258.26839,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":454.0,"raw_peak_contact_force":349.04617,"subtask_id":"insert_sub","tcp_end":[0.52629,-0.0089,0.08232],"tcp_start":[0.52665,-0.00816,0.08307],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `23bedb35dfb8044c9064b13b9f8101cd4e2be35581b8354b6b999b22e5fca070`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":46.0,"average_failure_rate":0.45545,"average_mean_iterations":96.69307,"average_solve_count":101.0,"average_success_count":55.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_tolerance":0.01358,"approach_1.approach_height":0.17248,"approach_1.arc_height":0.06704,"contact_descend_1.contact_force":15.25355,"insert_1.insert_depth":0.09487},"optimized_scores":{"best_composite_score":0.41978,"best_fitness_score":0.47978,"best_task_score":0.96203},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":15.0,"contact_point_centroid":[0.56901,0.00088,0.07756],"force_p95":1276.26624,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1324.71071,"mean_force":628.6633,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.55384,0.00086,0.08088]},{"body_a":"peg_socket","body_b":"link7","contact_count":145.0,"contact_point_centroid":[0.59337,0.00305,0.07927],"force_p95":812.51222,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1209.25726,"mean_force":340.72787,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48444,0.00053,0.14695]},{"body_a":"peg_socket","body_b":"link6","contact_count":398.0,"contact_point_centroid":[0.59535,-0.00082,0.07975],"force_p95":357.65235,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":933.17788,"mean_force":272.16211,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4803,0.0007,0.1713]},{"body_a":"attachment","body_b":"peg_socket","contact_count":8.0,"contact_point_centroid":[0.49872,0.00341,0.07863],"force_p95":868.02976,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":869.10848,"mean_force":216.89186,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49486,0.00061,0.09053]},{"body_a":"peg_socket","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.59525,0.0016,0.07995],"force_p95":451.37801,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":518.40074,"mean_force":330.66635,"phase_index":3.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.49469,-0.00247,0.17869]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.59521,-0.00023,0.07929],"force_p95":455.44336,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":486.3455,"mean_force":259.3302,"phase_index":2.0,"phase_name":"contact_descend_1","phase_type":"descend","tcp_position_centroid":[0.49452,0.00097,0.18082]},{"body_a":"peg_socket","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.59437,0.00575,0.07998],"force_p95":451.19279,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":461.39188,"mean_force":359.40092,"phase_index":2.0,"phase_name":"contact_descend_1","phase_type":"descend","tcp_position_centroid":[0.49452,0.00097,0.18079]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.59536,-0.00048,0.07917],"force_p95":401.06132,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":401.30248,"mean_force":315.02825,"phase_index":3.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.49457,0.00112,0.18044]}],"total_contact_groups":8},"final_pose_error":0.25491,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.51642,0.04396,0.23566],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1324.71071,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":96.0,"n_steps_budget":600.0,"object_pos_end":[0.53029,0.0007,0.30975],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.23174,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_sub","tcp_end":[0.52651,0.00069,0.26993],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":633.0,"n_steps_budget":1000.0,"object_pos_end":[0.53004,0.00104,0.16251],"object_pos_start":[0.53029,0.0007,0.30975],"object_to_goal_dist_end":0.08782,"object_to_goal_dist_start":0.23174,"object_z_max":0.30975,"peak_contact_force":432.97476,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":566.0,"raw_peak_contact_force":1324.71071,"subtask_id":"approach_sub","tcp_end":[0.4945,0.00096,0.18086],"tcp_start":[0.52651,0.00069,0.26993],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.53014,0.00113,0.16227],"object_pos_start":[0.53004,0.00104,0.16251],"object_to_goal_dist_end":0.08763,"object_to_goal_dist_start":0.08782,"object_z_max":0.16254,"peak_contact_force":486.3455,"phase_name":"contact_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":486.3455,"subtask_id":"insert_sub","tcp_end":[0.49456,0.0011,0.18055],"tcp_start":[0.4945,0.00096,0.18086],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":95.0,"n_steps_budget":1000.0,"object_pos_end":[0.55516,0.04733,0.22629],"object_pos_start":[0.53014,0.00113,0.16227],"object_to_goal_dist_end":0.16335,"object_to_goal_dist_start":0.08763,"object_z_max":0.22395,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":30.0,"raw_peak_contact_force":518.40074,"subtask_id":"insert_sub","tcp_end":[0.51642,0.04396,0.23566],"tcp_start":[0.49456,0.0011,0.18055],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0b9f57c3f8a8fdb0f6fef54a4b5c0cfa6a2779a7721b018896a4efe993ac60cd`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":41.0,"average_failure_rate":0.39806,"average_mean_iterations":83.95146,"average_solve_count":103.0,"average_success_count":62.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_tolerance":0.00795,"approach_1.approach_height":0.16831,"approach_1.arc_height":0.07975,"contact_descend_1.contact_force":16.63754,"insert_1.insert_depth":0.10741},"optimized_scores":{"best_composite_score":0.36339,"best_fitness_score":0.42339,"best_task_score":0.83817},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.55636,0.03502,0.07813],"force_p95":1304.68774,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1343.85282,"mean_force":744.14237,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53842,0.03599,0.08015]},{"body_a":"peg_socket","body_b":"link7","contact_count":225.0,"contact_point_centroid":[0.58361,0.03661,0.07945],"force_p95":440.07128,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1221.94211,"mean_force":297.62254,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47936,0.05072,0.15445]},{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.48829,0.03056,0.07828],"force_p95":898.19451,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":915.1933,"mean_force":265.57976,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4846,0.03513,0.08855]},{"body_a":"peg_socket","body_b":"link7","contact_count":226.0,"contact_point_centroid":[0.58434,0.08324,0.07986],"force_p95":400.56908,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":531.21326,"mean_force":292.25519,"phase_index":3.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.50633,0.08133,0.17212]},{"body_a":"peg_socket","body_b":"link6","contact_count":355.0,"contact_point_centroid":[0.58434,0.0337,0.07987],"force_p95":368.47599,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":441.07696,"mean_force":284.08108,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47813,0.05914,0.1798]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.58436,0.07834,0.07989],"force_p95":166.82678,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":166.82678,"mean_force":166.82678,"phase_index":2.0,"phase_name":"contact_descend_1","phase_type":"descend","tcp_position_centroid":[0.49772,0.09072,0.1778]}],"total_contact_groups":6},"final_pose_error":0.19665,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.51843,0.07226,0.16329],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":1343.85282,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":99.0,"n_steps_budget":600.0,"object_pos_end":[0.52244,0.01952,0.30621],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.22816,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_sub","tcp_end":[0.51783,0.01953,0.26648],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":723.0,"n_steps_budget":1000.0,"object_pos_end":[0.53236,0.08338,0.1592],"object_pos_start":[0.52244,0.01952,0.30621],"object_to_goal_dist_end":0.11947,"object_to_goal_dist_start":0.22816,"object_z_max":0.30621,"peak_contact_force":271.10415,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":603.0,"raw_peak_contact_force":1343.85282,"subtask_id":"approach_sub","tcp_end":[0.49772,0.09072,0.1778],"tcp_start":[0.51783,0.01953,0.26648],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":690.0,"object_pos_end":[0.53238,0.08347,0.15926],"object_pos_start":[0.53236,0.08338,0.1592],"object_to_goal_dist_end":0.11957,"object_to_goal_dist_start":0.11947,"object_z_max":0.1592,"peak_contact_force":166.82678,"phase_name":"contact_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":166.82678,"subtask_id":"insert_sub","tcp_end":[0.49772,0.09081,0.17784],"tcp_start":[0.49772,0.09072,0.1778],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.55416,0.06541,0.14667],"object_pos_start":[0.53238,0.08347,0.15926],"object_to_goal_dist_end":0.10797,"object_to_goal_dist_start":0.11957,"object_z_max":0.15951,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":226.0,"raw_peak_contact_force":531.21326,"subtask_id":"insert_sub","tcp_end":[0.51843,0.07226,0.16329],"tcp_start":[0.49772,0.09081,0.17784],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```