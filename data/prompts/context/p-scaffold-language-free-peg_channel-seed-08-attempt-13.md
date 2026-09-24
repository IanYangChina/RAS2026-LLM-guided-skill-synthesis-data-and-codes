## Search State

- **Seed**: 8
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.4301 | 0.07 | ❌ rejected |
| 12 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | -0.2059 | 0.16 | ❌ rejected |
| 11 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.1693 | 0.00 | ❌ rejected |
| 10 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.2430 | 0.00 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7 | 0.1176 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.07 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.430) — your mutation base

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

- **Composite score**: -0.430
- **task_score** (E): 0.066
- **fitness_score**: 0.027  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.590

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.1587 |
| approach_1 | 1.00 | 1.00 | 0.1225 |
| contact_1 | 0.67 | 1.00 | 0.0215 |
| push_1 | 0.67 | 1.00 | 0.0943 |
| retract_1 | 1.00 | 1.00 | 0.2636 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.518, 0.180, 0.148) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.555 | 3.526 |
| approach_1 | approach | 1.00 / step_budget | (0.518, 0.180, 0.148)→(0.501, 0.104, 0.056) | (0.503, 0.080, 0.034)→(0.503, 0.075, 0.034) | 0.160→0.155 | 1.00 / 1.333 | 13.877 | 70.362 |
| contact_1 | contact | 0.67 / force_exceeded | (0.501, 0.104, 0.056)→(0.499, 0.088, 0.041) | (0.503, 0.075, 0.034)→(0.503, 0.048, 0.027) | 0.155→0.129 | 1.00 / 1.667 | 21.256 | 21.985 |
| push_1 | push | 0.67 / step_budget | (0.499, 0.088, 0.041)→(0.497, 0.182, 0.038) | (0.503, 0.048, 0.027)→(0.503, 0.048, 0.027) | 0.129→0.129 | 1.00 / 1.333 | 17.554 | 20.368 |
| retract_1 | retract | 1.00 / step_budget | (0.497, 0.182, 0.038)→(0.497, -0.060, 0.141) | (0.503, 0.048, 0.027)→(0.502, 0.048, 0.027) | 0.129→0.129 | 1.00 / 1.000 | 0.587 | 22.625 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.268
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.091
- phase_score: 0.000
- phase_breakdown.reach_pre_contact_score: 0.000
- phase_breakdown.push_to_goal_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.036
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.091
- **Median Q (composite search score)**: -0.380
- **K-run variance**: 0.0081
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.238


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.8902,"average_solve_count":255.0,"average_success_count":255.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.approach_speed":0.09949,"align_1.lateral_offset_x":-0.00206,"approach_1.approach_lateral_x":0.00119,"approach_1.approach_speed_close":0.02619,"contact_1.contact_force_threshold":5.66419,"contact_1.contact_speed":0.02256,"push_1.retry_offset_x":0.00314,"push_1.retry_offset_y":0.00125,"retract_1.retract_arc_height":0.05035,"retract_1.retract_speed":0.03867},"optimized_scores":{"best_composite_score":-0.38011,"best_fitness_score":0.00989,"best_task_score":0.02473},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":969.0,"contact_point_centroid":[0.49677,0.11923,0.0094],"force_p95":45.41146,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.6222,"mean_force":5.04323,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48691,0.17628,0.09663]},{"body_a":"attachment","body_b":"peg","contact_count":98.0,"contact_point_centroid":[0.50158,0.13616,0.05693],"force_p95":64.76588,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.10968,"mean_force":44.58392,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49358,0.1449,0.0574]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51317,0.11987,0.00878],"force_p95":53.69986,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.69986,"mean_force":53.69986,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49523,0.14335,0.05535]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50427,0.13567,0.05509],"force_p95":53.35778,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.35778,"mean_force":53.35778,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49523,0.14335,0.05535]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.49681,0.11986,0.00875],"force_p95":49.8164,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.33373,"mean_force":39.88392,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49522,0.14333,0.05527]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50419,0.13559,0.05501],"force_p95":49.25754,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.78404,"mean_force":39.30764,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49522,0.14333,0.05527]},{"body_a":"peg","body_b":"channel_base_body","contact_count":673.0,"contact_point_centroid":[0.49552,0.11403,0.00941],"force_p95":0.65667,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.11178,"mean_force":1.14393,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49439,0.05663,0.12053]},{"body_a":"attachment","body_b":"peg","contact_count":29.0,"contact_point_centroid":[0.50329,0.13412,0.05687],"force_p95":44.57017,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.60214,"mean_force":14.04901,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49453,0.14211,0.05735]},{"body_a":"peg","body_b":"channel_base_body","contact_count":436.0,"contact_point_centroid":[0.49634,0.11913,0.0094],"force_p95":0.62585,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55896,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49042,0.20773,0.22075]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49949,0.19981,0.2975]}],"total_contact_groups":10},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49612,0.11391,0.03383],"final_tcp_position":[0.49686,-0.06033,0.14173],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":65.6222,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":461.0,"n_steps_budget":1000.0,"object_pos_end":[0.49598,0.11901,0.03381],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19915,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.617,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":460.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48277,0.21602,0.14927],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15138,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":969.0,"n_steps_budget":1000.0,"object_pos_end":[0.49709,0.11702,0.03299],"object_pos_start":[0.49598,0.11901,0.03381],"object_to_goal_dist_end":0.19716,"object_to_goal_dist_start":0.19915,"object_z_max":0.03409,"peak_contact_force":40.69691,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1067.0,"raw_peak_contact_force":65.6222,"tcp_end":[0.49523,0.14335,0.05535],"tcp_start":[0.48277,0.21602,0.14927],"tcp_to_object_dist_end":0.03459,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":960.0,"object_pos_end":[0.49707,0.117,0.03297],"object_pos_start":[0.49709,0.11702,0.03299],"object_to_goal_dist_end":0.19715,"object_to_goal_dist_start":0.19716,"object_z_max":0.03299,"peak_contact_force":53.69986,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":53.69986,"tcp_end":[0.49521,0.14332,0.05531],"tcp_start":[0.49523,0.14335,0.05535],"tcp_to_object_dist_end":0.03457,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.49706,0.11699,0.03295],"object_pos_start":[0.49707,0.117,0.03297],"object_to_goal_dist_end":0.19714,"object_to_goal_dist_start":0.19715,"object_z_max":0.03297,"peak_contact_force":51.33373,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":51.33373,"tcp_end":[0.4952,0.14338,0.05519],"tcp_start":[0.49522,0.14335,0.05522],"tcp_to_object_dist_end":0.03456,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":673.0,"n_steps_budget":1000.0,"object_pos_end":[0.49612,0.11391,0.03383],"object_pos_start":[0.49701,0.11702,0.03295],"object_to_goal_dist_end":0.19405,"object_to_goal_dist_start":0.19717,"object_z_max":0.03496,"peak_contact_force":0.5048,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":702.0,"raw_peak_contact_force":49.11178,"tcp_end":[0.49686,-0.06033,0.14173],"tcp_start":[0.4952,0.14338,0.05519],"tcp_to_object_dist_end":0.20495,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.02167,"average_solve_count":323.0,"average_success_count":323.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.approach_speed":0.07314,"align_1.lateral_offset_x":0.01057,"approach_1.approach_lateral_x":7e-05,"approach_1.approach_speed_close":0.0296,"contact_1.contact_force_threshold":6.44334,"contact_1.contact_speed":0.01863,"push_1.retry_offset_x":0.00539,"push_1.retry_offset_y":-0.00251,"retract_1.retract_arc_height":0.06848,"retract_1.retract_speed":0.0364},"optimized_scores":{"best_composite_score":-0.35376,"best_fitness_score":0.03624,"best_task_score":0.09061},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":736.0,"contact_point_centroid":[0.50629,0.06287,0.00936],"force_p95":35.18066,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.58485,"mean_force":3.51252,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51738,0.12504,0.09774]},{"body_a":"attachment","body_b":"peg","contact_count":54.0,"contact_point_centroid":[0.51006,0.07889,0.05756],"force_p95":70.37278,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.12547,"mean_force":40.50564,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50551,0.08969,0.05766]},{"body_a":"peg","body_b":"channel_base_body","contact_count":567.0,"contact_point_centroid":[0.50511,0.02105,0.0083],"force_p95":0.81721,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.46588,"mean_force":0.60499,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50201,0.07313,0.04174]},{"body_a":"peg","body_b":"channel_base_body","contact_count":884.0,"contact_point_centroid":[0.50478,0.0196,0.00805],"force_p95":0.72551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.19048,"mean_force":0.68612,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49611,0.09465,0.11818]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.04076,0.02381],"force_p95":9.0421,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.0421,"mean_force":9.0421,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50177,0.06493,0.03576]},{"body_a":"peg","body_b":"channel_base_body","contact_count":366.0,"contact_point_centroid":[0.50607,0.01721,0.0081],"force_p95":0.75972,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.99849,"mean_force":0.81502,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49874,0.1354,0.03142]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.525,0.04379,0.02448],"force_p95":8.63286,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.72823,"mean_force":3.95288,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49522,0.18166,0.06843]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":23.0,"contact_point_centroid":[0.525,0.04174,0.02446],"force_p95":8.38583,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.56538,"mean_force":3.76087,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49964,0.0885,0.03278]},{"body_a":"peg","body_b":"channel_base_body","contact_count":498.0,"contact_point_centroid":[0.50571,0.06304,0.00935],"force_p95":0.57422,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57372,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51665,0.18148,0.21927]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50026,0.19893,0.29634]}],"total_contact_groups":10},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50296,0.02012,0.0241],"final_tcp_position":[0.49714,-0.06056,0.1429],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":72.58485,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":526.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.06298,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54155,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":532.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.53389,0.16496,0.14726],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15507,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":736.0,"n_steps_budget":1000.0,"object_pos_end":[0.50584,0.05717,0.03487],"object_pos_start":[0.50603,0.06298,0.03381],"object_to_goal_dist_end":0.13739,"object_to_goal_dist_start":0.14324,"object_z_max":0.03451,"peak_contact_force":0.46079,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":790.0,"raw_peak_contact_force":72.58485,"tcp_end":[0.50541,0.08755,0.05561],"tcp_start":[0.53389,0.16496,0.14726],"tcp_to_object_dist_end":0.03679,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":577.0,"n_steps_budget":1000.0,"object_pos_end":[0.5061,0.01642,0.02402],"object_pos_start":[0.50584,0.05717,0.03487],"object_to_goal_dist_end":0.09792,"object_to_goal_dist_start":0.13739,"object_z_max":0.04081,"peak_contact_force":9.46588,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":568.0,"raw_peak_contact_force":9.46588,"tcp_end":[0.50177,0.0649,0.03574],"tcp_start":[0.50541,0.08755,0.05561],"tcp_to_object_dist_end":0.05007,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":366.0,"n_steps_budget":1000.0,"object_pos_end":[0.50608,0.01852,0.02411],"object_pos_start":[0.5061,0.01642,0.02402],"object_to_goal_dist_end":0.09998,"object_to_goal_dist_start":0.09792,"object_z_max":0.02481,"peak_contact_force":0.71722,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":389.0,"raw_peak_contact_force":8.99849,"tcp_end":[0.49824,0.20628,0.03041],"tcp_start":[0.50177,0.0649,0.03574],"tcp_to_object_dist_end":0.18803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":884.0,"n_steps_budget":1000.0,"object_pos_end":[0.50296,0.02012,0.0241],"object_pos_start":[0.50608,0.01852,0.02411],"object_to_goal_dist_end":0.10142,"object_to_goal_dist_start":0.09998,"object_z_max":0.02499,"peak_contact_force":0.63682,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":904.0,"raw_peak_contact_force":9.19048,"tcp_end":[0.49714,-0.06056,0.1429],"tcp_start":[0.49824,0.20628,0.03041],"tcp_to_object_dist_end":0.14372,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06667,"average_solve_count":315.0,"average_success_count":315.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.approach_speed":0.05653,"align_1.lateral_offset_x":0.00594,"approach_1.approach_lateral_x":-0.00361,"approach_1.approach_speed_close":0.03841,"contact_1.contact_force_threshold":6.37282,"contact_1.contact_speed":0.01353,"push_1.retry_offset_x":0.00212,"push_1.retry_offset_y":-0.00055,"retract_1.retract_arc_height":0.0525,"retract_1.retract_speed":0.05989},"optimized_scores":{"best_composite_score":-0.55641,"best_fitness_score":0.03359,"best_task_score":0.08399},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":708.0,"contact_point_centroid":[0.50617,0.05658,0.00936],"force_p95":39.44303,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.87956,"mean_force":3.79141,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51681,0.11903,0.09769]},{"body_a":"attachment","body_b":"peg","contact_count":53.0,"contact_point_centroid":[0.50791,0.07292,0.05753],"force_p95":70.40439,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.43032,"mean_force":43.42672,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50247,0.08333,0.05768]},{"body_a":"peg","body_b":"channel_base_body","contact_count":810.0,"contact_point_centroid":[0.50565,0.00991,0.00807],"force_p95":0.69576,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.57208,"mean_force":0.63727,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49591,0.08436,0.10734]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.525,0.03487,0.02421],"force_p95":9.09343,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.0981,"mean_force":2.97601,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49581,0.07509,0.09569]},{"body_a":"peg","body_b":"channel_base_body","contact_count":537.0,"contact_point_centroid":[0.50593,0.05662,0.00935],"force_p95":0.60137,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.57615,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51768,0.17848,0.21921]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50022,0.19879,0.29619]},{"body_a":"peg","body_b":"channel_base_body","contact_count":989.0,"contact_point_centroid":[0.506,0.013,0.00827],"force_p95":0.72551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.78823,"mean_force":0.595,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50051,0.06478,0.04017]},{"body_a":"peg","body_b":"channel_base_body","contact_count":363.0,"contact_point_centroid":[0.50597,0.00966,0.00806],"force_p95":0.69575,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77223,"mean_force":0.60521,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49845,0.12563,0.02901]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.525,0.03466,0.02415],"force_p95":0.40903,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41027,"mean_force":0.39634,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5007,0.06181,0.03789]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.03462,0.02415],"force_p95":0.38077,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38077,"mean_force":0.38077,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49856,0.08878,0.0293]}],"total_contact_groups":10},"final_pose_error":0.01968,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50674,0.01031,0.02431],"final_tcp_position":[0.49707,-0.06055,0.13938],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":72.87956,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":566.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.05661,0.03376],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13689,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.50661,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":574.0,"raw_peak_contact_force":4.44541,"tcp_end":[0.536,0.1591,0.14696],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1556,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":708.0,"n_steps_budget":1000.0,"object_pos_end":[0.50607,0.0509,0.03471],"object_pos_start":[0.50611,0.05661,0.03376],"object_to_goal_dist_end":0.13115,"object_to_goal_dist_start":0.13689,"object_z_max":0.03435,"peak_contact_force":0.47306,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":761.0,"raw_peak_contact_force":72.87956,"tcp_end":[0.50224,0.0811,0.05566],"tcp_start":[0.536,0.1591,0.14696],"tcp_to_object_dist_end":0.03696,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50663,0.00986,0.02424],"object_pos_start":[0.50607,0.0509,0.03471],"object_to_goal_dist_end":0.09147,"object_to_goal_dist_start":0.13115,"object_z_max":0.04078,"peak_contact_force":0.60294,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":992.0,"raw_peak_contact_force":2.78823,"tcp_end":[0.5015,0.05521,0.03328],"tcp_start":[0.50224,0.0811,0.05566],"tcp_to_object_dist_end":0.04653,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":363.0,"n_steps_budget":990.0,"object_pos_end":[0.50562,0.00978,0.02416],"object_pos_start":[0.50663,0.00986,0.02424],"object_to_goal_dist_end":0.09134,"object_to_goal_dist_start":0.09147,"object_z_max":0.02429,"peak_contact_force":0.61227,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":364.0,"raw_peak_contact_force":0.77223,"tcp_end":[0.49795,0.19631,0.02802],"tcp_start":[0.5015,0.05521,0.03328],"tcp_to_object_dist_end":0.18672,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":810.0,"n_steps_budget":1000.0,"object_pos_end":[0.50674,0.01031,0.02431],"object_pos_start":[0.50562,0.00978,0.02416],"object_to_goal_dist_end":0.09191,"object_to_goal_dist_start":0.09134,"object_z_max":0.02445,"peak_contact_force":0.62058,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":820.0,"raw_peak_contact_force":9.57208,"tcp_end":[0.49707,-0.06055,0.13938],"tcp_start":[0.49795,0.19631,0.02802],"tcp_to_object_dist_end":0.13548,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```