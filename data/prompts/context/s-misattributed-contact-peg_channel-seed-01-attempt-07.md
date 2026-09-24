## Search State

- **Seed**: 1
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.1045 | 0.19 | ❌ rejected |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.3286 | 0.00 | ❌ rejected |
| 5 | approach → align → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.1682 | 0.00 | ❌ rejected |
| 4 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1680 | 0.40 | ✅ accepted |
| 3 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1494 | 0.30 | ✅ accepted |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`
- Frozen object start: [0.5009457299760205, 0.11603709570607482, 0.04]
- Frozen task target: [0.5009457299760205, -0.04396290429392519, 0.04]
- Goal object position: (0.5009457299760205, -0.04396290429392519, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5009457299760205, 0.11603709570607482, 0.04)
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
  frozen_object_start: [0.5009, 0.116, 0.04]
  frozen_task_target: [0.5009, -0.044, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5009457299760205, 0.11603709570607482, 0.04]}
  frozen_targets: {'channel_exit': [0.5009457299760205, -0.04396290429392519, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a

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
| `object` | offset from object initial position (0.5009457299760205, 0.11603709570607482, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5009457299760205, -0.04396290429392519, 0.04) | final destination targets |
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

## Current Skill (Q=0.105) — your mutation base

```yaml
skill: peg_channel
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
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
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: align_2
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

