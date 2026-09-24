## Search State

- **Seed**: 9
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → grasp → lift → push | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | admittance_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 3 | 0.0260 | 0.00 | ❌ rejected |
| 5 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2566 | 0.05 | ❌ rejected |
| 4 | approach → align → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | -0.1558 | 0.00 | ❌ rejected |
| 3 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2569 | 0.06 | ❌ rejected |
| 2 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2568 | 0.06 | ✅ accepted |

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

## Current Skill (Q=0.026) — your mutation base

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

- **Composite score**: 0.026
- **task_score** (E): 0.001
- **fitness_score**: 0.236  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2023 |
| grasp_peg | 1.00 | 1.00 | 0.0098 |
| lift_and_align | 1.00 | 1.00 | 0.0511 |
| push_to_goal | 0.00 | 1.00 | 0.0176 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.074, 0.145) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.545 | 4.034 |
| grasp_peg | grasp | 1.00 / step_budget | (0.508, 0.074, 0.145)→(0.503, 0.073, 0.136) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.548 | 0.557 |
| lift_and_align | lift | 1.00 / step_budget | (0.503, 0.073, 0.136)→(0.495, 0.074, 0.090) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.548 | 220.141 |
| push_to_goal | push | 0.00 / step_budget | (0.495, 0.074, 0.090)→(0.504, 0.069, 0.080) | (0.502, 0.067, 0.034)→(0.504, 0.066, 0.032) | 0.147→0.146 | 1.00 / 2.667 | 314.333 | 360.437 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.410
- phase_breakdown.pre_insert_sub_score: 0.829
- phase_breakdown.push_through_sub_score: 0.048
- phase_breakdown.grasp_peg_sub_score: 0.217
- phase_breakdown.approach_peg_sub_score: 0.822

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.246
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.002
- **Median Q (composite search score)**: 0.029
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.429


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14783,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.10425,"lift_and_align.lift_speed":0.11672,"push_to_goal.push_speed":0.02056},"optimized_scores":{"best_composite_score":0.0359,"best_fitness_score":0.2459,"best_task_score":0.00018},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":979.0,"contact_point_centroid":[0.52505,0.11807,0.05992],"force_p95":353.05306,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":378.4646,"mean_force":296.38746,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49925,0.06434,0.08961]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":888.0,"contact_point_centroid":[0.47498,0.11998,0.05997],"force_p95":209.69096,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":247.9073,"mean_force":163.01932,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49947,0.06418,0.08963]},{"body_a":"peg","body_b":"channel_base_body","contact_count":661.0,"contact_point_centroid":[0.50582,0.06297,0.00936],"force_p95":0.56018,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56704,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51199,0.13258,0.21731]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49992,0.1975,0.29667]},{"body_a":"peg","body_b":"channel_base_body","contact_count":152.0,"contact_point_centroid":[0.50582,0.06286,0.00938],"force_p95":0.553,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54663,"phase_index":2.0,"phase_name":"lift_and_align","phase_type":"lift","tcp_position_centroid":[0.50094,0.0736,0.08696]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50603,0.06301,0.00939],"force_p95":0.55122,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55493,"mean_force":0.5464,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49922,0.06447,0.08965]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50599,0.06298,0.00938],"force_p95":0.55234,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55424,"mean_force":0.54655,"phase_index":1.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.52006,0.06953,0.13672]}],"total_contact_groups":7},"final_pose_error":0.15142,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50597,0.06287,0.03386],"final_tcp_position":[0.50193,0.06302,0.08969],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":378.4646,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":689.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.06294,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.55028,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":695.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach_peg_sub","tcp_end":[0.52473,0.07041,0.14405],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11207,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50595,0.06295,0.03381],"object_pos_start":[0.50596,0.06294,0.03381],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":0.54913,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":450.0,"raw_peak_contact_force":0.55424,"subtask_id":"grasp_peg_sub","tcp_end":[0.51922,0.06943,0.13543],"tcp_start":[0.52473,0.07041,0.14405],"tcp_to_object_dist_end":0.10269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":152.0,"n_steps_budget":600.0,"object_pos_end":[0.50593,0.063,0.03381],"object_pos_start":[0.50595,0.06295,0.03381],"object_to_goal_dist_end":0.14325,"object_to_goal_dist_start":0.14321,"object_z_max":0.03381,"peak_contact_force":0.54705,"phase_name":"lift_and_align","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":152.0,"raw_peak_contact_force":0.55532,"subtask_id":"pre_insert_sub","tcp_end":[0.49852,0.07137,0.09343],"tcp_start":[0.51922,0.06943,0.13543],"tcp_to_object_dist_end":0.06066,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.06287,0.03386],"object_pos_start":[0.50593,0.063,0.03381],"object_to_goal_dist_end":0.14313,"object_to_goal_dist_start":0.14325,"object_z_max":0.03386,"peak_contact_force":304.10143,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2867.0,"raw_peak_contact_force":378.4646,"subtask_id":"push_through_sub","tcp_end":[0.50193,0.06302,0.08969],"tcp_start":[0.49852,0.07137,0.09343],"tcp_to_object_dist_end":0.05598,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `cae0d95026bac46aa2e5d95cffd531753a79751757c4f25fa56c1ec6e19c2175`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43363,"average_solve_count":113.0,"average_success_count":113.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.09284,"lift_and_align.lift_speed":0.07917,"push_to_goal.push_speed":0.04053},"optimized_scores":{"best_composite_score":0.02887,"best_fitness_score":0.23887,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":989.0,"contact_point_centroid":[0.52506,0.11595,0.05991],"force_p95":387.52174,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":390.10729,"mean_force":376.45429,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50362,0.06157,0.09205]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.52502,0.11994,0.05991],"force_p95":71.62832,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":98.56814,"mean_force":49.82877,"phase_index":2.0,"phase_name":"lift_and_align","phase_type":"lift","tcp_position_centroid":[0.49341,0.06615,0.07677]},{"body_a":"peg","body_b":"channel_base_body","contact_count":699.0,"contact_point_centroid":[0.5059,0.05664,0.00936],"force_p95":0.601,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56928,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51532,0.1292,0.21689]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50004,0.19726,0.29641]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50612,0.0566,0.00938],"force_p95":0.55654,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5605,"mean_force":0.54657,"phase_index":1.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.52655,0.06329,0.13607]},{"body_a":"peg","body_b":"channel_base_body","contact_count":153.0,"contact_point_centroid":[0.5062,0.05671,0.00938],"force_p95":0.55653,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5566,"mean_force":0.54656,"phase_index":2.0,"phase_name":"lift_and_align","phase_type":"lift","tcp_position_centroid":[0.50606,0.06757,0.08774]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50613,0.05662,0.00938],"force_p95":0.55652,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55654,"mean_force":0.54656,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50361,0.06164,0.09208]}],"total_contact_groups":7},"final_pose_error":0.14749,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50617,0.05662,0.03379],"final_tcp_position":[0.50542,0.0578,0.09228],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":390.10729,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":728.0,"n_steps_budget":1000.0,"object_pos_end":[0.50615,0.05663,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.53942,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":736.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach_peg_sub","tcp_end":[0.53127,0.06412,0.14355],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50615,0.05664,0.03379],"object_pos_start":[0.50615,0.05663,0.03378],"object_to_goal_dist_end":0.13692,"object_to_goal_dist_start":0.13691,"object_z_max":0.03379,"peak_contact_force":0.54722,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":450.0,"raw_peak_contact_force":0.5605,"subtask_id":"grasp_peg_sub","tcp_end":[0.52571,0.0632,0.13476],"tcp_start":[0.53127,0.06412,0.14355],"tcp_to_object_dist_end":0.10305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":153.0,"n_steps_budget":600.0,"object_pos_end":[0.50616,0.05662,0.03379],"object_pos_start":[0.50615,0.05664,0.03379],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.13692,"object_z_max":0.03379,"peak_contact_force":0.54728,"phase_name":"lift_and_align","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":172.0,"raw_peak_contact_force":98.56814,"subtask_id":"pre_insert_sub","tcp_end":[0.50288,0.06773,0.09526],"tcp_start":[0.52571,0.0632,0.13476],"tcp_to_object_dist_end":0.06255,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50617,0.05662,0.03379],"object_pos_start":[0.50616,0.05662,0.03379],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.1369,"object_z_max":0.03379,"peak_contact_force":386.92865,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1989.0,"raw_peak_contact_force":390.10729,"subtask_id":"push_through_sub","tcp_end":[0.50542,0.0578,0.09228],"tcp_start":[0.50288,0.06773,0.09526],"tcp_to_object_dist_end":0.05851,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fd7ada9a67242f1adcdb6e23860d1223cdc8a17daf859e94e1687ff0564d9575`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88571,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.09842,"lift_and_align.lift_speed":0.16108,"push_to_goal.push_speed":0.07102},"optimized_scores":{"best_composite_score":0.01323,"best_fitness_score":0.22323,"best_task_score":0.00215},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":22.0,"contact_point_centroid":[0.4662,0.11702,0.05912],"force_p95":500.36338,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":561.30036,"mean_force":350.86449,"phase_index":2.0,"phase_name":"lift_and_align","phase_type":"lift","tcp_position_centroid":[0.46239,0.10957,0.06676]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":960.0,"contact_point_centroid":[0.46628,0.11985,0.05997],"force_p95":273.90985,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":312.73995,"mean_force":241.92004,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49292,0.08,0.06735]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49609,0.08273,0.00842],"force_p95":166.0776,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":202.1439,"mean_force":60.6748,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49273,0.08002,0.06758]},{"body_a":"attachment","body_b":"peg","contact_count":667.0,"contact_point_centroid":[0.49557,0.08355,0.0542],"force_p95":176.4742,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":201.61042,"mean_force":90.22649,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49579,0.0816,0.06434]},{"body_a":"peg","body_b":"channel_base_body","contact_count":584.0,"contact_point_centroid":[0.49411,0.07994,0.00937],"force_p95":0.58766,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.56843,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48345,0.14156,0.21875]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49893,0.19753,0.29637]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.49381,0.07994,0.00938],"force_p95":0.55245,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55695,"mean_force":0.54665,"phase_index":1.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.46508,0.08647,0.14035]},{"body_a":"peg","body_b":"channel_base_body","contact_count":148.0,"contact_point_centroid":[0.49363,0.07993,0.00938],"force_p95":0.55256,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55647,"mean_force":0.54666,"phase_index":2.0,"phase_name":"lift_and_align","phase_type":"lift","tcp_position_centroid":[0.47189,0.09768,0.08506]}],"total_contact_groups":8},"final_pose_error":0.16665,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49927,0.0788,0.02705],"final_tcp_position":[0.50331,0.08573,0.05717],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":561.30036,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":612.0,"n_steps_budget":1000.0,"object_pos_end":[0.49381,0.07996,0.03378],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.1602,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.54662,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":619.0,"raw_peak_contact_force":3.77147,"subtask_id":"approach_peg_sub","tcp_end":[0.46944,0.08739,0.14635],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11542,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4938,0.07996,0.03378],"object_pos_start":[0.49381,0.07996,0.03378],"object_to_goal_dist_end":0.1602,"object_to_goal_dist_start":0.1602,"object_z_max":0.03378,"peak_contact_force":0.54845,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":450.0,"raw_peak_contact_force":0.55695,"subtask_id":"grasp_peg_sub","tcp_end":[0.46431,0.08635,0.1393],"tcp_start":[0.46944,0.08739,0.14635],"tcp_to_object_dist_end":0.10976,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":148.0,"n_steps_budget":600.0,"object_pos_end":[0.49381,0.07995,0.03377],"object_pos_start":[0.4938,0.07996,0.03378],"object_to_goal_dist_end":0.16019,"object_to_goal_dist_start":0.1602,"object_z_max":0.03378,"peak_contact_force":0.54966,"phase_name":"lift_and_align","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":170.0,"raw_peak_contact_force":561.30036,"subtask_id":"pre_insert_sub","tcp_end":[0.48225,0.08234,0.08168],"tcp_start":[0.46431,0.08635,0.1393],"tcp_to_object_dist_end":0.04933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49927,0.0788,0.02705],"object_pos_start":[0.49381,0.07995,0.03377],"object_to_goal_dist_end":0.15933,"object_to_goal_dist_start":0.16019,"object_z_max":0.03411,"peak_contact_force":251.96744,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2627.0,"raw_peak_contact_force":312.73995,"subtask_id":"push_through_sub","tcp_end":[0.50331,0.08573,0.05717],"tcp_start":[0.48225,0.08234,0.08168],"tcp_to_object_dist_end":0.03117,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```