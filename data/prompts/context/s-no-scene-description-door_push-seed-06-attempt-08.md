## Search State

- **Seed**: 6
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 4 | 0.0103 | 0.24 | ❌ rejected |
| 7 | approach → push | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | force_exceeded | pose_tolerance | 4 | 0.0009 | 0.03 | ❌ rejected |
| 6 | approach → push | arc_cartesian | linear_cartesian | force_threshold_switch | admittance_control | force_exceeded | pose_tolerance | 5 | 0.0778 | 0.33 | ❌ rejected |
| 5 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | -0.0106 | 0.32 | ❌ rejected |
| 4 | rotate → align → lift → push → approach → approach → descend → grasp | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_control | position_control | position_control | position_control | force_threshold_switch | position_control | admittance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.0355 | 0.42 | ✅ accepted |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: door_push
- target_hinge_angle: 0.524 rad (task success = realised hinge-angle delta ratio; not TCP proximity)
- Goal tolerance: 0.05 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 30.0 N
- Primary evaluation target: **hinge angle delta ratio (realised hinge motion / target_hinge_angle)**

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
| `object` | offset from object initial position | approach/contact targets near object |
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

## Current Skill (Q=0.010) — your mutation base

```yaml
skill: door_push
skill_type: arm_gripper
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
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
- id: approach_2
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp

```

## Design Metrics

