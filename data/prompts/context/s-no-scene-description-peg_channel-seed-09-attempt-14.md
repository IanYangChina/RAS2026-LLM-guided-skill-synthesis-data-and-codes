## Search State

- **Seed**: 9
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2572 | 0.03 | ❌ rejected |
| 13 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2549 | 0.06 | ✅ accepted |
| 12 | approach → descend → grasp → rotate → push → release | linear_cartesian | linear_cartesian | — | joint_interpolation | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | time_limit | 6 | -0.1461 | 0.00 | ❌ rejected |
| 11 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2575 | 0.05 | ❌ rejected |
| 10 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2612 | 0.04 | ❌ rejected |

**Proposal policy**: task_score is 0.03 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.257) — your mutation base

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

- **Composite score**: -0.257
- **task_score** (E): 0.032
- **fitness_score**: 0.113  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_1 | 1.00 | 1.00 | 0.1691 |
| pull_1 | 1.00 | 1.00 | 0.1295 |
| push_1 | 1.00 | 1.00 | 0.2070 |
| descend_1 | 1.00 | 1.00 | 0.1676 |
| descend_2 | 1.00 | 1.00 | 0.0222 |
| grasp_1 | 1.00 | 1.00 | 0.0026 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.499, 0.051, 0.380) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.549 | 4.034 |
| pull_1 | pull | 1.00 / time_limit | (0.499, 0.051, 0.380)→(0.498, -0.075, 0.351) | (0.502, 0.067, 0.034)→(0.502, 0.066, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.546 | 0.552 |
| push_1 | push | 1.00 / time_limit | (0.498, -0.075, 0.351)→(0.496, -0.041, 0.147) | (0.502, 0.066, 0.034)→(0.502, 0.066, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.545 | 0.552 |
| descend_1 | descend | 1.00 / step_budget | (0.496, -0.041, 0.147)→(0.507, 0.095, 0.051) | (0.502, 0.066, 0.034)→(0.501, 0.081, 0.030) | 0.147→0.161 | 1.00 / 2.667 | 272.943 | 312.317 |
| descend_2 | descend | 1.00 / step_budget | (0.507, 0.095, 0.051)→(0.502, 0.112, 0.041) | (0.501, 0.081, 0.030)→(0.498, 0.065, 0.032) | 0.161→0.145 | 1.00 / 2.667 | 117.686 | 286.277 |
| grasp_1 | grasp | 1.00 / step_budget | (0.502, 0.112, 0.041)→(0.501, 0.113, 0.039) | (0.498, 0.065, 0.032)→(0.499, 0.062, 0.032) | 0.145→0.143 | 1.00 / 3.000 | 46.235 | 96.256 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.258
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.096
- phase_score: 0.151
- phase_breakdown.approach_score: 0.552
- phase_breakdown.contact_score: 0.000
- phase_breakdown.push_score: 0.068

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.129
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.096
- **Median Q (composite search score)**: -0.258
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.355


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41837,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"grasp_1.grip_force":24.37412,"pull_1.pull_distance":0.11161,"push_1.push_depth":0.06471,"push_1.push_distance":0.07283,"push_1.push_speed":0.04636},"optimized_scores":{"best_composite_score":-0.24088,"best_fitness_score":0.12912,"best_task_score":0.09619},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":84.0,"contact_point_centroid":[0.52512,0.08725,0.05995],"force_p95":319.54143,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":383.09198,"mean_force":235.40317,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50931,0.08723,0.05337]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":122.0,"contact_point_centroid":[0.54505,0.09862,0.0599],"force_p95":288.59159,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":293.03625,"mean_force":242.4271,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.49994,0.09766,0.03697]},{"body_a":"attachment","body_b":"peg","contact_count":222.0,"contact_point_centroid":[0.51597,0.0774,0.05438],"force_p95":167.31761,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":208.50159,"mean_force":127.87809,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50642,0.08068,0.05614]},{"body_a":"peg","body_b":"channel_base_body","contact_count":754.0,"contact_point_centroid":[0.50855,0.06825,0.00908],"force_p95":160.72935,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":193.41992,"mean_force":37.37019,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49954,0.03565,0.09634]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":450.0,"contact_point_centroid":[0.54575,0.0989,0.05998],"force_p95":76.3025,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.34132,"mean_force":68.91723,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50069,0.09794,0.03703]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":129.0,"contact_point_centroid":[0.52528,0.06821,0.05693],"force_p95":30.20548,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.01479,"mean_force":14.50864,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50585,0.07871,0.05677]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":411.0,"contact_point_centroid":[0.52501,0.09813,0.06],"force_p95":23.12544,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":23.13189,"mean_force":22.37247,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50069,0.09795,0.03703]},{"body_a":"peg","body_b":"channel_base_body","contact_count":209.0,"contact_point_centroid":[0.49694,0.03472,0.00888],"force_p95":1.13529,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.32069,"mean_force":0.6784,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50153,0.09578,0.0402]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50452,0.08002,0.05333],"force_p95":11.08062,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.37055,"mean_force":7.99199,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50797,0.09046,0.05154]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.5045,0.02121,0.0081],"force_p95":0.68645,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.12865,"mean_force":0.6973,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50069,0.09794,0.03703]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52501,0.04446,0.0244],"force_p95":7.75887,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.7917,"mean_force":3.38179,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50069,0.09794,0.03703]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50586,0.06296,0.00937],"force_p95":0.55508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56049,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49843,0.13187,0.34825]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.4993,0.19877,0.29989]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.475,0.02147,0.05394],"force_p95":0.66926,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68193,"mean_force":0.55526,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50034,0.09614,0.03866]},{"body_a":"peg","body_b":"channel_base_body","contact_count":787.0,"contact_point_centroid":[0.50601,0.06299,0.00938],"force_p95":0.55194,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54651,"phase_index":1.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49812,-0.01441,0.37954]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50599,0.06299,0.00939],"force_p95":0.55064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55442,"mean_force":0.54631,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49662,-0.054,0.25663]}],"total_contact_groups":17},"final_pose_error":0.00923,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50489,0.02168,0.02425],"final_tcp_position":[0.50052,0.0979,0.03699],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":383.09198,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54709,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1006.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.49865,0.0507,0.38034],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.34683,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":787.0,"n_steps_budget":840.0,"object_pos_end":[0.50593,0.06291,0.03384],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.14317,"object_to_goal_dist_start":0.14323,"object_z_max":0.03384,"peak_contact_force":0.54314,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":787.0,"raw_peak_contact_force":0.55532,"tcp_end":[0.4984,-0.07534,0.3508],"tcp_start":[0.49865,0.0507,0.38034],"tcp_to_object_dist_end":0.34588,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.06288,0.03386],"object_pos_start":[0.50593,0.06291,0.03384],"object_to_goal_dist_end":0.14313,"object_to_goal_dist_start":0.14317,"object_z_max":0.03386,"peak_contact_force":0.5494,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55442,"tcp_end":[0.49624,-0.03263,0.16598],"tcp_start":[0.4984,-0.07534,0.3508],"tcp_to_object_dist_end":0.16331,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":754.0,"n_steps_budget":1000.0,"object_pos_end":[0.49826,0.06498,0.03151],"object_pos_start":[0.50594,0.06288,0.03386],"object_to_goal_dist_end":0.14524,"object_to_goal_dist_start":0.14313,"object_z_max":0.03393,"peak_contact_force":383.09198,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1189.0,"raw_peak_contact_force":383.09198,"tcp_end":[0.50812,0.09035,0.05175],"tcp_start":[0.49624,-0.03263,0.16598],"tcp_to_object_dist_end":0.03392,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":218.0,"n_steps_budget":600.0,"object_pos_end":[0.5008,0.02134,0.02408],"object_pos_start":[0.49826,0.06498,0.03151],"object_to_goal_dist_end":0.10259,"object_to_goal_dist_start":0.14524,"object_z_max":0.04081,"peak_contact_force":277.73784,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":337.0,"raw_peak_contact_force":293.03625,"tcp_end":[0.50052,0.0979,0.03699],"tcp_start":[0.50812,0.09035,0.05175],"tcp_to_object_dist_end":0.07764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50489,0.02168,0.02425],"object_pos_start":[0.5008,0.02134,0.02408],"object_to_goal_dist_end":0.10301,"object_to_goal_dist_start":0.10259,"object_z_max":0.0251,"peak_contact_force":67.73654,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1325.0,"raw_peak_contact_force":77.34132,"tcp_end":[0.50069,0.09797,0.03703],"tcp_start":[0.50052,0.0979,0.03699],"tcp_to_object_dist_end":0.07746,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `cae0d95026bac46aa2e5d95cffd531753a79751757c4f25fa56c1ec6e19c2175`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79518,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"grasp_1.grip_force":18.08155,"pull_1.pull_distance":0.15824,"push_1.push_depth":0.0968,"push_1.push_distance":0.12727,"push_1.push_speed":0.09957},"optimized_scores":{"best_composite_score":-0.2579,"best_fitness_score":0.1121,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":109.0,"contact_point_centroid":[0.52509,0.07617,0.05996],"force_p95":311.51235,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":324.98512,"mean_force":197.90886,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50819,0.07616,0.05131]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":500.0,"contact_point_centroid":[0.52508,0.08444,0.05996],"force_p95":268.83777,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":280.7067,"mean_force":198.74752,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50748,0.08432,0.05132]},{"body_a":"peg","body_b":"channel_base_body","contact_count":769.0,"contact_point_centroid":[0.5101,0.06254,0.00863],"force_p95":201.74759,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":232.73472,"mean_force":52.11629,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49974,0.0234,0.0814]},{"body_a":"attachment","body_b":"peg","contact_count":293.0,"contact_point_centroid":[0.51638,0.06598,0.05245],"force_p95":212.75001,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":231.51221,"mean_force":135.78258,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50541,0.066,0.05495]},{"body_a":"peg","body_b":"channel_base_body","contact_count":513.0,"contact_point_centroid":[0.51137,0.07783,0.00735],"force_p95":204.37071,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":211.93801,"mean_force":181.55498,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50747,0.08441,0.05131]},{"body_a":"attachment","body_b":"peg","contact_count":513.0,"contact_point_centroid":[0.51727,0.08068,0.05033],"force_p95":203.89782,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":211.50056,"mean_force":183.19327,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50747,0.08441,0.05131]},{"body_a":"attachment","body_b":"peg","contact_count":450.0,"contact_point_centroid":[0.50658,0.0879,0.04689],"force_p95":101.97404,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":119.1456,"mean_force":30.6924,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50417,0.0992,0.04729]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.49614,0.0585,0.00955],"force_p95":100.01368,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":116.68173,"mean_force":29.18682,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50417,0.0992,0.04729]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":109.0,"contact_point_centroid":[0.52501,0.09879,0.06],"force_p95":61.44611,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.1669,"mean_force":47.56023,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50608,0.09856,0.0497]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":164.0,"contact_point_centroid":[0.52526,0.06572,0.04425],"force_p95":23.7878,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.19868,"mean_force":8.76878,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50504,0.06342,0.05568]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":207.0,"contact_point_centroid":[0.47418,0.06604,0.01692],"force_p95":54.92664,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.36321,"mean_force":48.69303,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50708,0.0886,0.05103]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":450.0,"contact_point_centroid":[0.47474,0.04938,0.0247],"force_p95":37.88496,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.75948,"mean_force":12.87712,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50417,0.0992,0.04729]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.506,0.05661,0.00937],"force_p95":0.59948,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56302,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49843,0.1318,0.3483]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49926,0.19868,0.29987]},{"body_a":"peg","body_b":"channel_base_body","contact_count":787.0,"contact_point_centroid":[0.50611,0.0566,0.00938],"force_p95":0.55015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55021,"mean_force":0.54674,"phase_index":1.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49812,-0.01441,0.37954]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50615,0.05664,0.00938],"force_p95":0.55015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55015,"mean_force":0.54674,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4966,-0.06325,0.24119]}],"total_contact_groups":16},"final_pose_error":0.02636,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4971,0.05985,0.03926],"final_tcp_position":[0.50565,0.09662,0.0489],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":324.98512,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.0566,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54967,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1008.0,"raw_peak_contact_force":4.44541,"tcp_end":[0.49865,0.0507,0.38034],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.3467,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":787.0,"n_steps_budget":840.0,"object_pos_end":[0.50611,0.05662,0.03378],"object_pos_start":[0.50611,0.0566,0.03378],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.13688,"object_z_max":0.03378,"peak_contact_force":0.54553,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":787.0,"raw_peak_contact_force":0.55021,"tcp_end":[0.4984,-0.07534,0.3508],"tcp_start":[0.49865,0.0507,0.38034],"tcp_to_object_dist_end":0.34348,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05659,0.03378],"object_pos_start":[0.50611,0.05662,0.03378],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.1369,"object_z_max":0.03378,"peak_contact_force":0.54501,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55015,"tcp_end":[0.49622,-0.05129,0.13548],"tcp_start":[0.4984,-0.07534,0.3508],"tcp_to_object_dist_end":0.1486,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":769.0,"n_steps_budget":1000.0,"object_pos_end":[0.50551,0.07295,0.02822],"object_pos_start":[0.50613,0.05659,0.03378],"object_to_goal_dist_end":0.1535,"object_to_goal_dist_start":0.13687,"object_z_max":0.03382,"peak_contact_force":214.8975,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1335.0,"raw_peak_contact_force":324.98512,"tcp_end":[0.50747,0.07935,0.05052],"tcp_start":[0.49622,-0.05129,0.13548],"tcp_to_object_dist_end":0.02328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49741,0.06976,0.03673],"object_pos_start":[0.50551,0.07295,0.02822],"object_to_goal_dist_end":0.14981,"object_to_goal_dist_start":0.1535,"object_z_max":0.0367,"peak_contact_force":71.83669,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1733.0,"raw_peak_contact_force":280.7067,"tcp_end":[0.50565,0.09662,0.0489],"tcp_start":[0.50747,0.07935,0.05052],"tcp_to_object_dist_end":0.03062,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4971,0.05985,0.03926],"object_pos_start":[0.49741,0.06976,0.03673],"object_to_goal_dist_end":0.13988,"object_to_goal_dist_start":0.14981,"object_z_max":0.03975,"peak_contact_force":1.38738,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1459.0,"raw_peak_contact_force":119.1456,"tcp_end":[0.50216,0.09818,0.04483],"tcp_start":[0.50565,0.09662,0.0489],"tcp_to_object_dist_end":0.03906,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fd7ada9a67242f1adcdb6e23860d1223cdc8a17daf859e94e1687ff0564d9575`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7929,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"grasp_1.grip_force":14.30654,"pull_1.pull_distance":0.08987,"push_1.push_depth":0.09993,"push_1.push_distance":0.02054,"push_1.push_speed":0.09837},"optimized_scores":{"best_composite_score":-0.27272,"best_fitness_score":0.09728,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":289.0,"contact_point_centroid":[0.52507,0.11839,0.05997],"force_p95":272.3507,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":285.08862,"mean_force":222.5398,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50873,0.11855,0.05174]},{"body_a":"peg","body_b":"channel_base_body","contact_count":814.0,"contact_point_centroid":[0.49956,0.0867,0.00871],"force_p95":222.27026,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":228.87293,"mean_force":55.38804,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49421,0.04322,0.08287]},{"body_a":"attachment","body_b":"peg","contact_count":304.0,"contact_point_centroid":[0.50864,0.09123,0.05255],"force_p95":226.06094,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":228.42713,"mean_force":146.88488,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49768,0.0914,0.05486]},{"body_a":"attachment","body_b":"peg","contact_count":443.0,"contact_point_centroid":[0.51407,0.11433,0.04962],"force_p95":158.94033,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":182.71422,"mean_force":132.90801,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50794,0.12357,0.04934]},{"body_a":"peg","body_b":"channel_base_body","contact_count":434.0,"contact_point_centroid":[0.50357,0.10412,0.00817],"force_p95":157.8198,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":181.46954,"mean_force":132.68269,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50806,0.12318,0.0496]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":436.0,"contact_point_centroid":[0.55058,0.12,0.05997],"force_p95":85.38949,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.28155,"mean_force":74.92581,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50001,0.14221,0.03415]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":400.0,"contact_point_centroid":[0.47425,0.09584,0.01844],"force_p95":47.74783,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.35407,"mean_force":40.90213,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50804,0.12393,0.04939]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.49397,0.07995,0.00937],"force_p95":0.57014,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.55973,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49843,0.13187,0.34825]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49929,0.19874,0.29988]},{"body_a":"peg","body_b":"channel_base_body","contact_count":444.0,"contact_point_centroid":[0.49506,0.08333,0.00999],"force_p95":0.53272,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.90299,"mean_force":0.45785,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50003,0.14222,0.03417]},{"body_a":"attachment","body_b":"peg","contact_count":420.0,"contact_point_centroid":[0.50126,0.13031,0.03359],"force_p95":0.39191,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.21345,"mean_force":0.29326,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50003,0.14222,0.03417]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":25.0,"contact_point_centroid":[0.47485,0.11999,0.03713],"force_p95":0.69895,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71997,"mean_force":0.42706,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4998,0.14213,0.03396]},{"body_a":"peg","body_b":"channel_base_body","contact_count":787.0,"contact_point_centroid":[0.49382,0.07993,0.00938],"force_p95":0.55022,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55037,"mean_force":0.54669,"phase_index":1.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49812,-0.01441,0.37954]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49382,0.07998,0.00938],"force_p95":0.55021,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55021,"mean_force":0.54668,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4966,-0.05678,0.24297]}],"total_contact_groups":14},"final_pose_error":0.0048,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4938,0.10506,0.03104],"final_tcp_position":[0.5013,0.14242,0.03576],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":285.08862,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49382,0.07993,0.03378],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16017,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.55002,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1007.0,"raw_peak_contact_force":3.77147,"tcp_end":[0.49865,0.0507,0.38034],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.34783,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":787.0,"n_steps_budget":840.0,"object_pos_end":[0.49382,0.07994,0.03378],"object_pos_start":[0.49382,0.07993,0.03378],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.16017,"object_z_max":0.03378,"peak_contact_force":0.54922,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":787.0,"raw_peak_contact_force":0.55037,"tcp_end":[0.4984,-0.07534,0.3508],"tcp_start":[0.49865,0.0507,0.38034],"tcp_to_object_dist_end":0.35304,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49379,0.07995,0.03378],"object_pos_start":[0.49382,0.07994,0.03378],"object_to_goal_dist_end":0.16019,"object_to_goal_dist_start":0.16018,"object_z_max":0.03378,"peak_contact_force":0.54143,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55021,"tcp_end":[0.49614,-0.03836,0.13925],"tcp_start":[0.4984,-0.07534,0.3508],"tcp_to_object_dist_end":0.15851,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":814.0,"n_steps_budget":1000.0,"object_pos_end":[0.4995,0.10393,0.03158],"object_pos_start":[0.49379,0.07995,0.03378],"object_to_goal_dist_end":0.18412,"object_to_goal_dist_start":0.16019,"object_z_max":0.03378,"peak_contact_force":220.8388,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1118.0,"raw_peak_contact_force":228.87293,"tcp_end":[0.50587,0.11512,0.0493],"tcp_start":[0.49614,-0.03836,0.13925],"tcp_to_object_dist_end":0.02191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":443.0,"n_steps_budget":600.0,"object_pos_end":[0.49552,0.1038,0.03611],"object_pos_start":[0.4995,0.10393,0.03158],"object_to_goal_dist_end":0.1839,"object_to_goal_dist_start":0.18412,"object_z_max":0.03792,"peak_contact_force":3.48207,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1566.0,"raw_peak_contact_force":285.08862,"tcp_end":[0.5013,0.14242,0.03576],"tcp_start":[0.50587,0.11512,0.0493],"tcp_to_object_dist_end":0.03906,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4938,0.10506,0.03104],"object_pos_start":[0.49552,0.1038,0.03611],"object_to_goal_dist_end":0.18538,"object_to_goal_dist_start":0.1839,"object_z_max":0.03611,"peak_contact_force":69.58137,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1325.0,"raw_peak_contact_force":92.28155,"tcp_end":[0.5002,0.14228,0.03414],"tcp_start":[0.5013,0.14242,0.03576],"tcp_to_object_dist_end":0.03789,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```