```

## Design Metrics

- **Composite score**: 0.105
- **task_score** (E): 0.186
- **fitness_score**: 0.385  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1831 |
| descend_to_push | 0.00 | 1.00 | 0.0900 |
| push_along_channel | 0.00 | 1.00 | 0.1697 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.482, 0.093, 0.154) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.543 | 0.585 |
| descend_to_push | descend | 0.00 / step_budget | (0.482, 0.093, 0.154)→(0.492, 0.080, 0.066) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 88.647 | 88.647 |
| push_along_channel | push | 0.00 / guard_failure | (0.492, 0.080, 0.066)→(0.493, -0.088, 0.044) | (0.497, 0.080, 0.034)→(0.495, 0.036, 0.024) | 0.160→0.117 | 1.00 / 1.000 | 0.555 | 2.857 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.274
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.274
- phase_score: 0.523
- phase_breakdown.reach_above_peg_score: 0.672
- phase_breakdown.reach_push_start_score: 0.930
- phase_breakdown.push_through_channel_score: 0.219

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.423
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.274
- **Median Q (composite search score)**: 0.121
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.292


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a904e23429ae963dd2788b3e8d0575d9ce341e1daddfe013fbb1224c3e0c850e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6bee39a4c127c6d39ee1365e3969a50bb09484f7e2580b1a3dc4d8c4ae20213b`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25974,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.13512,"descend_to_push.descend_force":12.88807,"descend_to_push.lateral_offset_x":0.00439,"push_along_channel.push_distance":0.05938,"push_along_channel.push_speed":0.02479},"optimized_scores":{"best_composite_score":0.14324,"best_fitness_score":0.42324,"best_task_score":0.27367},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.5006,-0.10014,0.065],"force_p95":93.52849,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.52849,"mean_force":93.52849,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4967,-0.08811,0.04051]},{"body_a":"peg","body_b":"channel_base_body","contact_count":511.0,"contact_point_centroid":[0.49932,0.08886,0.00898],"force_p95":11.57639,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.32092,"mean_force":1.52616,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49759,0.01399,0.05166]},{"body_a":"attachment","body_b":"peg","contact_count":52.0,"contact_point_centroid":[0.50536,0.09123,0.0584],"force_p95":17.61958,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.83381,"mean_force":9.46837,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49843,0.08182,0.05921]},{"body_a":"peg","body_b":"channel_base_body","contact_count":286.0,"contact_point_centroid":[0.5009,0.11591,0.00934],"force_p95":0.71997,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.57255,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49879,0.16229,0.2252]},{"body_a":"peg","body_b":"channel_base_body","contact_count":460.0,"contact_point_centroid":[0.50092,0.1161,0.00941],"force_p95":0.61069,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64865,"mean_force":0.54369,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"descend","tcp_position_centroid":[0.49865,0.12104,0.10979]}],"total_contact_groups":5},"final_pose_error":0.05105,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49727,0.07225,0.0241],"final_tcp_position":[0.4967,-0.08844,0.04047],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":93.52849,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":302.0,"n_steps_budget":840.0,"object_pos_end":[0.50098,0.11605,0.03382],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.53965,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":460.0,"raw_peak_contact_force":0.64865,"subtask_id":"reach_above_peg","tcp_end":[0.49851,0.12666,0.15665],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12331,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":460.0,"n_steps_budget":600.0,"object_pos_end":[0.50089,0.11605,0.0338],"object_pos_start":[0.50098,0.11605,0.03382],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19615,"object_z_max":0.03395,"peak_contact_force":93.52849,"phase_name":"descend_to_push","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":564.0,"raw_peak_contact_force":93.52849,"subtask_id":"reach_push_start","tcp_end":[0.50111,0.11605,0.06635],"tcp_start":[0.49851,0.12666,0.15665],"tcp_to_object_dist_end":0.03255,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":521.0,"n_steps_budget":1000.0,"object_pos_end":[0.49727,0.07225,0.0241],"object_pos_start":[0.50089,0.11605,0.0338],"object_to_goal_dist_end":0.1531,"object_to_goal_dist_start":0.19615,"object_z_max":0.04078,"peak_contact_force":0.56914,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":286.0,"raw_peak_contact_force":1.92055,"subtask_id":"push_through_channel","tcp_end":[0.4967,-0.08844,0.04047],"tcp_start":[0.50111,0.11605,0.06635],"tcp_to_object_dist_end":0.16152,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8416ac3bebb4dbec2abbf751596843a33db171fd8d70765023f3b940d846bd0c`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40845,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.09416,"descend_to_push.descend_force":14.58542,"descend_to_push.lateral_offset_x":-0.00266,"push_along_channel.push_distance":0.12874,"push_along_channel.push_speed":0.04234},"optimized_scores":{"best_composite_score":0.12123,"best_fitness_score":0.40123,"best_task_score":0.19293},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.4942,-0.10016,0.065],"force_p95":80.71077,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":80.71077,"mean_force":80.71077,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49126,-0.08816,0.04675]},{"body_a":"peg","body_b":"channel_base_body","contact_count":388.0,"contact_point_centroid":[0.49467,0.0381,0.00901],"force_p95":17.96409,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.37378,"mean_force":2.54444,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48842,-0.01143,0.05487]},{"body_a":"attachment","body_b":"peg","contact_count":60.0,"contact_point_centroid":[0.49375,0.03921,0.05863],"force_p95":21.64618,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.90686,"mean_force":12.23778,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.487,0.03025,0.05933]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.475,-0.00492,0.02438],"force_p95":8.92402,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.96653,"mean_force":3.42666,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49078,-0.07724,0.04783]},{"body_a":"peg","body_b":"channel_base_body","contact_count":349.0,"contact_point_centroid":[0.49545,0.06394,0.00936],"force_p95":0.6269,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56981,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48934,0.13608,0.22131]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49924,0.19707,0.29633]},{"body_a":"peg","body_b":"channel_base_body","contact_count":497.0,"contact_point_centroid":[0.4953,0.06375,0.0094],"force_p95":0.55032,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5516,"mean_force":0.54559,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"descend","tcp_position_centroid":[0.48314,0.07106,0.10755]}],"total_contact_groups":7},"final_pose_error":0.12076,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49314,0.0196,0.02456],"final_tcp_position":[0.49127,-0.08848,0.04672],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":80.71077,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":376.0,"n_steps_budget":1000.0,"object_pos_end":[0.49508,0.06369,0.03392],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.1439,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54336,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":497.0,"raw_peak_contact_force":0.5516,"subtask_id":"reach_above_peg","tcp_end":[0.48066,0.07841,0.15313],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12097,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":497.0,"n_steps_budget":600.0,"object_pos_end":[0.49525,0.06408,0.034],"object_pos_start":[0.49508,0.06369,0.03392],"object_to_goal_dist_end":0.14429,"object_to_goal_dist_start":0.1439,"object_z_max":0.034,"peak_contact_force":80.71077,"phase_name":"descend_to_push","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":460.0,"raw_peak_contact_force":80.71077,"subtask_id":"reach_push_start","tcp_end":[0.48791,0.06426,0.06585],"tcp_start":[0.48066,0.07841,0.15313],"tcp_to_object_dist_end":0.03269,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":397.0,"n_steps_budget":1000.0,"object_pos_end":[0.49314,0.0196,0.02456],"object_pos_start":[0.49525,0.06408,0.034],"object_to_goal_dist_end":0.10103,"object_to_goal_dist_start":0.14429,"object_z_max":0.04076,"peak_contact_force":0.54545,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":377.0,"raw_peak_contact_force":2.44546,"subtask_id":"push_through_channel","tcp_end":[0.49127,-0.08848,0.04672],"tcp_start":[0.48791,0.06426,0.06585],"tcp_to_object_dist_end":0.11035,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0188121de1b8142d5ff7a7406b62c43adf6da5520b986a997e46ef53b7d11bf9`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.11111,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.14891,"descend_to_push.descend_force":10.45805,"descend_to_push.lateral_offset_x":-0.00203,"push_along_channel.push_distance":0.10428,"push_along_channel.push_speed":0.08824},"optimized_scores":{"best_composite_score":0.04905,"best_fitness_score":0.32905,"best_task_score":0.09138},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49453,-0.1,0.065],"force_p95":91.70132,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.70132,"mean_force":91.70132,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4914,-0.08783,0.04549]},{"body_a":"peg","body_b":"channel_base_body","contact_count":351.0,"contact_point_centroid":[0.49488,0.03167,0.00894],"force_p95":26.86082,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.08601,"mean_force":3.65073,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48805,-0.01407,0.05425]},{"body_a":"attachment","body_b":"peg","contact_count":66.0,"contact_point_centroid":[0.49289,0.03449,0.05854],"force_p95":30.46046,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.68001,"mean_force":16.38118,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48645,0.02562,0.05911]},{"body_a":"peg","body_b":"channel_base_body","contact_count":338.0,"contact_point_centroid":[0.49446,0.05906,0.00933],"force_p95":0.61189,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.58948,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48271,0.13298,0.22046]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49858,0.19561,0.29454]},{"body_a":"peg","body_b":"channel_base_body","contact_count":536.0,"contact_point_centroid":[0.49427,0.05887,0.00939],"force_p95":0.55039,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54611,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"descend","tcp_position_centroid":[0.47618,0.06639,0.10791]}],"total_contact_groups":6},"final_pose_error":0.09664,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49371,0.01533,0.02423],"final_tcp_position":[0.49143,-0.08818,0.04545],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":91.70132,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":367.0,"n_steps_budget":900.0,"object_pos_end":[0.49407,0.05887,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54568,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":536.0,"raw_peak_contact_force":0.55382,"subtask_id":"reach_above_peg","tcp_end":[0.46818,0.07367,0.15289],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12272,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":536.0,"n_steps_budget":600.0,"object_pos_end":[0.49414,0.05913,0.03391],"object_pos_start":[0.49407,0.05887,0.03385],"object_to_goal_dist_end":0.13939,"object_to_goal_dist_start":0.13914,"object_z_max":0.03391,"peak_contact_force":91.70132,"phase_name":"descend_to_push","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":418.0,"raw_peak_contact_force":91.70132,"subtask_id":"reach_push_start","tcp_end":[0.48672,0.05946,0.06569],"tcp_start":[0.46818,0.07367,0.15289],"tcp_to_object_dist_end":0.03263,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":361.0,"n_steps_budget":1000.0,"object_pos_end":[0.49371,0.01533,0.02423],"object_pos_start":[0.49414,0.05913,0.03391],"object_to_goal_dist_end":0.09683,"object_to_goal_dist_start":0.13939,"object_z_max":0.04081,"peak_contact_force":0.54924,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":373.0,"raw_peak_contact_force":4.20518,"subtask_id":"push_through_channel","tcp_end":[0.49143,-0.08818,0.04545],"tcp_start":[0.48672,0.05946,0.06569],"tcp_to_object_dist_end":0.10569,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```