## Search State

- **Seed**: 6
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.0194 | 0.20 | ❌ rejected |
| 2 | rotate → align → lift → push → approach → approach → descend → grasp | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_control | position_control | position_control | position_control | force_threshold_switch | position_control | admittance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.0354 | 0.42 | ❌ rejected |
| 1 | approach → push | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | force_exceeded | pose_tolerance | 4 | 0.3000 | 0.00 | ❌ rejected |
| 0 | rotate → align → lift → push → approach → approach → descend → grasp | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_control | position_control | position_control | position_control | force_threshold_switch | position_control | admittance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.0354 | 0.42 | ✅ accepted |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.019) — your mutation base

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

- **Composite score**: 0.019
- **task_score** (E): 0.199
- **fitness_score**: 0.199  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.180

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 0.00 | 1.00 | 0.1663 |
| push_door | 0.00 | 1.00 | 0.0001 |
| retract_1 | 1.00 | 0.33 | 0.1926 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 0.00 / step_budget | (0.100, 0.399, 0.350)→(0.240, 0.310, 0.359) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 5.333 | 208.571 | 451.289 |
| push_door | push | 0.00 / guard_failure | (0.240, 0.310, 0.359)→(0.240, 0.311, 0.359) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 348.182 | 488.761 |
| retract_1 | retract | 1.00 / step_budget | (0.240, 0.311, 0.359)→(0.113, 0.192, 0.440) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.333 | 0.000 | 36.686 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.315
- arc_quality: 0.333

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.315
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.315
- **Median Q (composite search score)**: -0.016
- **K-run variance**: 0.0070
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Parameters at lower bound**: approach_handle.approach_offset_x
- **Final σ (mean)**: 0.402


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.08247,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_offset_x":0.30159,"push_door.push_distance":0.41469,"push_door.push_speed":0.08404},"optimized_scores":{"best_composite_score":-0.01646,"best_fitness_score":0.16354,"best_task_score":0.16354},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":3.0,"contact_point_centroid":[0.10086,0.16945,0.63183],"force_p95":555.73354,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":559.70681,"mean_force":513.28164,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.22307,0.31768,0.35744]},{"body_a":"door_panel","body_b":"link5","contact_count":766.0,"contact_point_centroid":[0.1011,0.16642,0.62982],"force_p95":434.47958,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":451.77877,"mean_force":416.7167,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.20526,0.32141,0.35228]},{"body_a":"door_panel","body_b":"link7","contact_count":47.0,"contact_point_centroid":[0.11524,0.17346,0.47674],"force_p95":29.8775,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.05151,"mean_force":17.22918,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.12312,0.20557,0.43112]},{"body_a":"door_panel","body_b":"link5","contact_count":4.0,"contact_point_centroid":[0.10078,0.16977,0.63176],"force_p95":24.41453,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.45603,"mean_force":9.82551,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.22265,0.31777,0.35738]},{"body_a":"door_panel","body_b":"link6","contact_count":13.0,"contact_point_centroid":[0.10021,0.1872,0.52214],"force_p95":19.83991,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.88921,"mean_force":13.37211,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.15503,0.24153,0.40653]},{"body_a":"world","body_b":"door_panel","contact_count":1004.0,"contact_point_centroid":[0.3004,0.18402,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.19102,0.33167,0.35141]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30034,0.18465,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.22312,0.31759,0.35742]},{"body_a":"world","body_b":"door_panel","contact_count":444.0,"contact_point_centroid":[0.3006,0.1821,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.16571,0.25352,0.3986]}],"total_contact_groups":8},"final_pose_error":0.01964,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.11148,0.19248,0.44009],"hinge_angle":0.09902,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":559.70681,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":420.65377,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1770.0,"raw_peak_contact_force":451.77877,"subtask_id":"reach_handle","tcp_end":[0.22312,0.31759,0.35742],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.52763,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":213.18713,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":7.0,"raw_peak_contact_force":559.70681,"subtask_id":"push_door","tcp_end":[0.22284,0.3179,0.35746],"tcp_start":[0.223,0.31778,0.35746],"tcp_to_object_dist_end":0.52773,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":434.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":508.0,"raw_peak_contact_force":31.05151,"tcp_end":[0.11148,0.19248,0.44009],"tcp_start":[0.22284,0.3179,0.35746],"tcp_to_object_dist_end":0.49311,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8ddc65539fcda71658f49649be9748aaabe492bbd016f1d18cf00d6d19f91cef`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.08333,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_offset_x":0.3,"push_door.push_distance":0.41327,"push_door.push_speed":0.07857},"optimized_scores":{"best_composite_score":-0.06016,"best_fitness_score":0.11984,"best_task_score":0.11984},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":3.0,"contact_point_centroid":[0.10326,0.15011,0.64107],"force_p95":536.17368,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":539.36611,"mean_force":501.02251,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.23442,0.30567,0.36765]},{"body_a":"door_panel","body_b":"link5","contact_count":765.0,"contact_point_centroid":[0.10234,0.1578,0.6341],"force_p95":478.97903,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":510.33423,"mean_force":441.19934,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.20832,0.31786,0.35492]},{"body_a":"door_panel","body_b":"link5","contact_count":4.0,"contact_point_centroid":[0.10324,0.15019,0.64108],"force_p95":29.86062,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.80035,"mean_force":10.33395,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.23404,0.30572,0.36764]},{"body_a":"world","body_b":"door_panel","contact_count":932.0,"contact_point_centroid":[0.30134,0.17521,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.19204,0.33,0.35352]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30228,0.16827,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.23444,0.30562,0.36759]},{"body_a":"world","body_b":"door_panel","contact_count":464.0,"contact_point_centroid":[0.30223,0.16858,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.17646,0.25147,0.40121]}],"total_contact_groups":6},"final_pose_error":0.01962,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.11279,0.19168,0.44077],"hinge_angle":0.10646,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":539.36611,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":204.2389,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1697.0,"raw_peak_contact_force":510.33423,"subtask_id":"reach_handle","tcp_end":[0.23444,0.30562,0.36759],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.53244,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":539.36611,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":7.0,"raw_peak_contact_force":539.36611,"subtask_id":"push_door","tcp_end":[0.23423,0.30581,0.36774],"tcp_start":[0.23437,0.30573,0.3677],"tcp_to_object_dist_end":0.53256,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":421.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":468.0,"raw_peak_contact_force":33.80035,"tcp_end":[0.11279,0.19168,0.44077],"tcp_start":[0.23423,0.30581,0.36774],"tcp_to_object_dist_end":0.4937,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ff14b28c151409e7d588c8444930f7538b4d5212a336dd723b958144baa5103b`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.07767,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_offset_x":0.33693,"push_door.push_distance":0.34531,"push_door.push_speed":0.05388},"optimized_scores":{"best_composite_score":0.1347,"best_fitness_score":0.3147,"best_task_score":0.3147},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":721.0,"contact_point_centroid":[0.09983,0.21222,0.60589],"force_p95":367.13787,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":391.75363,"mean_force":338.29994,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.23428,0.31462,0.35119]},{"body_a":"door_panel","body_b":"link5","contact_count":3.0,"contact_point_centroid":[0.10059,0.22785,0.5868],"force_p95":361.47234,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":367.20985,"mean_force":323.01264,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.26212,0.30791,0.35221]},{"body_a":"door_panel","body_b":"link6","contact_count":95.0,"contact_point_centroid":[0.20779,0.23354,0.488],"force_p95":106.21661,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":139.35432,"mean_force":88.65217,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.26003,0.30642,0.35179]},{"body_a":"door_panel","body_b":"link6","contact_count":110.0,"contact_point_centroid":[0.15201,0.2039,0.50713],"force_p95":40.96218,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.20552,"mean_force":22.23875,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.20922,0.26602,0.3819]},{"body_a":"door_panel","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.11579,0.16593,0.48058],"force_p95":31.58791,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.72922,"mean_force":19.227,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.12288,0.19781,0.43467]},{"body_a":"door_panel","body_b":"link5","contact_count":5.0,"contact_point_centroid":[0.10055,0.22795,0.58685],"force_p95":3.92195,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.90244,"mean_force":0.98049,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.2619,0.30773,0.35214]},{"body_a":"world","body_b":"door_panel","contact_count":1000.0,"contact_point_centroid":[0.29985,0.205,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.21029,0.32915,0.35028]},{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.20925,0.23476,0.48805],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.26212,0.30787,0.3522]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30023,0.21382,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.26212,0.30787,0.3522]},{"body_a":"world","body_b":"door_panel","contact_count":480.0,"contact_point_centroid":[0.30053,0.1885,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.18984,0.25069,0.39381]}],"total_contact_groups":10},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.11365,0.19055,0.44037],"hinge_angle":0.1045,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":391.75363,"phases":[{"contact_detected":true,"contact_event_count":6.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.81898,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1816.0,"raw_peak_contact_force":391.75363,"subtask_id":"reach_handle","tcp_end":[0.26212,0.30787,0.3522],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.53622,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":291.99328,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":367.20985,"subtask_id":"push_door","tcp_end":[0.26206,0.30791,0.35219],"tcp_start":[0.26211,0.30793,0.35221],"tcp_to_object_dist_end":0.53621,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":485.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":618.0,"raw_peak_contact_force":45.20552,"tcp_end":[0.11365,0.19055,0.44037],"tcp_start":[0.26206,0.30791,0.35219],"tcp_to_object_dist_end":0.4931,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```