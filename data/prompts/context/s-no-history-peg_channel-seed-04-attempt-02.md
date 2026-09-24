## Search State

- **Seed**: 4
- **Iteration**: 3 / 15

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
- Frozen realised-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`
- Frozen object start: [0.5354444884457894, 0.08090620422514894, 0.04]
- Frozen task target: [0.5354444884457894, -0.07909379577485107, 0.04]
- Goal object position: (0.5354444884457894, -0.07909379577485107, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5354444884457894, 0.08090620422514894, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
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
  frozen_object_start: [0.5354, 0.0809, 0.04]
  frozen_task_target: [0.5354, -0.0791, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5354444884457894, 0.08090620422514894, 0.04]}
  frozen_targets: {'channel_exit': [0.5354444884457894, -0.07909379577485107, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c

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
| `object` | offset from object initial position (0.5354444884457894, 0.08090620422514894, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5354444884457894, -0.07909379577485107, 0.04) | final destination targets |
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

## Current Skill (Q=0.163) — your mutation base

```yaml
skill: peg_channel
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

- **Composite score**: 0.163
- **task_score** (E): 0.161
- **fitness_score**: 0.473  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1907 |
| descend_align | 1.00 | 1.00 | 0.0814 |
| push_channel | 1.00 | 1.00 | 0.1438 |
| retract_tcp | 1.00 | 1.00 | 0.0804 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.097, 0.142) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.545 | 3.242 |
| descend_align | align | 1.00 / step_budget | (0.516, 0.097, 0.142)→(0.503, 0.086, 0.062) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.164 | 1.00 / 2.000 | 55.879 | 57.385 |
| push_channel | push | 1.00 / time_limit | (0.503, 0.086, 0.062)→(0.500, -0.056, 0.037) | (0.505, 0.084, 0.034)→(0.500, 0.038, 0.024) | 0.164→0.119 | 1.00 / 2.333 | 119.738 | 204.239 |
| retract_tcp | retract | 1.00 / step_budget | (0.500, -0.056, 0.037)→(0.497, -0.056, 0.118) | (0.500, 0.038, 0.024)→(0.501, 0.038, 0.024) | 0.119→0.119 | 1.00 / 1.000 | 0.539 | 67.721 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.292
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.292
- phase_score: 0.854
- phase_breakdown.push_channel_score: 0.898
- phase_breakdown.reach_peg_score: 0.752

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.629
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.292
- **Median Q (composite search score)**: 0.124
- **K-run variance**: 0.0133
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.421


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `424e8a040c59c1e1e42822c1022320b6050001458f7b9b4937cb9238911ce80b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `72d2436204c0f1ee3bbdbdfe3e5489661153a48f95d8f0dc3b73e6ce1e1e081b`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height_z":0.09143,"descend_align.descend_offset_z":0.01966,"push_channel.push_distance":0.19986,"push_channel.push_speed":0.09033,"push_channel.push_time":9.42698},"optimized_scores":{"best_composite_score":0.12429,"best_fitness_score":0.43429,"best_task_score":0.07783},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":64.0,"contact_point_centroid":[0.52501,-0.05547,0.06],"force_p95":137.57249,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":149.02665,"mean_force":84.99576,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50135,-0.05524,0.03769]},{"body_a":"peg","body_b":"channel_base_body","contact_count":996.0,"contact_point_centroid":[0.50316,0.04875,0.00886],"force_p95":79.60806,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.79699,"mean_force":26.22271,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50387,0.01077,0.04996]},{"body_a":"attachment","body_b":"peg","contact_count":509.0,"contact_point_centroid":[0.51332,0.05214,0.05493],"force_p95":80.10085,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.46737,"mean_force":50.23925,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50582,0.04627,0.05722]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,-0.05841,0.06],"force_p95":63.42421,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":63.42421,"mean_force":63.42421,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50094,-0.05816,0.0369]},{"body_a":"peg","body_b":"channel_base_body","contact_count":243.0,"contact_point_centroid":[0.50598,0.08072,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.11965,"mean_force":0.65613,"phase_index":1.0,"phase_name":"descend_align","phase_type":"align","tcp_position_centroid":[0.51685,0.08784,0.10405]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51702,0.08231,0.05877],"force_p95":26.72821,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.72821,"mean_force":26.72821,"phase_index":1.0,"phase_name":"descend_align","phase_type":"align","tcp_position_centroid":[0.50601,0.08235,0.06353]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":147.0,"contact_point_centroid":[0.52501,0.06416,0.05868],"force_p95":10.75093,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.51301,"mean_force":7.45155,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50724,0.05238,0.05955]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47499,0.05802,0.02425],"force_p95":7.60442,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.77241,"mean_force":2.43663,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50184,-0.0086,0.04499]},{"body_a":"peg","body_b":"channel_base_body","contact_count":349.0,"contact_point_centroid":[0.50555,0.08094,0.00934],"force_p95":0.56722,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59048,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51447,0.14372,0.21659]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50049,0.19639,0.29442]},{"body_a":"peg","body_b":"channel_base_body","contact_count":247.0,"contact_point_centroid":[0.50233,0.0352,0.00811],"force_p95":0.72018,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.98259,"mean_force":0.60252,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49801,-0.05798,0.07598]}],"total_contact_groups":11},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50462,0.03562,0.02411],"final_tcp_position":[0.49778,-0.05791,0.11722],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":149.02665,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54447,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":385.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.5287,0.09356,0.14473],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11396,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":243.0,"n_steps_budget":600.0,"object_pos_end":[0.50595,0.08088,0.03377],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.16111,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":27.11965,"phase_name":"descend_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":244.0,"raw_peak_contact_force":27.11965,"tcp_end":[0.50594,0.08231,0.06324],"tcp_start":[0.5287,0.09356,0.14473],"tcp_to_object_dist_end":0.0295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50044,0.03524,0.02413],"object_pos_start":[0.50595,0.08088,0.03377],"object_to_goal_dist_end":0.11633,"object_to_goal_dist_start":0.16111,"object_z_max":0.04012,"peak_contact_force":137.87125,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1723.0,"raw_peak_contact_force":149.02665,"subtask_id":"push_channel","tcp_end":[0.50094,-0.05816,0.0369],"tcp_start":[0.50594,0.08231,0.06324],"tcp_to_object_dist_end":0.09427,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":247.0,"n_steps_budget":630.0,"object_pos_end":[0.50462,0.03562,0.02411],"object_pos_start":[0.50044,0.03524,0.02413],"object_to_goal_dist_end":0.1168,"object_to_goal_dist_start":0.11633,"object_z_max":0.02455,"peak_contact_force":0.50672,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":248.0,"raw_peak_contact_force":63.42421,"tcp_end":[0.49778,-0.05791,0.11722],"tcp_start":[0.50094,-0.05816,0.0369],"tcp_to_object_dist_end":0.13216,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `54762c1e743ba455eff3c9979c2b42f5642abe1893e28eae37dc231d7efcd4e4`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89916,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height_z":0.08308,"descend_align.descend_offset_z":0.01774,"push_channel.push_distance":0.19445,"push_channel.push_speed":0.09953,"push_channel.push_time":3.37995},"optimized_scores":{"best_composite_score":0.04488,"best_fitness_score":0.35488,"best_task_score":0.11304},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":131.0,"contact_point_centroid":[0.54513,-0.03674,0.05997],"force_p95":248.13648,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.93148,"mean_force":140.04038,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50062,-0.03057,0.03674]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":184.0,"contact_point_centroid":[0.52502,-0.02941,0.05999],"force_p95":203.53337,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":290.44389,"mean_force":121.26147,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50073,-0.02933,0.03691]},{"body_a":"peg","body_b":"channel_base_body","contact_count":996.0,"contact_point_centroid":[0.50216,0.07072,0.00865],"force_p95":93.51561,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":98.1609,"mean_force":28.80092,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50311,0.02817,0.04767]},{"body_a":"attachment","body_b":"peg","contact_count":463.0,"contact_point_centroid":[0.5131,0.07522,0.05409],"force_p95":93.96273,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":97.63671,"mean_force":60.67765,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50539,0.06971,0.05624]},{"body_a":"peg","body_b":"channel_base_body","contact_count":234.0,"contact_point_centroid":[0.50628,0.10496,0.00939],"force_p95":0.57658,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.15852,"mean_force":2.73251,"phase_index":1.0,"phase_name":"descend_align","phase_type":"align","tcp_position_centroid":[0.51078,0.11028,0.0997]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.51558,0.10606,0.05819],"force_p95":78.18486,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.76885,"mean_force":64.10208,"phase_index":1.0,"phase_name":"descend_align","phase_type":"align","tcp_position_centroid":[0.50455,0.10586,0.06239]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52503,-0.0346,0.05999],"force_p95":64.00399,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.11555,"mean_force":23.70518,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50056,-0.03441,0.03705]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54517,-0.0408,0.05998],"force_p95":55.57367,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":57.02224,"mean_force":42.53661,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50055,-0.03441,0.03704]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":143.0,"contact_point_centroid":[0.52504,0.08692,0.05835],"force_p95":13.10453,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.5657,"mean_force":9.12839,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50693,0.07428,0.05852]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47498,0.08194,0.02459],"force_p95":7.32129,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.39166,"mean_force":2.70694,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50119,0.01594,0.04368]},{"body_a":"peg","body_b":"channel_base_body","contact_count":330.0,"contact_point_centroid":[0.50543,0.10454,0.00936],"force_p95":0.59995,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.58061,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50918,0.1554,0.21402]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50016,0.19739,0.29497]},{"body_a":"peg","body_b":"channel_base_body","contact_count":245.0,"contact_point_centroid":[0.49951,0.05832,0.00793],"force_p95":0.81722,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.81722,"mean_force":0.60597,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49769,-0.03431,0.07641]}],"total_contact_groups":13},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50072,0.05862,0.02401],"final_tcp_position":[0.49735,-0.03428,0.11738],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":316.93148,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":357.0,"n_steps_budget":1000.0,"object_pos_end":[0.50584,0.10467,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18487,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54467,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":362.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_peg","tcp_end":[0.51872,0.11526,0.13874],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10622,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":234.0,"n_steps_budget":600.0,"object_pos_end":[0.50604,0.10455,0.03348],"object_pos_start":[0.50584,0.10467,0.03384],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18487,"object_z_max":0.03384,"peak_contact_force":75.64179,"phase_name":"descend_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":242.0,"raw_peak_contact_force":80.15852,"tcp_end":[0.50455,0.10578,0.06132],"tcp_start":[0.51872,0.11526,0.13874],"tcp_to_object_dist_end":0.0279,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49833,0.05857,0.024],"object_pos_start":[0.50604,0.10455,0.03348],"object_to_goal_dist_end":0.1395,"object_to_goal_dist_start":0.18476,"object_z_max":0.04001,"peak_contact_force":219.92657,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1923.0,"raw_peak_contact_force":316.93148,"subtask_id":"push_channel","tcp_end":[0.50052,-0.0344,0.03703],"tcp_start":[0.50455,0.10578,0.06132],"tcp_to_object_dist_end":0.0939,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":245.0,"n_steps_budget":630.0,"object_pos_end":[0.50072,0.05862,0.02401],"object_pos_start":[0.49833,0.05857,0.024],"object_to_goal_dist_end":0.13954,"object_to_goal_dist_start":0.1395,"object_z_max":0.02401,"peak_contact_force":0.55154,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":250.0,"raw_peak_contact_force":71.11555,"tcp_end":[0.49735,-0.03428,0.11738],"tcp_start":[0.50052,-0.0344,0.03703],"tcp_to_object_dist_end":0.13176,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b230a5798f38c3fb8968a6bc74f96ee85fe7026f3170cf8216fc868a1c5c570f`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90164,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height_z":0.08748,"descend_align.descend_offset_z":0.01981,"push_channel.push_distance":0.19988,"push_channel.push_speed":0.09115,"push_channel.push_time":4.48352},"optimized_scores":{"best_composite_score":0.31932,"best_fitness_score":0.62932,"best_task_score":0.29213},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":55.0,"contact_point_centroid":[0.5412,-0.1,0.06499],"force_p95":136.48284,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":146.75958,"mean_force":84.52641,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4987,-0.0727,0.03774]},{"body_a":"peg","body_b":"channel_base_body","contact_count":996.0,"contact_point_centroid":[0.50256,0.0339,0.00876],"force_p95":90.04729,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.82767,"mean_force":29.99434,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4987,-0.00447,0.04956]},{"body_a":"attachment","body_b":"peg","contact_count":506.0,"contact_point_centroid":[0.5079,0.03761,0.05459],"force_p95":90.52219,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":93.24198,"mean_force":58.04066,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5,0.03232,0.05706]},{"body_a":"channel_base_body","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54245,-0.1,0.065],"force_p95":67.82694,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":68.62448,"mean_force":60.64911,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49996,-0.07504,0.038]},{"body_a":"peg","body_b":"channel_base_body","contact_count":252.0,"contact_point_centroid":[0.50308,0.06745,0.00938],"force_p95":0.55072,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":64.87616,"mean_force":1.36458,"phase_index":1.0,"phase_name":"descend_align","phase_type":"align","tcp_position_centroid":[0.49839,0.07508,0.1016]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50974,0.06931,0.05847],"force_p95":63.59137,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.47247,"mean_force":51.67977,"phase_index":1.0,"phase_name":"descend_align","phase_type":"align","tcp_position_centroid":[0.49882,0.06917,0.06315]},{"body_a":"peg","body_b":"channel_base_body","contact_count":373.0,"contact_point_centroid":[0.50312,0.06748,0.00932],"force_p95":0.61839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.5697,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49936,0.13941,0.2176]},{"body_a":"peg","body_b":"channel_base_body","contact_count":245.0,"contact_point_centroid":[0.4997,0.02081,0.00806],"force_p95":0.71701,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73896,"mean_force":0.60494,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49712,-0.07475,0.07732]}],"total_contact_groups":8},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49904,0.02072,0.02415],"final_tcp_position":[0.4968,-0.07466,0.11831],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":146.75958,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":389.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54682,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":373.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_peg","tcp_end":[0.49995,0.08132,0.14125],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":252.0,"n_steps_budget":600.0,"object_pos_end":[0.50313,0.06745,0.0337],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":64.87616,"phase_name":"descend_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":256.0,"raw_peak_contact_force":64.87616,"tcp_end":[0.49888,0.06906,0.06253],"tcp_start":[0.49995,0.08132,0.14125],"tcp_to_object_dist_end":0.02919,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50019,0.0208,0.02412],"object_pos_start":[0.50313,0.06745,0.0337],"object_to_goal_dist_end":0.10205,"object_to_goal_dist_start":0.14762,"object_z_max":0.04,"peak_contact_force":1.41475,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1557.0,"raw_peak_contact_force":146.75958,"subtask_id":"push_channel","tcp_end":[0.49994,-0.075,0.038],"tcp_start":[0.49888,0.06906,0.06253],"tcp_to_object_dist_end":0.09681,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":245.0,"n_steps_budget":630.0,"object_pos_end":[0.49904,0.02072,0.02415],"object_pos_start":[0.50019,0.0208,0.02412],"object_to_goal_dist_end":0.10197,"object_to_goal_dist_start":0.10205,"object_z_max":0.02422,"peak_contact_force":0.55943,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":247.0,"raw_peak_contact_force":68.62448,"tcp_end":[0.4968,-0.07466,0.11831],"tcp_start":[0.49994,-0.075,0.038],"tcp_to_object_dist_end":0.13405,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```