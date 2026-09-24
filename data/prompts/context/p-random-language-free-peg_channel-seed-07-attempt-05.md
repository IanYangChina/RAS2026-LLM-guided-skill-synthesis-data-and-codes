## Search State

- **Seed**: 7
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | descend → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.0821 | 0.24 | ❌ rejected |
| 4 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1314 | 0.26 | ❌ rejected |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0714 | 0.00 | ❌ rejected |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 4 | 0.1780 | 0.00 | ❌ rejected |
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 5 | 0.2562 | 0.07 | ❌ rejected |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5100076373283734, 0.11177710407756605, 0.04]
- Frozen task target: [0.5100076373283734, -0.04822289592243395, 0.04]
- Goal object position: (0.5100076373283734, -0.04822289592243395, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5100076373283734, 0.11177710407756605, 0.04)
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
  frozen_object_start: [0.51, 0.1118, 0.04]
  frozen_task_target: [0.51, -0.0482, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5100076373283734, 0.11177710407756605, 0.04]}
  frozen_targets: {'channel_exit': [0.5100076373283734, -0.04822289592243395, 0.04]}
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
| `object` | offset from object initial position (0.5100076373283734, 0.11177710407756605, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5100076373283734, -0.04822289592243395, 0.04) | final destination targets |
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

## Current Skill (Q=0.082) — your mutation base

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

