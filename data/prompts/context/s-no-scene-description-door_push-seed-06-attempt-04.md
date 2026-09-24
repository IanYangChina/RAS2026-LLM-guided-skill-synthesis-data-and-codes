## Search State

- **Seed**: 6
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | rotate → align → lift → push → approach → approach → descend → grasp | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_control | position_control | position_control | position_control | force_threshold_switch | position_control | admittance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.0355 | 0.42 | ✅ accepted |
| 3 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.0194 | 0.20 | ❌ rejected |
| 2 | rotate → align → lift → push → approach → approach → descend → grasp | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_control | position_control | position_control | position_control | force_threshold_switch | position_control | admittance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.0354 | 0.42 | ❌ rejected |
| 1 | approach → push | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | force_exceeded | pose_tolerance | 4 | 0.3000 | 0.00 | ❌ rejected |
| 0 | rotate → align → lift → push → approach → approach → descend → grasp | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_control | position_control | position_control | position_control | force_threshold_switch | position_control | admittance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.0354 | 0.42 | ✅ accepted |

**Proposal policy**: task_score is 0.42 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.035) — your mutation base

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

- **Composite score**: 0.035
- **task_score** (E): 0.415
- **fitness_score**: 0.415  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_1 | 1.00 | 1.00 | 0.1656 |
| align_1 | 1.00 | 1.00 | 0.0439 |
| lift_1 | 1.00 | 0.00 | 0.1402 |
| push_1 | 1.00 | 1.00 | 0.1305 |
| approach_1 | 1.00 | 0.33 | 0.0014 |
| approach_2 | 1.00 | 0.67 | 0.0011 |
| descend_1 | 1.00 | 1.00 | 0.0010 |
| grasp_1 | 1.00 | 1.00 | 0.0034 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 1.00 / time_limit | (0.100, 0.399, 0.350)→(0.100, 0.234, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 7.248 | 28.025 |
| align_1 | align | 1.00 / step_budget | (0.100, 0.234, 0.348)→(0.100, 0.190, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.667 | 9.957 | 22.677 |
| lift_1 | lift | 1.00 / step_budget | (0.100, 0.190, 0.348)→(-0.040, 0.180, 0.349) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.00 / 0.000 | 0.000 | 0.000 |
| push_1 | push | 1.00 / step_budget | (-0.040, 0.180, 0.349)→(0.090, 0.179, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.000 | 8.523 | 17.772 |
| approach_1 | approach | 1.00 / step_budget | (0.090, 0.179, 0.348)→(0.092, 0.179, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 0.000 | 17.390 |
| approach_2 | approach | 1.00 / step_budget | (0.092, 0.179, 0.348)→(0.093, 0.179, 0.349) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.000 | 2.502 | 16.205 |
| descend_1 | descend | 1.00 / step_budget | (0.093, 0.179, 0.349)→(0.094, 0.178, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.667 | 9.221 | 16.608 |
| grasp_1 | grasp | 1.00 / step_budget | (0.094, 0.178, 0.348)→(0.093, 0.176, 0.346) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 0.665 | 18.657 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.528
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.528
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.528
- **Median Q (composite search score)**: 0.008
- **K-run variance**: 0.0069
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.407


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.93088,"average_solve_count":217.0,"average_success_count":217.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00103,"approach_2.speed":0.06286,"push_1.push_depth":0.06025,"push_1.push_speed":0.04123},"optimized_scores":{"best_composite_score":0.00781,"best_fitness_score":0.38781,"best_task_score":0.38781},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":111.0,"contact_point_centroid":[0.15154,0.18634,0.39435],"force_p95":14.51121,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.12765,"mean_force":11.38894,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.09964,0.24368,0.34812]},{"body_a":"door_panel","body_b":"link7","contact_count":155.0,"contact_point_centroid":[0.14843,0.15442,0.39707],"force_p95":20.9881,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.05979,"mean_force":13.85532,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.09962,0.21201,0.34778]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.13704,0.1237,0.40214],"force_p95":19.02934,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.02934,"mean_force":19.02934,"phase_index":4.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09029,0.17897,0.34834]},{"body_a":"door_panel","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.13856,0.12301,0.40198],"force_p95":18.06589,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.83951,"mean_force":14.81097,"phase_index":5.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.09204,0.17858,0.34845]},{"body_a":"door_panel","body_b":"link7","contact_count":388.0,"contact_point_centroid":[0.14003,0.121,0.39855],"force_p95":4.27384,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.45251,"mean_force":1.6085,"phase_index":7.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.09331,0.17645,0.34583]},{"body_a":"door_panel","body_b":"link7","contact_count":49.0,"contact_point_centroid":[0.12585,0.12608,0.4022],"force_p95":17.69077,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.99515,"mean_force":13.67052,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.07753,0.17892,0.34824]},{"body_a":"door_panel","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.13949,0.12259,0.40167],"force_p95":12.86419,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.91334,"mean_force":12.4524,"phase_index":6.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.09315,0.17836,0.34823]},{"body_a":"world","body_b":"door_panel","contact_count":948.0,"contact_point_centroid":[0.30019,0.18682,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.09958,0.31715,0.34786]},{"body_a":"world","body_b":"door_panel","contact_count":188.0,"contact_point_centroid":[0.30307,0.16441,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.09962,0.21193,0.34779]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.14622,0.13187,0.39946],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.09974,0.18971,0.34822]},{"body_a":"world","body_b":"door_panel","contact_count":672.0,"contact_point_centroid":[0.30546,0.15252,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.02855,0.18415,0.34772]},{"body_a":"world","body_b":"door_panel","contact_count":604.0,"contact_point_centroid":[0.30533,0.15307,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.02218,0.17896,0.34794]},{"body_a":"world","body_b":"door_panel","contact_count":16.0,"contact_point_centroid":[0.30641,0.14877,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09083,0.17879,0.34833]},{"body_a":"world","body_b":"door_panel","contact_count":8.0,"contact_point_centroid":[0.3065,0.14846,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":5.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.09239,0.17853,0.34848]},{"body_a":"world","body_b":"door_panel","contact_count":24.0,"contact_point_centroid":[0.30655,0.14826,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":6.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.09303,0.17838,0.34827]},{"body_a":"world","body_b":"door_panel","contact_count":484.0,"contact_point_centroid":[0.30678,0.1474,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":7.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.09332,0.17654,0.34594]}],"total_contact_groups":16},"final_pose_error":0.00679,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09367,0.17835,0.34818],"hinge_angle":0.21654,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":28.12765,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1059.0,"raw_peak_contact_force":28.12765,"tcp_end":[0.09966,0.23369,0.34823],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.43105,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":195.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.84191,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":343.0,"raw_peak_contact_force":23.05979,"tcp_end":[0.09975,0.18975,0.34824],"tcp_start":[0.09966,0.23369,0.34823],"tcp_to_object_dist_end":0.40894,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":624.0,"n_steps_budget":960.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":674.0,"raw_peak_contact_force":0.0,"tcp_end":[-0.04012,0.17972,0.3486],"tcp_start":[0.09975,0.18975,0.34824],"tcp_to_object_dist_end":0.39424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":643.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.73521,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":653.0,"raw_peak_contact_force":17.99515,"tcp_end":[0.09029,0.17897,0.34834],"tcp_start":[-0.04012,0.17972,0.3486],"tcp_to_object_dist_end":0.4019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17.0,"raw_peak_contact_force":19.02934,"tcp_end":[0.09163,0.17873,0.34846],"tcp_start":[0.09029,0.17897,0.34834],"tcp_to_object_dist_end":0.4022,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12.0,"raw_peak_contact_force":18.83951,"tcp_end":[0.09274,0.17855,0.34852],"tcp_start":[0.09163,0.17873,0.34846],"tcp_to_object_dist_end":0.40243,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":11.93741,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":28.0,"raw_peak_contact_force":12.91334,"tcp_end":[0.09367,0.17835,0.34818],"tcp_start":[0.09274,0.17855,0.34852],"tcp_to_object_dist_end":0.40226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.6664,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":872.0,"raw_peak_contact_force":18.45251,"tcp_end":[0.09326,0.17622,0.34554],"tcp_start":[0.09367,0.17835,0.34818],"tcp_to_object_dist_end":0.39894,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8ddc65539fcda71658f49649be9748aaabe492bbd016f1d18cf00d6d19f91cef`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.76707,"average_solve_count":249.0,"average_success_count":249.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00284,"approach_2.speed":0.06388,"push_1.push_depth":0.04229,"push_1.push_speed":0.02825},"optimized_scores":{"best_composite_score":-0.04995,"best_fitness_score":0.33005,"best_task_score":0.33005},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":54.0,"contact_point_centroid":[0.15107,0.18129,0.39489],"force_p95":12.9588,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.47176,"mean_force":11.63241,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.09967,0.23866,0.34815]},{"body_a":"door_panel","body_b":"link7","contact_count":158.0,"contact_point_centroid":[0.14842,0.1542,0.39709],"force_p95":20.9601,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.48502,"mean_force":13.82642,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.09963,0.21178,0.34778]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.13944,0.12258,0.40197],"force_p95":18.33051,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.62093,"mean_force":15.60544,"phase_index":6.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.09326,0.17841,0.34827]},{"body_a":"door_panel","body_b":"link7","contact_count":384.0,"contact_point_centroid":[0.14004,0.12096,0.39851],"force_p95":4.21855,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.4445,"mean_force":1.54968,"phase_index":7.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.09332,0.17642,0.34578]},{"body_a":"door_panel","body_b":"link7","contact_count":52.0,"contact_point_centroid":[0.12513,0.12623,0.40223],"force_p95":16.94667,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.50713,"mean_force":13.36973,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.0767,0.17891,0.34823]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.13835,0.12304,0.40193],"force_p95":15.97086,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.24125,"mean_force":13.94434,"phase_index":5.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.09183,0.1786,0.34834]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.13741,0.12338,0.40206],"force_p95":14.18324,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.22307,"mean_force":13.76343,"phase_index":4.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09076,0.17874,0.34827]},{"body_a":"world","body_b":"door_panel","contact_count":928.0,"contact_point_centroid":[0.30062,0.18136,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.09958,0.317,0.34785]},{"body_a":"world","body_b":"door_panel","contact_count":260.0,"contact_point_centroid":[0.30311,0.16423,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.09964,0.21156,0.3478]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.14622,0.13187,0.39948],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.09974,0.18971,0.34823]},{"body_a":"world","body_b":"door_panel","contact_count":660.0,"contact_point_centroid":[0.30548,0.15244,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.02951,0.18422,0.34771]},{"body_a":"world","body_b":"door_panel","contact_count":644.0,"contact_point_centroid":[0.30533,0.15309,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.02578,0.17892,0.34794]},{"body_a":"world","body_b":"door_panel","contact_count":8.0,"contact_point_centroid":[0.30639,0.14888,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09081,0.17884,0.34837]},{"body_a":"world","body_b":"door_panel","contact_count":20.0,"contact_point_centroid":[0.30647,0.14855,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":5.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.09194,0.1786,0.34838]},{"body_a":"world","body_b":"door_panel","contact_count":20.0,"contact_point_centroid":[0.30655,0.14826,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":6.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.09292,0.17845,0.34833]},{"body_a":"world","body_b":"door_panel","contact_count":444.0,"contact_point_centroid":[0.30678,0.1474,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":7.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.09335,0.17659,0.34599]}],"total_contact_groups":16},"final_pose_error":0.00677,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09369,0.17834,0.34817],"hinge_angle":0.21661,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":26.47176,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":10.88851,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":982.0,"raw_peak_contact_force":26.47176,"tcp_end":[0.09967,0.23365,0.34822],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.43102,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":195.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.43953,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":418.0,"raw_peak_contact_force":23.48502,"tcp_end":[0.09975,0.18975,0.34826],"tcp_start":[0.09967,0.23365,0.34822],"tcp_to_object_dist_end":0.40895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":624.0,"n_steps_budget":960.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":662.0,"raw_peak_contact_force":0.0,"tcp_end":[-0.04012,0.17972,0.3486],"tcp_start":[0.09975,0.18975,0.34826],"tcp_to_object_dist_end":0.39425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":668.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":696.0,"raw_peak_contact_force":17.50713,"tcp_end":[0.09036,0.17895,0.34834],"tcp_start":[-0.04012,0.17972,0.3486],"tcp_to_object_dist_end":0.40191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11.0,"raw_peak_contact_force":14.22307,"tcp_end":[0.09167,0.17873,0.34845],"tcp_start":[0.09036,0.17895,0.34834],"tcp_to_object_dist_end":0.4022,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":7.50456,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23.0,"raw_peak_contact_force":16.24125,"tcp_end":[0.09271,0.17856,0.34849],"tcp_start":[0.09167,0.17873,0.34845],"tcp_to_object_dist_end":0.40239,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":9.28552,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":23.0,"raw_peak_contact_force":18.62093,"tcp_end":[0.09369,0.17834,0.34817],"tcp_start":[0.09271,0.17856,0.34849],"tcp_to_object_dist_end":0.40226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.66646,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":828.0,"raw_peak_contact_force":18.4445,"tcp_end":[0.09328,0.17621,0.34552],"tcp_start":[0.09369,0.17834,0.34817],"tcp_to_object_dist_end":0.39892,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ff14b28c151409e7d588c8444930f7538b4d5212a336dd723b958144baa5103b`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.9148,"average_solve_count":223.0,"average_success_count":223.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00614,"approach_2.speed":0.06004,"push_1.push_depth":0.07012,"push_1.push_speed":0.03809},"optimized_scores":{"best_composite_score":0.1485,"best_fitness_score":0.5285,"best_task_score":0.5285},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":238.0,"contact_point_centroid":[0.15119,0.19754,0.39264],"force_p95":15.52933,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.47479,"mean_force":11.5905,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.09953,0.25485,0.34796]},{"body_a":"door_panel","body_b":"link7","contact_count":154.0,"contact_point_centroid":[0.14844,0.15463,0.39703],"force_p95":21.0387,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.4867,"mean_force":13.84823,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.0996,0.21221,0.34775]},{"body_a":"door_panel","body_b":"link6","contact_count":30.0,"contact_point_centroid":[0.10066,0.22184,0.4715],"force_p95":18.14545,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.76337,"mean_force":10.22841,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.09954,0.27698,0.34789]},{"body_a":"door_panel","body_b":"link7","contact_count":394.0,"contact_point_centroid":[0.14005,0.12102,0.39858],"force_p95":4.85759,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.0754,"mean_force":1.66329,"phase_index":7.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.09332,0.17648,0.34586]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.1371,0.12369,0.40213],"force_p95":18.91771,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.91771,"mean_force":18.91771,"phase_index":4.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09035,0.17898,0.34834]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.13922,0.12286,0.40178],"force_p95":18.29078,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.29078,"mean_force":18.29078,"phase_index":6.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.09273,0.17854,0.3485]},{"body_a":"door_panel","body_b":"link7","contact_count":55.0,"contact_point_centroid":[0.12541,0.12617,0.40221],"force_p95":16.9319,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.81303,"mean_force":13.18252,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.07704,0.17893,0.34824]},{"body_a":"door_panel","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.13844,0.12303,0.40197],"force_p95":13.44687,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.53382,"mean_force":12.24606,"phase_index":5.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.09193,0.17859,0.34837]},{"body_a":"world","body_b":"door_panel","contact_count":1092.0,"contact_point_centroid":[0.29988,0.19827,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.09955,0.31463,0.34783]},{"body_a":"world","body_b":"door_panel","contact_count":216.0,"contact_point_centroid":[0.30317,0.16381,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.09961,0.21085,0.34777]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.14622,0.13187,0.39945],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.09973,0.18971,0.34821]},{"body_a":"world","body_b":"door_panel","contact_count":624.0,"contact_point_centroid":[0.30547,0.15248,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.03248,0.1844,0.34765]},{"body_a":"world","body_b":"door_panel","contact_count":716.0,"contact_point_centroid":[0.30534,0.15302,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.02672,0.17893,0.34793]},{"body_a":"world","body_b":"door_panel","contact_count":20.0,"contact_point_centroid":[0.30642,0.14876,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09054,0.17883,0.34826]},{"body_a":"world","body_b":"door_panel","contact_count":16.0,"contact_point_centroid":[0.30646,0.1486,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":5.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.09191,0.17862,0.34837]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30658,0.14814,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":6.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.09314,0.17834,0.3482]}],"total_contact_groups":17},"final_pose_error":0.00678,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09368,0.17834,0.34817],"hinge_angle":0.21654,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":29.47479,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":10.8555,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1360.0,"raw_peak_contact_force":29.47479,"tcp_end":[0.09964,0.23369,0.3482],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.43102,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":195.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":4.58839,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":370.0,"raw_peak_contact_force":21.4867,"tcp_end":[0.09974,0.18975,0.34823],"tcp_start":[0.09964,0.23369,0.3482],"tcp_to_object_dist_end":0.40893,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":624.0,"n_steps_budget":960.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":626.0,"raw_peak_contact_force":0.0,"tcp_end":[-0.04012,0.17972,0.3486],"tcp_start":[0.09974,0.18975,0.34823],"tcp_to_object_dist_end":0.39424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":645.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.83514,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":771.0,"raw_peak_contact_force":17.81303,"tcp_end":[0.09035,0.17898,0.34834],"tcp_start":[-0.04012,0.17972,0.3486],"tcp_to_object_dist_end":0.40192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21.0,"raw_peak_contact_force":18.91771,"tcp_end":[0.09168,0.17873,0.34846],"tcp_start":[0.09035,0.17898,0.34834],"tcp_to_object_dist_end":0.40221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22.0,"raw_peak_contact_force":13.53382,"tcp_end":[0.09273,0.17854,0.3485],"tcp_start":[0.09168,0.17873,0.34846],"tcp_to_object_dist_end":0.40241,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":6.43977,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":18.29078,"tcp_end":[0.09368,0.17834,0.34817],"tcp_start":[0.09273,0.17854,0.3485],"tcp_to_object_dist_end":0.40225,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.66197,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":790.0,"raw_peak_contact_force":19.0754,"tcp_end":[0.09327,0.17623,0.34555],"tcp_start":[0.09368,0.17834,0.34817],"tcp_to_object_dist_end":0.39895,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```