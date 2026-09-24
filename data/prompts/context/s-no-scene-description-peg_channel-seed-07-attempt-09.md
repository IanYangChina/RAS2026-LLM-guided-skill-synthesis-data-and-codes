## Search State

- **Seed**: 7
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | -0.2871 | 0.00 | ❌ rejected |
| 8 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1314 | 0.26 | ❌ rejected |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.2220 | 0.00 | ❌ rejected |
| 6 | approach → descend → grasp → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | time_limit | pose_tolerance | 5 | -0.3038 | 0.00 | ❌ rejected |
| 5 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1315 | 0.26 | ❌ rejected |

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

## Current Skill (Q=-0.287) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: insert_1
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: pose_tolerance
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
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
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

```

## Design Metrics

- **Composite score**: -0.287
- **task_score** (E): 0.000
- **fitness_score**: 0.053  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1757 |
| descend_1 | 1.00 | 1.00 | 0.0952 |
| align_1 | 0.00 | 1.00 | 0.1711 |
| push_1 | 0.00 | 1.00 | 0.0002 |
| retract_1 | 1.00 | 1.00 | 0.0901 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.503, 0.110, 0.151) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.573 | 2.732 |
| descend_1 | descend | 1.00 / step_budget | (0.503, 0.110, 0.151)→(0.499, 0.098, 0.058) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.033) | 0.178→0.178 | 1.00 / 2.000 | 69.513 | 69.513 |
| align_1 | align | 0.00 / step_budget | (0.499, 0.098, 0.058)→(0.457, -0.012, 0.180) | (0.502, 0.098, 0.033)→(0.523, 0.127, 0.021) | 0.178→0.210 | 1.00 / 2.333 | 215.765 | 1117.542 |
| push_1 | push | 0.00 / guard_failure | (0.457, -0.012, 0.180)→(0.457, -0.012, 0.181) | (0.523, 0.127, 0.021)→(0.523, 0.127, 0.021) | 0.210→0.210 | 1.00 / 2.333 | 75.163 | 75.163 |
| retract_1 | retract | 1.00 / step_budget | (0.457, -0.012, 0.181)→(0.456, -0.012, 0.271) | (0.523, 0.127, 0.021)→(0.555, 0.127, 0.021) | 0.210→0.217 | 1.00 / 1.000 | 0.547 | 71.504 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.114
- phase_breakdown.push_goal_score: 0.086
- phase_breakdown.reach_peg_score: 0.179

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.068
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.295
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.388


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66667,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.01411,"align_1.lateral_offset_y":-0.01103,"approach_1.approach_speed":0.06123,"push_1.push_force_threshold":29.982,"push_1.push_speed":0.07445},"optimized_scores":{"best_composite_score":-0.29469,"best_fitness_score":0.04531,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":529.0,"contact_point_centroid":[0.53448,0.0413,0.05985],"force_p95":507.64075,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1083.23904,"mean_force":362.23357,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52206,0.0974,0.14608]},{"body_a":"channel_base_body","body_b":"link6","contact_count":510.0,"contact_point_centroid":[0.54949,-0.11096,0.06487],"force_p95":382.27404,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":421.04299,"mean_force":302.50798,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47755,0.05002,0.17005]},{"body_a":"attachment","body_b":"peg","contact_count":45.0,"contact_point_centroid":[0.51115,0.12423,0.05506],"force_p95":314.2544,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":318.19217,"mean_force":210.33647,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50701,0.13389,0.05744]},{"body_a":"peg","body_b":"channel_base_body","contact_count":95.0,"contact_point_centroid":[0.50595,0.11907,0.00825],"force_p95":238.1893,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":255.81892,"mean_force":80.65543,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51508,0.13627,0.07395]},{"body_a":"peg","body_b":"world","contact_count":955.0,"contact_point_centroid":[0.50958,0.15693,-0.00178],"force_p95":0.76879,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":115.36901,"mean_force":2.68387,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50125,0.07544,0.15588]},{"body_a":"channel_base_body","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.5526,-0.11996,0.06481],"force_p95":80.45089,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":80.45089,"mean_force":80.45089,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.44911,0.00493,0.19445]},{"body_a":"peg","body_b":"channel_base_body","contact_count":407.0,"contact_point_centroid":[0.50424,0.11169,0.00937],"force_p95":0.61041,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.25003,"mean_force":2.94396,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50228,0.11273,0.09849]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.5126,0.11097,0.05802],"force_p95":67.30464,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.74153,"mean_force":51.44461,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50073,0.11137,0.05916]},{"body_a":"channel_base_body","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.55253,-0.11997,0.06488],"force_p95":64.84035,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":67.13487,"mean_force":37.66689,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.44901,0.00458,0.1947]},{"body_a":"peg","body_b":"channel_base_body","contact_count":961.0,"contact_point_centroid":[0.50362,0.1117,0.00938],"force_p95":0.60862,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55323,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50235,0.15573,0.21652]},{"body_a":"peg","body_b":"world","contact_count":542.0,"contact_point_centroid":[0.53854,0.16107,-0.00196],"force_p95":0.68377,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68378,"mean_force":0.60624,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.44817,0.00448,0.23939]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4997,0.19936,0.29938]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.52231,0.18545,-0.00195],"force_p95":0.53283,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53283,"mean_force":0.53283,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.44911,0.00493,0.19445]}],"total_contact_groups":13},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.55618,0.16191,0.01413],"final_tcp_position":[0.44832,0.00423,0.28462],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":1083.23904,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":983.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.11176,0.03376],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.60057,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":977.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_peg","tcp_end":[0.50642,0.11472,0.14164],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10796,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":407.0,"n_steps_budget":600.0,"object_pos_end":[0.50391,0.11176,0.03323],"object_pos_start":[0.50376,0.11176,0.03376],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.1919,"object_z_max":0.03385,"peak_contact_force":69.25003,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":426.0,"raw_peak_contact_force":69.25003,"subtask_id":"reach_peg","tcp_end":[0.5012,0.11142,0.05803],"tcp_start":[0.50642,0.11472,0.14164],"tcp_to_object_dist_end":0.02496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52354,0.16051,0.01413],"object_pos_start":[0.50391,0.11176,0.03323],"object_to_goal_dist_end":0.24304,"object_to_goal_dist_start":0.19192,"object_z_max":0.03351,"peak_contact_force":196.36746,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2134.0,"raw_peak_contact_force":1083.23904,"subtask_id":"push_goal","tcp_end":[0.44911,0.00493,0.19445],"tcp_start":[0.5012,0.11142,0.05803],"tcp_to_object_dist_end":0.24952,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.52358,0.16047,0.01412],"object_pos_start":[0.52354,0.16051,0.01413],"object_to_goal_dist_end":0.243,"object_to_goal_dist_start":0.24304,"object_z_max":0.01413,"peak_contact_force":80.45089,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":80.45089,"subtask_id":"push_goal","tcp_end":[0.44904,0.00474,0.19457],"tcp_start":[0.44911,0.00493,0.19445],"tcp_to_object_dist_end":0.24974,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":630.0,"object_pos_end":[0.55618,0.16191,0.01413],"object_pos_start":[0.52358,0.16047,0.01412],"object_to_goal_dist_end":0.2497,"object_to_goal_dist_start":0.243,"object_z_max":0.01413,"peak_contact_force":0.60177,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":547.0,"raw_peak_contact_force":67.13487,"tcp_end":[0.44832,0.00423,0.28462],"tcp_start":[0.44904,0.00474,0.19457],"tcp_to_object_dist_end":0.33116,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36548,"average_solve_count":197.0,"average_success_count":197.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.01497,"align_1.lateral_offset_y":0.01337,"approach_1.approach_speed":0.01013,"push_1.push_force_threshold":37.45111,"push_1.push_speed":0.09432},"optimized_scores":{"best_composite_score":-0.29507,"best_fitness_score":0.04493,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":550.0,"contact_point_centroid":[0.52831,0.06174,0.05988],"force_p95":515.25874,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1143.84794,"mean_force":308.79194,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50445,0.11187,0.14657]},{"body_a":"channel_base_body","body_b":"link6","contact_count":598.0,"contact_point_centroid":[0.53979,-0.10881,0.06486],"force_p95":391.50101,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":475.18675,"mean_force":325.08263,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47628,0.06808,0.16545]},{"body_a":"attachment","body_b":"peg","contact_count":42.0,"contact_point_centroid":[0.4999,0.13485,0.05321],"force_p95":222.53984,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":240.8907,"mean_force":184.55258,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49618,0.14467,0.05542]},{"body_a":"peg","body_b":"channel_base_body","contact_count":52.0,"contact_point_centroid":[0.50219,0.1194,0.00896],"force_p95":199.40207,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":211.19721,"mean_force":69.78053,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4978,0.14764,0.05655]},{"body_a":"peg","body_b":"world","contact_count":982.0,"contact_point_centroid":[0.51083,0.15641,-0.00193],"force_p95":0.79293,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":204.07002,"mean_force":4.94681,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49206,0.09069,0.15301]},{"body_a":"channel_base_body","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.55003,-0.11995,0.06473],"force_p95":86.0223,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.0223,"mean_force":86.0223,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4515,0.01435,0.19087]},{"body_a":"peg","body_b":"channel_base_body","contact_count":494.0,"contact_point_centroid":[0.49689,0.11921,0.00947],"force_p95":39.37479,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.18973,"mean_force":4.00669,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48647,0.12001,0.09762]},{"body_a":"attachment","body_b":"peg","contact_count":29.0,"contact_point_centroid":[0.50363,0.11785,0.05799],"force_p95":71.20213,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":71.65605,"mean_force":59.1675,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49179,0.11875,0.059]},{"body_a":"channel_base_body","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.55001,-0.11997,0.06483],"force_p95":66.27438,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.2523,"mean_force":33.08722,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.45136,0.01397,0.19122]},{"body_a":"peg","body_b":"channel_base_body","contact_count":905.0,"contact_point_centroid":[0.49612,0.1193,0.00943],"force_p95":0.61503,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.54953,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49077,0.15974,0.21766]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49945,0.19915,0.29868]},{"body_a":"peg","body_b":"world","contact_count":543.0,"contact_point_centroid":[0.57075,0.15606,-0.00199],"force_p95":0.72595,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72646,"mean_force":0.6058,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.45055,0.0139,0.23592]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.54128,0.18226,-0.00199],"force_p95":0.72577,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72577,"mean_force":0.72577,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4515,0.01435,0.19087]}],"total_contact_groups":13},"final_pose_error":0.00988,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.6032,0.15489,0.01409],"final_tcp_position":[0.4507,0.01367,0.28116],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":1143.84794,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":930.0,"n_steps_budget":1000.0,"object_pos_end":[0.49608,0.11915,0.03382],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19929,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.5715,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":929.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_peg","tcp_end":[0.48376,0.12208,0.14297],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":494.0,"n_steps_budget":600.0,"object_pos_end":[0.49701,0.11932,0.0331],"object_pos_start":[0.49608,0.11915,0.03382],"object_to_goal_dist_end":0.19946,"object_to_goal_dist_start":0.19929,"object_z_max":0.03406,"peak_contact_force":72.18973,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":523.0,"raw_peak_contact_force":72.18973,"subtask_id":"reach_peg","tcp_end":[0.49285,0.11882,0.05758],"tcp_start":[0.48376,0.12208,0.14297],"tcp_to_object_dist_end":0.02484,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54034,0.15732,0.01408],"object_pos_start":[0.49701,0.11932,0.0331],"object_to_goal_dist_end":0.24211,"object_to_goal_dist_start":0.19946,"object_z_max":0.0331,"peak_contact_force":221.52825,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2224.0,"raw_peak_contact_force":1143.84794,"subtask_id":"push_goal","tcp_end":[0.4515,0.01435,0.19087],"tcp_start":[0.49285,0.11882,0.05758],"tcp_to_object_dist_end":0.2441,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.54044,0.15734,0.01408],"object_pos_start":[0.54034,0.15732,0.01408],"object_to_goal_dist_end":0.24215,"object_to_goal_dist_start":0.24211,"object_z_max":0.01408,"peak_contact_force":86.0223,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":86.0223,"subtask_id":"push_goal","tcp_end":[0.45142,0.01416,0.19101],"tcp_start":[0.4515,0.01435,0.19087],"tcp_to_object_dist_end":0.24439,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.6032,0.15489,0.01409],"object_pos_start":[0.54044,0.15734,0.01408],"object_to_goal_dist_end":0.25786,"object_to_goal_dist_start":0.24215,"object_z_max":0.0141,"peak_contact_force":0.49903,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":549.0,"raw_peak_contact_force":69.2523,"tcp_end":[0.4507,0.01367,0.28116],"tcp_start":[0.45142,0.01416,0.19101],"tcp_to_object_dist_end":0.33842,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94872,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00293,"align_1.lateral_offset_y":-0.00602,"approach_1.approach_speed":0.0985,"push_1.push_force_threshold":33.19918,"push_1.push_speed":0.07369},"optimized_scores":{"best_composite_score":-0.27155,"best_fitness_score":0.06845,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":750.0,"contact_point_centroid":[0.53501,-0.03679,0.0598],"force_p95":477.05657,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1125.53774,"mean_force":379.59716,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53227,0.02068,0.14568]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.5255,0.07969,0.0599],"force_p95":376.16421,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":377.36453,"mean_force":300.43952,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51368,0.08028,0.05941]},{"body_a":"attachment","body_b":"peg","contact_count":45.0,"contact_point_centroid":[0.51814,0.06735,0.05639],"force_p95":315.82407,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":324.79893,"mean_force":174.25378,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51127,0.07584,0.05942]},{"body_a":"peg","body_b":"channel_base_body","contact_count":931.0,"contact_point_centroid":[0.50392,0.06427,0.00934],"force_p95":0.94106,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":291.34178,"mean_force":8.52315,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5261,0.01483,0.1439]},{"body_a":"channel_base_body","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.48454,-0.10011,0.06476],"force_p95":252.61854,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":253.04773,"mean_force":236.81816,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47049,-0.05422,0.15621]},{"body_a":"channel_base_body","body_b":"link6","contact_count":159.0,"contact_point_centroid":[0.5072,-0.11995,0.06492],"force_p95":239.764,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":244.8845,"mean_force":175.94094,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49423,-0.04646,0.16608]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":21.0,"contact_point_centroid":[0.52577,0.06857,0.05726],"force_p95":102.89864,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":123.4021,"mean_force":46.0577,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51142,0.07647,0.05842]},{"body_a":"channel_base_body","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.48436,-0.1001,0.06477],"force_p95":53.57642,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.12349,"mean_force":10.76406,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.46985,-0.05464,0.1564]},{"body_a":"peg","body_b":"channel_base_body","contact_count":525.0,"contact_point_centroid":[0.50638,0.06294,0.00938],"force_p95":0.55397,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.09939,"mean_force":2.34081,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51064,0.07821,0.11215]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.51567,0.06452,0.05799],"force_p95":64.38409,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.58029,"mean_force":49.6558,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50381,0.06505,0.05912]},{"body_a":"channel_base_body","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.49555,-0.11999,0.06498],"force_p95":60.67745,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":61.27773,"mean_force":55.19237,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.46989,-0.05458,0.15614]},{"body_a":"channel_base_body","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.48436,-0.10014,0.06469],"force_p95":59.01549,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":59.01549,"mean_force":59.01549,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46988,-0.05451,0.15612]},{"body_a":"channel_base_body","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.49555,-0.11998,0.06497],"force_p95":16.16328,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":16.16328,"mean_force":16.16328,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46988,-0.05451,0.15612]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50586,0.06296,0.00937],"force_p95":0.55508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56049,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50959,0.14312,0.22967]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49971,0.1982,0.29751]},{"body_a":"peg","body_b":"channel_base_body","contact_count":567.0,"contact_point_centroid":[0.50393,0.06397,0.00946],"force_p95":0.54613,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54793,"mean_force":0.54138,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.46864,-0.05448,0.20079]}],"total_contact_groups":17},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50463,0.06374,0.03454],"final_tcp_position":[0.46875,-0.05474,0.24624],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":1125.53774,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54709,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1006.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_peg","tcp_end":[0.52015,0.09189,0.16936],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":525.0,"n_steps_budget":750.0,"object_pos_end":[0.5061,0.06267,0.03317],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.14297,"object_to_goal_dist_start":0.14323,"object_z_max":0.03382,"peak_contact_force":67.09939,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":544.0,"raw_peak_contact_force":67.09939,"subtask_id":"reach_peg","tcp_end":[0.50411,0.06476,0.05801],"tcp_start":[0.52015,0.09189,0.16936],"tcp_to_object_dist_end":0.02501,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":931.0,"n_steps_budget":960.0,"object_pos_end":[0.50435,0.06451,0.03449],"object_pos_start":[0.5061,0.06267,0.03317],"object_to_goal_dist_end":0.14468,"object_to_goal_dist_start":0.14297,"object_z_max":0.0345,"peak_contact_force":229.40017,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1935.0,"raw_peak_contact_force":1125.53774,"subtask_id":"push_goal","tcp_end":[0.46988,-0.05451,0.15612],"tcp_start":[0.50411,0.06476,0.05801],"tcp_to_object_dist_end":0.17363,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50444,0.06442,0.03449],"object_pos_start":[0.50435,0.06451,0.03449],"object_to_goal_dist_end":0.14459,"object_to_goal_dist_start":0.14468,"object_z_max":0.03449,"peak_contact_force":59.01549,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":59.01549,"subtask_id":"push_goal","tcp_end":[0.46988,-0.05454,0.15613],"tcp_start":[0.46988,-0.05451,0.15612],"tcp_to_object_dist_end":0.17361,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":567.0,"n_steps_budget":660.0,"object_pos_end":[0.50463,0.06374,0.03454],"object_pos_start":[0.50444,0.06442,0.03449],"object_to_goal_dist_end":0.14392,"object_to_goal_dist_start":0.14459,"object_z_max":0.03454,"peak_contact_force":0.53914,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":578.0,"raw_peak_contact_force":78.12349,"tcp_end":[0.46875,-0.05474,0.24624],"tcp_start":[0.46988,-0.05454,0.15613],"tcp_to_object_dist_end":0.24524,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```