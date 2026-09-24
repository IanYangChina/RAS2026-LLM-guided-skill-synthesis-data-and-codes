## Search State

- **Seed**: 7
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 8  | -0.1315 | 0.26 | ❌ rejected |
| 13 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5  | 0.0674 | 0.21 | ❌ rejected |
| 12 | approach → push | linear_cartesian | impedance_motion | position_control | impedance_control | pose_tolerance | pose_tolerance | 3  | -0.0330 | 0.00 | ❌ rejected |
| 11 | approach → align → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5  | -0.0315 | 0.00 | ❌ rejected |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4  | -0.0934 | 0.00 | ❌ rejected |

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

## Current Skill (Q=-0.093) — your mutation base

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

- **Composite score**: -0.093
- **task_score** (E): 0.003
- **fitness_score**: 0.003  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.67 | 1.00 | 0.1802 |
| contact_1 | 1.00 | 1.00 | 0.0843 |
| push_1 | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.67 / step_budget | (0.500, 0.200, 0.300)→(0.503, 0.116, 0.143) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.556 | 2.732 |
| contact_1 | descend | 1.00 / force_exceeded | (0.503, 0.116, 0.143)→(0.498, 0.102, 0.060) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 2.000 | 19.301 | 19.301 |
| push_1 | push | 0.00 / guard_failure | (0.498, 0.101, 0.059)→(0.498, 0.101, 0.059) | (0.502, 0.098, 0.034)→(0.501, 0.097, 0.034) | 0.178→0.178 | 1.00 / 2.000 | 29.665 | 53.309 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.005
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.004
- phase_score: 0.003
- phase_breakdown.push_through_channel_score: 0.003

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.003
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.004
- **Median Q (composite search score)**: -0.094
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.347


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05263,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06368,"approach_1.approach_speed":0.05815,"contact_1.contact_force_threshold":13.71164,"push_1.force_threshold":44.9608,"push_1.lateral_offset_x":0.00676,"push_1.lateral_offset_y":0.00958,"push_1.push_depth":0.16268,"push_1.push_speed":0.03127},"optimized_scores":{"best_composite_score":-0.0932,"best_fitness_score":0.00347,"best_task_score":0.00428},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":15.0,"contact_point_centroid":[0.49398,0.10131,0.00941],"force_p95":50.85566,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.01525,"mean_force":35.27729,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50039,0.11524,0.05968]},{"body_a":"attachment","body_b":"peg","contact_count":15.0,"contact_point_centroid":[0.51225,0.1152,0.05847],"force_p95":50.42764,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.58266,"mean_force":34.83083,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50039,0.11524,0.05968]},{"body_a":"peg","body_b":"channel_base_body","contact_count":336.0,"contact_point_centroid":[0.50379,0.11178,0.00938],"force_p95":0.60127,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.30695,"mean_force":0.58642,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.50182,0.12036,0.09475]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51248,0.11537,0.05881],"force_p95":13.80281,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.80281,"mean_force":13.80281,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.50062,0.11577,0.06049]},{"body_a":"peg","body_b":"channel_base_body","contact_count":978.0,"contact_point_centroid":[0.50363,0.11163,0.0094],"force_p95":0.60366,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55129,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50168,0.16123,0.21107]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49969,0.19939,0.29937]}],"total_contact_groups":6},"final_pose_error":0.16731,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5031,0.11102,0.03404],"final_tcp_position":[0.50028,0.11435,0.05928],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":56.01525,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.11173,0.03377],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.55693,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":994.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.50516,0.12527,0.13059],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09776,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":336.0,"n_steps_budget":660.0,"object_pos_end":[0.50367,0.11171,0.03385],"object_pos_start":[0.50376,0.11173,0.03377],"object_to_goal_dist_end":0.19184,"object_to_goal_dist_start":0.19187,"object_z_max":0.03388,"peak_contact_force":14.30695,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":337.0,"raw_peak_contact_force":14.30695,"tcp_end":[0.50064,0.11575,0.06027],"tcp_start":[0.50516,0.12527,0.13059],"tcp_to_object_dist_end":0.0269,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":15.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.11116,0.03403],"object_pos_start":[0.50367,0.11171,0.03385],"object_to_goal_dist_end":0.19128,"object_to_goal_dist_start":0.19184,"object_z_max":0.03403,"peak_contact_force":27.60157,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":30.0,"raw_peak_contact_force":56.01525,"subtask_id":"push_through_channel","tcp_end":[0.50028,0.11435,0.05928],"tcp_start":[0.50026,0.11442,0.05931],"tcp_to_object_dist_end":0.0256,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.03597,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07865,"approach_1.approach_speed":0.01781,"contact_1.contact_force_threshold":9.54146,"push_1.force_threshold":44.94157,"push_1.lateral_offset_x":0.0128,"push_1.lateral_offset_y":0.00029,"push_1.push_depth":0.13263,"push_1.push_speed":0.07858},"optimized_scores":{"best_composite_score":-0.09357,"best_fitness_score":0.0031,"best_task_score":0.00274},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.48671,0.11245,0.00941],"force_p95":48.87036,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.5297,"mean_force":30.46025,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4876,0.11916,0.06001]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.49944,0.11881,0.05862],"force_p95":48.374,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.06084,"mean_force":29.99148,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4876,0.11916,0.06001]},{"body_a":"peg","body_b":"channel_base_body","contact_count":356.0,"contact_point_centroid":[0.49599,0.11914,0.00943],"force_p95":0.59611,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.68722,"mean_force":0.58194,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.48468,0.12123,0.0915]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49957,0.11863,0.05898],"force_p95":14.26324,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.26324,"mean_force":14.26324,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.48776,0.11986,0.06066]},{"body_a":"peg","body_b":"channel_base_body","contact_count":975.0,"contact_point_centroid":[0.49617,0.1192,0.00946],"force_p95":0.60198,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.54639,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49079,0.16023,0.20845]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49946,0.19917,0.29863]}],"total_contact_groups":6},"final_pose_error":0.1342,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49568,0.11843,0.0339],"final_tcp_position":[0.48756,0.1181,0.05956],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":52.5297,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.11924,0.0339],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19937,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.56359,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":999.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48384,0.12316,0.12514],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":356.0,"n_steps_budget":630.0,"object_pos_end":[0.49603,0.11925,0.03404],"object_pos_start":[0.49601,0.11924,0.0339],"object_to_goal_dist_end":0.19938,"object_to_goal_dist_start":0.19937,"object_z_max":0.03403,"peak_contact_force":14.68722,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":357.0,"raw_peak_contact_force":14.68722,"tcp_end":[0.48779,0.11985,0.06052],"tcp_start":[0.48384,0.12316,0.12514],"tcp_to_object_dist_end":0.02774,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.49567,0.11857,0.0339],"object_pos_start":[0.49603,0.11925,0.03404],"object_to_goal_dist_end":0.19871,"object_to_goal_dist_start":0.19938,"object_z_max":0.03404,"peak_contact_force":24.86585,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":28.0,"raw_peak_contact_force":52.5297,"subtask_id":"push_through_channel","tcp_end":[0.48756,0.1181,0.05956],"tcp_start":[0.48754,0.11818,0.0596],"tcp_to_object_dist_end":0.02692,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75,"average_solve_count":80.0,"average_success_count":80.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09451,"approach_1.approach_speed":0.07295,"contact_1.contact_force_threshold":13.52162,"push_1.force_threshold":43.5842,"push_1.lateral_offset_x":-0.00593,"push_1.lateral_offset_y":0.00133,"push_1.push_depth":0.13388,"push_1.push_speed":0.05717},"optimized_scores":{"best_composite_score":-0.09354,"best_fitness_score":0.00312,"best_task_score":0.00176},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.4977,0.05404,0.00934],"force_p95":47.27597,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.38219,"mean_force":33.27195,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50523,0.07083,0.05965]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.5171,0.07054,0.05838],"force_p95":46.84386,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.97566,"mean_force":32.83541,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50523,0.07083,0.05965]},{"body_a":"peg","body_b":"channel_base_body","contact_count":531.0,"contact_point_centroid":[0.50602,0.06304,0.00938],"force_p95":0.55272,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.9092,"mean_force":0.59997,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.51103,0.08499,0.11572]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5174,0.07114,0.05879],"force_p95":28.48395,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.48395,"mean_force":28.48395,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.50554,0.07144,0.0605]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50586,0.06296,0.00937],"force_p95":0.55508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56049,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50892,0.14616,0.23113]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49963,0.19842,0.29773]}],"total_contact_groups":6},"final_pose_error":0.14321,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50541,0.06221,0.03377],"final_tcp_position":[0.50509,0.06996,0.05919],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":51.38219,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54709,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1006.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.51875,0.09855,0.17317],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14441,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":531.0,"n_steps_budget":930.0,"object_pos_end":[0.50598,0.06291,0.03381],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.14316,"object_to_goal_dist_start":0.14323,"object_z_max":0.03382,"peak_contact_force":28.9092,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":532.0,"raw_peak_contact_force":28.9092,"tcp_end":[0.50554,0.0714,0.06029],"tcp_start":[0.51875,0.09855,0.17317],"tcp_to_object_dist_end":0.02781,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.50545,0.06235,0.03379],"object_pos_start":[0.50598,0.06291,0.03381],"object_to_goal_dist_end":0.14259,"object_to_goal_dist_start":0.14316,"object_z_max":0.03383,"peak_contact_force":36.52829,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":28.0,"raw_peak_contact_force":51.38219,"subtask_id":"push_through_channel","tcp_end":[0.50509,0.06996,0.05919],"tcp_start":[0.5051,0.07003,0.05923],"tcp_to_object_dist_end":0.02652,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```