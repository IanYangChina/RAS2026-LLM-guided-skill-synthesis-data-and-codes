## Search State

- **Seed**: 7
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | descend → grasp → lift → approach → descend → release → retract | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.6368 | 0.14 | ❌ rejected |
| 6 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 5 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 4 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 3 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |

**Proposal policy**: task_score is 0.14 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: grasp_place
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

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
| `fixture` | offset from fixture pose | targets near fixture |

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

## Current Skill (Q=-0.637) — your mutation base

```yaml
skill: grasp_place
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
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2

```

## Design Metrics

- **Composite score**: -0.637
- **task_score** (E): 0.145
- **fitness_score**: 0.163  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.800

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_1 | 0.00 | 1.00 | 0.1916 |
| grasp_1 | 1.00 | 1.00 | 0.0008 |
| lift_1 | 0.33 | 1.00 | 0.1078 |
| approach_goal_1 | 0.00 | 1.00 | 0.1314 |
| descend_place_1 | 0.00 | 1.00 | 0.0591 |
| release_1 | 1.00 | 1.00 | 0.0248 |
| retract_1 | 0.00 | 1.00 | 0.0004 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_1 | descend | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.393, 0.003, 0.142) | (0.511, 0.022, 0.030)→(0.470, 0.024, 0.016) | 0.271→0.296 | 1.00 / 5.000 | 192.186 | 1503.435 |
| grasp_1 | grasp | 1.00 / step_budget | (0.393, 0.003, 0.142)→(0.393, 0.003, 0.141) | (0.470, 0.024, 0.016)→(0.470, 0.024, 0.016) | 0.296→0.296 | 1.00 / 9.000 | 68.659 | 100.482 |
| lift_1 | lift | 0.33 / step_budget | (0.393, 0.003, 0.141)→(0.392, 0.003, 0.249) | (0.470, 0.024, 0.016)→(0.470, 0.024, 0.016) | 0.296→0.296 | 1.00 / 8.667 | 182003.204 | 90.351 |
| approach_goal_1 | approach | 0.00 / step_budget | (0.392, 0.003, 0.249)→(0.484, 0.093, 0.260) | (0.470, 0.024, 0.016)→(0.470, 0.024, 0.016) | 0.296→0.296 | 1.00 / 8.667 | 94359.028 | 114.086 |
| descend_place_1 | descend | 0.00 / step_budget | (0.484, 0.093, 0.260)→(0.513, 0.135, 0.235) | (0.470, 0.024, 0.016)→(0.470, 0.024, 0.016) | 0.296→0.296 | 1.00 / 9.000 | 309.707 | 362.272 |
| release_1 | release | 1.00 / step_budget | (0.513, 0.135, 0.235)→(0.515, 0.137, 0.260) | (0.470, 0.024, 0.016)→(0.470, 0.024, 0.016) | 0.296→0.296 | 1.00 / 6.667 | 262.455 | 280.867 |
| retract_1 | retract | 0.00 / step_budget | (0.515, 0.137, 0.260)→(0.515, 0.137, 0.260) | (0.470, 0.024, 0.016)→(0.470, 0.024, 0.016) | 0.296→0.296 | 1.00 / 6.667 | 287.115 | 278.985 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.205
- phase_score: 0.055
- phase_breakdown.reach_object_score: 0.092
- phase_breakdown.reach_goal_score: 0.040
- grasp_place_fitness: 0.191

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.191
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.205
- **Median Q (composite search score)**: -0.637
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: release_1.release_duration
- **Final σ (mean)**: 0.337


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0b279c554151a1bc107b4895d67067efa2444eadb5a644f2482f57ab9ff93d7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `079d4532bc3cff86c1b89933c7940f2ee474dc4233e12f8d134c76ceb3cd8d4d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":90.0,"average_failure_rate":0.39648,"average_mean_iterations":82.23789,"average_solve_count":227.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal_1.goal_approach_speed":0.0666,"approach_goal_1.goal_offset_x":0.03224,"approach_goal_1.goal_offset_y":-0.00833,"descend_1.descend_speed":0.03696,"descend_1.descend_z_offset":0.11942,"descend_place_1.place_speed":0.07639,"descend_place_1.place_z_offset":0.01441,"grasp_1.grasp_duration":1.2407,"lift_1.lift_height":0.15986,"lift_1.lift_speed":0.03585,"release_1.release_duration":0.67222,"retract_1.retract_height":0.08068,"retract_1.retract_speed":0.05951},"optimized_scores":{"best_composite_score":-0.60898,"best_fitness_score":0.19102,"best_task_score":0.20542},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63332,0.00471,-0.00046],"force_p95":197.16123,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1333.49537,"mean_force":200.38586,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.3917,0.00437,0.12253]},{"body_a":"link5","body_b":"hand","contact_count":24.0,"contact_point_centroid":[0.54316,-0.00244,0.23618],"force_p95":320.48864,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":342.01165,"mean_force":313.11149,"phase_index":3.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.50045,0.07161,0.24126]},{"body_a":"link5","body_b":"hand","contact_count":67.0,"contact_point_centroid":[0.53672,0.00816,0.20583],"force_p95":309.06387,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":317.9803,"mean_force":301.83778,"phase_index":4.0,"phase_name":"descend_place_1","phase_type":"descend","tcp_position_centroid":[0.50108,0.08435,0.22192]},{"body_a":"link5","body_b":"hand","contact_count":3.0,"contact_point_centroid":[0.53684,0.02506,0.20833],"force_p95":271.46878,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":274.52753,"mean_force":231.35809,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51012,0.09827,0.24322]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.53237,0.0202,0.18715],"force_p95":264.12487,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":265.80233,"mean_force":239.80884,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50855,0.09446,0.22284]},{"body_a":"world","body_b":"link6","contact_count":7.0,"contact_point_centroid":[0.62882,0.00712,-0.0001],"force_p95":82.75108,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":89.57674,"mean_force":64.6388,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.3998,0.00702,0.14858]},{"body_a":"world","body_b":"link6","contact_count":450.0,"contact_point_centroid":[0.62861,0.00716,-0.00014],"force_p95":81.74539,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.85576,"mean_force":72.73718,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.39972,0.00706,0.14872]},{"body_a":"grasp_target","body_b":"link7","contact_count":367.0,"contact_point_centroid":[0.49257,0.0228,0.04189],"force_p95":1.26216,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.0161,"mean_force":0.46243,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.38727,0.00297,0.10294]},{"body_a":"grasp_target","body_b":"hand","contact_count":335.0,"contact_point_centroid":[0.48597,0.02389,0.05513],"force_p95":1.69374,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.71509,"mean_force":0.41424,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.387,0.0029,0.1012]},{"body_a":"world","body_b":"grasp_target","contact_count":3187.0,"contact_point_centroid":[0.48262,0.04803,-0.00288],"force_p95":0.36602,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.35434,"mean_force":0.19558,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.40726,0.00435,0.137]},{"body_a":"left_finger","body_b":"link5","contact_count":178.0,"contact_point_centroid":[0.5005,0.06139,0.2275],"force_p95":0.8604,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1.0571,"mean_force":0.40745,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50936,0.0966,0.23344]},{"body_a":"left_finger","body_b":"link5","contact_count":9.0,"contact_point_centroid":[0.50255,0.06315,0.23649],"force_p95":0.79292,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.84966,"mean_force":0.33918,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51012,0.09827,0.24322]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4695,0.05114,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.39972,0.00706,0.14872]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.4695,0.05114,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.39771,0.00691,0.20049]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.4695,0.05114,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.46128,0.04723,0.24172]},{"body_a":"world","body_b":"grasp_target","contact_count":268.0,"contact_point_centroid":[0.4695,0.05114,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"descend_place_1","phase_type":"descend","tcp_position_centroid":[0.50108,0.08435,0.22192]}],"total_contact_groups":24},"final_pose_error":0.14006,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.4695,0.05114,0.01602],"final_tcp_position":[0.50992,0.09855,0.24315],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":273004.72767,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4695,0.05114,0.01602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.23741,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":191.92136,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4795.0,"raw_peak_contact_force":1333.49537,"subtask_id":"reach_object","tcp_end":[0.39933,0.00711,0.14909],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15675,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4695,0.05114,0.01602],"object_pos_start":[0.4695,0.05114,0.01602],"object_to_goal_dist_end":0.23741,"object_to_goal_dist_start":0.23741,"object_z_max":0.01602,"peak_contact_force":69.01001,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2570.0,"raw_peak_contact_force":84.85576,"tcp_end":[0.39981,0.00703,0.14855],"tcp_start":[0.39933,0.00711,0.14909],"tcp_to_object_dist_end":0.15609,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4695,0.05114,0.01602],"object_pos_start":[0.4695,0.05114,0.01602],"object_to_goal_dist_end":0.23741,"object_to_goal_dist_start":0.23741,"object_z_max":0.01602,"peak_contact_force":273004.72767,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8188.0,"raw_peak_contact_force":89.57674,"tcp_end":[0.39815,0.00692,0.25327],"tcp_start":[0.39981,0.00703,0.14855],"tcp_to_object_dist_end":0.25167,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4695,0.05114,0.01602],"object_pos_start":[0.4695,0.05114,0.01602],"object_to_goal_dist_end":0.23741,"object_to_goal_dist_start":0.23741,"object_z_max":0.01602,"peak_contact_force":309.01463,"phase_name":"approach_goal_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8320.0,"raw_peak_contact_force":342.01165,"tcp_end":[0.50127,0.07213,0.24136],"tcp_start":[0.39815,0.00692,0.25327],"tcp_to_object_dist_end":0.22854,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":67.0,"n_steps_budget":1000.0,"object_pos_end":[0.4695,0.05114,0.01602],"object_pos_start":[0.4695,0.05114,0.01602],"object_to_goal_dist_end":0.23741,"object_to_goal_dist_start":0.23741,"object_z_max":0.01602,"peak_contact_force":301.57108,"phase_name":"descend_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":626.0,"raw_peak_contact_force":317.9803,"subtask_id":"reach_goal","tcp_end":[0.50584,0.09397,0.21569],"tcp_start":[0.50127,0.07213,0.24136],"tcp_to_object_dist_end":0.20742,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4695,0.05114,0.01602],"object_pos_start":[0.4695,0.05114,0.01602],"object_to_goal_dist_end":0.23741,"object_to_goal_dist_start":0.23741,"object_z_max":0.01602,"peak_contact_force":250.83787,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1408.0,"raw_peak_contact_force":265.80233,"tcp_end":[0.51016,0.09821,0.24307],"tcp_start":[0.50584,0.09397,0.21569],"tcp_to_object_dist_end":0.23542,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.4695,0.05114,0.01602],"object_pos_start":[0.4695,0.05114,0.01602],"object_to_goal_dist_end":0.23741,"object_to_goal_dist_start":0.23741,"object_z_max":0.01602,"peak_contact_force":273.32719,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":24.0,"raw_peak_contact_force":274.52753,"tcp_end":[0.50992,0.09855,0.24315],"tcp_start":[0.51016,0.09821,0.24307],"tcp_to_object_dist_end":0.23552,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a74f7c08b88460953bfa7e35b953cddf9278fdc17d2d4db8a2ea121b328e8b73`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":107.0,"average_failure_rate":0.39051,"average_mean_iterations":80.78467,"average_solve_count":274.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal_1.goal_approach_speed":0.04042,"approach_goal_1.goal_offset_x":0.00499,"approach_goal_1.goal_offset_y":-0.01453,"descend_1.descend_speed":0.01102,"descend_1.descend_z_offset":0.19998,"descend_place_1.place_speed":0.03708,"descend_place_1.place_z_offset":-0.0099,"grasp_1.grasp_duration":1.64126,"lift_1.lift_height":0.12104,"lift_1.lift_speed":0.05515,"release_1.release_duration":0.49987,"retract_1.retract_height":0.16462,"retract_1.retract_speed":0.06641},"optimized_scores":{"best_composite_score":-0.63728,"best_fitness_score":0.16272,"best_task_score":0.12363},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":885.0,"contact_point_centroid":[0.6262,0.00578,-0.00047],"force_p95":194.58082,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1619.37549,"mean_force":201.87557,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.38134,0.00527,0.11764]},{"body_a":"link5","body_b":"hand","contact_count":279.0,"contact_point_centroid":[0.53578,0.06531,0.21779],"force_p95":362.81817,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":394.0476,"mean_force":316.04067,"phase_index":4.0,"phase_name":"descend_place_1","phase_type":"descend","tcp_position_centroid":[0.50879,0.1506,0.24645]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.53378,0.08482,0.20321],"force_p95":293.41011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":294.93112,"mean_force":259.70592,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51945,0.16209,0.25266]},{"body_a":"link5","body_b":"hand","contact_count":3.0,"contact_point_centroid":[0.53744,0.08712,0.22319],"force_p95":281.2966,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":282.17114,"mean_force":248.37856,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52013,0.16262,0.27328]},{"body_a":"world","body_b":"link6","contact_count":450.0,"contact_point_centroid":[0.62187,0.00784,-0.00014],"force_p95":87.83404,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":121.86355,"mean_force":73.32716,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.38319,0.00766,0.13248]},{"body_a":"world","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.6221,0.0078,-0.0001],"force_p95":85.32314,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.25152,"mean_force":60.9731,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.3833,0.00762,0.13233]},{"body_a":"grasp_target","body_b":"hand","contact_count":50.0,"contact_point_centroid":[0.4603,0.03183,0.04162],"force_p95":3.52846,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.05921,"mean_force":1.57282,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.37664,0.00337,0.0628]},{"body_a":"grasp_target","body_b":"link7","contact_count":32.0,"contact_point_centroid":[0.48164,0.02926,0.01765],"force_p95":2.58241,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.18634,"mean_force":0.75388,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.36974,0.00331,0.06029]},{"body_a":"world","body_b":"grasp_target","contact_count":3870.0,"contact_point_centroid":[0.44658,0.04873,-0.00216],"force_p95":0.13845,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.41587,"mean_force":0.14165,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.39447,0.00503,0.12818]},{"body_a":"left_finger","body_b":"link5","contact_count":3.0,"contact_point_centroid":[0.50854,0.12294,0.25424],"force_p95":0.19278,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.19533,"mean_force":0.16454,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52013,0.16262,0.27328]},{"body_a":"left_finger","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.50851,0.12292,0.25379],"force_p95":0.13592,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.13592,"mean_force":0.13592,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52012,0.16259,0.27277]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.44094,0.04866,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.38319,0.00766,0.13248]},{"body_a":"world","body_b":"grasp_target","contact_count":3944.0,"contact_point_centroid":[0.44094,0.04866,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.38105,0.0075,0.18749]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.44094,0.04866,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.42644,0.05397,0.25801]},{"body_a":"world","body_b":"grasp_target","contact_count":2204.0,"contact_point_centroid":[0.44094,0.04866,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"descend_place_1","phase_type":"descend","tcp_position_centroid":[0.49681,0.13373,0.25341]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.44094,0.04866,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51945,0.16209,0.25266]}],"total_contact_groups":23},"final_pose_error":0.15154,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.44094,0.04866,0.01602],"final_tcp_position":[0.52017,0.16283,0.27345],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273019.16783,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44094,0.04866,0.01602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.31357,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":194.13987,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4856.0,"raw_peak_contact_force":1619.37549,"subtask_id":"reach_object","tcp_end":[0.38277,0.00773,0.13285],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13678,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.44094,0.04866,0.01602],"object_pos_start":[0.44094,0.04866,0.01602],"object_to_goal_dist_end":0.31357,"object_to_goal_dist_start":0.31357,"object_z_max":0.01602,"peak_contact_force":68.29336,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2578.0,"raw_peak_contact_force":121.86355,"tcp_end":[0.38331,0.00763,0.13229],"tcp_start":[0.38277,0.00773,0.13285],"tcp_to_object_dist_end":0.1361,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":986.0,"n_steps_budget":1000.0,"object_pos_end":[0.44094,0.04866,0.01602],"object_pos_start":[0.44094,0.04866,0.01602],"object_to_goal_dist_end":0.31357,"object_to_goal_dist_start":0.31357,"object_z_max":0.01602,"peak_contact_force":273004.76119,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8086.0,"raw_peak_contact_force":91.25152,"tcp_end":[0.38151,0.00752,0.24357],"tcp_start":[0.38331,0.00763,0.13229],"tcp_to_object_dist_end":0.23876,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44094,0.04866,0.01602],"object_pos_start":[0.44094,0.04866,0.01602],"object_to_goal_dist_end":0.31357,"object_to_goal_dist_start":0.31357,"object_z_max":0.01602,"peak_contact_force":273019.16783,"phase_name":"approach_goal_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8229.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.46898,0.09616,0.27478],"tcp_start":[0.38151,0.00752,0.24357],"tcp_to_object_dist_end":0.26458,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":551.0,"n_steps_budget":1000.0,"object_pos_end":[0.44094,0.04866,0.01602],"object_pos_start":[0.44094,0.04866,0.01602],"object_to_goal_dist_end":0.31357,"object_to_goal_dist_start":0.31357,"object_z_max":0.01602,"peak_contact_force":318.26697,"phase_name":"descend_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4859.0,"raw_peak_contact_force":394.0476,"subtask_id":"reach_goal","tcp_end":[0.51923,0.1624,0.25019],"tcp_start":[0.46898,0.09616,0.27478],"tcp_to_object_dist_end":0.27185,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.44094,0.04866,0.01602],"object_pos_start":[0.44094,0.04866,0.01602],"object_to_goal_dist_end":0.31357,"object_to_goal_dist_start":0.31357,"object_z_max":0.01602,"peak_contact_force":269.83901,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1219.0,"raw_peak_contact_force":294.93112,"tcp_end":[0.52013,0.1626,0.27308],"tcp_start":[0.51923,0.1624,0.25019],"tcp_to_object_dist_end":0.29212,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.44094,0.04866,0.01602],"object_pos_start":[0.44094,0.04866,0.01602],"object_to_goal_dist_end":0.31357,"object_to_goal_dist_start":0.31357,"object_z_max":0.01602,"peak_contact_force":298.73181,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":18.0,"raw_peak_contact_force":282.17114,"tcp_end":[0.52017,0.16283,0.27345],"tcp_start":[0.52013,0.1626,0.27308],"tcp_to_object_dist_end":0.29255,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b1a72366a9c9a56aa2e80fc4399e157c8281abf492ab3c1ede02058762a86ed7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":96.0,"average_failure_rate":0.40336,"average_mean_iterations":83.59244,"average_solve_count":238.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal_1.goal_approach_speed":0.06597,"approach_goal_1.goal_offset_x":-0.00746,"approach_goal_1.goal_offset_y":0.03934,"descend_1.descend_speed":0.01598,"descend_1.descend_z_offset":0.19772,"descend_place_1.place_speed":0.06202,"descend_place_1.place_z_offset":0.00272,"grasp_1.grasp_duration":1.6767,"lift_1.lift_height":0.20422,"lift_1.lift_speed":0.04954,"release_1.release_duration":0.20002,"retract_1.retract_height":0.09971,"retract_1.retract_speed":0.04947},"optimized_scores":{"best_composite_score":-0.66426,"best_fitness_score":0.13574,"best_task_score":0.10552},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":885.0,"contact_point_centroid":[0.63406,-0.00318,-0.00046],"force_p95":194.66325,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1557.43309,"mean_force":199.39277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.39145,-0.00319,0.12145]},{"body_a":"link5","body_b":"hand","contact_count":152.0,"contact_point_centroid":[0.53773,0.05592,0.21774],"force_p95":357.21959,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":374.78951,"mean_force":313.81694,"phase_index":4.0,"phase_name":"descend_place_1","phase_type":"descend","tcp_position_centroid":[0.50561,0.1402,0.2388]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.53407,0.06907,0.20167],"force_p95":280.03134,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":281.86812,"mean_force":251.65437,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51495,0.14936,0.24336]},{"body_a":"link5","body_b":"hand","contact_count":3.0,"contact_point_centroid":[0.53774,0.07188,0.22184],"force_p95":279.50532,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":280.25548,"mean_force":246.95329,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51575,0.15049,0.26379]},{"body_a":"world","body_b":"link6","contact_count":450.0,"contact_point_centroid":[0.6293,-0.00415,-0.00014],"force_p95":83.24276,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":94.72568,"mean_force":72.77668,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.39712,-0.00452,0.14354]},{"body_a":"world","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.62952,-0.00418,-0.00011],"force_p95":85.67896,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.22457,"mean_force":66.70548,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.3972,-0.00455,0.14339]},{"body_a":"grasp_target","body_b":"link6","contact_count":215.0,"contact_point_centroid":[0.53424,-0.02453,0.03206],"force_p95":0.91485,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.50934,"mean_force":0.28987,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.38739,-0.00284,0.10655]},{"body_a":"grasp_target","body_b":"link7","contact_count":755.0,"contact_point_centroid":[0.52449,-0.01081,0.0327],"force_p95":0.77596,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.28883,"mean_force":0.25409,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.3909,-0.00297,0.11638]},{"body_a":"grasp_target","body_b":"hand","contact_count":107.0,"contact_point_centroid":[0.49088,-0.02697,0.04625],"force_p95":2.32553,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.00447,"mean_force":0.90113,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.38419,-0.00235,0.08119]},{"body_a":"world","body_b":"grasp_target","contact_count":3727.0,"contact_point_centroid":[0.50648,-0.0262,-0.00243],"force_p95":0.27984,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.70974,"mean_force":0.16504,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.40464,-0.00302,0.13308]},{"body_a":"left_finger","body_b":"link5","contact_count":3.0,"contact_point_centroid":[0.50691,0.10865,0.24939],"force_p95":0.31234,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.31472,"mean_force":0.29822,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51575,0.15049,0.26379]},{"body_a":"left_finger","body_b":"link5","contact_count":11.0,"contact_point_centroid":[0.50677,0.10854,0.24755],"force_p95":0.20065,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.20448,"mean_force":0.17554,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51569,0.15032,0.26178]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50033,-0.02732,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.39712,-0.00452,0.14354]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50033,-0.02732,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.39506,-0.00464,0.19673]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50033,-0.02732,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.4404,0.05561,0.25773]},{"body_a":"world","body_b":"grasp_target","contact_count":1308.0,"contact_point_centroid":[0.50033,-0.02732,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"descend_place_1","phase_type":"descend","tcp_position_centroid":[0.49731,0.13019,0.24548]}],"total_contact_groups":24},"final_pose_error":0.12937,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.50033,-0.02732,0.01602],"final_tcp_position":[0.51578,0.15089,0.26363],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":9748.90029,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50033,-0.02732,0.01602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.33733,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":190.49664,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5707.0,"raw_peak_contact_force":1557.43309,"subtask_id":"reach_object","tcp_end":[0.39672,-0.00448,0.1439],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16617,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50033,-0.02732,0.01602],"object_pos_start":[0.50033,-0.02732,0.01602],"object_to_goal_dist_end":0.33733,"object_to_goal_dist_start":0.33733,"object_z_max":0.01602,"peak_contact_force":68.67247,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2577.0,"raw_peak_contact_force":94.72568,"tcp_end":[0.39721,-0.00455,0.14336],"tcp_start":[0.39672,-0.00448,0.1439],"tcp_to_object_dist_end":0.16542,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50033,-0.02732,0.01602],"object_pos_start":[0.50033,-0.02732,0.01602],"object_to_goal_dist_end":0.33733,"object_to_goal_dist_start":0.33733,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8208.0,"raw_peak_contact_force":90.22457,"tcp_end":[0.39551,-0.00465,0.25084],"tcp_start":[0.39721,-0.00455,0.14336],"tcp_to_object_dist_end":0.25815,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50033,-0.02732,0.01602],"object_pos_start":[0.50033,-0.02732,0.01602],"object_to_goal_dist_end":0.33733,"object_to_goal_dist_start":0.33733,"object_z_max":0.01602,"peak_contact_force":9748.90029,"phase_name":"approach_goal_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8259.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.48075,0.10998,0.26285],"tcp_start":[0.39551,-0.00465,0.25084],"tcp_to_object_dist_end":0.28313,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":327.0,"n_steps_budget":1000.0,"object_pos_end":[0.50033,-0.02732,0.01602],"object_pos_start":[0.50033,-0.02732,0.01602],"object_to_goal_dist_end":0.33733,"object_to_goal_dist_start":0.33733,"object_z_max":0.01602,"peak_contact_force":309.28399,"phase_name":"descend_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2879.0,"raw_peak_contact_force":374.78951,"subtask_id":"reach_goal","tcp_end":[0.51459,0.14951,0.2404],"tcp_start":[0.48075,0.10998,0.26285],"tcp_to_object_dist_end":0.28604,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50033,-0.02732,0.01602],"object_pos_start":[0.50033,-0.02732,0.01602],"object_to_goal_dist_end":0.33733,"object_to_goal_dist_start":0.33733,"object_z_max":0.01602,"peak_contact_force":266.68773,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1229.0,"raw_peak_contact_force":281.86812,"tcp_end":[0.51574,0.15042,0.26365],"tcp_start":[0.51459,0.14951,0.2404],"tcp_to_object_dist_end":0.30521,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50033,-0.02732,0.01602],"object_pos_start":[0.50033,-0.02732,0.01602],"object_to_goal_dist_end":0.33733,"object_to_goal_dist_start":0.33733,"object_z_max":0.01602,"peak_contact_force":289.28502,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":18.0,"raw_peak_contact_force":280.25548,"tcp_end":[0.51578,0.15089,0.26363],"tcp_start":[0.51574,0.15042,0.26365],"tcp_to_object_dist_end":0.30546,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```