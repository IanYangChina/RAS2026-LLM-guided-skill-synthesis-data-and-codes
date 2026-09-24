## Search State

- **Seed**: 9
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → grasp → lift → approach → push | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 6 | -0.1790 | 0.00 | ❌ rejected |
| 8 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2555 | 0.03 | ❌ rejected |
| 7 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2555 | 0.05 | ❌ rejected |
| 6 | approach → grasp → lift → push | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | admittance_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 3 | 0.0260 | 0.00 | ❌ rejected |
| 5 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2566 | 0.05 | ❌ rejected |

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

- Task name: peg_channel
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

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

## Current Skill (Q=-0.179) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: rotate_1
  type: rotate
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
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
- id: push_1
  type: push
  generator: impedance_motion
  control: position_control
  termination: time_limit
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
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
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  parameters:
    grip_force:
      type: scalar
      range:
      - 5.0
      - 30.0

```

## Design Metrics

- **Composite score**: -0.179
- **task_score** (E): 0.000
- **fitness_score**: 0.211  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2317 |
| grasp_peg | 1.00 | 1.00 | 0.0000 |
| lift_peg | 1.00 | 1.00 | 0.0804 |
| approach_channel | 1.00 | 1.00 | 0.0525 |
| insert_and_push | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.079, 0.105) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.555 | 4.034 |
| grasp_peg | grasp | 1.00 / step_budget | (0.502, 0.077, 0.096)→(0.502, 0.077, 0.096) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.558 | 0.575 |
| lift_peg | lift | 1.00 / step_budget | (0.502, 0.077, 0.096)→(0.499, 0.077, 0.177) | (0.502, 0.067, 0.034)→(0.502, 0.066, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.553 | 0.566 |
| approach_channel | approach | 1.00 / step_budget | (0.499, 0.077, 0.177)→(0.486, 0.078, 0.131) | (0.502, 0.066, 0.034)→(0.502, 0.066, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.547 | 0.567 |
| insert_and_push | push | 0.00 / guard_failure | (0.486, 0.051, 0.112)→(0.486, 0.051, 0.112) | (0.502, 0.066, 0.034)→(0.502, 0.066, 0.034) | 0.147→0.147 | 1.00 / 2.000 | 66.150 | 66.150 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.353
- phase_breakdown.approach_channel_score: 0.702
- phase_breakdown.insert_through_channel_score: 0.000
- phase_breakdown.reach_peg_score: 0.711

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.212
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.179
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.275


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `bf8103833c1e96f48e87b3ce39b3b3bf17e268470bd7b5c037546fb78b5150b8`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `98954a34ee744fa939070f7dadee8a411de43cdcfeddcf3b4bfc5c3a4c536020`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75728,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_channel.channel_approach_speed":0.08846,"approach_peg.approach_speed":0.11832,"grasp_peg.grip_force":23.46776,"insert_and_push.insert_speed":0.07337,"insert_and_push.stroke_distance":0.17199,"lift_peg.lift_speed":0.13539},"optimized_scores":{"best_composite_score":-0.1783,"best_fitness_score":0.2117,"best_task_score":5e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.47499,0.11845,0.05996],"force_p95":56.39964,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":57.57357,"mean_force":46.35734,"phase_index":4.0,"phase_name":"insert_and_push","phase_type":"push","tcp_position_centroid":[0.48764,0.05596,0.1121]},{"body_a":"peg","body_b":"channel_base_body","contact_count":430.0,"contact_point_centroid":[0.50574,0.063,0.00935],"force_p95":0.5804,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57802,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51186,0.13467,0.19628]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50029,0.19678,0.29472]},{"body_a":"peg","body_b":"channel_base_body","contact_count":252.0,"contact_point_centroid":[0.50594,0.06284,0.00938],"force_p95":0.5528,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54656,"phase_index":2.0,"phase_name":"lift_peg","phase_type":"lift","tcp_position_centroid":[0.51508,0.07346,0.13447]},{"body_a":"peg","body_b":"channel_base_body","contact_count":550.0,"contact_point_centroid":[0.50599,0.063,0.00938],"force_p95":0.55142,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54658,"phase_index":1.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.51838,0.07395,0.09638]},{"body_a":"peg","body_b":"channel_base_body","contact_count":146.0,"contact_point_centroid":[0.5059,0.06335,0.00938],"force_p95":0.55312,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55493,"mean_force":0.54658,"phase_index":3.0,"phase_name":"approach_channel","phase_type":"approach","tcp_position_centroid":[0.49166,0.08613,0.12601]},{"body_a":"peg","body_b":"channel_base_body","contact_count":150.0,"contact_point_centroid":[0.50618,0.06269,0.00938],"force_p95":0.551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55339,"mean_force":0.54653,"phase_index":4.0,"phase_name":"insert_and_push","phase_type":"push","tcp_position_centroid":[0.48763,0.06651,0.11832]}],"total_contact_groups":7},"final_pose_error":0.16486,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50594,0.06292,0.03382],"final_tcp_position":[0.48762,0.05577,0.11206],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":57.57357,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":458.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.06294,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54594,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":464.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_peg","tcp_end":[0.52383,0.07514,0.10429],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50599,0.06294,0.03381],"object_pos_start":[0.50598,0.06294,0.03381],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":0.54269,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":550.0,"raw_peak_contact_force":0.55501,"subtask_id":"reach_peg","tcp_end":[0.51765,0.07386,0.09535],"tcp_start":[0.51765,0.07386,0.09535],"tcp_to_object_dist_end":0.06359,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":252.0,"n_steps_budget":660.0,"object_pos_end":[0.50594,0.06298,0.03381],"object_pos_start":[0.50599,0.06294,0.03381],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":0.54889,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":252.0,"raw_peak_contact_force":0.55532,"tcp_end":[0.51492,0.07343,0.17571],"tcp_start":[0.51765,0.07386,0.09535],"tcp_to_object_dist_end":0.14257,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":146.0,"n_steps_budget":600.0,"object_pos_end":[0.50603,0.06296,0.0338],"object_pos_start":[0.50594,0.06298,0.03381],"object_to_goal_dist_end":0.14322,"object_to_goal_dist_start":0.14323,"object_z_max":0.03381,"peak_contact_force":0.54621,"phase_name":"approach_channel","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":146.0,"raw_peak_contact_force":0.55493,"subtask_id":"approach_channel","tcp_end":[0.48897,0.07696,0.12646],"tcp_start":[0.51492,0.07343,0.17571],"tcp_to_object_dist_end":0.09525,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":150.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,0.06292,0.03382],"object_pos_start":[0.50603,0.06296,0.0338],"object_to_goal_dist_end":0.14318,"object_to_goal_dist_start":0.14322,"object_z_max":0.03382,"peak_contact_force":57.57357,"phase_name":"insert_and_push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":153.0,"raw_peak_contact_force":57.57357,"subtask_id":"insert_through_channel","tcp_end":[0.48762,0.05577,0.11206],"tcp_start":[0.48763,0.05585,0.11208],"tcp_to_object_dist_end":0.08068,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `cae0d95026bac46aa2e5d95cffd531753a79751757c4f25fa56c1ec6e19c2175`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76699,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_channel.channel_approach_speed":0.09224,"approach_peg.approach_speed":0.1239,"grasp_peg.grip_force":17.71856,"insert_and_push.insert_speed":0.06014,"insert_and_push.stroke_distance":0.16278,"lift_peg.lift_speed":0.12447},"optimized_scores":{"best_composite_score":-0.17966,"best_fitness_score":0.21034,"best_task_score":9e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.47498,0.11863,0.05994],"force_p95":79.32824,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":82.70089,"mean_force":58.43925,"phase_index":4.0,"phase_name":"insert_and_push","phase_type":"push","tcp_position_centroid":[0.48837,0.05604,0.11175]},{"body_a":"peg","body_b":"channel_base_body","contact_count":440.0,"contact_point_centroid":[0.50585,0.05662,0.00935],"force_p95":0.60663,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.58249,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51511,0.1315,0.19593]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50048,0.19633,0.29416]},{"body_a":"peg","body_b":"channel_base_body","contact_count":550.0,"contact_point_centroid":[0.50611,0.05658,0.00938],"force_p95":0.56575,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58619,"mean_force":0.54657,"phase_index":1.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.52454,0.06817,0.09596]},{"body_a":"peg","body_b":"channel_base_body","contact_count":144.0,"contact_point_centroid":[0.50613,0.05667,0.00938],"force_p95":0.55315,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56156,"mean_force":0.5466,"phase_index":3.0,"phase_name":"approach_channel","phase_type":"approach","tcp_position_centroid":[0.49477,0.08222,0.12564]},{"body_a":"peg","body_b":"channel_base_body","contact_count":142.0,"contact_point_centroid":[0.50617,0.05653,0.00938],"force_p95":0.55295,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55869,"mean_force":0.54659,"phase_index":4.0,"phase_name":"insert_and_push","phase_type":"push","tcp_position_centroid":[0.48839,0.06605,0.11802]},{"body_a":"peg","body_b":"channel_base_body","contact_count":252.0,"contact_point_centroid":[0.50621,0.05668,0.00938],"force_p95":0.55145,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55639,"mean_force":0.54664,"phase_index":2.0,"phase_name":"lift_peg","phase_type":"lift","tcp_position_centroid":[0.52122,0.06771,0.13406]}],"total_contact_groups":7},"final_pose_error":0.15649,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50609,0.05656,0.03381],"final_tcp_position":[0.48834,0.05583,0.11171],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":82.70089,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":469.0,"n_steps_budget":1000.0,"object_pos_end":[0.50612,0.05663,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.57168,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":477.0,"raw_peak_contact_force":4.44541,"subtask_id":"reach_peg","tcp_end":[0.53004,0.06932,0.10404],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07529,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.5061,0.05663,0.03379],"object_pos_start":[0.50612,0.05663,0.03378],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.13691,"object_z_max":0.03379,"peak_contact_force":0.55065,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":550.0,"raw_peak_contact_force":0.58619,"subtask_id":"reach_peg","tcp_end":[0.5238,0.06808,0.09492],"tcp_start":[0.5238,0.06808,0.09492],"tcp_to_object_dist_end":0.06466,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":252.0,"n_steps_budget":630.0,"object_pos_end":[0.5061,0.05659,0.0338],"object_pos_start":[0.50609,0.05662,0.03379],"object_to_goal_dist_end":0.13686,"object_to_goal_dist_start":0.1369,"object_z_max":0.0338,"peak_contact_force":0.54755,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":252.0,"raw_peak_contact_force":0.55639,"tcp_end":[0.52106,0.06768,0.17523],"tcp_start":[0.5238,0.06808,0.09492],"tcp_to_object_dist_end":0.14265,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":144.0,"n_steps_budget":600.0,"object_pos_end":[0.50611,0.05658,0.0338],"object_pos_start":[0.5061,0.05659,0.0338],"object_to_goal_dist_end":0.13686,"object_to_goal_dist_start":0.13686,"object_z_max":0.0338,"peak_contact_force":0.54896,"phase_name":"approach_channel","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":144.0,"raw_peak_contact_force":0.56156,"subtask_id":"approach_channel","tcp_end":[0.48979,0.07579,0.12608],"tcp_start":[0.52106,0.06768,0.17523],"tcp_to_object_dist_end":0.09567,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":142.0,"n_steps_budget":1000.0,"object_pos_end":[0.50615,0.05656,0.03381],"object_pos_start":[0.50611,0.05658,0.0338],"object_to_goal_dist_end":0.13683,"object_to_goal_dist_start":0.13686,"object_z_max":0.03381,"peak_contact_force":82.70089,"phase_name":"insert_and_push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":145.0,"raw_peak_contact_force":82.70089,"subtask_id":"insert_through_channel","tcp_end":[0.48834,0.05583,0.11171],"tcp_start":[0.48836,0.05592,0.11172],"tcp_to_object_dist_end":0.07991,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fd7ada9a67242f1adcdb6e23860d1223cdc8a17daf859e94e1687ff0564d9575`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75472,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_channel.channel_approach_speed":0.07258,"approach_peg.approach_speed":0.14192,"grasp_peg.grip_force":20.51766,"insert_and_push.insert_speed":0.03304,"insert_and_push.stroke_distance":0.17272,"lift_peg.lift_speed":0.12794},"optimized_scores":{"best_composite_score":-0.17914,"best_fitness_score":0.21086,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.475,0.10255,0.05997],"force_p95":56.54353,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":58.17582,"mean_force":46.19526,"phase_index":4.0,"phase_name":"insert_and_push","phase_type":"push","tcp_position_centroid":[0.48227,0.04041,0.11357]},{"body_a":"peg","body_b":"channel_base_body","contact_count":400.0,"contact_point_centroid":[0.49418,0.07993,0.00936],"force_p95":0.60712,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.57847,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4841,0.14297,0.19721]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49889,0.19684,0.29425]},{"body_a":"peg","body_b":"channel_base_body","contact_count":294.0,"contact_point_centroid":[0.49376,0.08002,0.00938],"force_p95":0.58225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58681,"mean_force":0.54652,"phase_index":4.0,"phase_name":"insert_and_push","phase_type":"push","tcp_position_centroid":[0.48045,0.06106,0.126]},{"body_a":"peg","body_b":"channel_base_body","contact_count":238.0,"contact_point_centroid":[0.49378,0.07994,0.00938],"force_p95":0.57891,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58554,"mean_force":0.54654,"phase_index":2.0,"phase_name":"lift_peg","phase_type":"lift","tcp_position_centroid":[0.46263,0.0895,0.13819]},{"body_a":"peg","body_b":"channel_base_body","contact_count":550.0,"contact_point_centroid":[0.49383,0.07997,0.00939],"force_p95":0.57847,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58485,"mean_force":0.54625,"phase_index":1.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.46556,0.09005,0.09989]},{"body_a":"peg","body_b":"channel_base_body","contact_count":185.0,"contact_point_centroid":[0.49391,0.07994,0.00938],"force_p95":0.57449,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58471,"mean_force":0.54658,"phase_index":3.0,"phase_name":"approach_channel","phase_type":"approach","tcp_position_centroid":[0.4604,0.09969,0.13791]}],"total_contact_groups":7},"final_pose_error":0.15295,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49382,0.07996,0.03378],"final_tcp_position":[0.48224,0.04022,0.11351],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":58.17582,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":428.0,"n_steps_budget":1000.0,"object_pos_end":[0.49382,0.07994,0.03378],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.54647,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":435.0,"raw_peak_contact_force":3.77147,"subtask_id":"reach_peg","tcp_end":[0.47061,0.09125,0.10645],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07713,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49381,0.07994,0.03377],"object_pos_start":[0.49382,0.07994,0.03378],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.16018,"object_z_max":0.03383,"peak_contact_force":0.58167,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":550.0,"raw_peak_contact_force":0.58485,"subtask_id":"reach_peg","tcp_end":[0.4649,0.08995,0.09906],"tcp_start":[0.4649,0.08995,0.09906],"tcp_to_object_dist_end":0.0721,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":238.0,"n_steps_budget":660.0,"object_pos_end":[0.49383,0.07994,0.03378],"object_pos_start":[0.49384,0.07995,0.03377],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.16019,"object_z_max":0.03378,"peak_contact_force":0.56227,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":238.0,"raw_peak_contact_force":0.58554,"tcp_end":[0.46246,0.08946,0.17932],"tcp_start":[0.4649,0.08995,0.09906],"tcp_to_object_dist_end":0.14919,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":185.0,"n_steps_budget":600.0,"object_pos_end":[0.49382,0.07993,0.03377],"object_pos_start":[0.49383,0.07994,0.03378],"object_to_goal_dist_end":0.16017,"object_to_goal_dist_start":0.16018,"object_z_max":0.03378,"peak_contact_force":0.54725,"phase_name":"approach_channel","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":185.0,"raw_peak_contact_force":0.58471,"subtask_id":"approach_channel","tcp_end":[0.48033,0.08199,0.14119],"tcp_start":[0.46246,0.08946,0.17932],"tcp_to_object_dist_end":0.10828,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":294.0,"n_steps_budget":1000.0,"object_pos_end":[0.4938,0.07996,0.03378],"object_pos_start":[0.49382,0.07993,0.03377],"object_to_goal_dist_end":0.1602,"object_to_goal_dist_start":0.16017,"object_z_max":0.03378,"peak_contact_force":58.17582,"phase_name":"insert_and_push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":297.0,"raw_peak_contact_force":58.17582,"subtask_id":"insert_through_channel","tcp_end":[0.48224,0.04022,0.11351],"tcp_start":[0.48226,0.0403,0.11355],"tcp_to_object_dist_end":0.08984,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```