## Search State

- **Seed**: 4
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4187 | 0.80 | ❌ rejected |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 6 | -0.2283 | 0.00 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | force_exceeded | 8 | -0.3614 | 0.00 | ❌ rejected |
| 7 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 8 | -0.3071 | 0.04 | ❌ rejected |
| 6 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | -0.0059 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.80 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: push_to_goal
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Primary evaluation target: **object displacement ratio toward goal_object_position**

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

## Current Skill (Q=0.419) — your mutation base

```yaml
skill: push_to_goal
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
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
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
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

```

## Design Metrics

- **Composite score**: 0.419
- **task_score** (E): 0.796
- **fitness_score**: 0.445  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| push_1 | 1.00 | 1.00 | 0.1910 |
| align_1 | 1.00 | 1.00 | 0.1697 |
| release_1 | 0.33 | 1.00 | 0.1671 |
| insert_1 | 1.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| push_1 | push | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.496, -0.057, 0.120) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| align_1 | align | 1.00 / step_budget | (0.496, -0.057, 0.120)→(0.527, 0.079, 0.027) | (0.531, 0.007, 0.025)→(0.534, 0.017, 0.028) | 0.161→0.171 | 1.00 / 3.667 | 24.790 | 68.965 |
| release_1 | release | 0.33 / step_budget | (0.527, 0.079, 0.027)→(0.505, -0.086, 0.021) | (0.534, 0.017, 0.028)→(0.524, -0.130, 0.025) | 0.171→0.035 | 1.00 / 4.667 | 20.113 | 111.941 |
| insert_1 | insert | 1.00 / force_exceeded | (0.505, -0.086, 0.021)→(0.505, -0.086, 0.021) | (0.524, -0.130, 0.025)→(0.524, -0.130, 0.025) | 0.035→0.035 | 1.00 / 4.667 | 37.096 | 37.096 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.688
- goal_progress: 0.943
- terminal_score: 0.943
- phase_score: 0.215
- phase_breakdown.approach_score: 0.821
- phase_breakdown.contact_score: 0.000
- phase_breakdown.push_score: 0.101

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.506
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.943
- **Median Q (composite search score)**: 0.408
- **K-run variance**: 0.0021
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.257


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8d5a7e825d9524a0954b44a69bda19e1d764760f64bb1262d03aec3c389fadbb`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c4094dd933e0897d422d7ea261a82b80810f7dec183b19c1da5b940157e7d0c4`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75385,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00038,"align_1.lateral_offset_y":0.00402,"insert_1.insertion_depth":0.07588,"insert_1.insertion_force":10.65125,"push_1.push_distance":0.04648,"push_1.push_speed":0.06957},"optimized_scores":{"best_composite_score":0.40753,"best_fitness_score":0.4342,"best_task_score":0.77838},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2257.0,"contact_point_centroid":[0.55491,-0.05573,-0.00016],"force_p95":59.28926,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":86.92498,"mean_force":20.2948,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.526,-0.00932,0.02099]},{"body_a":"push_box","body_b":"link7","contact_count":1077.0,"contact_point_centroid":[0.56058,-0.04855,0.04967],"force_p95":57.48733,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.8611,"mean_force":36.02134,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.522,-0.02923,0.02124]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54558,-0.1123,0.0491],"force_p95":47.7651,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.7651,"mean_force":47.7651,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50851,-0.09317,0.02103]},{"body_a":"attachment","body_b":"push_box","contact_count":870.0,"contact_point_centroid":[0.52888,-0.05557,0.03778],"force_p95":40.55606,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.73555,"mean_force":13.8568,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51892,-0.04505,0.02156]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.53174,-0.13444,-0.00015],"force_p95":27.5099,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.60778,"mean_force":14.39103,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50851,-0.09317,0.02103]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.53197,0.02637,0.04998],"force_p95":18.05894,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.06881,"mean_force":17.81558,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52682,0.03702,0.05199]},{"body_a":"world","body_b":"push_box","contact_count":2753.0,"contact_point_centroid":[0.55317,0.00139,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.45696,"mean_force":0.26507,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52034,0.02361,0.06235]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.53033,-0.1013,0.04947],"force_p95":12.44356,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.44356,"mean_force":12.44356,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50851,-0.09317,0.02103]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49719,-0.01534,0.20211]}],"total_contact_groups":9},"final_pose_error":0.0576,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5319,-0.1343,0.02469],"final_tcp_position":[0.50851,-0.09317,0.02102],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":86.92498,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49638,-0.03071,0.10749],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10516,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":689.0,"n_steps_budget":960.0,"object_pos_end":[0.55319,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2756.0,"raw_peak_contact_force":18.06881,"tcp_end":[0.54574,0.07496,0.02343],"tcp_start":[0.49638,-0.03071,0.10749],"tcp_to_object_dist_end":0.07399,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5319,-0.1343,0.02469],"object_pos_start":[0.55319,0.00136,0.02499],"object_to_goal_dist_end":0.03555,"object_to_goal_dist_start":0.16043,"object_z_max":0.02953,"peak_contact_force":35.09363,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4204.0,"raw_peak_contact_force":86.92498,"tcp_end":[0.50851,-0.09317,0.02103],"tcp_start":[0.54574,0.07496,0.02343],"tcp_to_object_dist_end":0.04745,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.5319,-0.1343,0.02469],"object_pos_start":[0.5319,-0.1343,0.02469],"object_to_goal_dist_end":0.03555,"object_to_goal_dist_start":0.03555,"object_z_max":0.02469,"peak_contact_force":47.7651,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":6.0,"raw_peak_contact_force":47.7651,"tcp_end":[0.50851,-0.09317,0.02102],"tcp_start":[0.50851,-0.09317,0.02103],"tcp_to_object_dist_end":0.04746,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `452b4d03bf1b69f7d6475210c4cc0fbd85197208ecbf5594cd2cfcf54c82bcbb`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90769,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00289,"align_1.lateral_offset_y":0.00824,"insert_1.insertion_depth":0.0194,"insert_1.insertion_force":19.30428,"push_1.push_distance":0.16179,"push_1.push_speed":0.08745},"optimized_scores":{"best_composite_score":0.36902,"best_fitness_score":0.39569,"best_task_score":0.6677},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":245.0,"contact_point_centroid":[0.53594,0.06958,0.04631],"force_p95":155.45284,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":188.58067,"mean_force":104.84729,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52846,0.0767,0.04835]},{"body_a":"attachment","body_b":"push_box","contact_count":912.0,"contact_point_centroid":[0.53385,0.0305,0.03487],"force_p95":158.0217,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":167.64709,"mean_force":117.30733,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5296,0.04064,0.03567]},{"body_a":"world","body_b":"push_box","contact_count":3153.0,"contact_point_centroid":[0.53717,0.04096,-8e-05],"force_p95":65.6216,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":150.25697,"mean_force":9.11558,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51031,0.00435,0.08202]},{"body_a":"world","body_b":"push_box","contact_count":2432.0,"contact_point_centroid":[0.5388,-0.02301,-0.00043],"force_p95":107.06454,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":120.45766,"mean_force":60.03947,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52596,0.02369,0.03317]},{"body_a":"push_box","body_b":"link7","contact_count":1050.0,"contact_point_centroid":[0.56214,-9e-05,0.06719],"force_p95":73.03899,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":86.30198,"mean_force":48.02674,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52814,0.03495,0.03449]},{"body_a":"push_box","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.56785,0.07397,0.06703],"force_p95":77.56916,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.62916,"mean_force":64.31563,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53399,0.10648,0.03432]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55333,-0.07206,0.04973],"force_p95":32.29364,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.29364,"mean_force":32.29364,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5099,-0.04945,0.02252]},{"body_a":"world","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.54497,-0.08994,-5e-05],"force_p95":20.60232,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.22024,"mean_force":11.14226,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5099,-0.04945,0.02252]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49726,-0.03801,0.21175]}],"total_contact_groups":9},"final_pose_error":0.10107,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53773,-0.09917,0.02493],"final_tcp_position":[0.5099,-0.04945,0.0225],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":188.58067,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49652,-0.07531,0.12861],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15795,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":921.0,"n_steps_budget":1000.0,"object_pos_end":[0.54296,0.06715,0.03275],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.22149,"object_to_goal_dist_start":0.1905,"object_z_max":0.03485,"peak_contact_force":73.88093,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3431.0,"raw_peak_contact_force":188.58067,"tcp_end":[0.53513,0.11024,0.03208],"tcp_start":[0.49652,-0.07531,0.12861],"tcp_to_object_dist_end":0.0438,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53773,-0.09917,0.02493],"object_pos_start":[0.54296,0.06715,0.03275],"object_to_goal_dist_end":0.0633,"object_to_goal_dist_start":0.22149,"object_z_max":0.03447,"peak_contact_force":6.6427,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4394.0,"raw_peak_contact_force":167.64709,"tcp_end":[0.5099,-0.04945,0.02252],"tcp_start":[0.53513,0.11024,0.03208],"tcp_to_object_dist_end":0.05703,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":660.0,"object_pos_end":[0.53773,-0.09917,0.02493],"object_pos_start":[0.53773,-0.09917,0.02493],"object_to_goal_dist_end":0.0633,"object_to_goal_dist_start":0.0633,"object_z_max":0.02493,"peak_contact_force":32.29364,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":32.29364,"tcp_end":[0.5099,-0.04945,0.0225],"tcp_start":[0.5099,-0.04945,0.02252],"tcp_to_object_dist_end":0.05704,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e3aaa9b30183e782395a479a1824f41a69a2557638e862a63e7a5368dd2a464a`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89683,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00205,"align_1.lateral_offset_y":-0.0011,"insert_1.insertion_depth":0.07443,"insert_1.insertion_force":12.43569,"push_1.push_distance":0.08624,"push_1.push_speed":0.07472},"optimized_scores":{"best_composite_score":0.47957,"best_fitness_score":0.50623,"best_task_score":0.94331},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2236.0,"contact_point_centroid":[0.51389,-0.0895,-0.00013],"force_p95":62.13612,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":81.25129,"mean_force":21.37616,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.4982,-0.03504,0.02284]},{"body_a":"attachment","body_b":"push_box","contact_count":958.0,"contact_point_centroid":[0.51699,-0.07052,0.05091],"force_p95":64.49395,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.65967,"mean_force":34.92826,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49879,-0.06015,0.02305]},{"body_a":"push_box","body_b":"link7","contact_count":944.0,"contact_point_centroid":[0.52619,-0.0812,0.05493],"force_p95":51.05281,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.52023,"mean_force":34.75963,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49883,-0.06098,0.02307]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52367,-0.14117,0.05182],"force_p95":31.22913,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.22913,"mean_force":31.22913,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.4972,-0.11427,0.01954]},{"body_a":"world","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.51242,-0.17751,-0.00015],"force_p95":24.70029,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.58018,"mean_force":16.7813,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.4972,-0.11427,0.01954]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.51686,-0.1256,0.05344],"force_p95":14.92411,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.92411,"mean_force":14.92411,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.4972,-0.11427,0.01954]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49724,-0.03294,0.20924]},{"body_a":"world","body_b":"push_box","contact_count":2400.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4968,-0.00617,0.07241]}],"total_contact_groups":8},"final_pose_error":0.03626,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50318,-0.15654,0.0266],"final_tcp_position":[0.49718,-0.11426,0.01951],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":81.25129,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49651,-0.06557,0.12285],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10876,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":600.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2400.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49985,0.05265,0.02627],"tcp_start":[0.49651,-0.06557,0.12285],"tcp_to_object_dist_end":0.07163,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50319,-0.15653,0.02662],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00744,"object_to_goal_dist_start":0.13127,"object_z_max":0.03312,"peak_contact_force":18.60261,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4138.0,"raw_peak_contact_force":81.25129,"tcp_end":[0.4972,-0.11427,0.01954],"tcp_start":[0.49985,0.05265,0.02627],"tcp_to_object_dist_end":0.04326,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50318,-0.15654,0.0266],"object_pos_start":[0.50319,-0.15653,0.02662],"object_to_goal_dist_end":0.00744,"object_to_goal_dist_start":0.00744,"object_z_max":0.02662,"peak_contact_force":31.22913,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":31.22913,"tcp_end":[0.49718,-0.11426,0.01951],"tcp_start":[0.4972,-0.11427,0.01954],"tcp_to_object_dist_end":0.04328,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```