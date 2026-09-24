## Search State

- **Seed**: 4
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.4455 | 0.20 | ❌ rejected |
| 1 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.0888 | 0.41 | ❌ rejected |
| 0 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.2470 | 0.45 | ✅ accepted |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.446) — your mutation base

```yaml
skill: peg_channel
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
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: -0.446
- **task_score** (E): 0.199
- **fitness_score**: 0.144  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.590

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_behind | 1.00 | 1.00 | 0.1284 |
| descend_to_peg | 1.00 | 1.00 | 0.1650 |
| contact_peg | 0.00 | 1.00 | 0.0129 |
| push_through_channel | 1.00 | 1.00 | 0.0307 |
| retract_up | 0.67 | 1.00 | 0.1211 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.517, 0.092, 0.247) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.548 | 3.242 |
| descend_to_peg | descend | 1.00 / step_budget | (0.517, 0.092, 0.247)→(0.503, 0.083, 0.083) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 1.000 | 0.557 | 0.559 |
| contact_peg | contact | 0.00 / step_budget | (0.503, 0.083, 0.083)→(0.501, 0.080, 0.071) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 1.000 | 0.544 | 0.559 |
| push_through_channel | push | 1.00 / time_limit | (0.501, 0.080, 0.071)→(0.517, 0.066, 0.088) | (0.505, 0.084, 0.034)→(0.494, 0.091, 0.034) | 0.165→0.171 | 1.00 / 3.333 | 262.260 | 921.251 |
| retract_up | retract | 0.67 / step_budget | (0.517, 0.066, 0.088)→(0.506, -0.049, 0.109) | (0.494, 0.091, 0.034)→(0.502, 0.031, 0.024) | 0.171→0.113 | 1.00 / 2.000 | 57.966 | 184.228 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.371
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.371
- phase_score: 0.127
- phase_breakdown.pre_insert_alignment_score: 0.242
- phase_breakdown.channel_insertion_score: 0.078

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.225
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.371
- **Median Q (composite search score)**: -0.474
- **K-run variance**: 0.0033
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.342


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.92,"average_solve_count":300.0,"average_success_count":300.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.approach_height":0.1538,"align_behind.speed":0.02102,"contact_peg.contact_force_threshold":15.53014,"contact_peg.speed":0.03292,"descend_to_peg.descend_y_offset":-0.0057,"descend_to_peg.speed":0.03185,"push_through_channel.push_distance":0.21248,"push_through_channel.push_speed":0.06493,"retract_up.retract_height":0.05346,"retract_up.speed":0.07204},"optimized_scores":{"best_composite_score":-0.49709,"best_fitness_score":0.09291,"best_task_score":0.08014},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":945.0,"contact_point_centroid":[0.52523,0.11993,0.0599],"force_p95":316.55408,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":943.06458,"mean_force":282.44694,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51722,0.06796,0.09449]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52556,0.06263,0.05982],"force_p95":786.30544,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":810.38304,"mean_force":353.09867,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51239,0.06131,0.05648]},{"body_a":"attachment","body_b":"peg","contact_count":24.0,"contact_point_centroid":[0.51474,0.07218,0.05478],"force_p95":237.60212,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":324.43334,"mean_force":201.05818,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51067,0.06235,0.0562]},{"body_a":"peg","body_b":"channel_base_body","contact_count":997.0,"contact_point_centroid":[0.49433,0.09018,0.00937],"force_p95":0.78922,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":323.99012,"mean_force":5.4033,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5167,0.06783,0.09272]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":192.0,"contact_point_centroid":[0.47498,0.0229,0.05998],"force_p95":171.87494,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":206.63852,"mean_force":116.29579,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50553,-0.05641,0.09924]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":110.0,"contact_point_centroid":[0.52501,0.11998,0.05998],"force_p95":101.13426,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":105.05939,"mean_force":79.60304,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.52065,0.06625,0.0969]},{"body_a":"peg","body_b":"link7","contact_count":273.0,"contact_point_centroid":[0.4941,0.08157,0.06471],"force_p95":33.64577,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.73286,"mean_force":26.29033,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51531,0.03165,0.10374]},{"body_a":"peg","body_b":"channel_base_body","contact_count":845.0,"contact_point_centroid":[0.49507,0.0482,0.00893],"force_p95":28.55549,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.64288,"mean_force":7.99221,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51156,0.00188,0.10177]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":43.0,"contact_point_centroid":[0.4743,0.09485,0.05813],"force_p95":4.72794,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.59158,"mean_force":1.38579,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50873,0.06768,0.07927]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":167.0,"contact_point_centroid":[0.475,0.06154,0.05988],"force_p95":14.75509,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.76363,"mean_force":12.06733,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51489,0.02815,0.10444]},{"body_a":"peg","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.51192,0.11388,0.05973],"force_p95":9.36034,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.33424,"mean_force":1.43689,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49659,0.06572,0.05599]},{"body_a":"peg","body_b":"channel_base_body","contact_count":612.0,"contact_point_centroid":[0.50571,0.08089,0.00936],"force_p95":0.55693,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.5717,"phase_index":0.0,"phase_name":"align_behind","phase_type":"approach","tcp_position_centroid":[0.51467,0.1421,0.24405]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"align_behind","phase_type":"approach","tcp_position_centroid":[0.49987,0.19781,0.29744]},{"body_a":"peg","body_b":"channel_base_body","contact_count":370.0,"contact_point_centroid":[0.50602,0.0808,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55007,"mean_force":0.54676,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51729,0.08264,0.1403]},{"body_a":"peg","body_b":"channel_base_body","contact_count":62.0,"contact_point_centroid":[0.50574,0.08129,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.5468,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50371,0.0759,0.07809]}],"total_contact_groups":15},"final_pose_error":0.01734,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.501,0.02502,0.02416],"final_tcp_position":[0.50783,-0.06502,0.09736],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":943.06458,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":641.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.55006,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":648.0,"raw_peak_contact_force":4.32595,"subtask_id":"pre_insert_alignment","tcp_end":[0.5301,0.08889,0.1959],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1641,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08088,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.5464,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":370.0,"raw_peak_contact_force":0.55007,"subtask_id":"pre_insert_alignment","tcp_end":[0.50537,0.07629,0.08353],"tcp_start":[0.5301,0.08889,0.1959],"tcp_to_object_dist_end":0.04997,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":62.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.50596,0.08088,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.55006,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":62.0,"raw_peak_contact_force":0.55006,"subtask_id":"pre_insert_alignment","tcp_end":[0.50284,0.07564,0.07258],"tcp_start":[0.50537,0.07629,0.08353],"tcp_to_object_dist_end":0.03928,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49363,0.08903,0.0338],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.16926,"object_to_goal_dist_start":0.16112,"object_z_max":0.04028,"peak_contact_force":274.91516,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2041.0,"raw_peak_contact_force":943.06458,"subtask_id":"channel_insertion","tcp_end":[0.52192,0.06866,0.09579],"tcp_start":[0.50284,0.07564,0.07258],"tcp_to_object_dist_end":0.07113,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":854.0,"n_steps_budget":1000.0,"object_pos_end":[0.501,0.02502,0.02416],"object_pos_start":[0.49363,0.08903,0.0338],"object_to_goal_dist_end":0.10622,"object_to_goal_dist_start":0.16926,"object_z_max":0.04052,"peak_contact_force":171.97501,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1587.0,"raw_peak_contact_force":206.63852,"tcp_end":[0.50783,-0.06502,0.09736],"tcp_start":[0.52192,0.06866,0.09579],"tcp_to_object_dist_end":0.11624,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.98413,"average_solve_count":252.0,"average_success_count":252.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.approach_height":0.27564,"align_behind.speed":0.11089,"contact_peg.contact_force_threshold":9.6027,"contact_peg.speed":0.01942,"descend_to_peg.descend_y_offset":0.00101,"descend_to_peg.speed":0.03465,"push_through_channel.push_distance":0.15743,"push_through_channel.push_speed":0.04614,"retract_up.retract_height":0.10892,"retract_up.speed":0.04767},"optimized_scores":{"best_composite_score":-0.47428,"best_fitness_score":0.11572,"best_task_score":0.14512},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.52799,0.0951,0.05941],"force_p95":1101.923,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1225.09074,"mean_force":472.22084,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5213,0.0868,0.06346]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50564,0.09169,0.00944],"force_p95":135.97036,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":279.50411,"mean_force":31.05882,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50736,0.0819,0.06928]},{"body_a":"attachment","body_b":"peg","contact_count":952.0,"contact_point_centroid":[0.50603,0.08864,0.05841],"force_p95":142.883,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":279.01171,"mean_force":31.86721,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50682,0.08151,0.06943]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":774.0,"contact_point_centroid":[0.47497,0.11995,0.05999],"force_p95":213.23373,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":228.58122,"mean_force":193.33481,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50704,0.08092,0.07032]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":483.0,"contact_point_centroid":[0.47499,0.11996,0.05998],"force_p95":113.02945,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":147.92212,"mean_force":92.92195,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51097,0.07868,0.07899]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":61.0,"contact_point_centroid":[0.52903,0.1199,0.06],"force_p95":73.3406,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.62255,"mean_force":38.89308,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50268,0.07945,0.0699]},{"body_a":"peg","body_b":"channel_base_body","contact_count":990.0,"contact_point_centroid":[0.49866,0.08002,0.00941],"force_p95":2.07459,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.66419,"mean_force":0.95981,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50841,0.05198,0.09547]},{"body_a":"attachment","body_b":"peg","contact_count":38.0,"contact_point_centroid":[0.50892,0.09104,0.05902],"force_p95":38.3566,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.92096,"mean_force":9.96567,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51088,0.08303,0.0701]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":120.0,"contact_point_centroid":[0.47487,0.10239,0.01285],"force_p95":9.26593,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.50247,"mean_force":3.90472,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50288,0.07982,0.06991]},{"body_a":"peg","body_b":"link7","contact_count":413.0,"contact_point_centroid":[0.49252,0.11754,0.06304],"force_p95":4.62548,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.6183,"mean_force":0.59513,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51095,0.07792,0.0794]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52505,0.08563,0.02428],"force_p95":9.17435,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.27246,"mean_force":2.88965,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50268,-0.0144,0.13205]},{"body_a":"peg","body_b":"channel_base_body","contact_count":461.0,"contact_point_centroid":[0.50554,0.10458,0.00937],"force_p95":0.57865,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57088,"phase_index":0.0,"phase_name":"align_behind","phase_type":"approach","tcp_position_centroid":[0.51041,0.15151,0.3029]},{"body_a":"peg","body_b":"link7","contact_count":491.0,"contact_point_centroid":[0.49404,0.121,0.06043],"force_p95":1.79236,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.88818,"mean_force":0.92161,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50845,0.08154,0.06987]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"align_behind","phase_type":"approach","tcp_position_centroid":[0.5,0.19687,0.2995]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.04502,0.04221],"force_p95":1.27669,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.27669,"mean_force":1.27669,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50564,0.03088,0.10953]},{"body_a":"peg","body_b":"channel_base_body","contact_count":744.0,"contact_point_centroid":[0.50588,0.1047,0.00939],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57678,"mean_force":0.54634,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51147,0.10809,0.1961]}],"total_contact_groups":17},"final_pose_error":0.06708,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50677,0.06098,0.02436],"final_tcp_position":[0.50263,-0.01506,0.13229],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":1225.09074,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":488.0,"n_steps_budget":600.0,"object_pos_end":[0.50585,0.1047,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.1849,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54418,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":493.0,"raw_peak_contact_force":3.33087,"subtask_id":"pre_insert_alignment","tcp_end":[0.52078,0.11114,0.30907],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.27572,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":744.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.1047,0.03384],"object_pos_start":[0.50585,0.1047,0.03384],"object_to_goal_dist_end":0.1849,"object_to_goal_dist_start":0.1849,"object_z_max":0.03384,"peak_contact_force":0.57571,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":744.0,"raw_peak_contact_force":0.57678,"subtask_id":"pre_insert_alignment","tcp_end":[0.50338,0.10534,0.08349],"tcp_start":[0.52078,0.11114,0.30907],"tcp_to_object_dist_end":0.04972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":81.0,"n_steps_budget":600.0,"object_pos_end":[0.50598,0.1046,0.03384],"object_pos_start":[0.50596,0.1047,0.03384],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.1849,"object_z_max":0.03384,"peak_contact_force":0.53561,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":81.0,"raw_peak_contact_force":0.57571,"subtask_id":"pre_insert_alignment","tcp_end":[0.50183,0.1015,0.07099],"tcp_start":[0.50338,0.10534,0.08349],"tcp_to_object_dist_end":0.03752,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49588,0.10494,0.03504],"object_pos_start":[0.50598,0.1046,0.03384],"object_to_goal_dist_end":0.18505,"object_to_goal_dist_start":0.1848,"object_z_max":0.03513,"peak_contact_force":207.33994,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3432.0,"raw_peak_contact_force":1225.09074,"subtask_id":"channel_insertion","tcp_end":[0.51113,0.08298,0.06912],"tcp_start":[0.50183,0.1015,0.07099],"tcp_to_object_dist_end":0.04331,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50677,0.06098,0.02436],"object_pos_start":[0.49588,0.10494,0.03504],"object_to_goal_dist_end":0.142,"object_to_goal_dist_start":0.18505,"object_z_max":0.04078,"peak_contact_force":0.51488,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1932.0,"raw_peak_contact_force":147.92212,"tcp_end":[0.50263,-0.01506,0.13229],"tcp_start":[0.51113,0.08298,0.06912],"tcp_to_object_dist_end":0.1321,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17568,"average_solve_count":222.0,"average_success_count":222.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.approach_height":0.1958,"align_behind.speed":0.14699,"contact_peg.contact_force_threshold":8.98248,"contact_peg.speed":0.03896,"descend_to_peg.descend_y_offset":0.00096,"descend_to_peg.speed":0.03335,"push_through_channel.push_distance":0.22177,"push_through_channel.push_speed":0.07591,"retract_up.retract_height":0.05164,"retract_up.speed":0.05824},"optimized_scores":{"best_composite_score":-0.36526,"best_fitness_score":0.22474,"best_task_score":0.37127},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":930.0,"contact_point_centroid":[0.52507,0.11462,0.05995],"force_p95":320.46255,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":595.59664,"mean_force":295.21575,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51633,0.05361,0.09866]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52571,0.05227,0.05975],"force_p95":439.25752,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":459.89302,"mean_force":195.47771,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51135,0.04936,0.05286]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49411,0.08046,0.00926],"force_p95":10.82243,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":359.02359,"mean_force":12.20206,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51571,0.05364,0.09618]},{"body_a":"attachment","body_b":"peg","contact_count":47.0,"contact_point_centroid":[0.51202,0.06043,0.05206],"force_p95":351.10093,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":358.84513,"mean_force":238.90405,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50761,0.05214,0.05521]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":244.0,"contact_point_centroid":[0.47498,0.02268,0.05997],"force_p95":175.66642,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":198.12386,"mean_force":115.58533,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50596,-0.05649,0.09827]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":575.0,"contact_point_centroid":[0.47483,0.08203,0.0446],"force_p95":2.59781,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":119.02971,"mean_force":2.19528,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51548,0.05356,0.09628]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.52502,0.10642,0.05997],"force_p95":101.94914,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":109.49432,"mean_force":59.49754,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51932,0.04586,0.09892]},{"body_a":"peg","body_b":"link7","contact_count":363.0,"contact_point_centroid":[0.49409,0.06991,0.06396],"force_p95":33.02405,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.14332,"mean_force":27.66238,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51441,0.01883,0.10313]},{"body_a":"peg","body_b":"channel_base_body","contact_count":775.0,"contact_point_centroid":[0.49452,0.02707,0.00896],"force_p95":29.23538,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.51878,"mean_force":11.03981,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50995,-0.01599,0.1015]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":313.0,"contact_point_centroid":[0.47492,0.05545,0.05751],"force_p95":16.75052,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.3683,"mean_force":12.77813,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51474,0.02089,0.10281]},{"body_a":"peg","body_b":"link7","contact_count":122.0,"contact_point_centroid":[0.4972,0.09837,0.05928],"force_p95":9.79593,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.68565,"mean_force":7.6504,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51873,0.04662,0.09894]},{"body_a":"peg","body_b":"channel_base_body","contact_count":477.0,"contact_point_centroid":[0.503,0.06746,0.00933],"force_p95":0.56109,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56468,"phase_index":0.0,"phase_name":"align_behind","phase_type":"approach","tcp_position_centroid":[0.49939,0.13666,0.26505]},{"body_a":"peg","body_b":"channel_base_body","contact_count":527.0,"contact_point_centroid":[0.50315,0.06744,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55098,"mean_force":0.54664,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49889,0.07278,0.15933]},{"body_a":"peg","body_b":"channel_base_body","contact_count":100.0,"contact_point_centroid":[0.50294,0.06732,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55071,"mean_force":0.54665,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49819,0.06646,0.07554]}],"total_contact_groups":14},"final_pose_error":0.01741,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49844,0.00806,0.02412],"final_tcp_position":[0.50833,-0.06543,0.09627],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":595.59664,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":493.0,"n_steps_budget":660.0,"object_pos_end":[0.50307,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.55014,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":477.0,"raw_peak_contact_force":2.06903,"subtask_id":"pre_insert_alignment","tcp_end":[0.50042,0.07706,0.23566],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.2021,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":527.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50307,0.0675,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":0.54762,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":527.0,"raw_peak_contact_force":0.55098,"subtask_id":"pre_insert_alignment","tcp_end":[0.4993,0.06869,0.08284],"tcp_start":[0.50042,0.07706,0.23566],"tcp_to_object_dist_end":0.0492,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":100.0,"n_steps_budget":600.0,"object_pos_end":[0.50301,0.06745,0.0338],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54668,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":100.0,"raw_peak_contact_force":0.55071,"subtask_id":"pre_insert_alignment","tcp_end":[0.49835,0.06412,0.06932],"tcp_start":[0.4993,0.06869,0.08284],"tcp_to_object_dist_end":0.03598,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4929,0.07956,0.03464],"object_pos_start":[0.50301,0.06745,0.0338],"object_to_goal_dist_end":0.15981,"object_to_goal_dist_start":0.14761,"object_z_max":0.03463,"peak_contact_force":304.52494,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2690.0,"raw_peak_contact_force":595.59664,"subtask_id":"channel_insertion","tcp_end":[0.51934,0.04594,0.09885],"tcp_start":[0.49835,0.06412,0.06932],"tcp_to_object_dist_end":0.07716,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":784.0,"n_steps_budget":1000.0,"object_pos_end":[0.49844,0.00806,0.02412],"object_pos_start":[0.4929,0.07956,0.03464],"object_to_goal_dist_end":0.08949,"object_to_goal_dist_start":0.15981,"object_z_max":0.04045,"peak_contact_force":1.40672,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1700.0,"raw_peak_contact_force":198.12386,"tcp_end":[0.50833,-0.06543,0.09627],"tcp_start":[0.51934,0.04594,0.09885],"tcp_to_object_dist_end":0.10347,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```