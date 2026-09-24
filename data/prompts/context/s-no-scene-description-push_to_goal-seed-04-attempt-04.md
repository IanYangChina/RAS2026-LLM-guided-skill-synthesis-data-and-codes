## Search State

- **Seed**: 4
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → push | linear_cartesian | linear_cartesian | position_control | admittance_control | pose_tolerance | pose_tolerance | 7 | -0.2633 | 0.00 | ❌ rejected |
| 3 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4198 | 0.80 | ✅ accepted |
| 2 | approach → push | linear_cartesian | linear_cartesian | position_control | admittance_control | pose_tolerance | time_limit | 5 | -0.1282 | 0.00 | ❌ rejected |
| 1 | approach → push | linear_cartesian | linear_cartesian | position_control | admittance_control | pose_tolerance | time_limit | 3 | -0.1228 | 0.00 | ❌ rejected |
| 0 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4172 | 0.80 | ✅ accepted |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.263) — your mutation base

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

- **Composite score**: -0.263
- **task_score** (E): 0.001
- **fitness_score**: 0.087  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.350

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| behind_1 | 1.00 | 1.00 | 0.2466 |
| push_1 | 0.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| behind_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.528, 0.015, 0.058) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_1 | push | 0.00 / guard_failure | (0.522, -0.004, 0.052)→(0.522, -0.004, 0.052) | (0.531, 0.007, 0.025)→(0.531, 0.006, 0.025) | 0.161→0.161 | 1.00 / 2.333 | 11.021 | 52.104 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.001
- lateral_force_integral: None
- approach_alignment: 0.565
- goal_progress: 0.001
- terminal_score: 0.001
- phase_score: 0.169
- phase_breakdown.behind_object_score: 0.488
- phase_breakdown.push_to_goal_score: 0.089

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.102
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: -0.267
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at lower bound**: behind_1.behind_distance
- **Final σ (mean)**: 0.312


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74648,"average_solve_count":71.0,"average_success_count":71.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"behind_1.approach_speed":0.09285,"behind_1.behind_distance":0.01027,"push_1.contact_force_threshold":4.83547,"push_1.push_distance":0.21011,"push_1.push_speed":0.03591,"push_1.retry_offset_x":-0.01199,"push_1.retry_offset_y":-0.01977},"optimized_scores":{"best_composite_score":-0.26656,"best_fitness_score":0.08344,"best_task_score":0.00028},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.55429,-0.00353,0.04993],"force_p95":62.06399,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.6674,"mean_force":41.58081,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54254,-0.0036,0.05234]},{"body_a":"world","body_b":"push_box","contact_count":172.0,"contact_point_centroid":[0.55317,0.00078,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.19402,"mean_force":0.9679,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54614,0.00453,0.05439]},{"body_a":"world","body_b":"push_box","contact_count":3304.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"behind_1","phase_type":"approach","tcp_position_centroid":[0.52378,0.00511,0.17801]}],"total_contact_groups":3},"final_pose_error":0.36287,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55327,0.00128,0.025],"final_tcp_position":[0.54234,-0.00414,0.05219],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":65.6674,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":826.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"behind_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3304.0,"raw_peak_contact_force":0.24534,"subtask_id":"behind_object","tcp_end":[0.54973,0.01033,0.0571],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.03351,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":44.0,"n_steps_budget":1000.0,"object_pos_end":[0.55316,0.00133,0.02501],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.1604,"object_to_goal_dist_start":0.16043,"object_z_max":0.02502,"peak_contact_force":29.82581,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":175.0,"raw_peak_contact_force":65.6674,"subtask_id":"push_to_goal","tcp_end":[0.54234,-0.00414,0.05219],"tcp_start":[0.54241,-0.00393,0.05227],"tcp_to_object_dist_end":0.02977,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `452b4d03bf1b69f7d6475210c4cc0fbd85197208ecbf5594cd2cfcf54c82bcbb`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44792,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"behind_1.approach_speed":0.06526,"behind_1.behind_distance":0.01043,"push_1.contact_force_threshold":2.14452,"push_1.push_distance":0.2226,"push_1.push_speed":0.06535,"push_1.retry_offset_x":0.00391,"push_1.retry_offset_y":0.00085},"optimized_scores":{"best_composite_score":-0.27518,"best_fitness_score":0.07482,"best_task_score":0.00045},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.53844,0.0259,0.04996],"force_p95":55.39397,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.36805,"mean_force":36.25094,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5267,0.02566,0.05239]},{"body_a":"world","body_b":"push_box","contact_count":208.0,"contact_point_centroid":[0.5366,0.03647,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.31259,"mean_force":0.76935,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52954,0.03628,0.05456]},{"body_a":"world","body_b":"push_box","contact_count":3448.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"behind_1","phase_type":"approach","tcp_position_centroid":[0.51529,0.02197,0.17825]}],"total_contact_groups":3},"final_pose_error":0.40051,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53666,0.03685,0.02503],"final_tcp_position":[0.52657,0.02507,0.05227],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":58.36805,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":862.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"behind_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3448.0,"raw_peak_contact_force":0.24534,"subtask_id":"behind_object","tcp_end":[0.53277,0.04439,0.05753],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":53.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03692,0.02502],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.19047,"object_to_goal_dist_start":0.1905,"object_z_max":0.02504,"peak_contact_force":1.64503,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":211.0,"raw_peak_contact_force":58.36805,"subtask_id":"push_to_goal","tcp_end":[0.52657,0.02507,0.05227],"tcp_start":[0.52661,0.02531,0.05233],"tcp_to_object_dist_end":0.03136,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e3aaa9b30183e782395a479a1824f41a69a2557638e862a63e7a5368dd2a464a`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68,"average_solve_count":75.0,"average_success_count":75.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"behind_1.approach_speed":0.09082,"behind_1.behind_distance":0.01,"push_1.contact_force_threshold":2.28289,"push_1.push_distance":0.12146,"push_1.push_speed":0.0604,"push_1.retry_offset_x":-0.00335,"push_1.retry_offset_y":-0.00052},"optimized_scores":{"best_composite_score":-0.2482,"best_fitness_score":0.1018,"best_task_score":0.00086},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":264.0,"contact_point_centroid":[0.50458,-0.01919,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.27724,"mean_force":0.54005,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49897,-0.01888,0.05528]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.5095,-0.03172,0.04995],"force_p95":31.7058,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.18211,"mean_force":25.83643,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49776,-0.0318,0.05237]},{"body_a":"world","body_b":"push_box","contact_count":3072.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"behind_1","phase_type":"approach","tcp_position_centroid":[0.49962,-0.00412,0.17937]}],"total_contact_groups":3},"final_pose_error":0.24058,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50453,-0.01892,0.02506],"final_tcp_position":[0.4977,-0.03236,0.05226],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":32.27724,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":768.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"behind_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3072.0,"raw_peak_contact_force":0.24534,"subtask_id":"behind_object","tcp_end":[0.50094,-0.00835,0.0591],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.03586,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":67.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01885,0.02502],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13123,"object_to_goal_dist_start":0.13127,"object_z_max":0.02506,"peak_contact_force":1.59255,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":267.0,"raw_peak_contact_force":32.27724,"subtask_id":"push_to_goal","tcp_end":[0.4977,-0.03236,0.05226],"tcp_start":[0.49774,-0.03214,0.05232],"tcp_to_object_dist_end":0.03118,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```