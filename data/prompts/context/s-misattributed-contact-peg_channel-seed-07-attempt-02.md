## Search State

- **Seed**: 7
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.0772 | 0.10 | ❌ rejected |
| 1 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1314 | 0.26 | ❌ rejected |
| 0 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1315 | 0.26 | ✅ accepted |

**Proposal policy**: task_score is 0.10 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.077) — your mutation base

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

- **Composite score**: -0.077
- **task_score** (E): 0.098
- **fitness_score**: 0.203  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2486 |
| push_channel | 0.00 | 1.00 | 0.0001 |
| retract | 1.00 | 1.00 | 0.0887 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.121, 0.066) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 2.333 | 27.119 | 61.458 |
| push_channel | push | 0.00 / guard_failure | (0.504, 0.105, 0.063)→(0.504, 0.105, 0.063) | (0.502, 0.098, 0.034)→(0.503, 0.087, 0.038) | 0.178→0.167 | 1.00 / 1.000 | 0.529 | 62.068 |
| retract | retract | 1.00 / step_budget | (0.504, 0.105, 0.063)→(0.502, 0.104, 0.151) | (0.503, 0.087, 0.038)→(0.502, 0.080, 0.031) | 0.167→0.160 | 1.00 / 1.333 | 0.802 | 2.732 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.309
- alignment_error: None
- force_efficiency: 0.376
- terminal_score: 0.270
- phase_score: 0.271
- phase_breakdown.behind_peg_score: 0.850
- phase_breakdown.push_goal_score: 0.022

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.270
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.270
- **Median Q (composite search score)**: -0.092
- **K-run variance**: 0.0025
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.378


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1938,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.speed":0.05229,"approach_behind.z_offset":0.01812,"push_channel.force_threshold":28.82178,"push_channel.push_distance":0.14895,"retract.speed":0.14748},"optimized_scores":{"best_composite_score":-0.00966,"best_fitness_score":0.27034,"best_task_score":0.26979},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":107.0,"contact_point_centroid":[0.50278,0.09585,0.00966],"force_p95":21.0772,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.18434,"mean_force":8.96182,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5044,0.12116,0.06282]},{"body_a":"attachment","body_b":"peg","contact_count":63.0,"contact_point_centroid":[0.50377,0.11636,0.04987],"force_p95":25.0211,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.91978,"mean_force":14.49182,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50395,0.11626,0.06179]},{"body_a":"peg","body_b":"channel_base_body","contact_count":512.0,"contact_point_centroid":[0.50107,0.06997,0.00863],"force_p95":0.76646,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.44945,"mean_force":0.67421,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50113,0.10722,0.10379]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50368,0.10833,0.049],"force_p95":15.23957,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.91501,"mean_force":3.32849,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50343,0.10826,0.06092]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52501,0.08337,0.02428],"force_p95":6.03692,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.07714,"mean_force":2.79333,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50095,0.10716,0.11422]},{"body_a":"peg","body_b":"channel_base_body","contact_count":845.0,"contact_point_centroid":[0.50357,0.11171,0.00937],"force_p95":0.62041,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55422,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49975,0.17213,0.18478]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50377,0.20566,0.29958]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47494,0.06719,0.05466],"force_p95":0.46299,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49241,"mean_force":0.28398,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50089,0.10709,0.07706]}],"total_contact_groups":8},"final_pose_error":0.01234,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50228,0.06231,0.0241],"final_tcp_position":[0.50125,0.10732,0.14881],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":31.18434,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":867.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11176,0.03376],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.64228,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":170.0,"raw_peak_contact_force":31.18434,"subtask_id":"behind_peg","tcp_end":[0.50643,0.13399,0.06695],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04005,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":107.0,"n_steps_budget":960.0,"object_pos_end":[0.50383,0.09375,0.03999],"object_pos_start":[0.50375,0.11176,0.03376],"object_to_goal_dist_end":0.17379,"object_to_goal_dist_start":0.1919,"object_z_max":0.04,"peak_contact_force":0.56204,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":537.0,"raw_peak_contact_force":21.44945,"subtask_id":"push_goal","tcp_end":[0.50362,0.1086,0.06086],"tcp_start":[0.50366,0.10874,0.06087],"tcp_to_object_dist_end":0.02561,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":521.0,"n_steps_budget":600.0,"object_pos_end":[0.50228,0.06231,0.0241],"object_pos_start":[0.50392,0.09339,0.04002],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.17344,"object_z_max":0.04078,"peak_contact_force":0.48684,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":861.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.50125,0.10732,0.14881],"tcp_start":[0.50362,0.1086,0.06086],"tcp_to_object_dist_end":0.1326,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82292,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.speed":0.09301,"approach_behind.z_offset":0.01064,"push_channel.force_threshold":28.30058,"push_channel.push_distance":0.1573,"retract.speed":0.07079},"optimized_scores":{"best_composite_score":-0.09202,"best_fitness_score":0.18798,"best_task_score":0.02475},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":102.0,"contact_point_centroid":[0.475,0.11997,0.05246],"force_p95":83.36959,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":119.07449,"mean_force":38.81253,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48066,0.12007,0.06292]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.475,0.11988,0.04692],"force_p95":50.09582,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":51.02054,"mean_force":32.31468,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48318,0.11981,0.05559]},{"body_a":"peg","body_b":"channel_base_body","contact_count":91.0,"contact_point_centroid":[0.49801,0.10345,0.00967],"force_p95":18.8123,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.90141,"mean_force":8.98663,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48307,0.12995,0.05691]},{"body_a":"attachment","body_b":"peg","contact_count":60.0,"contact_point_centroid":[0.49252,0.12663,0.04929],"force_p95":23.39393,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.73598,"mean_force":12.9887,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.483,0.12651,0.05627]},{"body_a":"peg","body_b":"channel_base_body","contact_count":786.0,"contact_point_centroid":[0.49912,0.11055,0.00955],"force_p95":0.62295,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.17182,"mean_force":0.53506,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48048,0.11856,0.10033]},{"body_a":"attachment","body_b":"peg","contact_count":83.0,"contact_point_centroid":[0.49114,0.11997,0.05925],"force_p95":0.48733,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.81113,"mean_force":0.27795,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48045,0.12007,0.06432]},{"body_a":"peg","body_b":"channel_base_body","contact_count":753.0,"contact_point_centroid":[0.49616,0.11917,0.00944],"force_p95":0.60565,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.54987,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48885,0.1741,0.17565]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50459,0.21209,0.29581]}],"total_contact_groups":8},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49704,0.11367,0.03385],"final_tcp_position":[0.4808,0.11821,0.14596],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":119.07449,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":778.0,"n_steps_budget":1000.0,"object_pos_end":[0.49605,0.11915,0.03391],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19928,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":41.77327,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":154.0,"raw_peak_contact_force":51.02054,"subtask_id":"behind_peg","tcp_end":[0.48402,0.14064,0.06001],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03589,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":91.0,"n_steps_budget":990.0,"object_pos_end":[0.49765,0.10497,0.03919],"object_pos_start":[0.49605,0.11915,0.03391],"object_to_goal_dist_end":0.18499,"object_to_goal_dist_start":0.19928,"object_z_max":0.03922,"peak_contact_force":0.48009,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":971.0,"raw_peak_contact_force":119.07449,"subtask_id":"push_goal","tcp_end":[0.48316,0.11957,0.05553],"tcp_start":[0.48316,0.11965,0.05558],"tcp_to_object_dist_end":0.02627,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":787.0,"n_steps_budget":900.0,"object_pos_end":[0.49704,0.11367,0.03385],"object_pos_start":[0.49776,0.10479,0.03922],"object_to_goal_dist_end":0.19379,"object_to_goal_dist_start":0.18481,"object_z_max":0.03923,"peak_contact_force":0.51838,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":777.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.4808,0.11821,0.14596],"tcp_start":[0.48316,0.11957,0.05553],"tcp_to_object_dist_end":0.11337,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11888,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.speed":0.03973,"approach_behind.z_offset":0.02474,"push_channel.force_threshold":27.90724,"push_channel.push_distance":0.14901,"retract.speed":0.12494},"optimized_scores":{"best_composite_score":-0.12989,"best_fitness_score":0.15011,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.525,0.12,0.05988],"force_p95":100.14807,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":102.16806,"mean_force":74.35886,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.52494,0.0876,0.07193]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.525,0.12,0.05984],"force_p95":44.6817,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.6793,"mean_force":22.6825,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52481,0.08708,0.0719]},{"body_a":"peg","body_b":"channel_base_body","contact_count":927.0,"contact_point_centroid":[0.50582,0.06301,0.00937],"force_p95":0.55553,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56116,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50838,0.1504,0.1874]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50336,0.22031,0.28873]},{"body_a":"peg","body_b":"channel_base_body","contact_count":519.0,"contact_point_centroid":[0.5059,0.0629,0.00938],"force_p95":0.55273,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54658,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52243,0.08615,0.11431]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.5211,0.06005,0.00938],"force_p95":0.54872,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54899,"mean_force":0.54573,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.52494,0.0876,0.07193]}],"total_contact_groups":6},"final_pose_error":0.01257,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50593,0.06303,0.03381],"final_tcp_position":[0.52254,0.08625,0.15948],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":102.16806,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":955.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.06301,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14327,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":38.94038,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6.0,"raw_peak_contact_force":102.16806,"subtask_id":"behind_peg","tcp_end":[0.52494,0.08774,0.07202],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04929,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":990.0,"object_pos_end":[0.50603,0.06298,0.03381],"object_pos_start":[0.50603,0.06301,0.03381],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.14327,"object_z_max":0.03381,"peak_contact_force":0.54584,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":527.0,"raw_peak_contact_force":45.6793,"subtask_id":"push_goal","tcp_end":[0.52493,0.08737,0.07177],"tcp_start":[0.52493,0.08747,0.07184],"tcp_to_object_dist_end":0.04892,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":519.0,"n_steps_budget":600.0,"object_pos_end":[0.50593,0.06303,0.03381],"object_pos_start":[0.50599,0.06294,0.03381],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14319,"object_z_max":0.03381,"peak_contact_force":1.40206,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":961.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.52254,0.08625,0.15948],"tcp_start":[0.52493,0.08737,0.07177],"tcp_to_object_dist_end":0.12887,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```