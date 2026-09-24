## Search State

- **Seed**: 7
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.0141 | 0.16 | ❌ rejected |
| 7 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.2492 | 0.08 | ❌ rejected |
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | -0.1048 | 0.01 | ❌ rejected |
| 5 | descend → approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7 | -0.2446 | 0.00 | ❌ rejected |
| 4 | descend → approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | -0.0575 | 0.03 | ❌ rejected |

**Proposal policy**: task_score is 0.16 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`
- Frozen object start: [0.5100076373283734, -0.04822289592243395, 0.04]
- Frozen task target: [0.5, 0.2, 0.3]
- Goal object position: (0.5, 0.2, 0.3)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5100076373283734, -0.04822289592243395, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5100076373283734, 0.11177710407756605, 0.04)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5100076373283734, 0.11177710407756605, 0.04]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.51, 0.1118, 0.04]
  frozen_task_target: [0.51, -0.0482, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5100076373283734, -0.04822289592243395, 0.04]}
  frozen_targets: {'channel_exit': [0.5, 0.2, 0.3]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415

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
| `object` | offset from object initial position (0.5100076373283734, -0.04822289592243395, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.2, 0.3) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

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

## Current Skill (Q=0.014) — your mutation base

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

- **Composite score**: 0.014
- **task_score** (E): 0.164
- **fitness_score**: 0.111  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2274 |
| push_1 | 1.00 | 1.00 | 0.0699 |
| retract_1 | 1.00 | 1.00 | 0.0615 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.507, 0.153, 0.078) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.564 | 2.732 |
| push_1 | push | 1.00 / force_exceeded | (0.507, 0.153, 0.078)→(0.502, 0.085, 0.062) | (0.502, 0.098, 0.034)→(0.502, 0.080, 0.037) | 0.178→0.160 | 1.00 / 2.667 | 43.561 | 20.140 |
| retract_1 | retract | 1.00 / step_budget | (0.502, 0.085, 0.062)→(0.499, 0.130, 0.104) | (0.502, 0.080, 0.037)→(0.502, 0.071, 0.031) | 0.160→0.152 | 1.00 / 1.000 | 0.577 | 29.456 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.445
- alignment_error: None
- force_efficiency: 0.467
- terminal_score: 0.410
- phase_score: 0.161
- phase_breakdown.push_exit_score: 0.230
- phase_breakdown.reach_pre_contact_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.260
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.410
- **Median Q (composite search score)**: -0.030
- **K-run variance**: 0.0118
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.320


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,-0.04822,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,-0.04822,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45926,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.01052,"approach_1.approach_lateral_x":0.00293,"approach_1.approach_lateral_y":0.04446,"approach_1.approach_speed":0.08377,"push_1.push_distance":0.11065,"push_1.push_force_limit":18.17639,"push_1.push_speed":0.02291,"retract_1.retract_speed":0.03889},"optimized_scores":{"best_composite_score":0.16371,"best_fitness_score":0.26038,"best_task_score":0.40981},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":635.0,"contact_point_centroid":[0.50212,0.04569,0.00845],"force_p95":0.72425,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.64783,"mean_force":0.65345,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50103,0.11013,0.0765]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.50316,0.08666,0.04423],"force_p95":16.0777,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.11046,"mean_force":3.05793,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50361,0.08654,0.0561]},{"body_a":"peg","body_b":"channel_base_body","contact_count":920.0,"contact_point_centroid":[0.50329,0.09273,0.00972],"force_p95":10.07025,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.39236,"mean_force":4.14662,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50486,0.12087,0.0601]},{"body_a":"attachment","body_b":"peg","contact_count":578.0,"contact_point_centroid":[0.50361,0.10808,0.04654],"force_p95":10.20404,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.02073,"mean_force":5.88066,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50437,0.10803,0.05847]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52501,0.06251,0.02422],"force_p95":5.27377,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.47192,"mean_force":1.61264,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50075,0.10538,0.07152]},{"body_a":"peg","body_b":"channel_base_body","contact_count":462.0,"contact_point_centroid":[0.50355,0.11173,0.00937],"force_p95":0.61648,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56134,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49895,0.18595,0.18074]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47489,0.04438,0.05404],"force_p95":0.53335,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57222,"mean_force":0.30938,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50131,0.09303,0.05995]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50379,0.20564,0.29959]}],"total_contact_groups":8},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50334,0.0405,0.02417],"final_tcp_position":[0.50099,0.13185,0.09783],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":26.64783,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":484.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11173,0.03387],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.57717,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":478.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_pre_contact","tcp_end":[0.50908,0.15886,0.0696],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05938,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":920.0,"n_steps_budget":1000.0,"object_pos_end":[0.50281,0.06778,0.04047],"object_pos_start":[0.50373,0.11173,0.03387],"object_to_goal_dist_end":0.14781,"object_to_goal_dist_start":0.19187,"object_z_max":0.04049,"peak_contact_force":18.39236,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1498.0,"raw_peak_contact_force":18.39236,"subtask_id":"push_exit","tcp_end":[0.50382,0.08661,0.05613],"tcp_start":[0.50908,0.15886,0.0696],"tcp_to_object_dist_end":0.02451,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":642.0,"n_steps_budget":1000.0,"object_pos_end":[0.50334,0.0405,0.02417],"object_pos_start":[0.50281,0.06778,0.04047],"object_to_goal_dist_end":0.12158,"object_to_goal_dist_start":0.14781,"object_z_max":0.04068,"peak_contact_force":0.60598,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":660.0,"raw_peak_contact_force":26.64783,"tcp_end":[0.50099,0.13185,0.09783],"tcp_start":[0.50382,0.08661,0.05613],"tcp_to_object_dist_end":0.11737,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,-0.04102,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,-0.04102,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60714,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0344,"approach_1.approach_lateral_x":0.01286,"approach_1.approach_lateral_y":0.03828,"approach_1.approach_speed":0.0833,"push_1.push_distance":0.1173,"push_1.push_force_limit":24.69747,"push_1.push_speed":0.04144,"retract_1.retract_speed":0.07045},"optimized_scores":{"best_composite_score":-0.02976,"best_fitness_score":0.06691,"best_task_score":0.07883},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":879.0,"contact_point_centroid":[0.49599,0.1164,0.0095],"force_p95":4.45895,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.75209,"mean_force":1.00953,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49433,0.12238,0.08131]},{"body_a":"peg","body_b":"link7","contact_count":127.0,"contact_point_centroid":[0.49604,0.13372,0.04685],"force_p95":6.27049,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.44361,"mean_force":3.42835,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49453,0.09359,0.07524]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49568,0.11116,0.00944],"force_p95":0.6218,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.08709,"mean_force":0.56388,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49206,0.11157,0.09448]},{"body_a":"peg","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.49597,0.13021,0.0546],"force_p95":3.09388,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.86849,"mean_force":0.70502,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49368,0.09006,0.07518]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.4946,0.12705,0.062],"force_p95":3.29179,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.79434,"mean_force":1.04276,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49453,0.08817,0.07413]},{"body_a":"peg","body_b":"channel_base_body","contact_count":411.0,"contact_point_centroid":[0.49634,0.11905,0.00939],"force_p95":0.63799,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56154,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49267,0.18716,0.19096]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50464,0.2121,0.29582]}],"total_contact_groups":7},"final_pose_error":0.01013,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49574,0.11157,0.03382],"final_tcp_position":[0.492,0.13328,0.11575],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":78.01543,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":436.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11903,0.03386],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19917,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.57269,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":435.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_pre_contact","tcp_end":[0.49677,0.16035,0.09384],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":883.0,"n_steps_budget":1000.0,"object_pos_end":[0.49612,0.11084,0.03601],"object_pos_start":[0.49602,0.11903,0.03386],"object_to_goal_dist_end":0.19092,"object_to_goal_dist_start":0.19917,"object_z_max":0.036,"peak_contact_force":78.01543,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1006.0,"raw_peak_contact_force":7.75209,"subtask_id":"push_exit","tcp_end":[0.49464,0.08824,0.07418],"tcp_start":[0.49677,0.16035,0.09384],"tcp_to_object_dist_end":0.04438,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":546.0,"n_steps_budget":660.0,"object_pos_end":[0.49574,0.11157,0.03382],"object_pos_start":[0.49612,0.11084,0.03601],"object_to_goal_dist_end":0.19171,"object_to_goal_dist_start":0.19092,"object_z_max":0.03606,"peak_contact_force":0.58121,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":564.0,"raw_peak_contact_force":7.08709,"tcp_end":[0.492,0.13328,0.11575],"tcp_start":[0.49464,0.08824,0.07418],"tcp_to_object_dist_end":0.08485,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,-0.09705,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,-0.09705,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54331,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.01237,"approach_1.approach_lateral_x":-0.0103,"approach_1.approach_lateral_y":0.07098,"approach_1.approach_speed":0.07743,"push_1.push_distance":0.07682,"push_1.push_force_limit":30.37412,"push_1.push_speed":0.04344,"retract_1.retract_speed":0.05354},"optimized_scores":{"best_composite_score":-0.09154,"best_fitness_score":0.00513,"best_task_score":0.00289},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.525,0.11991,0.0313],"force_p95":53.08756,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":54.63418,"mean_force":40.08543,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50758,0.07969,0.05646]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.525,0.11988,0.03124],"force_p95":27.03939,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.27503,"mean_force":23.71487,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50761,0.07964,0.05649]},{"body_a":"peg","body_b":"channel_base_body","contact_count":786.0,"contact_point_centroid":[0.50599,0.06223,0.0094],"force_p95":0.5541,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.36307,"mean_force":0.67111,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5096,0.10659,0.061]},{"body_a":"attachment","body_b":"peg","contact_count":36.0,"contact_point_centroid":[0.50591,0.08008,0.04472],"force_p95":8.23759,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.94727,"mean_force":2.90826,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50762,0.08009,0.05655]},{"body_a":"peg","body_b":"channel_base_body","contact_count":475.0,"contact_point_centroid":[0.50564,0.06297,0.00935],"force_p95":0.5788,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57503,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50158,0.17613,0.1818]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50351,0.22024,0.28833]},{"body_a":"peg","body_b":"channel_base_body","contact_count":624.0,"contact_point_centroid":[0.50587,0.06162,0.00939],"force_p95":0.62,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.79413,"mean_force":0.54946,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50483,0.10332,0.07694]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50587,0.07967,0.04463],"force_p95":1.99705,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.44184,"mean_force":0.62793,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50759,0.07965,0.05645]}],"total_contact_groups":8},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50591,0.06177,0.03377],"final_tcp_position":[0.50476,0.12492,0.09817],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":54.63418,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":503.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.06304,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1433,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54155,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":509.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_pre_contact","tcp_end":[0.51481,0.13878,0.0711],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08488,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":786.0,"n_steps_budget":1000.0,"object_pos_end":[0.50589,0.06173,0.03494],"object_pos_start":[0.50599,0.06304,0.03381],"object_to_goal_dist_end":0.14194,"object_to_goal_dist_start":0.1433,"object_z_max":0.03494,"peak_contact_force":34.27503,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":840.0,"raw_peak_contact_force":34.27503,"subtask_id":"push_exit","tcp_end":[0.50761,0.0796,0.05645],"tcp_start":[0.51481,0.13878,0.0711],"tcp_to_object_dist_end":0.02802,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":624.0,"n_steps_budget":840.0,"object_pos_end":[0.50591,0.06177,0.03377],"object_pos_start":[0.50589,0.06173,0.03494],"object_to_goal_dist_end":0.14203,"object_to_goal_dist_start":0.14194,"object_z_max":0.03494,"peak_contact_force":0.54244,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":635.0,"raw_peak_contact_force":54.63418,"tcp_end":[0.50476,0.12492,0.09817],"tcp_start":[0.50761,0.0796,0.05645],"tcp_to_object_dist_end":0.0902,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```