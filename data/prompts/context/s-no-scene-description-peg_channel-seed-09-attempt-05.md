## Search State

- **Seed**: 9
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2566 | 0.05 | ❌ rejected |
| 4 | approach → align → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | -0.1558 | 0.00 | ❌ rejected |
| 3 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2569 | 0.06 | ❌ rejected |
| 2 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2568 | 0.06 | ✅ accepted |
| 1 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2566 | 0.06 | ✅ accepted |

**Proposal policy**: task_score is 0.05 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- **task_score** (E): 0.053
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
| push_1 | 1.00 | 1.00 | 0.2026 |
| descend_1 | 1.00 | 1.00 | 0.1633 |
| descend_2 | 1.00 | 1.00 | 0.0206 |
| grasp_1 | 1.00 | 1.00 | 0.0012 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.499, 0.051, 0.380) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.549 | 4.034 |
| pull_1 | pull | 1.00 / time_limit | (0.499, 0.051, 0.380)→(0.498, -0.075, 0.351) | (0.502, 0.067, 0.034)→(0.502, 0.066, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.546 | 0.552 |
| push_1 | push | 1.00 / time_limit | (0.498, -0.075, 0.351)→(0.496, -0.029, 0.154) | (0.502, 0.066, 0.034)→(0.502, 0.066, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.545 | 0.552 |
| descend_1 | descend | 1.00 / step_budget | (0.496, -0.029, 0.154)→(0.507, 0.097, 0.051) | (0.502, 0.066, 0.034)→(0.498, 0.074, 0.032) | 0.147→0.155 | 1.00 / 2.667 | 171.618 | 298.738 |
| descend_2 | descend | 1.00 / step_budget | (0.507, 0.097, 0.051)→(0.500, 0.109, 0.037) | (0.498, 0.074, 0.032)→(0.498, 0.047, 0.032) | 0.155→0.128 | 1.00 / 2.333 | 64.372 | 279.329 |
| grasp_1 | grasp | 1.00 / step_budget | (0.500, 0.109, 0.037)→(0.500, 0.109, 0.036) | (0.498, 0.047, 0.032)→(0.501, 0.046, 0.027) | 0.128→0.127 | 1.00 / 3.000 | 69.083 | 88.746 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.256
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.095
- phase_score: 0.152
- phase_breakdown.approach_score: 0.555
- phase_breakdown.contact_score: 0.000
- phase_breakdown.push_score: 0.068

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.129
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.095
- **Median Q (composite search score)**: -0.257
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.361


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41837,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"grasp_1.grip_force":18.12334,"pull_1.pull_distance":0.11843,"push_1.push_depth":0.06444,"push_1.push_distance":0.13362,"push_1.push_speed":0.04893},"optimized_scores":{"best_composite_score":-0.24116,"best_fitness_score":0.12884,"best_task_score":0.09477},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":85.0,"contact_point_centroid":[0.52513,0.08727,0.05994],"force_p95":311.29977,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":338.10065,"mean_force":236.09572,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50935,0.08725,0.05342]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":122.0,"contact_point_centroid":[0.54542,0.09865,0.0599],"force_p95":267.25972,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":269.85649,"mean_force":223.97816,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50032,0.09768,0.03696]},{"body_a":"attachment","body_b":"peg","contact_count":222.0,"contact_point_centroid":[0.51605,0.0774,0.0544],"force_p95":166.8064,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":207.62458,"mean_force":127.86722,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50645,0.08072,0.05618]},{"body_a":"peg","body_b":"channel_base_body","contact_count":753.0,"contact_point_centroid":[0.50846,0.06817,0.00908],"force_p95":160.5334,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":192.55903,"mean_force":37.44431,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49956,0.03576,0.09632]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":31.0,"contact_point_centroid":[0.52504,0.09804,0.05998],"force_p95":189.88372,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":190.1846,"mean_force":165.39833,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50073,0.09785,0.03701]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":450.0,"contact_point_centroid":[0.54577,0.09888,0.05998],"force_p95":74.53179,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.6914,"mean_force":68.84019,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50069,0.09791,0.03707]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":450.0,"contact_point_centroid":[0.52501,0.0981,0.06],"force_p95":59.62698,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":68.71194,"mean_force":27.65233,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50069,0.09791,0.03707]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":129.0,"contact_point_centroid":[0.52528,0.06832,0.05694],"force_p95":30.59085,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.54744,"mean_force":14.37296,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50594,0.07891,0.05672]},{"body_a":"peg","body_b":"channel_base_body","contact_count":213.0,"contact_point_centroid":[0.49827,0.03461,0.009],"force_p95":1.23449,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.33919,"mean_force":0.80425,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50187,0.09569,0.04037]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.5049,0.0794,0.05386],"force_p95":17.22551,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.75419,"mean_force":12.8296,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50814,0.09009,0.05218]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":20.0,"contact_point_centroid":[0.47489,0.04664,0.03838],"force_p95":8.01707,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.59154,"mean_force":1.28258,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50314,0.09505,0.04224]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50138,0.02206,0.0081],"force_p95":0.65685,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.4779,"mean_force":0.62317,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50069,0.09791,0.03707]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52501,-0.00173,0.02428],"force_p95":6.97869,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.13334,"mean_force":2.32305,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50068,0.09793,0.03708]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50586,0.06296,0.00937],"force_p95":0.55508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56049,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49843,0.13187,0.34825]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.4993,0.19877,0.29989]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52511,0.01832,0.05152],"force_p95":0.91213,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.96229,"mean_force":0.58358,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50081,0.0959,0.03906]}],"total_contact_groups":18},"final_pose_error":0.00922,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50476,0.02201,0.02415],"final_tcp_position":[0.50077,0.09789,0.03701],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":338.10065,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54709,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1006.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.49865,0.0507,0.38034],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.34683,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":787.0,"n_steps_budget":840.0,"object_pos_end":[0.50593,0.06291,0.03384],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.14317,"object_to_goal_dist_start":0.14323,"object_z_max":0.03384,"peak_contact_force":0.54314,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":787.0,"raw_peak_contact_force":0.55532,"tcp_end":[0.4984,-0.07534,0.3508],"tcp_start":[0.49865,0.0507,0.38034],"tcp_to_object_dist_end":0.34588,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.06288,0.03386],"object_pos_start":[0.50593,0.06291,0.03384],"object_to_goal_dist_end":0.14313,"object_to_goal_dist_start":0.14317,"object_z_max":0.03386,"peak_contact_force":0.5494,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55442,"tcp_end":[0.49624,-0.03247,0.16598],"tcp_start":[0.4984,-0.07534,0.3508],"tcp_to_object_dist_end":0.16322,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":753.0,"n_steps_budget":1000.0,"object_pos_end":[0.49907,0.06509,0.0315],"object_pos_start":[0.50594,0.06288,0.03386],"object_to_goal_dist_end":0.14534,"object_to_goal_dist_start":0.14313,"object_z_max":0.0339,"peak_contact_force":11.82427,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1189.0,"raw_peak_contact_force":338.10065,"tcp_end":[0.50823,0.08998,0.0523],"tcp_start":[0.49624,-0.03247,0.16598],"tcp_to_object_dist_end":0.03371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":224.0,"n_steps_budget":600.0,"object_pos_end":[0.49523,0.02154,0.02482],"object_pos_start":[0.49907,0.06509,0.0315],"object_to_goal_dist_end":0.10277,"object_to_goal_dist_start":0.14534,"object_z_max":0.04081,"peak_contact_force":190.1846,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":396.0,"raw_peak_contact_force":269.85649,"tcp_end":[0.50077,0.09789,0.03701],"tcp_start":[0.50823,0.08998,0.0523],"tcp_to_object_dist_end":0.07752,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50476,0.02201,0.02415],"object_pos_start":[0.49523,0.02154,0.02482],"object_to_goal_dist_end":0.10334,"object_to_goal_dist_start":0.10277,"object_z_max":0.02482,"peak_contact_force":67.9843,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1354.0,"raw_peak_contact_force":90.6914,"tcp_end":[0.50068,0.09793,0.03708],"tcp_start":[0.50077,0.09789,0.03701],"tcp_to_object_dist_end":0.07712,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `cae0d95026bac46aa2e5d95cffd531753a79751757c4f25fa56c1ec6e19c2175`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75429,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"grasp_1.grip_force":18.60174,"pull_1.pull_distance":0.11873,"push_1.push_depth":0.04975,"push_1.push_distance":0.1511,"push_1.push_speed":0.07524},"optimized_scores":{"best_composite_score":-0.25682,"best_fitness_score":0.11318,"best_task_score":0.0655},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":84.0,"contact_point_centroid":[0.52513,0.08099,0.05994],"force_p95":319.43843,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":345.36805,"mean_force":239.18109,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50928,0.08097,0.05334]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":123.0,"contact_point_centroid":[0.54514,0.09165,0.0599],"force_p95":291.53578,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":295.88997,"mean_force":245.1915,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.49997,0.09102,0.03707]},{"body_a":"attachment","body_b":"peg","contact_count":221.0,"contact_point_centroid":[0.51573,0.07117,0.05435],"force_p95":167.52241,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":208.04278,"mean_force":126.1149,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50633,0.07456,0.05608]},{"body_a":"peg","body_b":"channel_base_body","contact_count":680.0,"contact_point_centroid":[0.50886,0.06217,0.00903],"force_p95":161.66591,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":193.09063,"mean_force":40.6238,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49975,0.03642,0.09015]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":450.0,"contact_point_centroid":[0.54579,0.09191,0.05998],"force_p95":75.50794,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":81.83881,"mean_force":68.75861,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50066,0.0913,0.03714]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":129.0,"contact_point_centroid":[0.52531,0.06152,0.05653],"force_p95":31.23121,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.46048,"mean_force":15.6109,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50569,0.07256,0.05673]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":442.0,"contact_point_centroid":[0.52501,0.09148,0.06],"force_p95":27.91476,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":30.50406,"mean_force":24.03291,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50066,0.0913,0.03714]},{"body_a":"peg","body_b":"channel_base_body","contact_count":211.0,"contact_point_centroid":[0.50009,0.04149,0.00983],"force_p95":0.51393,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.44175,"mean_force":0.55944,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5015,0.08926,0.04021]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50437,0.0734,0.0533],"force_p95":12.69692,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.9672,"mean_force":10.2644,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50796,0.08414,0.05149]},{"body_a":"peg","body_b":"channel_base_body","contact_count":448.0,"contact_point_centroid":[0.50033,0.01479,0.00813],"force_p95":0.77599,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.67629,"mean_force":0.66311,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50066,0.0913,0.03714]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47495,0.03701,0.02437],"force_p95":7.17637,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.42203,"mean_force":1.87609,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50066,0.09129,0.03714]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52501,-0.00733,0.02425],"force_p95":5.98329,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.96258,"mean_force":2.04337,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50066,0.09132,0.03714]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.506,0.05661,0.00937],"force_p95":0.59948,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56302,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49843,0.1318,0.3483]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49926,0.19868,0.29987]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":25.0,"contact_point_centroid":[0.52514,0.02337,0.05699],"force_p95":0.3053,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.99672,"mean_force":0.12147,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.49974,0.09096,0.037]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47487,0.0414,0.05985],"force_p95":0.7209,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76469,"mean_force":0.44321,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50584,0.08522,0.04831]}],"total_contact_groups":19},"final_pose_error":0.0094,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50404,0.0153,0.02433],"final_tcp_position":[0.50055,0.09126,0.03709],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":345.36805,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.0566,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54967,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1008.0,"raw_peak_contact_force":4.44541,"tcp_end":[0.49865,0.0507,0.38034],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.3467,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":787.0,"n_steps_budget":840.0,"object_pos_end":[0.50611,0.05662,0.03378],"object_pos_start":[0.50611,0.0566,0.03378],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.13688,"object_z_max":0.03378,"peak_contact_force":0.54553,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":787.0,"raw_peak_contact_force":0.55021,"tcp_end":[0.4984,-0.07534,0.3508],"tcp_start":[0.49865,0.0507,0.38034],"tcp_to_object_dist_end":0.34348,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05659,0.03378],"object_pos_start":[0.50611,0.05662,0.03378],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.1369,"object_z_max":0.03378,"peak_contact_force":0.54501,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55015,"tcp_end":[0.49622,-0.02413,0.15265],"tcp_start":[0.4984,-0.07534,0.3508],"tcp_to_object_dist_end":0.14403,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":680.0,"n_steps_budget":1000.0,"object_pos_end":[0.4981,0.05825,0.03131],"object_pos_start":[0.50613,0.05659,0.03378],"object_to_goal_dist_end":0.13854,"object_to_goal_dist_start":0.13687,"object_z_max":0.03386,"peak_contact_force":297.67214,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1114.0,"raw_peak_contact_force":345.36805,"tcp_end":[0.50803,0.08407,0.05159],"tcp_start":[0.49622,-0.02413,0.15265],"tcp_to_object_dist_end":0.0343,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":216.0,"n_steps_budget":600.0,"object_pos_end":[0.50406,0.0212,0.03348],"object_pos_start":[0.4981,0.05825,0.03131],"object_to_goal_dist_end":0.10149,"object_to_goal_dist_start":0.13854,"object_z_max":0.0408,"peak_contact_force":0.0,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":369.0,"raw_peak_contact_force":295.88997,"tcp_end":[0.50055,0.09126,0.03709],"tcp_start":[0.50803,0.08407,0.05159],"tcp_to_object_dist_end":0.07024,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50404,0.0153,0.02433],"object_pos_start":[0.50406,0.0212,0.03348],"object_to_goal_dist_end":0.09666,"object_to_goal_dist_start":0.10149,"object_z_max":0.03348,"peak_contact_force":67.96037,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1353.0,"raw_peak_contact_force":81.83881,"tcp_end":[0.50066,0.09132,0.03714],"tcp_start":[0.50055,0.09126,0.03709],"tcp_to_object_dist_end":0.07717,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fd7ada9a67242f1adcdb6e23860d1223cdc8a17daf859e94e1687ff0564d9575`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79167,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"grasp_1.grip_force":23.8747,"pull_1.pull_distance":0.12299,"push_1.push_depth":0.08757,"push_1.push_distance":0.13075,"push_1.push_speed":0.09813},"optimized_scores":{"best_composite_score":-0.27193,"best_fitness_score":0.09807,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":190.0,"contact_point_centroid":[0.52505,0.11953,0.05998],"force_p95":263.99461,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":272.24016,"mean_force":182.1027,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50858,0.11963,0.05136]},{"body_a":"peg","body_b":"channel_base_body","contact_count":785.0,"contact_point_centroid":[0.49912,0.08655,0.0088],"force_p95":206.08238,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":212.74397,"mean_force":54.14306,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49429,0.0468,0.08428]},{"body_a":"attachment","body_b":"peg","contact_count":287.0,"contact_point_centroid":[0.50869,0.09229,0.05295],"force_p95":208.48638,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":212.30104,"mean_force":146.52039,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49789,0.09334,0.05515]},{"body_a":"peg","body_b":"channel_base_body","contact_count":344.0,"contact_point_centroid":[0.5011,0.09932,0.00841],"force_p95":149.25579,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":164.71033,"mean_force":113.91424,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50719,0.1238,0.04901]},{"body_a":"attachment","body_b":"peg","contact_count":351.0,"contact_point_centroid":[0.51155,0.11381,0.04932],"force_p95":145.83006,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":150.36865,"mean_force":112.62833,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50705,0.12406,0.0488]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":419.0,"contact_point_centroid":[0.54659,0.12,0.05997],"force_p95":90.16885,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.70815,"mean_force":76.41298,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49736,0.13685,0.03467]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":346.0,"contact_point_centroid":[0.47438,0.08953,0.01905],"force_p95":38.98771,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.13731,"mean_force":35.00687,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50715,0.12387,0.04896]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.47476,0.0964,0.01369],"force_p95":32.59373,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.14965,"mean_force":24.87431,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50564,0.11502,0.04951]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.49397,0.07995,0.00937],"force_p95":0.57014,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.55973,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49843,0.13187,0.34825]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49929,0.19874,0.29988]},{"body_a":"peg","body_b":"channel_base_body","contact_count":442.0,"contact_point_centroid":[0.49332,0.07933,0.00998],"force_p95":0.57754,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.82898,"mean_force":0.46542,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4974,0.13686,0.03473]},{"body_a":"attachment","body_b":"peg","contact_count":416.0,"contact_point_centroid":[0.49849,0.12493,0.03422],"force_p95":0.28201,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.3351,"mean_force":0.26435,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49739,0.13686,0.03471]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":22.0,"contact_point_centroid":[0.47499,0.12,0.03828],"force_p95":0.5556,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65575,"mean_force":0.15159,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49764,0.13694,0.03491]},{"body_a":"peg","body_b":"channel_base_body","contact_count":787.0,"contact_point_centroid":[0.49382,0.07993,0.00938],"force_p95":0.55022,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55037,"mean_force":0.54669,"phase_index":1.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49812,-0.01441,0.37954]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49382,0.07998,0.00938],"force_p95":0.55021,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55021,"mean_force":0.54668,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49661,-0.05298,0.24429]}],"total_contact_groups":15},"final_pose_error":0.00484,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49315,0.09989,0.03232],"final_tcp_position":[0.49947,0.13722,0.03735],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":272.24016,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49382,0.07993,0.03378],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16017,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.55002,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1007.0,"raw_peak_contact_force":3.77147,"tcp_end":[0.49865,0.0507,0.38034],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.34783,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":787.0,"n_steps_budget":840.0,"object_pos_end":[0.49382,0.07994,0.03378],"object_pos_start":[0.49382,0.07993,0.03378],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.16017,"object_z_max":0.03378,"peak_contact_force":0.54922,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":787.0,"raw_peak_contact_force":0.55037,"tcp_end":[0.4984,-0.07534,0.3508],"tcp_start":[0.49865,0.0507,0.38034],"tcp_to_object_dist_end":0.35304,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49379,0.07995,0.03378],"object_pos_start":[0.49382,0.07994,0.03378],"object_to_goal_dist_end":0.16019,"object_to_goal_dist_start":0.16018,"object_z_max":0.03378,"peak_contact_force":0.54143,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55021,"tcp_end":[0.49623,-0.0308,0.14205],"tcp_start":[0.4984,-0.07534,0.3508],"tcp_to_object_dist_end":0.1549,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":785.0,"n_steps_budget":1000.0,"object_pos_end":[0.49756,0.09978,0.03371],"object_pos_start":[0.49379,0.07995,0.03378],"object_to_goal_dist_end":0.17991,"object_to_goal_dist_start":0.16019,"object_z_max":0.03379,"peak_contact_force":205.35681,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1085.0,"raw_peak_contact_force":212.74397,"tcp_end":[0.50592,0.11602,0.04923],"tcp_start":[0.49623,-0.0308,0.14205],"tcp_to_object_dist_end":0.02396,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":351.0,"n_steps_budget":600.0,"object_pos_end":[0.49467,0.09834,0.03686],"object_pos_start":[0.49756,0.09978,0.03371],"object_to_goal_dist_end":0.17845,"object_to_goal_dist_start":0.17991,"object_z_max":0.03847,"peak_contact_force":2.93105,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1231.0,"raw_peak_contact_force":272.24016,"tcp_end":[0.49947,0.13722,0.03735],"tcp_start":[0.50592,0.11602,0.04923],"tcp_to_object_dist_end":0.03918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49315,0.09989,0.03232],"object_pos_start":[0.49467,0.09834,0.03686],"object_to_goal_dist_end":0.18018,"object_to_goal_dist_start":0.17845,"object_z_max":0.03686,"peak_contact_force":71.30555,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1299.0,"raw_peak_contact_force":93.70815,"tcp_end":[0.49755,0.13692,0.03466],"tcp_start":[0.49947,0.13722,0.03735],"tcp_to_object_dist_end":0.03737,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```