- **Composite score**: 0.010
- **task_score** (E): 0.240
- **fitness_score**: 0.240  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 0.33 | 0.3589 |
| push_1 | 0.00 | 0.67 | 0.0006 |
| retract_1 | 1.00 | 0.33 | 0.0977 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.100, 0.399, 0.350)→(0.391, 0.401, 0.560) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 25.955 | 149.947 |
| push_1 | push | 0.00 / guard_failure | (0.391, 0.401, 0.560)→(0.391, 0.401, 0.560) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.000 | 4.790 | 4.478 |
| retract_1 | retract | 1.00 / step_budget | (0.391, 0.401, 0.560)→(0.357, 0.400, 0.468) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.333 | 0.000 | 42.626 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.369
- arc_quality: 0.333

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.369
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.369
- **Median Q (composite search score)**: -0.052
- **K-run variance**: 0.0084
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.449


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `60c29f30561fee2ce06b067ae52309dfc2791a8d10a0f8247d4f057dc1f7bbf4`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `34da519aca1008b6dc2cb922623d951e3d277879157a381e988a54565a8fccc4`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.09476,"approach_1.arc_height":0.16843,"push_1.push_distance":0.26616,"push_1.push_speed":0.07462},"optimized_scores":{"best_composite_score":-0.05157,"best_fitness_score":0.17843,"best_task_score":0.17843},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":44.0,"contact_point_centroid":[0.10074,0.17821,0.60555],"force_p95":64.32646,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.22476,"mean_force":38.59491,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.34758,0.40099,0.55986]},{"body_a":"door_panel","body_b":"link5","contact_count":3.0,"contact_point_centroid":[0.10225,0.15766,0.66441],"force_p95":8.55076,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.50084,"mean_force":3.16695,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.39279,0.40006,0.54637]},{"body_a":"world","body_b":"door_panel","contact_count":984.0,"contact_point_centroid":[0.3003,0.18571,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.21308,0.39943,0.50659]},{"body_a":"world","body_b":"door_panel","contact_count":212.0,"contact_point_centroid":[0.30222,0.16866,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.37716,0.40012,0.51003]}],"total_contact_groups":4},"final_pose_error":0.01968,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.35817,0.40052,0.46789],"hinge_angle":0.10682,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":75.22476,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1028.0,"raw_peak_contact_force":75.22476,"subtask_id":"reach_door","tcp_end":[0.39213,0.40079,0.54691],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.78327,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.93408,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"push_door","tcp_end":[0.39235,0.40046,0.54662],"tcp_start":[0.39213,0.40079,0.54691],"tcp_to_object_dist_end":0.78301,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":179.0,"n_steps_budget":690.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":215.0,"raw_peak_contact_force":9.50084,"tcp_end":[0.35817,0.40052,0.46789],"tcp_start":[0.39235,0.40046,0.54662],"tcp_to_object_dist_end":0.71248,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8ddc65539fcda71658f49649be9748aaabe492bbd016f1d18cf00d6d19f91cef`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.63415,"average_solve_count":82.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.11956,"approach_1.arc_height":0.19663,"push_1.push_distance":0.15388,"push_1.push_speed":0.08977},"optimized_scores":{"best_composite_score":-0.05714,"best_fitness_score":0.17286,"best_task_score":0.17286},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":36.0,"contact_point_centroid":[0.1016,0.16615,0.63552],"force_p95":78.28403,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":96.93726,"mean_force":49.60645,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3563,0.40093,0.58347]},{"body_a":"world","body_b":"door_panel","contact_count":924.0,"contact_point_centroid":[0.30073,0.18045,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.19562,0.39927,0.52002]},{"body_a":"world","body_b":"door_panel","contact_count":208.0,"contact_point_centroid":[0.30316,0.1632,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.37215,0.40043,0.51877]}],"total_contact_groups":3},"final_pose_error":0.01959,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.35607,0.40033,0.46862],"hinge_angle":0.13424,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":96.93726,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":960.0,"raw_peak_contact_force":96.93726,"subtask_id":"reach_door","tcp_end":[0.38761,0.40119,0.57233],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.79922,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"push_door","tcp_end":[0.38796,0.40104,0.57185],"tcp_start":[0.38761,0.40119,0.57233],"tcp_to_object_dist_end":0.79897,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":224.0,"n_steps_budget":810.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":208.0,"raw_peak_contact_force":0.0,"tcp_end":[0.35607,0.40033,0.46862],"tcp_start":[0.38796,0.40104,0.57185],"tcp_to_object_dist_end":0.7118,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ff14b28c151409e7d588c8444930f7538b4d5212a336dd723b958144baa5103b`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.66265,"average_solve_count":83.0,"average_success_count":83.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.11556,"approach_1.arc_height":0.18706,"push_1.push_distance":0.22288,"push_1.push_speed":0.04077},"optimized_scores":{"best_composite_score":0.13948,"best_fitness_score":0.36948,"best_task_score":0.36948},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":80.0,"contact_point_centroid":[0.10079,0.18727,0.59093],"force_p95":101.95877,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":277.67985,"mean_force":57.70301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.31951,0.40106,0.57801]},{"body_a":"door_panel","body_b":"link4","contact_count":11.0,"contact_point_centroid":[0.10382,0.14689,0.68787],"force_p95":59.18881,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":118.37761,"mean_force":10.7616,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.39302,0.40016,0.55983]},{"body_a":"door_panel","body_b":"link4","contact_count":1.0,"contact_point_centroid":[0.10352,0.14816,0.6886],"force_p95":13.43476,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.43476,"mean_force":13.43476,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.39217,0.40138,0.56179]},{"body_a":"world","body_b":"door_panel","contact_count":1028.0,"contact_point_centroid":[0.30006,0.19604,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.2014,0.3995,0.51433]},{"body_a":"world","body_b":"door_panel","contact_count":228.0,"contact_point_centroid":[0.30312,0.16341,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.3771,0.40058,0.51895]}],"total_contact_groups":5},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.35739,0.40047,0.46848],"hinge_angle":0.13321,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":277.67985,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":77.86509,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1108.0,"raw_peak_contact_force":277.67985,"subtask_id":"reach_door","tcp_end":[0.39217,0.40138,0.56179],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.79405,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.43476,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":13.43476,"subtask_id":"push_door","tcp_end":[0.39251,0.40109,0.56139],"tcp_start":[0.39217,0.40138,0.56179],"tcp_to_object_dist_end":0.79379,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":204.0,"n_steps_budget":750.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":239.0,"raw_peak_contact_force":118.37761,"tcp_end":[0.35739,0.40047,0.46848],"tcp_start":[0.39251,0.40109,0.56139],"tcp_to_object_dist_end":0.71244,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```