- **Composite score**: 0.082
- **task_score** (E): 0.240
- **fitness_score**: 0.412  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_to_peg | 1.00 | 1.00 | 0.2093 |
| approach_peg | 1.00 | 1.00 | 0.0612 |
| push_channel | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_to_peg | descend | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.122, 0.108) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.531 | 2.732 |
| approach_peg | approach | 1.00 / step_budget | (0.505, 0.122, 0.108)→(0.500, 0.117, 0.048) | (0.502, 0.098, 0.034)→(0.501, 0.091, 0.032) | 0.178→0.171 | 1.00 / 1.667 | 57.464 | 193.248 |
| push_channel | push | 0.00 / guard_failure | (0.495, 0.051, 0.042)→(0.495, 0.051, 0.042) | (0.501, 0.091, 0.032)→(0.502, 0.025, 0.032) | 0.171→0.107 | 1.00 / 3.000 | 77.733 | 93.055 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.858
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.310
- phase_score: 0.805
- phase_breakdown.pre_push_score: 0.599
- phase_breakdown.push_goal_score: 0.894

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.607
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.404
- **Median Q (composite search score)**: 0.129
- **K-run variance**: 0.0329
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.322


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
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.59223,"average_solve_count":206.0,"average_success_count":206.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.01869,"approach_peg.lateral_x":0.00205,"approach_peg.lateral_y":0.01487,"descend_to_peg.descent_speed":0.08247,"push_channel.push_speed":0.02311,"push_channel.push_stroke":0.10005},"optimized_scores":{"best_composite_score":0.1289,"best_fitness_score":0.4589,"best_task_score":0.40372},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":261.0,"contact_point_centroid":[0.50626,0.1144,0.009],"force_p95":133.37413,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":142.10272,"mean_force":32.435,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5039,0.136,0.07481]},{"body_a":"attachment","body_b":"peg","contact_count":89.0,"contact_point_centroid":[0.51171,0.12924,0.05464],"force_p95":136.95092,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":141.4505,"mean_force":93.55262,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50481,0.13766,0.05578]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54562,0.06228,0.05999],"force_p95":98.08959,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":98.27161,"mean_force":79.77548,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50081,0.06334,0.03656]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.525,0.0671,0.06],"force_p95":33.17796,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.87495,"mean_force":28.2356,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50112,0.06694,0.03709]},{"body_a":"peg","body_b":"channel_base_body","contact_count":470.0,"contact_point_centroid":[0.50154,0.06131,0.00987],"force_p95":16.04376,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.50201,"mean_force":12.71834,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50223,0.1012,0.04082]},{"body_a":"attachment","body_b":"peg","contact_count":454.0,"contact_point_centroid":[0.50312,0.08653,0.04005],"force_p95":16.05296,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.31308,"mean_force":12.78309,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50205,0.09821,0.04037]},{"body_a":"peg","body_b":"channel_base_body","contact_count":613.0,"contact_point_centroid":[0.50359,0.11166,0.00937],"force_p95":0.61794,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55723,"phase_index":0.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50219,0.16676,0.20055]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49973,0.19933,0.29895]}],"total_contact_groups":8},"final_pose_error":0.04657,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50034,0.03021,0.04],"final_tcp_position":[0.5008,0.06314,0.03655],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":142.10272,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":635.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11177,0.03383],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.52687,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":629.0,"raw_peak_contact_force":2.06328,"subtask_id":"pre_push","tcp_end":[0.50594,0.13543,0.10816],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":261.0,"n_steps_budget":1000.0,"object_pos_end":[0.50393,0.10673,0.03171],"object_pos_start":[0.50371,0.11177,0.03383],"object_to_goal_dist_end":0.18695,"object_to_goal_dist_start":0.19191,"object_z_max":0.03384,"peak_contact_force":1.12117,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":350.0,"raw_peak_contact_force":142.10272,"subtask_id":"pre_push","tcp_end":[0.50619,0.1391,0.04841],"tcp_start":[0.50594,0.13543,0.10816],"tcp_to_object_dist_end":0.0365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.50036,0.03039,0.04006],"object_pos_start":[0.50393,0.10673,0.03171],"object_to_goal_dist_end":0.11039,"object_to_goal_dist_start":0.18695,"object_z_max":0.04035,"peak_contact_force":96.45139,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":942.0,"raw_peak_contact_force":98.27161,"subtask_id":"push_goal","tcp_end":[0.5008,0.06314,0.03655],"tcp_start":[0.50081,0.06323,0.03655],"tcp_to_object_dist_end":0.03294,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.92029,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.0308,"approach_peg.lateral_x":-0.01405,"approach_peg.lateral_y":-0.00496,"descend_to_peg.descent_speed":0.04939,"push_channel.push_speed":0.03556,"push_channel.push_stroke":0.16893},"optimized_scores":{"best_composite_score":-0.15977,"best_fitness_score":0.17023,"best_task_score":0.00468},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":165.0,"contact_point_centroid":[0.49391,0.12773,0.0504],"force_p95":183.22625,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":201.08933,"mean_force":133.10187,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48335,0.12994,0.05318]},{"body_a":"peg","body_b":"channel_base_body","contact_count":325.0,"contact_point_centroid":[0.49623,0.11929,0.00797],"force_p95":144.36381,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":188.05189,"mean_force":59.53621,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48211,0.13332,0.06975]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49793,0.1268,0.04663],"force_p95":136.36066,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":136.74687,"mean_force":132.90395,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48738,0.12932,0.04815]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49513,0.11944,0.00531],"force_p95":120.41888,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":120.54291,"mean_force":114.58646,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48738,0.12932,0.04815]},{"body_a":"peg","body_b":"world","contact_count":84.0,"contact_point_centroid":[0.4999,0.13279,-0.00033],"force_p95":59.01929,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":61.69977,"mean_force":35.89374,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48552,0.12961,0.04957]},{"body_a":"peg","body_b":"world","contact_count":3.0,"contact_point_centroid":[0.50056,0.13266,-0.0005],"force_p95":34.33697,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.43931,"mean_force":21.42997,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48738,0.12932,0.04815]},{"body_a":"peg","body_b":"channel_base_body","contact_count":630.0,"contact_point_centroid":[0.4962,0.11933,0.00942],"force_p95":0.60459,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55294,"phase_index":0.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49094,0.17023,0.20102]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49945,0.19912,0.29799]}],"total_contact_groups":8},"final_pose_error":0.17193,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50073,0.11777,0.02606],"final_tcp_position":[0.4875,0.12937,0.04825],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":201.08933,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":655.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.1193,0.03384],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19943,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52256,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":654.0,"raw_peak_contact_force":2.24822,"subtask_id":"pre_push","tcp_end":[0.4838,0.14225,0.10895],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07948,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.50067,0.11775,0.02593],"object_pos_start":[0.49601,0.1193,0.03384],"object_to_goal_dist_end":0.19825,"object_to_goal_dist_start":0.19943,"object_z_max":0.03384,"peak_contact_force":171.07478,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":574.0,"raw_peak_contact_force":201.08933,"subtask_id":"pre_push","tcp_end":[0.48731,0.12931,0.04812],"tcp_start":[0.4838,0.14225,0.10895],"tcp_to_object_dist_end":0.02836,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.5007,0.11775,0.02596],"object_pos_start":[0.50067,0.11775,0.02593],"object_to_goal_dist_end":0.19825,"object_to_goal_dist_start":0.19825,"object_z_max":0.02601,"peak_contact_force":136.74687,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":136.74687,"subtask_id":"push_goal","tcp_end":[0.4875,0.12937,0.04825],"tcp_start":[0.48746,0.12934,0.0482],"tcp_to_object_dist_end":0.02839,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.69323,"average_solve_count":251.0,"average_success_count":251.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.01433,"approach_peg.lateral_x":-0.00373,"approach_peg.lateral_y":0.00746,"descend_to_peg.descent_speed":0.06758,"push_channel.push_speed":0.03478,"push_channel.push_stroke":0.17243},"optimized_scores":{"best_composite_score":0.27727,"best_fitness_score":0.60727,"best_task_score":0.31016},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52502,0.08339,0.05999],"force_p95":232.56292,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":236.55229,"mean_force":159.40595,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50822,0.08338,0.05135]},{"body_a":"peg","body_b":"channel_base_body","contact_count":274.0,"contact_point_centroid":[0.50702,0.0636,0.00878],"force_p95":129.76902,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":139.80872,"mean_force":36.63139,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51266,0.08496,0.07218]},{"body_a":"attachment","body_b":"peg","contact_count":102.0,"contact_point_centroid":[0.51489,0.07481,0.05424],"force_p95":133.6511,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":139.26271,"mean_force":96.99342,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50801,0.08323,0.05554]},{"body_a":"attachment","body_b":"peg","contact_count":440.0,"contact_point_centroid":[0.50223,-0.00909,0.04548],"force_p95":29.12115,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.14792,"mean_force":4.3898,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49893,0.00276,0.04117]},{"body_a":"peg","body_b":"channel_base_body","contact_count":38.0,"contact_point_centroid":[0.48968,-0.10045,0.0311],"force_p95":35.32867,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.77828,"mean_force":26.81576,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49743,-0.03815,0.04043]},{"body_a":"peg","body_b":"channel_base_body","contact_count":704.0,"contact_point_centroid":[0.5045,-0.02294,0.00958],"force_p95":6.73001,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.69433,"mean_force":1.85606,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49974,0.01815,0.04172]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":135.0,"contact_point_centroid":[0.52503,-0.05088,0.02738],"force_p95":5.4295,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.54049,"mean_force":2.4135,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49903,0.00461,0.04124]},{"body_a":"peg","body_b":"channel_base_body","contact_count":741.0,"contact_point_centroid":[0.50584,0.06297,0.00936],"force_p95":0.55676,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56482,"phase_index":0.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51165,0.14256,0.19834]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49979,0.19811,0.29661]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.4749,0.02992,0.05814],"force_p95":0.95242,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.00782,"mean_force":0.57893,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50483,0.08159,0.04623]}],"total_contact_groups":10},"final_pose_error":0.07589,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50428,-0.07426,0.02856],"final_tcp_position":[0.4975,-0.0394,0.04045],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":236.55229,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":769.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.06295,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54404,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":775.0,"raw_peak_contact_force":3.88411,"subtask_id":"pre_push","tcp_end":[0.5244,0.08899,0.10601],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07894,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.49848,0.04721,0.03872],"object_pos_start":[0.50595,0.06295,0.03381],"object_to_goal_dist_end":0.12723,"object_to_goal_dist_start":0.14321,"object_z_max":0.03843,"peak_contact_force":0.19558,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":390.0,"raw_peak_contact_force":236.55229,"subtask_id":"pre_push","tcp_end":[0.50611,0.08284,0.04768],"tcp_start":[0.5244,0.08899,0.10601],"tcp_to_object_dist_end":0.03752,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":748.0,"n_steps_budget":1000.0,"object_pos_end":[0.50428,-0.07425,0.02856],"object_pos_start":[0.49848,0.04721,0.03872],"object_to_goal_dist_end":0.0135,"object_to_goal_dist_start":0.12723,"object_z_max":0.0408,"peak_contact_force":0.0,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1324.0,"raw_peak_contact_force":44.14792,"subtask_id":"push_goal","tcp_end":[0.4975,-0.0394,0.04045],"tcp_start":[0.49752,-0.0394,0.04048],"tcp_to_object_dist_end":0.03744,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```