## Search State

- **Seed**: 7
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.0888 | 0.00 | ❌ rejected |
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | contact_detected | pose_tolerance | 6 | -0.2605 | 0.08 | ❌ rejected |
| 11 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1314 | 0.26 | ❌ rejected |
| 10 | approach → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.0816 | 0.00 | ❌ rejected |
| 9 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1314 | 0.26 | ❌ rejected |

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

## Current Skill (Q=-0.089) — your mutation base

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

- **Composite score**: -0.089
- **task_score** (E): 0.000
- **fitness_score**: 0.191  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1562 |
| descend_1 | 1.00 | 1.00 | 0.0823 |
| push_1 | 1.00 | 1.00 | 0.1629 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.111, 0.174) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.584 | 2.732 |
| descend_1 | descend | 1.00 / step_budget | (0.505, 0.111, 0.174)→(0.500, 0.100, 0.093) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 1.000 | 0.534 | 0.599 |
| push_1 | push | 1.00 / step_budget | (0.500, 0.100, 0.093)→(0.497, -0.062, 0.088) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 1.000 | 0.534 | 0.605 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.922
- terminal_score: 0.000
- phase_score: 0.341
- phase_breakdown.reach_peg_score: 0.243
- phase_breakdown.push_goal_score: 0.383

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.205
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.089
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.456


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.74427,"average_solve_count":262.0,"average_success_count":262.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.01793,"descend_1.descend_speed":0.05225,"push_1.force_limit":24.2184,"push_1.push_distance":0.19976,"push_1.push_speed":0.04018},"optimized_scores":{"best_composite_score":-0.0894,"best_fitness_score":0.1906,"best_task_score":0.00024},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":290.0,"contact_point_centroid":[0.50344,0.11167,0.00934],"force_p95":0.68736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.57175,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50243,0.1609,0.23469]},{"body_a":"peg","body_b":"channel_base_body","contact_count":296.0,"contact_point_centroid":[0.50368,0.11161,0.00944],"force_p95":0.59507,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62319,"mean_force":0.54127,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49851,0.03149,0.08867]},{"body_a":"peg","body_b":"channel_base_body","contact_count":167.0,"contact_point_centroid":[0.50363,0.11169,0.00939],"force_p95":0.59032,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59983,"mean_force":0.54563,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5032,0.11887,0.13536]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49968,0.1993,0.29932]}],"total_contact_groups":4},"final_pose_error":0.02985,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50372,0.11174,0.03387],"final_tcp_position":[0.49827,-0.05653,0.08816],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":2.06328,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":312.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.11178,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.5807,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":306.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_peg","tcp_end":[0.50603,0.12382,0.17507],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":167.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11178,0.0338],"object_pos_start":[0.50374,0.11178,0.03382],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.19191,"object_z_max":0.03382,"peak_contact_force":0.5304,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":167.0,"raw_peak_contact_force":0.59983,"subtask_id":"reach_peg","tcp_end":[0.50125,0.11396,0.0932],"tcp_start":[0.50603,0.12382,0.17507],"tcp_to_object_dist_end":0.05949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":296.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11174,0.03387],"object_pos_start":[0.50371,0.11178,0.0338],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19192,"object_z_max":0.03411,"peak_contact_force":0.52775,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":296.0,"raw_peak_contact_force":0.62319,"subtask_id":"push_goal","tcp_end":[0.49827,-0.05653,0.08816],"tcp_start":[0.50125,0.11396,0.0932],"tcp_to_object_dist_end":0.17689,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.70833,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.126,"descend_1.descend_speed":0.01473,"push_1.force_limit":32.64436,"push_1.push_distance":0.19994,"push_1.push_speed":0.0917},"optimized_scores":{"best_composite_score":-0.1016,"best_fitness_score":0.1784,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":244.0,"contact_point_centroid":[0.49665,0.11901,0.00937],"force_p95":0.66037,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.57383,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49202,0.16295,0.23299]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49929,0.19795,0.29657]},{"body_a":"peg","body_b":"channel_base_body","contact_count":190.0,"contact_point_centroid":[0.49581,0.11929,0.00939],"force_p95":0.61737,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64316,"mean_force":0.54468,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48715,0.12579,0.13734]},{"body_a":"peg","body_b":"channel_base_body","contact_count":279.0,"contact_point_centroid":[0.49613,0.11919,0.00945],"force_p95":0.59627,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63569,"mean_force":0.54013,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48791,0.03704,0.08865]}],"total_contact_groups":4},"final_pose_error":0.02959,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.496,0.11903,0.03388],"final_tcp_position":[0.48769,-0.04992,0.08815],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":2.24822,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":269.0,"n_steps_budget":810.0,"object_pos_end":[0.49595,0.11906,0.03386],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1992,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.62883,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":268.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_peg","tcp_end":[0.48585,0.13031,0.17598],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14292,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":190.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11922,0.03384],"object_pos_start":[0.49595,0.11906,0.03386],"object_to_goal_dist_end":0.19935,"object_to_goal_dist_start":0.1992,"object_z_max":0.03387,"peak_contact_force":0.52265,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":190.0,"raw_peak_contact_force":0.64316,"subtask_id":"reach_peg","tcp_end":[0.49054,0.12097,0.093],"tcp_start":[0.48585,0.13031,0.17598],"tcp_to_object_dist_end":0.05943,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.496,0.11903,0.03388],"object_pos_start":[0.49602,0.11922,0.03384],"object_to_goal_dist_end":0.19916,"object_to_goal_dist_start":0.19935,"object_z_max":0.03406,"peak_contact_force":0.52778,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":279.0,"raw_peak_contact_force":0.63569,"subtask_id":"push_goal","tcp_end":[0.48769,-0.04992,0.08815],"tcp_start":[0.49054,0.12097,0.093],"tcp_to_object_dist_end":0.17764,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41727,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.10791,"descend_1.descend_speed":0.07365,"push_1.force_limit":27.16726,"push_1.push_distance":0.17613,"push_1.push_speed":0.04998},"optimized_scores":{"best_composite_score":-0.07544,"best_fitness_score":0.20456,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":332.0,"contact_point_centroid":[0.50563,0.06291,0.00934],"force_p95":0.60355,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.58731,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51178,0.13567,0.23027]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50027,0.19598,0.29535]},{"body_a":"peg","body_b":"channel_base_body","contact_count":257.0,"contact_point_centroid":[0.50608,0.06284,0.00938],"force_p95":0.55171,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54656,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50453,-0.00477,0.08844]},{"body_a":"peg","body_b":"channel_base_body","contact_count":154.0,"contact_point_centroid":[0.50568,0.0632,0.00938],"force_p95":0.55164,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55423,"mean_force":0.54657,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51542,0.07235,0.13309]}],"total_contact_groups":4},"final_pose_error":0.02964,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50594,0.06301,0.03381],"final_tcp_position":[0.50426,-0.08079,0.0878],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":3.88411,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54355,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":366.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_peg","tcp_end":[0.52358,0.07837,0.17092],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":154.0,"n_steps_budget":870.0,"object_pos_end":[0.50602,0.06303,0.0338],"object_pos_start":[0.50594,0.06297,0.0338],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14323,"object_z_max":0.03381,"peak_contact_force":0.54967,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":154.0,"raw_peak_contact_force":0.55423,"subtask_id":"reach_peg","tcp_end":[0.50727,0.06632,0.09297],"tcp_start":[0.52358,0.07837,0.17092],"tcp_to_object_dist_end":0.05927,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":257.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.06301,0.03381],"object_pos_start":[0.50602,0.06303,0.0338],"object_to_goal_dist_end":0.14327,"object_to_goal_dist_start":0.14329,"object_z_max":0.03381,"peak_contact_force":0.54792,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":257.0,"raw_peak_contact_force":0.55501,"subtask_id":"push_goal","tcp_end":[0.50426,-0.08079,0.0878],"tcp_start":[0.50727,0.06632,0.09297],"tcp_to_object_dist_end":0.15361,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```