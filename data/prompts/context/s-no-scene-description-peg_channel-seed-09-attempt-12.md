## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → rotate → push → release | linear_cartesian | linear_cartesian | — | joint_interpolation | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | 6 | -0.1461 | 0.00 | ❌ rejected |
| 11 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2575 | 0.05 | ❌ rejected |
| 10 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2612 | 0.04 | ❌ rejected |
| 9 | approach → grasp → lift → approach → push | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 6 | -0.1790 | 0.00 | ❌ rejected |
| 8 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2555 | 0.03 | ❌ rejected |

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

## Current Skill (Q=-0.146) — your mutation base

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

- **Composite score**: -0.146
- **task_score** (E): 0.000
- **fitness_score**: 0.141  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2409 |
| descend_contact | 0.67 | 1.00 | 0.0389 |
| grasp_peg | 1.00 | 1.00 | 0.0015 |
| align_orientation | 1.00 | 1.00 | 0.0210 |
| push_channel | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.074, 0.097) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.565 | 4.034 |
| descend_contact | descend | 0.67 / force_exceeded | (0.508, 0.074, 0.097)→(0.502, 0.070, 0.061) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 2.000 | 37.001 | 37.001 |
| grasp_peg | grasp | 1.00 / step_budget | (0.495, 0.074, 0.060)→(0.494, 0.074, 0.059) | (0.500, 0.072, 0.034)→(0.500, 0.072, 0.034) | 0.152→0.152 | 1.00 / 2.500 | 45.311 | 58.219 |
| align_orientation | rotate | 1.00 / step_budget | (0.494, 0.074, 0.059)→(0.492, 0.095, 0.059) | (0.500, 0.072, 0.034)→(0.498, 0.081, 0.035) | 0.152→0.161 | 1.00 / 2.000 | 26.815 | 67.961 |
| push_channel | push | 0.00 / guard_failure | (0.492, 0.095, 0.059)→(0.492, 0.095, 0.059) | (0.498, 0.081, 0.035)→(0.498, 0.081, 0.035) | 0.161→0.161 | 1.00 / 2.500 | 56.661 | 45.868 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.361
- phase_breakdown.pre_contact_score: 0.823
- phase_breakdown.grasp_peg_score: 0.655
- phase_breakdown.push_channel_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.217
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.015
- **K-run variance**: 0.0375
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.394


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83636,"average_solve_count":55.0,"average_success_count":55.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_orientation.rotate_speed":0.38562,"approach_peg.approach_speed":0.14696,"descend_contact.contact_force_threshold":10.21909,"descend_contact.descend_speed":0.0529,"push_channel.push_distance":0.12989,"push_channel.push_speed":0.09366},"optimized_scores":{"best_composite_score":-0.01507,"best_fitness_score":0.20493,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":409.0,"contact_point_centroid":[0.51714,0.07966,0.00927],"force_p95":56.22309,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.91797,"mean_force":54.67092,"phase_index":3.0,"phase_name":"align_orientation","phase_type":"rotate","tcp_position_centroid":[0.50947,0.07934,0.05811]},{"body_a":"attachment","body_b":"peg","contact_count":409.0,"contact_point_centroid":[0.52016,0.07464,0.0576],"force_p95":55.7365,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.43018,"mean_force":54.18441,"phase_index":3.0,"phase_name":"align_orientation","phase_type":"rotate","tcp_position_centroid":[0.50947,0.07934,0.05811]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51446,0.08357,0.0093],"force_p95":52.66164,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.66164,"mean_force":52.66164,"phase_index":4.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50772,0.08984,0.05797]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51709,0.08243,0.05763],"force_p95":52.08913,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.08913,"mean_force":52.08913,"phase_index":4.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50772,0.08984,0.05797]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.52234,0.06487,0.00928],"force_p95":51.69376,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.69491,"mean_force":48.40922,"phase_index":2.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.51102,0.06554,0.05845]},{"body_a":"attachment","body_b":"peg","contact_count":450.0,"contact_point_centroid":[0.52286,0.06472,0.05761],"force_p95":51.19323,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.19435,"mean_force":47.91712,"phase_index":2.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.51102,0.06554,0.05845]},{"body_a":"peg","body_b":"channel_base_body","contact_count":172.0,"contact_point_centroid":[0.50578,0.06298,0.00938],"force_p95":0.55247,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.92143,"mean_force":0.60688,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.5178,0.06751,0.07807]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.52368,0.06513,0.05879],"force_p95":10.45993,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.45993,"mean_force":10.45993,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.51183,0.06578,0.06049]},{"body_a":"peg","body_b":"channel_base_body","contact_count":722.0,"contact_point_centroid":[0.50582,0.06295,0.00936],"force_p95":0.55893,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56531,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51193,0.13219,0.19246]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49993,0.19771,0.29624]}],"total_contact_groups":10},"final_pose_error":0.12991,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50225,0.07383,0.03515],"final_tcp_position":[0.50772,0.08985,0.05797],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":56.91797,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":750.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.06297,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14322,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54731,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":756.0,"raw_peak_contact_force":3.88411,"subtask_id":"pre_contact","tcp_end":[0.52463,0.06945,0.09562],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0649,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":172.0,"n_steps_budget":780.0,"object_pos_end":[0.50595,0.06303,0.0338],"object_pos_start":[0.50594,0.06297,0.03381],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14322,"object_z_max":0.03381,"peak_contact_force":10.92143,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":173.0,"raw_peak_contact_force":10.92143,"subtask_id":"grasp_peg","tcp_end":[0.5118,0.06576,0.06029],"tcp_start":[0.52463,0.06945,0.09562],"tcp_to_object_dist_end":0.02727,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50569,0.06307,0.0335],"object_pos_start":[0.50595,0.06303,0.0338],"object_to_goal_dist_end":0.14333,"object_to_goal_dist_start":0.14328,"object_z_max":0.03394,"peak_contact_force":48.03233,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":900.0,"raw_peak_contact_force":51.69491,"subtask_id":"grasp_peg","tcp_end":[0.51102,0.06554,0.05828],"tcp_start":[0.5118,0.06576,0.06029],"tcp_to_object_dist_end":0.02547,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":409.0,"n_steps_budget":600.0,"object_pos_end":[0.50225,0.07382,0.03515],"object_pos_start":[0.50569,0.06307,0.0335],"object_to_goal_dist_end":0.15391,"object_to_goal_dist_start":0.14333,"object_z_max":0.03515,"peak_contact_force":52.61437,"phase_name":"align_orientation","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":818.0,"raw_peak_contact_force":56.91797,"tcp_end":[0.50772,0.08984,0.05797],"tcp_start":[0.51102,0.06554,0.05828],"tcp_to_object_dist_end":0.02841,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":870.0,"object_pos_end":[0.50225,0.07383,0.03515],"object_pos_start":[0.50225,0.07382,0.03515],"object_to_goal_dist_end":0.15392,"object_to_goal_dist_start":0.15391,"object_z_max":0.03515,"peak_contact_force":52.66164,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":52.66164,"subtask_id":"push_channel","tcp_end":[0.50772,0.08985,0.05797],"tcp_start":[0.50772,0.08984,0.05797],"tcp_to_object_dist_end":0.02841,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `cae0d95026bac46aa2e5d95cffd531753a79751757c4f25fa56c1ec6e19c2175`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.17143,"average_solve_count":35.0,"average_success_count":35.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_orientation.rotate_speed":0.70497,"approach_peg.approach_speed":0.29654,"descend_contact.contact_force_threshold":9.20099,"descend_contact.descend_speed":0.0678,"push_channel.push_distance":0.14128,"push_channel.push_speed":0.1085},"optimized_scores":{"best_composite_score":-0.41993,"best_fitness_score":7e-05,"best_task_score":7e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52678,0.06033,0.05996],"force_p95":85.62562,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":85.62562,"mean_force":85.62562,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.51492,0.06072,0.06168]},{"body_a":"peg","body_b":"channel_base_body","contact_count":526.0,"contact_point_centroid":[0.5059,0.05658,0.00935],"force_p95":0.61909,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.57674,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51497,0.13115,0.1954]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50009,0.19711,0.29536]},{"body_a":"peg","body_b":"channel_base_body","contact_count":171.0,"contact_point_centroid":[0.50603,0.05679,0.00937],"force_p95":0.61974,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62212,"mean_force":0.54682,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.52248,0.06306,0.0801]}],"total_contact_groups":4},"final_pose_error":0.02935,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50616,0.05657,0.03378],"final_tcp_position":[0.51485,0.0607,0.06149],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":85.62562,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":555.0,"n_steps_budget":600.0,"object_pos_end":[0.5061,0.05665,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13693,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.60485,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":563.0,"raw_peak_contact_force":4.44541,"subtask_id":"pre_contact","tcp_end":[0.53071,0.06561,0.09856],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":171.0,"n_steps_budget":660.0,"object_pos_end":[0.50616,0.05657,0.03378],"object_pos_start":[0.5061,0.05665,0.03377],"object_to_goal_dist_end":0.13685,"object_to_goal_dist_start":0.13693,"object_z_max":0.03378,"peak_contact_force":85.62562,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":172.0,"raw_peak_contact_force":85.62562,"subtask_id":"grasp_peg","tcp_end":[0.51485,0.0607,0.06149],"tcp_start":[0.53071,0.06561,0.09856],"tcp_to_object_dist_end":0.02933,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fd7ada9a67242f1adcdb6e23860d1223cdc8a17daf859e94e1687ff0564d9575`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14953,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_orientation.rotate_speed":0.72899,"approach_peg.approach_speed":0.07704,"descend_contact.contact_force_threshold":3.42589,"descend_contact.descend_speed":0.01989,"push_channel.push_distance":0.14639,"push_channel.push_speed":0.05364},"optimized_scores":{"best_composite_score":-0.00337,"best_fitness_score":0.21663,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":347.0,"contact_point_centroid":[0.475,0.09021,0.05999],"force_p95":69.22944,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.0036,"mean_force":59.31206,"phase_index":3.0,"phase_name":"align_orientation","phase_type":"rotate","tcp_position_centroid":[0.47678,0.0914,0.05975]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":429.0,"contact_point_centroid":[0.475,0.07057,0.05998],"force_p95":56.81512,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":64.74393,"mean_force":46.47875,"phase_index":2.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.47769,0.0822,0.05964]},{"body_a":"peg","body_b":"channel_base_body","contact_count":405.0,"contact_point_centroid":[0.48763,0.09926,0.00954],"force_p95":50.87176,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.27117,"mean_force":28.80843,"phase_index":3.0,"phase_name":"align_orientation","phase_type":"rotate","tcp_position_centroid":[0.4768,0.09131,0.05975]},{"body_a":"attachment","body_b":"peg","contact_count":405.0,"contact_point_centroid":[0.48865,0.09059,0.05859],"force_p95":50.36542,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.86119,"mean_force":28.34067,"phase_index":3.0,"phase_name":"align_orientation","phase_type":"rotate","tcp_position_centroid":[0.4768,0.09131,0.05975]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.48588,0.10516,0.00962],"force_p95":39.07428,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.07428,"mean_force":39.07428,"phase_index":4.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.47551,0.09955,0.05995]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.48738,0.09965,0.05875],"force_p95":38.65935,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.65935,"mean_force":38.65935,"phase_index":4.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.47551,0.09955,0.05995]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.48985,0.08165,0.00944],"force_p95":29.729,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.96489,"mean_force":26.22458,"phase_index":2.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.47769,0.0822,0.05966]},{"body_a":"attachment","body_b":"peg","contact_count":450.0,"contact_point_centroid":[0.48955,0.08176,0.05839],"force_p95":29.25396,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.51978,"mean_force":25.75992,"phase_index":2.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.47769,0.0822,0.05966]},{"body_a":"peg","body_b":"channel_base_body","contact_count":463.0,"contact_point_centroid":[0.49385,0.07998,0.00938],"force_p95":0.55033,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.45512,"mean_force":0.57672,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.47268,0.08376,0.07567]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.48986,0.08188,0.05877],"force_p95":13.93577,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.93577,"mean_force":13.93577,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.47799,0.08232,0.0605]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":56.0,"contact_point_centroid":[0.47499,0.08856,0.05934],"force_p95":0.57321,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.09975,"mean_force":0.61143,"phase_index":3.0,"phase_name":"align_orientation","phase_type":"rotate","tcp_position_centroid":[0.47564,0.0987,0.05992]},{"body_a":"peg","body_b":"channel_base_body","contact_count":721.0,"contact_point_centroid":[0.49404,0.07992,0.00937],"force_p95":0.5815,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.56428,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4832,0.1411,0.19401]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49907,0.198,0.29637]}],"total_contact_groups":13},"final_pose_error":0.1464,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49306,0.08874,0.03425],"final_tcp_position":[0.47551,0.09956,0.05995],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":79.0036,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":749.0,"n_steps_budget":1000.0,"object_pos_end":[0.49383,0.07996,0.03378],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.1602,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.54149,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":756.0,"raw_peak_contact_force":3.77147,"subtask_id":"pre_contact","tcp_end":[0.46876,0.08603,0.09745],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0687,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":463.0,"n_steps_budget":1000.0,"object_pos_end":[0.49382,0.07998,0.03378],"object_pos_start":[0.49383,0.07996,0.03378],"object_to_goal_dist_end":0.16022,"object_to_goal_dist_start":0.1602,"object_z_max":0.03378,"peak_contact_force":14.45512,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":464.0,"raw_peak_contact_force":14.45512,"subtask_id":"grasp_peg","tcp_end":[0.47802,0.08231,0.06045],"tcp_start":[0.46876,0.08603,0.09745],"tcp_to_object_dist_end":0.03108,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49411,0.07994,0.03388],"object_pos_start":[0.49382,0.07998,0.03378],"object_to_goal_dist_end":0.16016,"object_to_goal_dist_start":0.16022,"object_z_max":0.03396,"peak_contact_force":42.58883,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1329.0,"raw_peak_contact_force":64.74393,"subtask_id":"grasp_peg","tcp_end":[0.47787,0.08221,0.05963],"tcp_start":[0.47802,0.08231,0.06045],"tcp_to_object_dist_end":0.03052,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":405.0,"n_steps_budget":600.0,"object_pos_end":[0.49305,0.08873,0.03426],"object_pos_start":[0.49411,0.07994,0.03388],"object_to_goal_dist_end":0.16897,"object_to_goal_dist_start":0.16016,"object_z_max":0.03448,"peak_contact_force":1.0165,"phase_name":"align_orientation","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1213.0,"raw_peak_contact_force":79.0036,"tcp_end":[0.47551,0.09955,0.05995],"tcp_start":[0.47787,0.08221,0.05963],"tcp_to_object_dist_end":0.03294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49306,0.08874,0.03425],"object_pos_start":[0.49305,0.08873,0.03426],"object_to_goal_dist_end":0.16898,"object_to_goal_dist_start":0.16897,"object_z_max":0.03426,"peak_contact_force":60.65956,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":39.07428,"subtask_id":"push_channel","tcp_end":[0.47551,0.09956,0.05995],"tcp_start":[0.47551,0.09955,0.05995],"tcp_to_object_dist_end":0.03294,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```