## Search State

- **Seed**: 0
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.3809 | 0.15 | ❌ rejected |
| 12 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1730 | 0.17 | ❌ rejected |
| 11 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1715 | 0.18 | ❌ rejected |
| 10 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1718 | 0.18 | ❌ rejected |
| 9 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1712 | 0.18 | ❌ rejected |

**Proposal policy**: task_score is 0.15 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.381) — your mutation base

```yaml
skill: grasp_place
phases:
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  parameters:
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: push_1
  type: push
  generator: impedance_motion
  control: position_control
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
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: insert_2
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
- id: push_2
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2

```

## Design Metrics

- **Composite score**: -0.381
- **task_score** (E): 0.149
- **fitness_score**: 0.176  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.2070 |
| descend_to_object | 1.00 | 1.00 | 0.0000 |
| grasp_object | 1.00 | 1.00 | 0.0000 |
| lift_object | 0.67 | 1.00 | 0.1021 |
| move_to_goal | 0.00 | 1.00 | 0.0974 |
| descend_to_place | 0.00 | 1.00 | 0.0058 |
| release_object | 1.00 | 1.00 | 0.0251 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.384, -0.003, 0.130) | (0.497, 0.001, 0.030)→(0.456, -0.001, 0.016) | 0.263→0.288 | 1.00 / 5.000 | 199.204 | 1566.858 |
| descend_to_object | descend | 1.00 / force_exceeded | (0.384, -0.003, 0.130)→(0.384, -0.003, 0.130) | (0.456, -0.001, 0.016)→(0.456, -0.001, 0.016) | 0.288→0.288 | 1.00 / 5.000 | 175.163 | 111.582 |
| grasp_object | grasp | 1.00 / step_budget | (0.384, -0.003, 0.129)→(0.384, -0.003, 0.129) | (0.456, -0.001, 0.016)→(0.456, -0.001, 0.016) | 0.288→0.288 | 1.00 / 9.000 | 85.358 | 99.972 |
| lift_object | lift | 0.67 / step_budget | (0.384, -0.003, 0.129)→(0.443, 0.001, 0.208) | (0.456, -0.001, 0.016)→(0.456, -0.001, 0.016) | 0.288→0.288 | 1.00 / 8.333 | 94240.265 | 165.175 |
| move_to_goal | approach | 0.00 / step_budget | (0.443, 0.001, 0.208)→(0.505, 0.052, 0.246) | (0.456, -0.001, 0.016)→(0.456, -0.001, 0.016) | 0.288→0.288 | 1.00 / 8.667 | 3272.410 | 190.211 |
| descend_to_place | descend | 0.00 / step_budget | (0.505, 0.052, 0.246)→(0.505, 0.057, 0.246) | (0.456, -0.001, 0.016)→(0.456, -0.001, 0.016) | 0.288→0.288 | 1.00 / 8.000 | 0.123 | 50.914 |
| release_object | release | 1.00 / step_budget | (0.505, 0.057, 0.246)→(0.504, 0.057, 0.271) | (0.456, -0.001, 0.016)→(0.456, -0.001, 0.016) | 0.288→0.288 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.181
- phase_score: 0.104
- phase_breakdown.place_at_goal_score: 0.027
- phase_breakdown.lift_object_score: 0.238
- phase_breakdown.reach_object_score: 0.095
- grasp_place_fitness: 0.186

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.186
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.181
- **Median Q (composite search score)**: -0.381
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.371


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `096c354712624ed6bd8f9b9cbbbc2b7d35a94d9c1517cfb8353e2e383be5aaf0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3798aa6551d21849355469c7d63897f628ac7de9267c18bb4301fe6cfaae0164`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":105.0,"average_failure_rate":0.48387,"average_mean_iterations":99.77419,"average_solve_count":217.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.24637,"approach_object.approach_speed":0.02008,"descend_to_object.descend_force":3.86704,"descend_to_object.descend_speed":0.03513,"descend_to_place.place_speed":0.02152,"descend_to_place.place_z":0.04339,"lift_object.lift_height":0.19835,"lift_object.lift_speed":0.0507,"move_to_goal.goal_approach_height":0.14051,"move_to_goal.goal_speed":0.06449,"release_object.max_release_time":1.3878},"optimized_scores":{"best_composite_score":-0.39048,"best_fitness_score":0.16667,"best_task_score":0.15008},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":885.0,"contact_point_centroid":[0.63366,-0.00936,-0.00046],"force_p95":196.02335,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1526.76475,"mean_force":200.85482,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39122,-0.00909,0.12177]},{"body_a":"world","body_b":"link6","contact_count":10.0,"contact_point_centroid":[0.629,-0.01252,-0.0001],"force_p95":260.20552,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":269.00795,"mean_force":154.17418,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.39738,-0.01316,0.14451]},{"body_a":"link5","body_b":"hand","contact_count":510.0,"contact_point_centroid":[0.53904,0.08503,0.19726],"force_p95":130.1997,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":174.55008,"mean_force":91.65362,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.49857,-0.02048,0.20192]},{"body_a":"link5","body_b":"hand","contact_count":41.0,"contact_point_centroid":[0.52943,0.07826,0.19629],"force_p95":127.42423,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":152.49604,"mean_force":83.92758,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.51773,-0.03152,0.21127]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.62809,-0.01241,-0.00025],"force_p95":94.93602,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":94.93602,"mean_force":94.93602,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.39666,-0.01304,0.14452]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.62892,-0.01244,-0.00013],"force_p95":82.24017,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":85.40148,"mean_force":71.98427,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.39708,-0.01308,0.1441]},{"body_a":"grasp_target","body_b":"link7","contact_count":267.0,"contact_point_centroid":[0.4934,-0.02118,0.03798],"force_p95":2.15428,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.45904,"mean_force":0.60669,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38693,-0.00677,0.09921]},{"body_a":"grasp_target","body_b":"hand","contact_count":229.0,"contact_point_centroid":[0.48742,-0.03105,0.05213],"force_p95":2.11059,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.59385,"mean_force":0.57487,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.3864,-0.00667,0.09664]},{"body_a":"world","body_b":"grasp_target","contact_count":3441.0,"contact_point_centroid":[0.48445,-0.02694,-0.00276],"force_p95":0.43849,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24686,"mean_force":0.18814,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40561,-0.00878,0.13475]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.47514,-0.02801,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.39666,-0.01304,0.14452]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.47514,-0.02801,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.39708,-0.01308,0.1441]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47514,-0.02801,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.43341,-0.02051,0.17367]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47514,-0.02801,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.48755,-0.01477,0.20664]},{"body_a":"world","body_b":"grasp_target","contact_count":756.0,"contact_point_centroid":[0.47514,-0.02801,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.51754,-0.02555,0.21029]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.47514,-0.02801,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.51713,-0.02011,0.21792]},{"body_a":"left_finger","body_b":"right_finger","contact_count":750.0,"contact_point_centroid":[0.39897,-0.0131,0.14308],"force_p95":0.01318,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01566,"mean_force":0.01097,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.39716,-0.0131,0.14396]}],"total_contact_groups":21},"final_pose_error":0.18173,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.47514,-0.02801,0.01602],"final_tcp_position":[0.51843,-0.01894,0.2139],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":272972.02955,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47514,-0.02801,0.01602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.28449,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":193.44704,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4840.0,"raw_peak_contact_force":1526.76475,"subtask_id":"reach_object","tcp_end":[0.39666,-0.01304,0.14452],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15131,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.47514,-0.02801,0.01602],"object_pos_start":[0.47514,-0.02801,0.01602],"object_to_goal_dist_end":0.28449,"object_to_goal_dist_start":0.28449,"object_z_max":0.01602,"peak_contact_force":192.04079,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":94.93602,"subtask_id":"reach_object","tcp_end":[0.39666,-0.01304,0.1445],"tcp_start":[0.39666,-0.01304,0.14452],"tcp_to_object_dist_end":0.15129,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.47514,-0.02801,0.01602],"object_pos_start":[0.47514,-0.02801,0.01602],"object_to_goal_dist_end":0.28449,"object_to_goal_dist_start":0.28449,"object_z_max":0.01602,"peak_contact_force":85.46696,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3500.0,"raw_peak_contact_force":85.40148,"tcp_end":[0.39716,-0.01311,0.14395],"tcp_start":[0.39716,-0.01311,0.14395],"tcp_to_object_dist_end":0.15056,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47514,-0.02801,0.01602],"object_pos_start":[0.47514,-0.02801,0.01602],"object_to_goal_dist_end":0.28449,"object_to_goal_dist_start":0.28449,"object_z_max":0.01602,"peak_contact_force":272972.02955,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8207.0,"raw_peak_contact_force":269.00795,"subtask_id":"lift_object","tcp_end":[0.46684,-0.02681,0.20245],"tcp_start":[0.39716,-0.01311,0.14395],"tcp_to_object_dist_end":0.18662,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47514,-0.02801,0.01602],"object_pos_start":[0.47514,-0.02801,0.01602],"object_to_goal_dist_end":0.28449,"object_to_goal_dist_start":0.28449,"object_z_max":0.01602,"peak_contact_force":68.33296,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8851.0,"raw_peak_contact_force":174.55008,"subtask_id":"place_at_goal","tcp_end":[0.51711,-0.03284,0.2126],"tcp_start":[0.46684,-0.02681,0.20245],"tcp_to_object_dist_end":0.20107,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":189.0,"n_steps_budget":1000.0,"object_pos_end":[0.47514,-0.02801,0.01602],"object_pos_start":[0.47514,-0.02801,0.01602],"object_to_goal_dist_end":0.28449,"object_to_goal_dist_start":0.28449,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1632.0,"raw_peak_contact_force":152.49604,"subtask_id":"place_at_goal","tcp_end":[0.51843,-0.01894,0.2139],"tcp_start":[0.51711,-0.03284,0.2126],"tcp_to_object_dist_end":0.20277,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47514,-0.02801,0.01602],"object_pos_start":[0.47514,-0.02801,0.01602],"object_to_goal_dist_end":0.28449,"object_to_goal_dist_start":0.28449,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1037.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51677,-0.02043,0.23855],"tcp_start":[0.51843,-0.01894,0.2139],"tcp_to_object_dist_end":0.22652,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `ed2df336ade3d991e9495251c8398520a59dd014a70bd2d7bb71dc7aefccaa8a`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":161.0,"average_failure_rate":0.60985,"average_mean_iterations":124.43939,"average_solve_count":264.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.24279,"approach_object.approach_speed":0.02296,"descend_to_object.descend_force":7.46695,"descend_to_object.descend_speed":0.04865,"descend_to_place.place_speed":0.0192,"descend_to_place.place_z":0.07946,"lift_object.lift_height":0.21925,"lift_object.lift_speed":0.07247,"move_to_goal.goal_approach_height":0.08955,"move_to_goal.goal_speed":0.05736,"release_object.max_release_time":2.19734},"optimized_scores":{"best_composite_score":-0.37081,"best_fitness_score":0.18633,"best_task_score":0.181},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":885.0,"contact_point_centroid":[0.62823,0.01249,-0.00046],"force_p95":199.63107,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1583.34712,"mean_force":204.31736,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38408,0.01164,0.11885]},{"body_a":"link5","body_b":"hand","contact_count":151.0,"contact_point_centroid":[0.53121,0.03242,0.20172],"force_p95":376.53758,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":395.96131,"mean_force":267.59441,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.4921,0.12169,0.2233]},{"body_a":"world","body_b":"link6","contact_count":10.0,"contact_point_centroid":[0.62402,0.01728,-9e-05],"force_p95":125.99042,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":133.71103,"mean_force":89.3518,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.38746,0.01726,0.13631]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.62301,0.01733,-0.00025],"force_p95":113.35792,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":113.35792,"mean_force":113.35792,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.38679,0.0173,0.13657]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.62383,0.01726,-0.00013],"force_p95":85.02521,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.80918,"mean_force":72.29961,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.38723,0.01722,0.13616]},{"body_a":"grasp_target","body_b":"link7","contact_count":312.0,"contact_point_centroid":[0.48582,0.02858,0.0403],"force_p95":1.2399,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.38191,"mean_force":0.42029,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38174,0.00846,0.10239]},{"body_a":"grasp_target","body_b":"hand","contact_count":292.0,"contact_point_centroid":[0.4748,0.02908,0.0547],"force_p95":2.03769,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.61857,"mean_force":0.4254,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38176,0.00836,0.10108]},{"body_a":"world","body_b":"grasp_target","contact_count":3306.0,"contact_point_centroid":[0.47055,0.04994,-0.00277],"force_p95":0.3522,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24307,"mean_force":0.18542,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39935,0.01141,0.13213]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.45902,0.05113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.38679,0.0173,0.13657]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.45902,0.05113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.38723,0.01722,0.13616]},{"body_a":"world","body_b":"grasp_target","contact_count":3988.0,"contact_point_centroid":[0.45902,0.05113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.42085,0.03393,0.18062]},{"body_a":"world","body_b":"grasp_target","contact_count":3280.0,"contact_point_centroid":[0.45902,0.05113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.48025,0.0988,0.22517]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.45902,0.05113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.50651,0.1393,0.29976]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.45902,0.05113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.50705,0.13922,0.31048]},{"body_a":"left_finger","body_b":"right_finger","contact_count":751.0,"contact_point_centroid":[0.38926,0.01719,0.13504],"force_p95":0.01329,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01096,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.38732,0.01719,0.136]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3526.0,"contact_point_centroid":[0.48228,0.09897,0.22401],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01289,"mean_force":0.01037,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.48032,0.09893,0.22507]}],"total_contact_groups":20},"final_pose_error":0.14163,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.45902,0.05113,0.01602],"final_tcp_position":[0.50665,0.13923,0.30082],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1583.34712,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45902,0.05113,0.01602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.25639,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":199.51425,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4813.0,"raw_peak_contact_force":1583.34712,"subtask_id":"reach_object","tcp_end":[0.38679,0.0173,0.13657],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14455,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.45902,0.05113,0.01602],"object_pos_start":[0.45902,0.05113,0.01602],"object_to_goal_dist_end":0.25639,"object_to_goal_dist_start":0.25639,"object_z_max":0.01602,"peak_contact_force":144.96472,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":113.35792,"subtask_id":"reach_object","tcp_end":[0.38679,0.0173,0.13656],"tcp_start":[0.38679,0.0173,0.13657],"tcp_to_object_dist_end":0.14454,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.45902,0.05113,0.01602],"object_pos_start":[0.45902,0.05113,0.01602],"object_to_goal_dist_end":0.25639,"object_to_goal_dist_start":0.25639,"object_z_max":0.01602,"peak_contact_force":85.42689,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3501.0,"raw_peak_contact_force":91.80918,"tcp_end":[0.38733,0.01718,0.13599],"tcp_start":[0.38732,0.01719,0.136],"tcp_to_object_dist_end":0.14383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":997.0,"n_steps_budget":1000.0,"object_pos_end":[0.45902,0.05113,0.01602],"object_pos_start":[0.45902,0.05113,0.01602],"object_to_goal_dist_end":0.25639,"object_to_goal_dist_start":0.25639,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8174.0,"raw_peak_contact_force":133.71103,"subtask_id":"lift_object","tcp_end":[0.45454,0.04968,0.22559],"tcp_start":[0.38733,0.01718,0.13599],"tcp_to_object_dist_end":0.20963,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":820.0,"n_steps_budget":1000.0,"object_pos_end":[0.45902,0.05113,0.01602],"object_pos_start":[0.45902,0.05113,0.01602],"object_to_goal_dist_end":0.25639,"object_to_goal_dist_start":0.25639,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6957.0,"raw_peak_contact_force":395.96131,"subtask_id":"place_at_goal","tcp_end":[0.50643,0.13936,0.29921],"tcp_start":[0.45454,0.04968,0.22559],"tcp_to_object_dist_end":0.30038,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.45902,0.05113,0.01602],"object_pos_start":[0.45902,0.05113,0.01602],"object_to_goal_dist_end":0.25639,"object_to_goal_dist_start":0.25639,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":26.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.50665,0.13923,0.30082],"tcp_start":[0.50643,0.13936,0.29921],"tcp_to_object_dist_end":0.30189,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45902,0.05113,0.01602],"object_pos_start":[0.45902,0.05113,0.01602],"object_to_goal_dist_end":0.25639,"object_to_goal_dist_start":0.25639,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50738,0.13927,0.33123],"tcp_start":[0.50665,0.13923,0.30082],"tcp_to_object_dist_end":0.33086,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `291bc6f2bd023fc25503740a7343328e565e43fc71fa3c9c5d2fdbe2d4351fd2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":113.0,"average_failure_rate":0.47479,"average_mean_iterations":97.32353,"average_solve_count":238.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.24978,"approach_object.approach_speed":0.05998,"descend_to_object.descend_force":8.26881,"descend_to_object.descend_speed":0.01809,"descend_to_place.place_speed":0.0141,"descend_to_place.place_z":0.02194,"lift_object.lift_height":0.23889,"lift_object.lift_speed":0.03965,"move_to_goal.goal_approach_height":0.10753,"move_to_goal.goal_speed":0.06078,"release_object.max_release_time":0.76728},"optimized_scores":{"best_composite_score":-0.38131,"best_fitness_score":0.17583,"best_task_score":0.11656},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":790.0,"contact_point_centroid":[0.6213,-0.00897,-0.0005],"force_p95":205.44765,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1590.46363,"mean_force":208.55375,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37122,-0.00854,0.10647]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.61809,-0.01325,-0.00027],"force_p95":126.45192,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":126.45192,"mean_force":126.45192,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.36788,-0.01319,0.10895]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.61887,-0.01333,-0.00013],"force_p95":91.13075,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":122.70543,"mean_force":72.2165,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.36836,-0.01327,0.10852]},{"body_a":"world","body_b":"link6","contact_count":11.0,"contact_point_centroid":[0.61907,-0.01338,-0.0001],"force_p95":83.80783,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.80639,"mean_force":26.11813,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.36853,-0.01332,0.10854]},{"body_a":"grasp_target","body_b":"link7","contact_count":58.0,"contact_point_centroid":[0.47473,-0.00907,0.01815],"force_p95":2.78102,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.1477,"mean_force":0.63064,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.36626,-0.00531,0.07468]},{"body_a":"grasp_target","body_b":"hand","contact_count":86.0,"contact_point_centroid":[0.4526,-0.03529,0.04746],"force_p95":3.38464,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.00316,"mean_force":1.01271,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.3707,-0.00532,0.07817]},{"body_a":"world","body_b":"grasp_target","contact_count":3381.0,"contact_point_centroid":[0.44048,-0.02462,-0.00228],"force_p95":0.275,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.19662,"mean_force":0.15103,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38699,-0.00805,0.11945]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.43279,-0.02578,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.36788,-0.01319,0.10895]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.43279,-0.02578,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.36836,-0.01327,0.10852]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.43279,-0.02578,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.3874,-0.01753,0.15324]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.43279,-0.02578,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.45205,0.0164,0.21228]},{"body_a":"world","body_b":"grasp_target","contact_count":28.0,"contact_point_centroid":[0.43279,-0.02578,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.49016,0.05102,0.22524]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.43279,-0.02578,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.48783,0.052,0.22354]},{"body_a":"left_finger","body_b":"right_finger","contact_count":742.0,"contact_point_centroid":[0.3706,-0.0133,0.10766],"force_p95":0.01306,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01108,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.36848,-0.01329,0.10834]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4231.0,"contact_point_centroid":[0.45439,0.01662,0.21164],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0129,"mean_force":0.01053,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.45234,0.01663,0.21239]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4166.0,"contact_point_centroid":[0.38947,-0.01753,0.15254],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01289,"mean_force":0.01068,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.38738,-0.01753,0.15322]}],"total_contact_groups":19},"final_pose_error":0.17802,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.43279,-0.02578,0.01602],"final_tcp_position":[0.49017,0.05152,0.22402],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9748.77318,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":905.0,"n_steps_budget":1000.0,"object_pos_end":[0.43279,-0.02578,0.01602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.32241,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":204.65139,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4332.0,"raw_peak_contact_force":1590.46363,"subtask_id":"reach_object","tcp_end":[0.36788,-0.01319,0.10895],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11405,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.43279,-0.02578,0.01602],"object_pos_start":[0.43279,-0.02578,0.01602],"object_to_goal_dist_end":0.32241,"object_to_goal_dist_start":0.32241,"object_z_max":0.01602,"peak_contact_force":188.4835,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":126.45192,"subtask_id":"reach_object","tcp_end":[0.36787,-0.01319,0.10897],"tcp_start":[0.36788,-0.01319,0.10895],"tcp_to_object_dist_end":0.11406,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.43279,-0.02578,0.01602],"object_pos_start":[0.43279,-0.02578,0.01602],"object_to_goal_dist_end":0.32241,"object_to_goal_dist_start":0.32241,"object_z_max":0.01602,"peak_contact_force":85.18134,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3492.0,"raw_peak_contact_force":122.70543,"tcp_end":[0.36849,-0.0133,0.10833],"tcp_start":[0.36849,-0.01329,0.10833],"tcp_to_object_dist_end":0.11318,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43279,-0.02578,0.01602],"object_pos_start":[0.43279,-0.02578,0.01602],"object_to_goal_dist_end":0.32241,"object_to_goal_dist_start":0.32241,"object_z_max":0.01602,"peak_contact_force":9748.64289,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8177.0,"raw_peak_contact_force":92.80639,"subtask_id":"lift_object","tcp_end":[0.40734,-0.02135,0.19741],"tcp_start":[0.36849,-0.0133,0.10833],"tcp_to_object_dist_end":0.18322,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43279,-0.02578,0.01602],"object_pos_start":[0.43279,-0.02578,0.01602],"object_to_goal_dist_end":0.32241,"object_to_goal_dist_start":0.32241,"object_z_max":0.01602,"peak_contact_force":9748.77318,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8231.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.49018,0.05096,0.2258],"tcp_start":[0.40734,-0.02135,0.19741],"tcp_to_object_dist_end":0.23064,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.43279,-0.02578,0.01602],"object_pos_start":[0.43279,-0.02578,0.01602],"object_to_goal_dist_end":0.32241,"object_to_goal_dist_start":0.32241,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":57.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.49017,0.05152,0.22402],"tcp_start":[0.49018,0.05096,0.2258],"tcp_to_object_dist_end":0.2292,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.43279,-0.02578,0.01602],"object_pos_start":[0.43279,-0.02578,0.01602],"object_to_goal_dist_end":0.32241,"object_to_goal_dist_start":0.32241,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.48736,0.0526,0.24384],"tcp_start":[0.49017,0.05152,0.22402],"tcp_to_object_dist_end":0.24703,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```