## Search State

- **Seed**: 8
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.1693 | 0.00 | ❌ rejected |
| 10 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.2430 | 0.00 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7 | 0.1176 | 0.00 | ❌ rejected |
| 8 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.1014 | 0.00 | ❌ rejected |
| 7 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.0361 | 0.05 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`
- Frozen object start: [0.48615778212844485, 0.11898214746703403, 0.04]
- Frozen task target: [0.48615778212844485, -0.04101785253296597, 0.04]
- Goal object position: (0.48615778212844485, -0.04101785253296597, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48615778212844485, 0.11898214746703403, 0.04)
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
  frozen_object_start: [0.4862, 0.119, 0.04]
  frozen_task_target: [0.4862, -0.041, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48615778212844485, 0.11898214746703403, 0.04]}
  frozen_targets: {'channel_exit': [0.48615778212844485, -0.04101785253296597, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e

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
| `object` | offset from object initial position (0.48615778212844485, 0.11898214746703403, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48615778212844485, -0.04101785253296597, 0.04) | final destination targets |
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

## Current Skill (Q=-0.169) — your mutation base

```yaml
skill: peg_channel
phases:
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
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: contact_1
  type: contact
  generator: impedance_motion
  control: force_threshold_switch
  termination: contact_detected
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
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
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
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: -0.169
- **task_score** (E): 0.002
- **fitness_score**: 0.071  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2109 |
| descend_1 | 1.00 | 1.00 | 0.0655 |
| contact_1 | 1.00 | 1.00 | 0.0027 |
| push_1 | 0.00 | 1.00 | 0.0010 |
| retract_1 | 1.00 | 1.00 | 0.1808 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.086, 0.126) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.521 | 3.526 |
| descend_1 | descend | 1.00 / step_budget | (0.513, 0.086, 0.126)→(0.501, 0.080, 0.063) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.558 | 0.603 |
| contact_1 | contact | 1.00 / force_exceeded | (0.501, 0.080, 0.063)→(0.500, 0.080, 0.061) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 19.765 | 19.765 |
| push_1 | push | 0.00 / guard_failure | (0.501, 0.080, 0.060)→(0.502, 0.079, 0.060) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 2.667 | 256.350 | 256.350 |
| retract_1 | retract | 1.00 / step_budget | (0.502, 0.079, 0.060)→(0.500, 0.084, 0.240) | (0.504, 0.079, 0.034)→(0.504, 0.093, 0.027) | 0.160→0.173 | 1.00 / 1.000 | 0.550 | 67.102 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.006
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.002
- phase_score: 0.124
- phase_breakdown.reach_goal_score: 0.065
- phase_breakdown.reach_pre_contact_score: 0.263

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.075
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.003
- **Median Q (composite search score)**: -0.165
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.309


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a8ce855c7f52ba2d198de8387bdd2f3b869655c206850d620daaec6ac6f298cd`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `79b30dd7102e96fb2fa0880d3932c959e04a6f943c7e87b878f77a0e54f87a94`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.12481,"contact_1.contact_force":7.00092,"contact_1.probe_speed":0.00535,"descend_1.descend_speed":0.05761,"push_1.push_force_limit":10.68772,"push_1.push_speed":0.04963,"retract_1.retract_speed":0.06313},"optimized_scores":{"best_composite_score":-0.17764,"best_fitness_score":0.06236,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.51385,0.11999,0.00952],"force_p95":150.57216,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":154.71915,"mean_force":120.71485,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48973,0.11942,0.06062]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50131,0.11692,0.05902],"force_p95":150.01564,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":154.1287,"mean_force":120.34195,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48973,0.11942,0.06062]},{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.49547,0.11999,0.0095],"force_p95":11.40808,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.21378,"mean_force":2.49363,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49003,0.11909,0.06146]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5014,0.11724,0.05911],"force_p95":21.70261,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.70261,"mean_force":21.70261,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48966,0.11898,0.06087]},{"body_a":"peg","body_b":"channel_base_body","contact_count":139.0,"contact_point_centroid":[0.49595,0.11992,0.00944],"force_p95":0.79327,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.28894,"mean_force":0.76068,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48812,0.12674,0.07779]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.50129,0.11668,0.05871],"force_p95":12.07382,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.74068,"mean_force":2.62031,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49007,0.12049,0.06002]},{"body_a":"peg","body_b":"world","contact_count":450.0,"contact_point_centroid":[0.4969,0.15812,-0.00182],"force_p95":0.74916,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.87177,"mean_force":0.61572,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48765,0.13552,0.17021]},{"body_a":"peg","body_b":"channel_base_body","contact_count":538.0,"contact_point_centroid":[0.49629,0.11911,0.00942],"force_p95":0.61095,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55522,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49117,0.16069,0.21008]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49947,0.19879,0.29771]},{"body_a":"peg","body_b":"channel_base_body","contact_count":242.0,"contact_point_centroid":[0.49594,0.11904,0.00945],"force_p95":0.59902,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65083,"mean_force":0.54078,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48629,0.12145,0.09512]}],"total_contact_groups":10},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50021,0.16035,0.01409],"final_tcp_position":[0.48812,0.12498,0.2409],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":154.71915,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":563.0,"n_steps_budget":990.0,"object_pos_end":[0.49603,0.11925,0.0339],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19938,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50543,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":562.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_pre_contact","tcp_end":[0.48421,0.12399,0.12823],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09518,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":242.0,"n_steps_budget":840.0,"object_pos_end":[0.49602,0.11936,0.03396],"object_pos_start":[0.49603,0.11925,0.0339],"object_to_goal_dist_end":0.19949,"object_to_goal_dist_start":0.19938,"object_z_max":0.03403,"peak_contact_force":0.53543,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":242.0,"raw_peak_contact_force":0.65083,"subtask_id":"reach_pre_contact","tcp_end":[0.4905,0.11926,0.06221],"tcp_start":[0.48421,0.12399,0.12823],"tcp_to_object_dist_end":0.02878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":11.0,"n_steps_budget":1000.0,"object_pos_end":[0.49606,0.11941,0.03409],"object_pos_start":[0.49602,0.11936,0.03396],"object_to_goal_dist_end":0.19953,"object_to_goal_dist_start":0.19949,"object_z_max":0.03408,"peak_contact_force":22.21378,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":12.0,"raw_peak_contact_force":22.21378,"subtask_id":"reach_pre_contact","tcp_end":[0.48962,0.11897,0.06077],"tcp_start":[0.4905,0.11926,0.06221],"tcp_to_object_dist_end":0.02745,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49612,0.11957,0.0341],"object_pos_start":[0.49606,0.11941,0.03409],"object_to_goal_dist_end":0.1997,"object_to_goal_dist_start":0.19953,"object_z_max":0.03412,"peak_contact_force":154.71915,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":154.71915,"subtask_id":"reach_goal","tcp_end":[0.49034,0.12057,0.06028],"tcp_start":[0.4899,0.11999,0.06047],"tcp_to_object_dist_end":0.02682,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":592.0,"n_steps_budget":1000.0,"object_pos_end":[0.50021,0.16035,0.01409],"object_pos_start":[0.49643,0.12018,0.03417],"object_to_goal_dist_end":0.24174,"object_to_goal_dist_start":0.2003,"object_z_max":0.03422,"peak_contact_force":0.56216,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":603.0,"raw_peak_contact_force":19.28894,"tcp_end":[0.48812,0.12498,0.2409],"tcp_start":[0.49034,0.12057,0.06028],"tcp_to_object_dist_end":0.22987,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":23.0,"average_failure_rate":0.09957,"average_mean_iterations":23.05195,"average_solve_count":231.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.03173,"contact_1.contact_force":17.54102,"contact_1.probe_speed":0.02827,"descend_1.descend_speed":0.04261,"push_1.push_force_limit":23.93794,"push_1.push_speed":0.05403,"retract_1.retract_speed":0.09842},"optimized_scores":{"best_composite_score":-0.16525,"best_fitness_score":0.07475,"best_task_score":0.00324},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.5174,0.06371,0.05842],"force_p95":294.47216,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":317.05323,"mean_force":159.28514,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50557,0.06318,0.05999]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.51449,0.05915,0.00925],"force_p95":227.14344,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":237.59296,"mean_force":140.13365,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50557,0.06318,0.05999]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52521,0.06201,0.05827],"force_p95":137.83423,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":137.83423,"mean_force":137.83423,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50642,0.0625,0.05953]},{"body_a":"attachment","body_b":"peg","contact_count":17.0,"contact_point_centroid":[0.51916,0.06384,0.05769],"force_p95":88.95798,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":102.20087,"mean_force":24.31419,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50752,0.06161,0.05897]},{"body_a":"peg","body_b":"channel_base_body","contact_count":576.0,"contact_point_centroid":[0.50533,0.06087,0.00939],"force_p95":0.60116,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":95.54904,"mean_force":1.19617,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50481,0.07422,0.14618]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52564,0.06145,0.05782],"force_p95":30.7452,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.0444,"mean_force":17.01416,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50808,0.06162,0.05861]},{"body_a":"peg","body_b":"channel_base_body","contact_count":16.0,"contact_point_centroid":[0.50486,0.05987,0.00939],"force_p95":4.90001,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.94736,"mean_force":1.63416,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50552,0.06382,0.06202]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5169,0.06315,0.05883],"force_p95":17.51246,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.51246,"mean_force":17.51246,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50505,0.06374,0.06062]},{"body_a":"peg","body_b":"channel_base_body","contact_count":783.0,"contact_point_centroid":[0.50581,0.06295,0.00937],"force_p95":0.55639,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56384,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51178,0.1328,0.20788]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49973,0.19805,0.29711]},{"body_a":"peg","body_b":"channel_base_body","contact_count":205.0,"contact_point_centroid":[0.50597,0.06326,0.00938],"force_p95":0.55119,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55419,"mean_force":0.54657,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51519,0.06699,0.09473]}],"total_contact_groups":11},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50493,0.06156,0.03383],"final_tcp_position":[0.50509,0.06651,0.23989],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":317.05323,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":811.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.063,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54465,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":817.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_pre_contact","tcp_end":[0.5247,0.07007,0.1248],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09317,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":205.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.06298,0.03381],"object_pos_start":[0.50594,0.063,0.03381],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.14326,"object_z_max":0.03381,"peak_contact_force":0.54194,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":205.0,"raw_peak_contact_force":0.55419,"subtask_id":"reach_pre_contact","tcp_end":[0.50622,0.06397,0.06346],"tcp_start":[0.5247,0.07007,0.1248],"tcp_to_object_dist_end":0.02967,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":16.0,"n_steps_budget":900.0,"object_pos_end":[0.50595,0.06303,0.0338],"object_pos_start":[0.50603,0.06298,0.03381],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14324,"object_z_max":0.03381,"peak_contact_force":17.94736,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":17.0,"raw_peak_contact_force":17.94736,"subtask_id":"reach_pre_contact","tcp_end":[0.50501,0.06373,0.06044],"tcp_start":[0.50622,0.06397,0.06346],"tcp_to_object_dist_end":0.02667,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50629,0.06275,0.03372],"object_pos_start":[0.50595,0.06303,0.0338],"object_to_goal_dist_end":0.14303,"object_to_goal_dist_start":0.14328,"object_z_max":0.03384,"peak_contact_force":317.05323,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":317.05323,"subtask_id":"reach_goal","tcp_end":[0.50732,0.06194,0.05921],"tcp_start":[0.50642,0.0625,0.05953],"tcp_to_object_dist_end":0.02552,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":576.0,"n_steps_budget":1000.0,"object_pos_end":[0.50493,0.06156,0.03383],"object_pos_start":[0.50701,0.06226,0.03391],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14256,"object_z_max":0.03455,"peak_contact_force":0.54801,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":600.0,"raw_peak_contact_force":102.20087,"tcp_end":[0.50509,0.06651,0.23989],"tcp_start":[0.50732,0.06194,0.05921],"tcp_to_object_dist_end":0.20612,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":38.0,"average_failure_rate":0.19792,"average_mean_iterations":43.07292,"average_solve_count":192.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.10356,"contact_1.contact_force":13.04356,"contact_1.probe_speed":0.01475,"descend_1.descend_speed":0.03607,"push_1.push_force_limit":17.52664,"push_1.push_speed":0.01711,"retract_1.retract_speed":0.08351},"optimized_scores":{"best_composite_score":-0.1649,"best_fitness_score":0.0751,"best_task_score":0.00179},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.51874,0.05748,0.05836],"force_p95":278.60503,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":297.27815,"mean_force":154.37643,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50693,0.05683,0.05991]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.51524,0.05256,0.00923],"force_p95":207.42225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":213.2577,"mean_force":134.16338,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50693,0.05683,0.05991]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.5253,0.0555,0.05827],"force_p95":142.03202,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":142.03202,"mean_force":142.03202,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5078,0.05607,0.05947]},{"body_a":"attachment","body_b":"peg","contact_count":17.0,"contact_point_centroid":[0.52049,0.05728,0.05765],"force_p95":51.08929,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.8175,"mean_force":14.36706,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50889,0.0554,0.05891]},{"body_a":"peg","body_b":"channel_base_body","contact_count":576.0,"contact_point_centroid":[0.50617,0.05611,0.00938],"force_p95":0.60692,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":79.80795,"mean_force":0.94434,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50605,0.06858,0.14734]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.52531,0.05564,0.0584],"force_p95":21.52889,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.33465,"mean_force":3.13421,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50753,0.05935,0.06935]},{"body_a":"peg","body_b":"channel_base_body","contact_count":17.0,"contact_point_centroid":[0.50587,0.0575,0.00937],"force_p95":4.30868,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.13463,"mean_force":1.63981,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5069,0.05749,0.06188]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51825,0.05678,0.05875],"force_p95":18.65815,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.65815,"mean_force":18.65815,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5064,0.05741,0.06052]},{"body_a":"peg","body_b":"channel_base_body","contact_count":730.0,"contact_point_centroid":[0.5059,0.05663,0.00936],"force_p95":0.60032,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56839,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51534,0.12901,0.20691]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50003,0.1973,0.29615]},{"body_a":"peg","body_b":"channel_base_body","contact_count":206.0,"contact_point_centroid":[0.50631,0.05653,0.00938],"force_p95":0.59761,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60282,"mean_force":0.54671,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51939,0.06067,0.0944]}],"total_contact_groups":11},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50601,0.05559,0.03413],"final_tcp_position":[0.50643,0.05994,0.24009],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":297.27815,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":759.0,"n_steps_budget":1000.0,"object_pos_end":[0.50615,0.05661,0.03376],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13689,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.51393,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":767.0,"raw_peak_contact_force":4.44541,"subtask_id":"reach_pre_contact","tcp_end":[0.5312,0.06374,0.12421],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09412,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":206.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.05664,0.03377],"object_pos_start":[0.50615,0.05661,0.03376],"object_to_goal_dist_end":0.13692,"object_to_goal_dist_start":0.13689,"object_z_max":0.03378,"peak_contact_force":0.5974,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":206.0,"raw_peak_contact_force":0.60282,"subtask_id":"reach_pre_contact","tcp_end":[0.50772,0.05763,0.06328],"tcp_start":[0.5312,0.06374,0.12421],"tcp_to_object_dist_end":0.02957,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":17.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.05665,0.03377],"object_pos_start":[0.50611,0.05664,0.03377],"object_to_goal_dist_end":0.13693,"object_to_goal_dist_start":0.13692,"object_z_max":0.03377,"peak_contact_force":19.13463,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":18.0,"raw_peak_contact_force":19.13463,"subtask_id":"reach_pre_contact","tcp_end":[0.50636,0.0574,0.06035],"tcp_start":[0.50772,0.05763,0.06328],"tcp_to_object_dist_end":0.02659,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50644,0.05635,0.0337],"object_pos_start":[0.50611,0.05665,0.03377],"object_to_goal_dist_end":0.13664,"object_to_goal_dist_start":0.13693,"object_z_max":0.03384,"peak_contact_force":297.27815,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":297.27815,"subtask_id":"reach_goal","tcp_end":[0.50871,0.05543,0.05916],"tcp_start":[0.5078,0.05607,0.05947],"tcp_to_object_dist_end":0.02558,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":576.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,0.05559,0.03413],"object_pos_start":[0.50718,0.0558,0.03394],"object_to_goal_dist_end":0.13585,"object_to_goal_dist_start":0.13612,"object_z_max":0.0343,"peak_contact_force":0.5405,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":613.0,"raw_peak_contact_force":79.8175,"tcp_end":[0.50643,0.05994,0.24009],"tcp_start":[0.50871,0.05543,0.05916],"tcp_to_object_dist_end":0.206,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```