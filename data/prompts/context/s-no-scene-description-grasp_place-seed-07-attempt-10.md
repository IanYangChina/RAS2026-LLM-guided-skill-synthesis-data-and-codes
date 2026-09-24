## Search State

- **Seed**: 7
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.2181 | 0.17 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.4938 | 0.15 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.3831 | 0.17 | ❌ rejected |
| 7 | descend → grasp → lift → approach → descend → release → retract | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.6368 | 0.14 | ❌ rejected |
| 6 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.218) — your mutation base

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

- **Composite score**: -0.218
- **task_score** (E): 0.166
- **fitness_score**: 0.212  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 1.00 | 1.00 | 0.1205 |
| descend_to_grasp | 1.00 | 1.00 | 0.0439 |
| grasp_object | 1.00 | 1.00 | 0.0115 |
| lift_object | 1.00 | 1.00 | 0.0820 |
| approach_goal | 0.00 | 1.00 | 0.1017 |
| descend_place | 1.00 | 1.00 | 0.0004 |
| release_object | 1.00 | 1.00 | 0.0232 |
| retract_from_goal | 0.67 | 1.00 | 0.1030 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.020, 0.187) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / force_exceeded | (0.506, 0.020, 0.187)→(0.506, 0.019, 0.143) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 81.142 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.506, 0.019, 0.143)→(0.499, 0.019, 0.134) | (0.511, 0.022, 0.026)→(0.511, 0.023, 0.026) | 0.273→0.273 | 1.00 / 15.667 | 0.128 | 0.142 |
| lift_object | lift | 1.00 / step_budget | (0.499, 0.019, 0.134)→(0.496, 0.019, 0.216) | (0.511, 0.023, 0.026)→(0.503, 0.021, 0.023) | 0.273→0.278 | 1.00 / 8.333 | 91002.116 | 0.407 |
| approach_goal | approach | 0.00 / step_budget | (0.496, 0.019, 0.216)→(0.542, 0.096, 0.260) | (0.503, 0.021, 0.023)→(0.503, 0.021, 0.023) | 0.278→0.278 | 1.00 / 8.000 | 3249.713 | 0.123 |
| descend_place | descend | 1.00 / force_exceeded | (0.542, 0.096, 0.260)→(0.542, 0.096, 0.260) | (0.503, 0.021, 0.023)→(0.503, 0.021, 0.023) | 0.278→0.278 | 1.00 / 9.000 | 272955.384 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.542, 0.096, 0.260)→(0.538, 0.095, 0.282) | (0.503, 0.021, 0.023)→(0.503, 0.021, 0.023) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_from_goal | retract | 0.67 / step_budget | (0.538, 0.095, 0.282)→(0.590, 0.176, 0.312) | (0.503, 0.021, 0.023)→(0.503, 0.021, 0.023) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.110
- phase_score: 0.071
- phase_breakdown.reach_object_score: 0.273
- phase_breakdown.achieve_goal_score: 0.020
- grasp_place_fitness: 0.255

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.255
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.243
- **Median Q (composite search score)**: -0.215
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.372


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_speed":0.1116,"approach_goal.goal_approach_speed":0.10035,"descend_place.place_force_threshold":15.46465,"descend_to_grasp.descend_force_threshold":10.10238,"grasp_object.grasp_duration":1.09401,"lift_object.lift_height":0.05624,"lift_object.lift_speed":0.10746,"release_object.release_duration":1.08705,"retract_from_goal.retract_height":0.14259,"retract_from_goal.retract_speed":0.06813},"optimized_scores":{"best_composite_score":-0.21493,"best_fitness_score":0.21507,"best_task_score":0.24298},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1480.0,"contact_point_centroid":[0.51251,0.03972,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.50284,0.01702,0.24372]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50713,0.03538,0.1848]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5011,0.035,0.1742]},{"body_a":"world","body_b":"grasp_target","contact_count":1924.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49687,0.0347,0.19532]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53133,0.07393,0.23473]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56224,0.10635,0.25162]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55919,0.10586,0.25341]},{"body_a":"world","body_b":"grasp_target","contact_count":3100.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.59051,0.13847,0.27327]},{"body_a":"left_finger","body_b":"right_finger","contact_count":339.0,"contact_point_centroid":[0.50019,0.03494,0.175],"force_p95":0.01423,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01566,"mean_force":0.01118,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50015,0.03493,0.17281]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4303.0,"contact_point_centroid":[0.53139,0.07375,0.2369],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01287,"mean_force":0.01037,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53115,0.07374,0.23463]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2041.0,"contact_point_centroid":[0.49711,0.0347,0.19776],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.0105,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49687,0.0347,0.19551]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.56142,0.10636,0.25089],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01267,"mean_force":0.01005,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.56122,0.10635,0.2488]},{"body_a":"left_finger","body_b":"right_finger","contact_count":12.0,"contact_point_centroid":[0.56251,0.10637,0.25371],"force_p95":0.01083,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01083,"mean_force":0.01081,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56224,0.10635,0.25162]}],"total_contact_groups":13},"final_pose_error":0.01195,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.51251,0.03972,0.02602],"final_tcp_position":[0.62162,0.16837,0.27812],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":272932.95076,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":371.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1480.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50772,0.0352,0.18725],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16136,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":21.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":84.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.5065,0.03539,0.18221],"tcp_start":[0.50772,0.0352,0.18725],"tcp_to_object_dist_end":0.15637,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2139.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50015,0.03493,0.17281],"tcp_start":[0.5065,0.03539,0.18221],"tcp_to_object_dist_end":0.14739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":481.0,"n_steps_budget":600.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3965.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49675,0.03469,0.21891],"tcp_start":[0.50015,0.03493,0.17281],"tcp_to_object_dist_end":0.1936,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8303.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5622,0.1063,0.25165],"tcp_start":[0.49675,0.03469,0.21891],"tcp_to_object_dist_end":0.24044,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":272932.95076,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":24.0,"raw_peak_contact_force":0.12263,"subtask_id":"achieve_goal","tcp_end":[0.56236,0.10647,0.2515],"tcp_start":[0.5622,0.1063,0.25165],"tcp_to_object_dist_end":0.24038,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55806,0.10558,0.27361],"tcp_start":[0.56236,0.10647,0.2515],"tcp_to_object_dist_end":0.26022,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":775.0,"n_steps_budget":900.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3100.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62162,0.16837,0.27812],"tcp_start":[0.55806,0.10558,0.27361],"tcp_to_object_dist_end":0.30333,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a74f7c08b88460953bfa7e35b953cddf9278fdc17d2d4db8a2ea121b328e8b73`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81053,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_speed":0.13717,"approach_goal.goal_approach_speed":0.11385,"descend_place.place_force_threshold":7.58752,"descend_to_grasp.descend_force_threshold":9.82798,"grasp_object.grasp_duration":0.95762,"lift_object.lift_height":0.09637,"lift_object.lift_speed":0.10773,"release_object.release_duration":1.31215,"retract_from_goal.retract_height":0.1448,"retract_from_goal.retract_speed":0.10731},"optimized_scores":{"best_composite_score":-0.26469,"best_fitness_score":0.16531,"best_task_score":0.14469},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1436.0,"contact_point_centroid":[0.4827,0.04873,-0.00191],"force_p95":0.13523,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.49005,0.02077,0.24427]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47461,0.04292,0.17528]},{"body_a":"world","body_b":"grasp_target","contact_count":2072.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47069,0.04258,0.21495]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49802,0.09204,0.2855]},{"body_a":"world","body_b":"grasp_target","contact_count":28.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52455,0.13597,0.31315]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5224,0.13575,0.31514]},{"body_a":"world","body_b":"grasp_target","contact_count":2424.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.54897,0.17952,0.34824]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4805,0.04336,0.18527]},{"body_a":"left_finger","body_b":"right_finger","contact_count":328.0,"contact_point_centroid":[0.474,0.04285,0.1762],"force_p95":0.01477,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01887,"mean_force":0.01149,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47369,0.04284,0.17402]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2180.0,"contact_point_centroid":[0.47097,0.04259,0.21724],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01288,"mean_force":0.01058,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47069,0.04258,0.21497]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4239.0,"contact_point_centroid":[0.49846,0.09229,0.28793],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01051,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49816,0.09227,0.28565]},{"body_a":"left_finger","body_b":"right_finger","contact_count":28.0,"contact_point_centroid":[0.5248,0.13599,0.31524],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.01093,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52455,0.13597,0.31315]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.52407,0.13628,0.31225],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.00997,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52383,0.13626,0.31005]}],"total_contact_groups":13},"final_pose_error":0.01298,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.4827,0.04873,0.02602],"final_tcp_position":[0.57694,0.22246,0.36513],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273006.10244,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1436.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.48121,0.04314,0.18783],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":92.0,"raw_peak_contact_force":0.12262,"subtask_id":"reach_object","tcp_end":[0.47986,0.04337,0.18257],"tcp_start":[0.48121,0.04314,0.18783],"tcp_to_object_dist_end":0.15667,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2128.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47368,0.04284,0.17401],"tcp_start":[0.47986,0.04337,0.18257],"tcp_to_object_dist_end":0.14839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":518.0,"n_steps_budget":600.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":273006.10244,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4252.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47081,0.04258,0.25837],"tcp_start":[0.47368,0.04284,0.17401],"tcp_to_object_dist_end":0.23273,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8239.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52438,0.13576,0.31332],"tcp_start":[0.47081,0.04258,0.25837],"tcp_to_object_dist_end":0.30307,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":273005.26297,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":56.0,"raw_peak_contact_force":0.12263,"subtask_id":"achieve_goal","tcp_end":[0.52479,0.13634,0.31269],"tcp_start":[0.52438,0.13576,0.31332],"tcp_to_object_dist_end":0.3027,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52165,0.13547,0.33563],"tcp_start":[0.52479,0.13634,0.31269],"tcp_to_object_dist_end":0.32389,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":606.0,"n_steps_budget":690.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2424.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57694,0.22246,0.36513],"tcp_start":[0.52165,0.13547,0.33563],"tcp_to_object_dist_end":0.3925,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b1a72366a9c9a56aa2e80fc4399e157c8281abf492ab3c1ede02058762a86ed7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57143,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_speed":0.08858,"approach_goal.goal_approach_speed":0.05184,"descend_place.place_force_threshold":10.59333,"descend_to_grasp.descend_force_threshold":14.99056,"grasp_object.grasp_duration":1.18247,"lift_object.lift_height":0.12633,"lift_object.lift_speed":0.07189,"release_object.release_duration":0.949,"retract_from_goal.retract_height":0.15268,"retract_from_goal.retract_speed":0.06817},"optimized_scores":{"best_composite_score":-0.17468,"best_fitness_score":0.25532,"best_task_score":0.10965},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2553.0,"contact_point_centroid":[0.5155,-0.02534,-0.00208],"force_p95":0.14919,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.97499,"mean_force":0.12955,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51884,-0.02056,0.13081]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3597.0,"contact_point_centroid":[0.51985,-0.00202,0.06923],"force_p95":0.15252,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35609,"mean_force":0.09651,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5189,-0.02056,0.07309]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4198.0,"contact_point_centroid":[0.52003,-0.03874,0.07051],"force_p95":0.12766,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28107,"mean_force":0.08514,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51886,-0.02056,0.07436]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02129,-0.00206],"force_p95":0.14031,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18137,"mean_force":0.12701,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52412,-0.02067,0.05721]},{"body_a":"world","body_b":"grasp_target","contact_count":1588.0,"contact_point_centroid":[0.53702,-0.02132,-0.00191],"force_p95":0.13466,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.51361,-0.00929,0.24289]},{"body_a":"world","body_b":"grasp_target","contact_count":2684.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.529,-0.01998,0.11891]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51412,-0.02534,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52881,0.01534,0.19214]},{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.51412,-0.02534,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54003,0.04563,0.21439]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51412,-0.02534,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53646,0.04544,0.21718]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51412,-0.02534,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.55221,0.09276,0.26334]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2908.0,"contact_point_centroid":[0.52351,-0.00182,0.05229],"force_p95":0.09281,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10639,"mean_force":0.07092,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52294,-0.02065,0.05579]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3198.0,"contact_point_centroid":[0.52307,-0.03942,0.05269],"force_p95":0.08843,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08871,"mean_force":0.06501,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52294,-0.02065,0.05579]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2122.0,"contact_point_centroid":[0.51909,-0.02056,0.14418],"force_p95":0.01141,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01474,"mean_force":0.0106,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51872,-0.02055,0.14191]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4250.0,"contact_point_centroid":[0.5292,0.01546,0.19458],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01049,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52885,0.01546,0.19223]},{"body_a":"left_finger","body_b":"right_finger","contact_count":227.0,"contact_point_centroid":[0.53906,0.04572,0.21418],"force_p95":0.01089,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01091,"mean_force":0.00985,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5388,0.04572,0.21206]},{"body_a":"left_finger","body_b":"right_finger","contact_count":8.0,"contact_point_centroid":[0.54031,0.04563,0.21647],"force_p95":0.01088,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01088,"mean_force":0.01087,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54003,0.04563,0.21439]}],"total_contact_groups":16},"final_pose_error":0.1201,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.51412,-0.02534,0.01602],"final_tcp_position":[0.57074,0.13697,0.29216],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":272927.93772,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":398.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1588.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52975,-0.01904,0.18638],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16054,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":671.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2684.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53097,-0.02081,0.06545],"tcp_start":[0.52975,-0.01904,0.18638],"tcp_to_object_dist_end":0.03989,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53697,-0.0209,0.02579],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31653,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13933,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7906.0,"raw_peak_contact_force":0.18137,"tcp_end":[0.52291,-0.02065,0.05575],"tcp_start":[0.53097,-0.02081,0.06545],"tcp_to_object_dist_end":0.0331,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51412,-0.02534,0.01602],"object_pos_start":[0.53697,-0.0209,0.02579],"object_to_goal_dist_end":0.33157,"object_to_goal_dist_start":0.31653,"object_z_max":0.05823,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12470.0,"raw_peak_contact_force":0.97499,"tcp_end":[0.51902,-0.02056,0.17097],"tcp_start":[0.52291,-0.02065,0.05575],"tcp_to_object_dist_end":0.1551,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51412,-0.02534,0.01602],"object_pos_start":[0.51412,-0.02534,0.01602],"object_to_goal_dist_end":0.33157,"object_to_goal_dist_start":0.33157,"object_z_max":0.01602,"peak_contact_force":9748.89499,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8250.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54,0.0456,0.21438],"tcp_start":[0.51902,-0.02056,0.17097],"tcp_to_object_dist_end":0.21225,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.51412,-0.02534,0.01602],"object_pos_start":[0.51412,-0.02534,0.01602],"object_to_goal_dist_end":0.33157,"object_to_goal_dist_start":0.33157,"object_z_max":0.01602,"peak_contact_force":272927.93772,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16.0,"raw_peak_contact_force":0.12263,"subtask_id":"achieve_goal","tcp_end":[0.54005,0.04571,0.21437],"tcp_start":[0.54,0.0456,0.21438],"tcp_to_object_dist_end":0.21229,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51412,-0.02534,0.01602],"object_pos_start":[0.51412,-0.02534,0.01602],"object_to_goal_dist_end":0.33157,"object_to_goal_dist_start":0.33157,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53511,0.04529,0.23772],"tcp_start":[0.54005,0.04571,0.21437],"tcp_to_object_dist_end":0.23363,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51412,-0.02534,0.01602],"object_pos_start":[0.51412,-0.02534,0.01602],"object_to_goal_dist_end":0.33157,"object_to_goal_dist_start":0.33157,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57074,0.13697,0.29216],"tcp_start":[0.53511,0.04529,0.23772],"tcp_to_object_dist_end":0.32527,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```