## Search State

- **Seed**: 5
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | push → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.9106 | 0.86 | ❌ rejected |
| 3 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | 0.6642 | 0.96 | ❌ rejected |
| 2 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | 0.6642 | 0.96 | ❌ rejected |
| 1 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.5974 | 0.83 | ❌ rejected |
| 0 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | 0.6642 | 0.96 | ✅ accepted |

**Proposal policy**: task_score is 0.86 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.911) — your mutation base

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

- **Composite score**: 0.911
- **task_score** (E): 0.857
- **fitness_score**: 0.857  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_push | 0.33 | 1.00 | 0.1100 |
| insert_peg | 1.00 | 1.00 | 0.0001 |
| retract_free | 0.67 | 1.00 | 0.0195 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_push | push | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.476, 0.012, 0.195) | (0.504, -0.000, 0.340)→(0.509, 0.012, 0.173) | 0.260→0.096 | 1.00 / 1.000 | 277.666 | 1635.012 |
| insert_peg | insert | 1.00 / force_exceeded | (0.476, 0.012, 0.195)→(0.476, 0.012, 0.195) | (0.509, 0.012, 0.173)→(0.510, 0.012, 0.173) | 0.096→0.096 | 1.00 / 1.000 | 338.021 | 338.021 |
| retract_free | retract | 0.67 / step_budget | (0.476, 0.012, 0.195)→(0.468, 0.023, 0.202) | (0.510, 0.012, 0.173)→(0.501, 0.021, 0.180) | 0.096→0.105 | 1.00 / 1.000 | 299.183 | 501.182 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.862
- alignment_error: None
- force_efficiency: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.862
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.862
- **Median Q (composite search score)**: 0.909
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.486


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.14583,"average_solve_count":48.0,"average_success_count":48.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_push.push_z_offset":0.09714,"approach_push.speed":0.09987,"insert_peg.force_threshold":23.86538,"insert_peg.insert_depth":0.06746,"retract_free.speed":0.07556},"optimized_scores":{"best_composite_score":0.91505,"best_fitness_score":0.86172,"best_task_score":0.86172},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":584.0,"contact_point_centroid":[0.5843,0.00845,0.0796],"force_p95":818.07046,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2735.43465,"mean_force":354.8346,"phase_index":0.0,"phase_name":"approach_push","phase_type":"push","tcp_position_centroid":[0.46114,0.01033,0.16675]},{"body_a":"peg_socket","body_b":"link7","contact_count":218.0,"contact_point_centroid":[0.57962,0.00945,0.07958],"force_p95":2311.50482,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2722.45422,"mean_force":486.30591,"phase_index":0.0,"phase_name":"approach_push","phase_type":"push","tcp_position_centroid":[0.45901,0.00505,0.14259]},{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.46582,0.00337,0.07858],"force_p95":1049.96837,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1090.33092,"mean_force":274.75684,"phase_index":0.0,"phase_name":"approach_push","phase_type":"push","tcp_position_centroid":[0.45776,0.00337,0.09029]},{"body_a":"peg_socket","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.55148,-0.00562,0.07838],"force_p95":910.00036,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1031.55171,"mean_force":294.44566,"phase_index":0.0,"phase_name":"approach_push","phase_type":"push","tcp_position_centroid":[0.45482,0.00384,0.10024]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58433,0.01621,0.07989],"force_p95":344.49961,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":344.49961,"mean_force":344.49961,"phase_index":1.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.47778,0.02003,0.20393]},{"body_a":"peg_socket","body_b":"link6","contact_count":478.0,"contact_point_centroid":[0.5843,0.02084,0.07982],"force_p95":314.38088,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":326.87369,"mean_force":263.73076,"phase_index":2.0,"phase_name":"retract_free","phase_type":"retract","tcp_position_centroid":[0.46502,0.02897,0.2003]}],"total_contact_groups":6},"final_pose_error":0.05934,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.47951,0.0402,0.21555],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":2735.43465,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.51103,0.01961,0.18169],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10415,"object_to_goal_dist_start":0.26034,"object_z_max":0.34463,"peak_contact_force":270.71156,"phase_name":"approach_push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":838.0,"raw_peak_contact_force":2735.43465,"subtask_id":"reach_pre_insert","tcp_end":[0.47778,0.02003,0.20393],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51107,0.01963,0.18183],"object_pos_start":[0.51103,0.01961,0.18169],"object_to_goal_dist_end":0.10429,"object_to_goal_dist_start":0.10415,"object_z_max":0.18169,"peak_contact_force":344.49961,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":344.49961,"subtask_id":"reach_insertion","tcp_end":[0.47785,0.02003,0.2041],"tcp_start":[0.47778,0.02003,0.20393],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.51104,0.03596,0.1913],"object_pos_start":[0.51107,0.01963,0.18183],"object_to_goal_dist_end":0.11749,"object_to_goal_dist_start":0.10429,"object_z_max":0.19193,"peak_contact_force":281.46729,"phase_name":"retract_free","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":478.0,"raw_peak_contact_force":326.87369,"tcp_end":[0.47951,0.0402,0.21555],"tcp_start":[0.47785,0.02003,0.2041],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `619899a8ac3451ebc6b92c72992387b20e095386c555898a9ee2a3180ddd0ca3`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.04,"average_solve_count":50.0,"average_success_count":50.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_push.push_z_offset":0.08436,"approach_push.speed":0.09841,"insert_peg.force_threshold":16.603,"insert_peg.insert_depth":0.04858,"retract_free.speed":0.06218},"optimized_scores":{"best_composite_score":0.90771,"best_fitness_score":0.85438,"best_task_score":0.85438},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.46127,-0.00188,0.07864],"force_p95":1034.52841,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1083.10733,"mean_force":314.66322,"phase_index":0.0,"phase_name":"approach_push","phase_type":"push","tcp_position_centroid":[0.45649,-0.0018,0.09148]},{"body_a":"peg_socket","body_b":"link6","contact_count":203.0,"contact_point_centroid":[0.56298,-0.00801,0.07984],"force_p95":308.89672,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":932.77591,"mean_force":287.56879,"phase_index":0.0,"phase_name":"approach_push","phase_type":"push","tcp_position_centroid":[0.45871,-0.00684,0.18113]},{"body_a":"peg_socket","body_b":"link7","contact_count":487.0,"contact_point_centroid":[0.56212,-0.00125,0.0798],"force_p95":323.17173,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":787.04551,"mean_force":271.97223,"phase_index":0.0,"phase_name":"approach_push","phase_type":"push","tcp_position_centroid":[0.45595,-0.00387,0.15816]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.563,-0.00886,0.07991],"force_p95":312.06309,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":312.06309,"mean_force":312.06309,"phase_index":1.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.46527,-0.00787,0.19058]},{"body_a":"peg_socket","body_b":"link6","contact_count":444.0,"contact_point_centroid":[0.56303,-0.00913,0.07995],"force_p95":299.2395,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":299.90509,"mean_force":281.32237,"phase_index":2.0,"phase_name":"retract_free","phase_type":"retract","tcp_position_centroid":[0.45846,-0.01034,0.18783]}],"total_contact_groups":5},"final_pose_error":0.04618,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.45878,-0.0139,0.19306],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":1083.10733,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.49948,-0.00762,0.16986],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09019,"object_to_goal_dist_start":0.26034,"object_z_max":0.34453,"peak_contact_force":300.39193,"phase_name":"approach_push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":702.0,"raw_peak_contact_force":1083.10733,"subtask_id":"reach_pre_insert","tcp_end":[0.46527,-0.00787,0.19058],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49953,-0.0076,0.16993],"object_pos_start":[0.49948,-0.00762,0.16986],"object_to_goal_dist_end":0.09025,"object_to_goal_dist_start":0.09019,"object_z_max":0.16986,"peak_contact_force":312.06309,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":312.06309,"subtask_id":"reach_insertion","tcp_end":[0.46533,-0.00785,0.19067],"tcp_start":[0.46527,-0.00787,0.19058],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":444.0,"n_steps_budget":600.0,"object_pos_end":[0.49314,-0.01262,0.17262],"object_pos_start":[0.49953,-0.0076,0.16993],"object_to_goal_dist_end":0.09373,"object_to_goal_dist_start":0.09025,"object_z_max":0.17258,"peak_contact_force":286.77344,"phase_name":"retract_free","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":444.0,"raw_peak_contact_force":299.90509,"tcp_end":[0.45878,-0.0139,0.19306],"tcp_start":[0.46533,-0.00785,0.19067],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `09a021eaed2a28b8f97b40a956e668b0df532c8dfcbc8d48b91f00ceefb0c83a`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.08065,"average_solve_count":62.0,"average_success_count":62.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_push.push_z_offset":0.03718,"approach_push.speed":0.09986,"insert_peg.force_threshold":43.703,"insert_peg.insert_depth":0.03159,"retract_free.speed":0.0247},"optimized_scores":{"best_composite_score":0.90917,"best_fitness_score":0.85583,"best_task_score":0.85583},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.46153,0.00297,0.07864],"force_p95":1034.29772,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1086.49514,"mean_force":291.54133,"phase_index":0.0,"phase_name":"approach_push","phase_type":"push","tcp_position_centroid":[0.45682,0.00294,0.09151]},{"body_a":"peg_socket","body_b":"link6","contact_count":416.0,"contact_point_centroid":[0.56993,0.02753,0.07984],"force_p95":311.7841,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":876.7668,"mean_force":281.51715,"phase_index":2.0,"phase_name":"retract_free","phase_type":"retract","tcp_position_centroid":[0.46027,0.03247,0.18618]},{"body_a":"peg_socket","body_b":"link7","contact_count":79.0,"contact_point_centroid":[0.56973,0.02532,0.07992],"force_p95":393.4134,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":714.82341,"mean_force":314.58472,"phase_index":2.0,"phase_name":"retract_free","phase_type":"retract","tcp_position_centroid":[0.4776,0.02447,0.18605]},{"body_a":"peg_socket","body_b":"link7","contact_count":835.0,"contact_point_centroid":[0.5684,0.01329,0.07982],"force_p95":549.55677,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":710.48764,"mean_force":353.95439,"phase_index":0.0,"phase_name":"approach_push","phase_type":"push","tcp_position_centroid":[0.4602,0.01005,0.164]},{"body_a":"peg_socket","body_b":"link6","contact_count":598.0,"contact_point_centroid":[0.56974,0.00976,0.07935],"force_p95":666.8829,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":688.71367,"mean_force":484.43457,"phase_index":0.0,"phase_name":"approach_push","phase_type":"push","tcp_position_centroid":[0.46227,0.0123,0.17248]},{"body_a":"peg_socket","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.53999,0.00109,0.07992],"force_p95":440.03642,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":517.6899,"mean_force":129.42248,"phase_index":0.0,"phase_name":"approach_push","phase_type":"push","tcp_position_centroid":[0.45199,0.00384,0.129]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.56992,0.02198,0.07988],"force_p95":357.50139,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":357.50139,"mean_force":357.50139,"phase_index":1.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.48501,0.02454,0.19092]}],"total_contact_groups":7},"final_pose_error":0.04822,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.4659,0.04129,0.19701],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1086.49514,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51799,0.02256,0.16837],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09296,"object_to_goal_dist_start":0.26034,"object_z_max":0.34454,"peak_contact_force":261.89574,"phase_name":"approach_push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1450.0,"raw_peak_contact_force":1086.49514,"subtask_id":"reach_pre_insert","tcp_end":[0.48501,0.02454,0.19092],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":900.0,"object_pos_end":[0.51802,0.02259,0.16829],"object_pos_start":[0.51799,0.02256,0.16837],"object_to_goal_dist_end":0.0929,"object_to_goal_dist_start":0.09296,"object_z_max":0.16837,"peak_contact_force":357.50139,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":357.50139,"subtask_id":"reach_insertion","tcp_end":[0.48503,0.02458,0.19082],"tcp_start":[0.48501,0.02454,0.19092],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":488.0,"n_steps_budget":720.0,"object_pos_end":[0.49966,0.03842,0.17575],"object_pos_start":[0.51802,0.02259,0.16829],"object_to_goal_dist_end":0.10317,"object_to_goal_dist_start":0.0929,"object_z_max":0.17571,"peak_contact_force":329.30836,"phase_name":"retract_free","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":495.0,"raw_peak_contact_force":876.7668,"tcp_end":[0.4659,0.04129,0.19701],"tcp_start":[0.48503,0.02458,0.19082],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```