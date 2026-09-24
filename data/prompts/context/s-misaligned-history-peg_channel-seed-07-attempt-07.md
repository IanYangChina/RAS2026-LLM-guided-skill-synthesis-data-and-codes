## Search State

- **Seed**: 7
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 3  | -0.1314 | 0.26 | ❌ rejected |
| 6 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5  | -0.1315 | 0.26 | ❌ rejected |
| 5 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5  | -0.1314 | 0.26 | ❌ rejected |
| 4 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5  | 0.0681 | 0.19 | ❌ rejected |
| 3 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 3  | 0.3061 | 0.01 | ❌ rejected |

**Proposal policy**: task_score is 0.01 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.306) — your mutation base

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

- **Composite score**: 0.306
- **task_score** (E): 0.015
- **fitness_score**: 0.153  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.180

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2264 |
| descend_1 | 1.00 | 1.00 | 0.0255 |
| push_1 | 0.00 | 1.00 | 0.0395 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.103, 0.097) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.544 | 2.732 |
| descend_1 | descend | 1.00 / force_exceeded | (0.505, 0.103, 0.097)→(0.501, 0.101, 0.073) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 1.667 | 16.087 | 16.087 |
| push_1 | push | 0.00 / step_budget | (0.501, 0.101, 0.073)→(0.521, 0.083, 0.071) | (0.502, 0.098, 0.034)→(0.441, 0.037, 0.028) | 0.178→0.163 | 1.00 / 3.000 | 219.842 | 872.625 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.069
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.039
- phase_score: 0.287
- phase_breakdown.push_to_goal_score: 0.057
- phase_breakdown.reach_object_score: 0.825

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.188
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.039
- **Median Q (composite search score)**: 0.322
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.451


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25309,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.02199,"descend_1.contact_force":0.52509,"push_1.insertion_depth":0.02561},"optimized_scores":{"best_composite_score":0.34107,"best_fitness_score":0.18774,"best_task_score":0.03862},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":265.0,"contact_point_centroid":[0.52514,0.08724,0.05989],"force_p95":341.91757,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1264.36514,"mean_force":291.24489,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51899,0.0854,0.06928]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":651.0,"contact_point_centroid":[0.47497,0.11993,0.05998],"force_p95":414.52467,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":443.1102,"mean_force":310.98128,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51483,0.08156,0.07323]},{"body_a":"attachment","body_b":"peg","contact_count":435.0,"contact_point_centroid":[0.51124,0.10366,0.05864],"force_p95":229.49494,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":291.6055,"mean_force":39.26577,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51624,0.08612,0.06881]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49939,0.09312,0.0096],"force_p95":168.9155,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":291.14678,"mean_force":19.7247,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51184,0.08279,0.07301]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":230.0,"contact_point_centroid":[0.52544,0.1199,0.05999],"force_p95":205.91583,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":213.72951,"mean_force":167.20396,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50628,0.07787,0.07671]},{"body_a":"peg","body_b":"link7","contact_count":485.0,"contact_point_centroid":[0.49233,0.11909,0.05298],"force_p95":63.25894,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":76.19739,"mean_force":5.31067,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50832,0.0788,0.07617]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":451.0,"contact_point_centroid":[0.47475,0.1031,0.02169],"force_p95":54.06731,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.79962,"mean_force":8.3272,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51255,0.08357,0.07015]},{"body_a":"peg","body_b":"channel_base_body","contact_count":725.0,"contact_point_centroid":[0.50359,0.11168,0.00938],"force_p95":0.61895,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.5547,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50219,0.15708,0.19529]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4997,0.19934,0.29918]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51735,0.10021,0.0094],"force_p95":0.5342,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5342,"mean_force":0.5342,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50606,0.11633,0.09775]}],"total_contact_groups":10},"final_pose_error":0.1946,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49354,0.10081,0.0353],"final_tcp_position":[0.52042,0.08545,0.0708],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":1264.36514,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":747.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11174,0.03381],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.53324,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":741.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_object","tcp_end":[0.50606,0.11633,0.09775],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06414,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50371,0.11173,0.03381],"object_pos_start":[0.50373,0.11174,0.03381],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19187,"object_z_max":0.03381,"peak_contact_force":0.5342,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":0.5342,"subtask_id":"reach_object","tcp_end":[0.50597,0.11623,0.09752],"tcp_start":[0.50606,0.11633,0.09775],"tcp_to_object_dist_end":0.06391,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49354,0.10081,0.0353],"object_pos_start":[0.50371,0.11173,0.03381],"object_to_goal_dist_end":0.18099,"object_to_goal_dist_start":0.19187,"object_z_max":0.03665,"peak_contact_force":356.61634,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3517.0,"raw_peak_contact_force":1264.36514,"subtask_id":"push_to_goal","tcp_end":[0.52042,0.08545,0.0708],"tcp_start":[0.50597,0.11623,0.09752],"tcp_to_object_dist_end":0.04711,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28161,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.02984,"descend_1.contact_force":19.64669,"push_1.insertion_depth":0.08311},"optimized_scores":{"best_composite_score":0.32219,"best_fitness_score":0.16886,"best_task_score":0.00077},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":818.0,"contact_point_centroid":[0.46081,0.1199,0.05758],"force_p95":281.87728,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":510.78626,"mean_force":229.08722,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49642,0.08525,0.05189]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":13.0,"contact_point_centroid":[0.52614,0.11476,0.05984],"force_p95":483.82006,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":498.03428,"mean_force":307.21564,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51472,0.11369,0.05671]},{"body_a":"world","body_b":"link7","contact_count":360.0,"contact_point_centroid":[0.48627,0.14964,-7e-05],"force_p95":263.54377,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":362.75177,"mean_force":198.80336,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49925,0.08817,0.05197]},{"body_a":"peg","body_b":"channel_base_body","contact_count":96.0,"contact_point_centroid":[0.50742,0.11762,0.00832],"force_p95":275.10246,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":346.54987,"mean_force":149.10335,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5086,0.12621,0.05447]},{"body_a":"attachment","body_b":"peg","contact_count":94.0,"contact_point_centroid":[0.50948,0.13477,0.05132],"force_p95":275.10837,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":346.30202,"mean_force":209.62795,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50853,0.12593,0.05464]},{"body_a":"peg","body_b":"world","contact_count":951.0,"contact_point_centroid":[0.38245,0.07853,-0.00184],"force_p95":112.61819,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":184.05191,"mean_force":12.37184,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49732,0.08952,0.05132]},{"body_a":"peg","body_b":"link7","contact_count":47.0,"contact_point_centroid":[0.46419,0.1736,0.0404],"force_p95":178.73747,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":183.62748,"mean_force":113.54926,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49868,0.10732,0.04276]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52659,0.1146,0.05504],"force_p95":62.26412,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.57166,"mean_force":25.49503,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51141,0.11158,0.05795]},{"body_a":"peg","body_b":"channel_base_body","contact_count":236.0,"contact_point_centroid":[0.49593,0.11918,0.00942],"force_p95":0.61314,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.21242,"mean_force":0.83972,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48419,0.12148,0.07821]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.49772,0.11602,0.05899],"force_p95":20.34109,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.72552,"mean_force":17.55042,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48662,0.12026,0.06052]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47498,0.12,0.01561],"force_p95":8.50024,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.50024,"mean_force":8.50024,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51091,0.1383,0.04561]},{"body_a":"peg","body_b":"channel_base_body","contact_count":696.0,"contact_point_centroid":[0.4962,0.11913,0.00944],"force_p95":0.60872,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55071,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49088,0.16044,0.19532]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49947,0.19904,0.29813]}],"total_contact_groups":13},"final_pose_error":0.25406,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.3378,-0.04825,0.01413],"final_tcp_position":[0.50267,0.09064,0.05224],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":510.78626,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":721.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.1191,0.03401],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19923,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.55761,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":720.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_object","tcp_end":[0.48382,0.12328,0.09866],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06592,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":236.0,"n_steps_budget":600.0,"object_pos_end":[0.49601,0.12027,0.03384],"object_pos_start":[0.49603,0.1191,0.03401],"object_to_goal_dist_end":0.2004,"object_to_goal_dist_start":0.19923,"object_z_max":0.03405,"peak_contact_force":21.21242,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":240.0,"raw_peak_contact_force":21.21242,"subtask_id":"reach_object","tcp_end":[0.48672,0.12024,0.06022],"tcp_start":[0.48382,0.12328,0.09866],"tcp_to_object_dist_end":0.02796,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.3378,-0.04825,0.01413],"object_pos_start":[0.49601,0.12027,0.03384],"object_to_goal_dist_end":0.16729,"object_to_goal_dist_start":0.2004,"object_z_max":0.03581,"peak_contact_force":300.67022,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2396.0,"raw_peak_contact_force":510.78626,"subtask_id":"push_to_goal","tcp_end":[0.50267,0.09064,0.05224],"tcp_start":[0.48672,0.12024,0.06022],"tcp_to_object_dist_end":0.21891,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32168,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05706,"descend_1.contact_force":26.04149,"push_1.insertion_depth":0.09861},"optimized_scores":{"best_composite_score":0.25505,"best_fitness_score":0.10171,"best_task_score":0.00449},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":25.0,"contact_point_centroid":[0.5254,0.06513,0.05993],"force_p95":772.31558,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":842.72431,"mean_force":384.64495,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51377,0.06482,0.06064]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":921.0,"contact_point_centroid":[0.52551,0.11993,0.05993],"force_p95":372.49173,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":808.87069,"mean_force":322.14286,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53168,0.06818,0.09221]},{"body_a":"attachment","body_b":"peg","contact_count":81.0,"contact_point_centroid":[0.51882,0.07409,0.05667],"force_p95":235.86596,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":271.98439,"mean_force":160.21831,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51333,0.06703,0.06205]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49497,0.06083,0.00927],"force_p95":165.02459,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":240.41994,"mean_force":13.45309,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53026,0.06809,0.08992]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52543,0.0609,0.05845],"force_p95":69.8214,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":139.64281,"mean_force":12.6948,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51415,0.06281,0.05898]},{"body_a":"peg","body_b":"channel_base_body","contact_count":164.0,"contact_point_centroid":[0.50629,0.06315,0.00938],"force_p95":0.55226,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.51461,"mean_force":0.70496,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51786,0.06752,0.07813]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5237,0.06515,0.05877],"force_p95":25.87242,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.87242,"mean_force":25.87242,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51185,0.0658,0.06052]},{"body_a":"peg","body_b":"channel_base_body","contact_count":845.0,"contact_point_centroid":[0.50579,0.06298,0.00937],"force_p95":0.55598,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56257,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51173,0.13248,0.19289]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49976,0.19811,0.29688]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":203.0,"contact_point_centroid":[0.47493,0.05935,0.05866],"force_p95":0.19455,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.10893,"mean_force":0.05821,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53186,0.06828,0.09182]}],"total_contact_groups":10},"final_pose_error":0.25971,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49305,0.05946,0.0338],"final_tcp_position":[0.53849,0.07328,0.09021],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":842.72431,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":873.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.06304,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1433,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54145,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":879.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_object","tcp_end":[0.52461,0.06943,0.09555],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06481,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":164.0,"n_steps_budget":600.0,"object_pos_end":[0.50604,0.06295,0.03382],"object_pos_start":[0.50599,0.06304,0.03381],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.1433,"object_z_max":0.03381,"peak_contact_force":26.51461,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":165.0,"raw_peak_contact_force":26.51461,"subtask_id":"reach_object","tcp_end":[0.5118,0.06578,0.06031],"tcp_start":[0.52461,0.06943,0.09555],"tcp_to_object_dist_end":0.02726,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49305,0.05946,0.0338],"object_pos_start":[0.50604,0.06295,0.03382],"object_to_goal_dist_end":0.13977,"object_to_goal_dist_start":0.14321,"object_z_max":0.03641,"peak_contact_force":2.23808,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2241.0,"raw_peak_contact_force":842.72431,"subtask_id":"push_to_goal","tcp_end":[0.53849,0.07328,0.09021],"tcp_start":[0.5118,0.06578,0.06031],"tcp_to_object_dist_end":0.07374,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```