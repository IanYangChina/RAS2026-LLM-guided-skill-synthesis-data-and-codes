## Search State

- **Seed**: 6
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2877 | 0.23 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | admittance_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 15 | -0.7858 | 0.17 | ❌ rejected |
| 3 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1415 | 0.25 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1266 | 0.20 | ❌ rejected |
| 1 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1417 | 0.25 | ❌ rejected |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.288) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
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
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
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
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    yaw_angle:
      type: angle
      range:
      - 0.1
      - 1.57

```

## Design Metrics

- **Composite score**: -0.288
- **task_score** (E): 0.228
- **fitness_score**: 0.592  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_pre_grasp | 1.00 | 1.00 | 0.1236 |
| descend_to_grasp | 1.00 | 1.00 | 0.1639 |
| grasp_object | 0.00 | 1.00 | 0.0000 |
| lift_object | 0.00 | 1.00 | 0.0958 |
| transport_to_goal | 0.00 | 1.00 | 0.1052 |
| descend_to_place | 0.00 | 1.00 | 0.1361 |
| release_object | 1.00 | 1.00 | 0.0238 |
| retract_after_place | 0.00 | 1.00 | 0.0831 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_pre_grasp | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.029, 0.184) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.029, 0.184)→(0.495, 0.024, 0.020) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.333 | 8.709 | 0.128 |
| grasp_object | grasp | 0.00 / guard_failure | (0.490, 0.024, 0.015)→(0.490, 0.024, 0.015) | (0.500, 0.024, 0.026)→(0.499, 0.024, 0.025) | 0.271→0.272 | 1.00 / 44.667 | 0.157 | 0.310 |
| lift_object | lift | 0.00 / step_budget | (0.490, 0.024, 0.015)→(0.489, 0.024, 0.111) | (0.499, 0.024, 0.025)→(0.501, 0.024, 0.113) | 0.272→0.224 | 1.00 / 41.333 | 0.072 | 0.909 |
| transport_to_goal | approach | 0.00 / step_budget | (0.489, 0.024, 0.111)→(0.476, 0.006, 0.213) | (0.501, 0.024, 0.113)→(0.492, 0.006, 0.204) | 0.224→0.224 | 1.00 / 35.000 | 0.092 | 0.105 |
| descend_to_place | descend | 0.00 / step_budget | (0.476, 0.006, 0.213)→(0.543, 0.113, 0.172) | (0.492, 0.006, 0.204)→(0.527, 0.087, 0.049) | 0.224→0.209 | 1.00 / 14.333 | 6499.168 | 1.311 |
| release_object | release | 1.00 / step_budget | (0.543, 0.113, 0.172)→(0.538, 0.111, 0.195) | (0.527, 0.087, 0.049)→(0.524, 0.086, 0.016) | 0.209→0.234 | 1.00 / 4.000 | 0.117 | 0.441 |
| retract_after_place | retract | 0.00 / step_budget | (0.538, 0.111, 0.195)→(0.559, 0.143, 0.269) | (0.524, 0.086, 0.016)→(0.524, 0.086, 0.016) | 0.234→0.234 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.369
- phase_score: 0.231
- phase_breakdown.reach_retract_score: 0.047
- phase_breakdown.reach_lift_score: 0.104
- phase_breakdown.reach_pre_grasp_score: 0.821
- phase_breakdown.reach_place_score: 0.015
- phase_breakdown.reach_grasp_score: 0.486
- grasp_place_fitness: 0.665

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.665
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.369
- **Median Q (composite search score)**: -0.319
- **K-run variance**: 0.0026
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.363


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `daf90631fcbaf423e19452d0c9b90b9715013985cc94ef12ca0cd881e96195aa`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `94660347aa4f41f6801e53bd449f8df59691da8bebfa4fef4947a3513fe04781`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94118,"average_solve_count":357.0,"average_success_count":357.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_grasp.arc_height":0.05708,"approach_pre_grasp.speed":0.03672,"descend_to_grasp.descend_z":-0.01678,"descend_to_grasp.speed":0.02897,"descend_to_place.place_z_offset":-0.03921,"descend_to_place.speed":0.02268,"grasp_object.grasp_duration":0.49492,"lift_object.lift_height":0.2868,"lift_object.speed":0.05624,"release_object.release_duration":0.31648,"retract_after_place.retract_z":0.29879,"retract_after_place.speed":0.05615,"transport_to_goal.arc_height":0.11971,"transport_to_goal.speed":0.03973},"optimized_scores":{"best_composite_score":-0.32916,"best_fitness_score":0.55084,"best_task_score":0.14943},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1604.0,"contact_point_centroid":[0.50828,0.04171,-0.00265],"force_p95":0.29829,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.919,"mean_force":0.15241,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.52055,0.05717,0.20376]},{"body_a":"world","body_b":"grasp_target","contact_count":247.0,"contact_point_centroid":[0.49978,-0.01499,-0.00148],"force_p95":0.65551,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.97851,"mean_force":0.13762,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49168,-0.01489,0.01476]},{"body_a":"grasp_target","body_b":"hand","contact_count":451.0,"contact_point_centroid":[0.51126,-0.01693,0.05287],"force_p95":0.15581,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50541,"mean_force":0.14293,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49416,-0.01493,0.01287]},{"body_a":"grasp_target","body_b":"hand","contact_count":1000.0,"contact_point_centroid":[0.49635,-0.01552,0.0984],"force_p95":0.14595,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39694,"mean_force":0.06839,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49082,-0.01485,0.05866]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.50331,-0.01523,-0.00261],"force_p95":0.18879,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24886,"mean_force":0.16412,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49416,-0.01493,0.01287]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.49102,0.00428,0.06057],"force_p95":0.07113,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24775,"mean_force":0.04977,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49082,-0.01485,0.05866]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.49103,-0.03399,0.06053],"force_p95":0.07197,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24704,"mean_force":0.0498,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49082,-0.01485,0.05866]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5835.0,"contact_point_centroid":[0.49037,-0.02428,0.20314],"force_p95":0.13397,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23797,"mean_force":0.08884,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.49055,-0.00547,0.20546]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7118.0,"contact_point_centroid":[0.49138,0.01402,0.20258],"force_p95":0.11129,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13946,"mean_force":0.07544,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.491,-0.00448,0.20541]},{"body_a":"world","body_b":"grasp_target","contact_count":2232.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13898,"mean_force":0.12264,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49791,-0.01137,0.09603]},{"body_a":"world","body_b":"grasp_target","contact_count":2744.0,"contact_point_centroid":[0.50382,-0.01567,-0.00195],"force_p95":0.12911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.49902,0.02603,0.23201]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50817,0.04173,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52686,0.07725,0.20639]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50817,0.04173,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.53233,0.09355,0.27018]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19404.0,"contact_point_centroid":[0.48159,-0.01168,0.1567],"force_p95":0.07866,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10997,"mean_force":0.05344,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48103,-0.03081,0.15535]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20371.0,"contact_point_centroid":[0.48131,-0.0502,0.15784],"force_p95":0.07697,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10115,"mean_force":0.05161,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48089,-0.0311,0.15675]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5944.0,"contact_point_centroid":[0.49389,-0.03415,0.01428],"force_p95":0.0689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09416,"mean_force":0.04566,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49371,-0.01492,0.0124]}],"total_contact_groups":21},"final_pose_error":0.24924,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.50817,0.04173,0.01602],"final_tcp_position":[0.54136,0.10912,0.31473],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9748.76313,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":687.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2744.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.50004,-0.00789,0.17512],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14935,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":558.0,"n_steps_budget":1000.0,"object_pos_end":[0.50381,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31224,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13898,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2233.0,"raw_peak_contact_force":0.13898,"subtask_id":"reach_grasp","tcp_end":[0.49874,-0.01497,0.0177],"tcp_start":[0.50004,-0.00789,0.17512],"tcp_to_object_dist_end":0.00977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50253,-0.01496,0.02456],"object_pos_start":[0.50381,-0.01567,0.02602],"object_to_goal_dist_end":0.31316,"object_to_goal_dist_start":0.31224,"object_z_max":0.02602,"peak_contact_force":0.17517,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13964.0,"raw_peak_contact_force":0.50541,"tcp_end":[0.49368,-0.01491,0.01237],"tcp_start":[0.49368,-0.01491,0.01237],"tcp_to_object_dist_end":0.01506,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50342,-0.01486,0.11048],"object_pos_start":[0.50256,-0.01496,0.02455],"object_to_goal_dist_end":0.25854,"object_to_goal_dist_start":0.31315,"object_z_max":0.1104,"peak_contact_force":0.07216,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41247.0,"raw_peak_contact_force":0.97851,"subtask_id":"reach_lift","tcp_end":[0.4923,-0.01485,0.10525],"tcp_start":[0.49368,-0.01491,0.01237],"tcp_to_object_dist_end":0.0123,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49782,-0.0364,0.20234],"object_pos_start":[0.50342,-0.01486,0.11048],"object_to_goal_dist_end":0.24524,"object_to_goal_dist_start":0.25854,"object_z_max":0.20223,"peak_contact_force":0.08108,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39981.0,"raw_peak_contact_force":0.10997,"subtask_id":"reach_place","tcp_end":[0.4785,-0.03661,0.21051],"tcp_start":[0.4923,-0.01485,0.10525],"tcp_to_object_dist_end":0.02098,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50817,0.04173,0.01602],"object_pos_start":[0.49782,-0.0364,0.20234],"object_to_goal_dist_end":0.28514,"object_to_goal_dist_start":0.24524,"object_z_max":0.20237,"peak_contact_force":9748.76313,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16004.0,"raw_peak_contact_force":1.919,"tcp_end":[0.53053,0.07766,0.20337],"tcp_start":[0.4785,-0.03661,0.21051],"tcp_to_object_dist_end":0.19208,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50817,0.04173,0.01602],"object_pos_start":[0.50817,0.04173,0.01602],"object_to_goal_dist_end":0.28514,"object_to_goal_dist_start":0.28514,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52548,0.077,0.22701],"tcp_start":[0.53053,0.07766,0.20337],"tcp_to_object_dist_end":0.21462,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50817,0.04173,0.01602],"object_pos_start":[0.50817,0.04173,0.01602],"object_to_goal_dist_end":0.28514,"object_to_goal_dist_start":0.28514,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_retract","tcp_end":[0.54136,0.10912,0.31473],"tcp_start":[0.52548,0.077,0.22701],"tcp_to_object_dist_end":0.30801,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96571,"average_solve_count":350.0,"average_success_count":350.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_grasp.arc_height":0.20281,"approach_pre_grasp.speed":0.07706,"descend_to_grasp.descend_z":-0.0103,"descend_to_grasp.speed":0.01277,"descend_to_place.place_z_offset":-0.03689,"descend_to_place.speed":0.02034,"grasp_object.grasp_duration":0.27563,"lift_object.lift_height":0.21751,"lift_object.speed":0.06067,"release_object.release_duration":0.10481,"retract_after_place.retract_z":0.15617,"retract_after_place.speed":0.03297,"transport_to_goal.arc_height":0.20279,"transport_to_goal.speed":0.04473},"optimized_scores":{"best_composite_score":-0.21546,"best_fitness_score":0.66454,"best_task_score":0.36855},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":282.0,"contact_point_centroid":[0.57048,0.12216,-0.00507],"force_p95":0.79087,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.07676,"mean_force":0.24141,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57112,0.12238,0.14403]},{"body_a":"world","body_b":"grasp_target","contact_count":188.0,"contact_point_centroid":[0.50902,0.0387,-0.00118],"force_p95":0.63222,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.82172,"mean_force":0.12056,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50063,0.0389,0.02036]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20520.0,"contact_point_centroid":[0.5003,0.05787,0.06982],"force_p95":0.07202,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30051,"mean_force":0.0499,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50034,0.0387,0.06811]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20868.0,"contact_point_centroid":[0.50028,0.01955,0.0706],"force_p95":0.07124,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27034,"mean_force":0.04876,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50036,0.0387,0.06872]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5125,0.03946,-0.00206],"force_p95":0.13789,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19574,"mean_force":0.12789,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50276,0.03909,0.01923]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":866.0,"contact_point_centroid":[0.57528,0.14217,0.12659],"force_p95":0.09191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16612,"mean_force":0.05981,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57559,0.12349,0.12958]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":749.0,"contact_point_centroid":[0.57426,0.1046,0.12694],"force_p95":0.1039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15747,"mean_force":0.06708,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57556,0.12348,0.12953]},{"body_a":"world","body_b":"grasp_target","contact_count":1648.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.50225,0.02914,0.24901]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16767.0,"contact_point_centroid":[0.53746,0.06216,0.16283],"force_p95":0.08742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12956,"mean_force":0.05773,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53678,0.08103,0.163]},{"body_a":"grasp_target","body_b":"hand","contact_count":43.0,"contact_point_centroid":[0.51744,0.05873,0.05913],"force_p95":0.00943,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12936,"mean_force":0.00971,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5,0.03884,0.02147]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.57067,0.12215,-0.00198],"force_p95":0.12281,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12426,"mean_force":0.12252,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.57904,0.13178,0.17749]},{"body_a":"world","body_b":"grasp_target","contact_count":2284.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50601,0.0405,0.1056]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15617.0,"contact_point_centroid":[0.54163,0.10373,0.16013],"force_p95":0.09215,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11597,"mean_force":0.06162,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54032,0.08478,0.16032]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20293.0,"contact_point_centroid":[0.49576,0.05383,0.15962],"force_p95":0.0715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10316,"mean_force":0.05014,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49543,0.03464,0.15834]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5800.0,"contact_point_centroid":[0.50249,0.01989,0.02069],"force_p95":0.06954,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10025,"mean_force":0.04492,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5023,0.03906,0.01874]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5924.0,"contact_point_centroid":[0.50247,0.05828,0.02059],"force_p95":0.06989,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09433,"mean_force":0.04521,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5023,0.03906,0.01874]}],"total_contact_groups":17},"final_pose_error":0.11201,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.57067,0.12215,0.01602],"final_tcp_position":[0.58855,0.14013,0.20133],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.07676,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":413.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1648.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.50767,0.04174,0.18837],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16244,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":571.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2284.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50736,0.03948,0.02428],"tcp_start":[0.50767,0.04174,0.18837],"tcp_to_object_dist_end":0.00545,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51237,0.03905,0.02581],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21283,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.13509,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13528.0,"raw_peak_contact_force":0.19574,"tcp_end":[0.50227,0.03905,0.01872],"tcp_start":[0.50228,0.03905,0.01872],"tcp_to_object_dist_end":0.01233,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51574,0.03872,0.11592],"object_pos_start":[0.51236,0.03905,0.02582],"object_to_goal_dist_end":0.17679,"object_to_goal_dist_start":0.21283,"object_z_max":0.11582,"peak_contact_force":0.07239,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41619.0,"raw_peak_contact_force":0.82172,"subtask_id":"reach_lift","tcp_end":[0.50267,0.03871,0.11736],"tcp_start":[0.50227,0.03905,0.01872],"tcp_to_object_dist_end":0.01316,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50812,0.03811,0.18729],"object_pos_start":[0.51574,0.03872,0.11592],"object_to_goal_dist_end":0.18472,"object_to_goal_dist_start":0.17679,"object_z_max":0.18721,"peak_contact_force":0.09574,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":41462.0,"raw_peak_contact_force":0.10316,"subtask_id":"reach_place","tcp_end":[0.49848,0.03779,0.19848],"tcp_start":[0.50267,0.03871,0.11736],"tcp_to_object_dist_end":0.01477,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58094,0.12355,0.1138],"object_pos_start":[0.50812,0.03811,0.18729],"object_to_goal_dist_end":0.07448,"object_to_goal_dist_start":0.18472,"object_z_max":0.18731,"peak_contact_force":0.10234,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":32384.0,"raw_peak_contact_force":0.12956,"tcp_end":[0.57745,0.12377,0.13271],"tcp_start":[0.49848,0.03779,0.19848],"tcp_to_object_dist_end":0.01923,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57068,0.12214,0.01637],"object_pos_start":[0.58094,0.12355,0.1138],"object_to_goal_dist_end":0.14942,"object_to_goal_dist_start":0.07448,"object_z_max":0.1138,"peak_contact_force":0.10517,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1897.0,"raw_peak_contact_force":1.07676,"tcp_end":[0.57102,0.12236,0.15455],"tcp_start":[0.57745,0.12377,0.13271],"tcp_to_object_dist_end":0.13817,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57067,0.12215,0.01602],"object_pos_start":[0.57068,0.12214,0.01637],"object_to_goal_dist_end":0.14973,"object_to_goal_dist_start":0.14942,"object_z_max":0.01649,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12426,"subtask_id":"reach_retract","tcp_end":[0.58855,0.14013,0.20133],"tcp_start":[0.57102,0.12236,0.15455],"tcp_to_object_dist_end":0.18704,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0989,"average_solve_count":364.0,"average_success_count":364.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_grasp.arc_height":0.15547,"approach_pre_grasp.speed":0.04174,"descend_to_grasp.descend_z":-0.01547,"descend_to_grasp.speed":0.02129,"descend_to_place.place_z_offset":-0.07749,"descend_to_place.speed":0.02319,"grasp_object.grasp_duration":0.45514,"lift_object.lift_height":0.20483,"lift_object.speed":0.05778,"release_object.release_duration":0.19837,"retract_after_place.retract_z":0.16293,"retract_after_place.speed":0.06308,"transport_to_goal.arc_height":0.21895,"transport_to_goal.speed":0.06544},"optimized_scores":{"best_composite_score":-0.3186,"best_fitness_score":0.5614,"best_task_score":0.1669},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1637.0,"contact_point_centroid":[0.49238,0.09428,-0.00262],"force_p95":0.29354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.88473,"mean_force":0.15315,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.50815,0.11403,0.1883]},{"body_a":"world","body_b":"grasp_target","contact_count":215.0,"contact_point_centroid":[0.47905,0.04813,-0.00134],"force_p95":0.69981,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.92818,"mean_force":0.12206,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47146,0.04783,0.0164]},{"body_a":"grasp_target","body_b":"hand","contact_count":525.0,"contact_point_centroid":[0.48291,0.04247,0.07915],"force_p95":0.10622,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38945,"mean_force":0.05529,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47027,0.04763,0.04028]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5662.0,"contact_point_centroid":[0.46728,0.02851,0.21173],"force_p95":0.135,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28113,"mean_force":0.08995,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.46753,0.04735,0.214]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.47127,0.06678,0.06395],"force_p95":0.07237,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26494,"mean_force":0.05006,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47109,0.04763,0.06214]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.4713,0.02851,0.06411],"force_p95":0.0719,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23467,"mean_force":0.04982,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47109,0.04763,0.06214]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.48238,0.04827,-0.0024],"force_p95":0.16595,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22831,"mean_force":0.15038,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47365,0.04807,0.01466]},{"body_a":"grasp_target","body_b":"hand","contact_count":443.0,"contact_point_centroid":[0.49062,0.05511,0.05388],"force_p95":0.10465,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17328,"mean_force":0.09522,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47358,0.04807,0.01459]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6962.0,"contact_point_centroid":[0.46848,0.06686,0.21052],"force_p95":0.11161,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15057,"mean_force":0.07594,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.46815,0.04839,0.21357]},{"body_a":"world","body_b":"grasp_target","contact_count":1864.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.49123,0.03661,0.25304]},{"body_a":"world","body_b":"grasp_target","contact_count":2384.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47833,0.05026,0.1034]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49225,0.09433,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.51793,0.13532,0.18288]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49225,0.09433,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.53029,0.15796,0.24553]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20330.0,"contact_point_centroid":[0.45596,0.04318,0.16924],"force_p95":0.07588,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10279,"mean_force":0.0514,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.4555,0.02404,0.1681]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20176.0,"contact_point_centroid":[0.45572,0.00464,0.17012],"force_p95":0.07604,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09961,"mean_force":0.05156,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.45533,0.02377,0.16882]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5924.0,"contact_point_centroid":[0.47337,0.06726,0.01605],"force_p95":0.06877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09668,"mean_force":0.04555,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47321,0.04803,0.01422]}],"total_contact_groups":19},"final_pose_error":0.1203,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.49225,0.09433,0.01602],"final_tcp_position":[0.54602,0.18006,0.28946],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9748.63989,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":467.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1864.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.48152,0.05226,0.1892],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":596.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":25.86654,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2384.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.47804,0.04853,0.01915],"tcp_start":[0.48152,0.05226,0.1892],"tcp_to_object_dist_end":0.0083,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48183,0.04811,0.02501],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29137,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.1605,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13954.0,"raw_peak_contact_force":0.22831,"tcp_end":[0.47319,0.04803,0.0142],"tcp_start":[0.47319,0.04803,0.0142],"tcp_to_object_dist_end":0.01385,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48394,0.0477,0.11365],"object_pos_start":[0.48185,0.04811,0.02501],"object_to_goal_dist_end":0.23677,"object_to_goal_dist_start":0.29137,"object_z_max":0.11356,"peak_contact_force":0.07277,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40740.0,"raw_peak_contact_force":0.92818,"subtask_id":"reach_lift","tcp_end":[0.47309,0.04767,0.11007],"tcp_start":[0.47319,0.04803,0.0142],"tcp_to_object_dist_end":0.01143,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46981,0.01578,0.22129],"object_pos_start":[0.48394,0.0477,0.11365],"object_to_goal_dist_end":0.24092,"object_to_goal_dist_start":0.23677,"object_z_max":0.22121,"peak_contact_force":0.09961,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40506.0,"raw_peak_contact_force":0.10279,"subtask_id":"reach_place","tcp_end":[0.45085,0.01584,0.22998],"tcp_start":[0.47309,0.04767,0.11007],"tcp_to_object_dist_end":0.02086,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49225,0.09433,0.01602],"object_pos_start":[0.46981,0.01578,0.22129],"object_to_goal_dist_end":0.26856,"object_to_goal_dist_start":0.24092,"object_z_max":0.2213,"peak_contact_force":9748.63989,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":15734.0,"raw_peak_contact_force":1.88473,"tcp_end":[0.5218,0.1362,0.17989],"tcp_start":[0.45085,0.01584,0.22998],"tcp_to_object_dist_end":0.17169,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49225,0.09433,0.01602],"object_pos_start":[0.49225,0.09433,0.01602],"object_to_goal_dist_end":0.26856,"object_to_goal_dist_start":0.26856,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51647,0.1349,0.20354],"tcp_start":[0.5218,0.1362,0.17989],"tcp_to_object_dist_end":0.19339,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49225,0.09433,0.01602],"object_pos_start":[0.49225,0.09433,0.01602],"object_to_goal_dist_end":0.26856,"object_to_goal_dist_start":0.26856,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_retract","tcp_end":[0.54602,0.18006,0.28946],"tcp_start":[0.51647,0.1349,0.20354],"tcp_to_object_dist_end":0.29157,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```