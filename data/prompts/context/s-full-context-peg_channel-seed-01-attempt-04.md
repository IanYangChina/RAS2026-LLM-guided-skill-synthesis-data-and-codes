## Search State

- **Seed**: 1
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1990 | 0.00 | ❌ rejected |
| 3 | approach → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 2 | 0.0689 | 0.08 | ❌ rejected |
| 2 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1153 | 0.34 | ❌ rejected |
| 1 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1706 | 0.42 | ✅ accepted |
| 0 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1472 | 0.30 | ✅ accepted |

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

## Current Skill (Q=-0.199) — your mutation base

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

- **Composite score**: -0.199
- **task_score** (E): 0.000
- **fitness_score**: 0.111  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_behind | 1.00 | 1.00 | 0.1990 |
| descend_to_contact | 1.00 | 1.00 | 0.0504 |
| push_along_channel | 0.00 | 1.00 | 0.0001 |
| retract_up | 1.00 | 1.00 | 0.0636 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.482, 0.105, 0.128) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.547 | 2.857 |
| descend_to_contact | descend | 1.00 / step_budget | (0.482, 0.105, 0.128)→(0.494, 0.096, 0.081) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.667 | 75.540 | 124.732 |
| push_along_channel | push | 0.00 / guard_failure | (0.494, 0.096, 0.081)→(0.493, 0.096, 0.081) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.353 | 87.051 |
| retract_up | retract | 1.00 / step_budget | (0.493, 0.096, 0.081)→(0.494, 0.098, 0.144) | (0.497, 0.079, 0.034)→(0.497, 0.079, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.565 | 49.371 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.962
- terminal_score: 0.000
- phase_score: 0.212
- phase_breakdown.push_channel_score: 0.000
- phase_breakdown.reach_contact_score: 0.707

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.127
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: -0.195
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.3
- **Final σ (mean)**: 0.285


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8254,"average_solve_count":63.0,"average_success_count":63.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_behind.approach_speed":0.30088,"descend_to_contact.descend_speed":0.14864,"push_along_channel.push_distance":0.17588,"push_along_channel.push_speed":0.13844,"retract_up.retract_speed":0.14813},"optimized_scores":{"best_composite_score":-0.18274,"best_fitness_score":0.12726,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":466.0,"contact_point_centroid":[0.50086,0.116,0.00936],"force_p95":0.62343,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56178,"phase_index":0.0,"phase_name":"approach_to_behind","phase_type":"approach","tcp_position_centroid":[0.49403,0.17624,0.20456]},{"body_a":"peg","body_b":"channel_base_body","contact_count":506.0,"contact_point_centroid":[0.50086,0.11592,0.00941],"force_p95":0.60645,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65081,"mean_force":0.54361,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49663,0.13022,0.11226]},{"body_a":"peg","body_b":"channel_base_body","contact_count":155.0,"contact_point_centroid":[0.5009,0.11612,0.00944],"force_p95":0.59702,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62856,"mean_force":0.54122,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.49746,0.13366,0.10619]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.51789,0.11601,0.0094],"force_p95":0.54679,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54975,"mean_force":0.52822,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49751,0.12781,0.08289]}],"total_contact_groups":4},"final_pose_error":0.01065,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50094,0.11607,0.03393],"final_tcp_position":[0.49826,0.13399,0.14371],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":1.92055,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":482.0,"n_steps_budget":600.0,"object_pos_end":[0.50094,0.11605,0.03385],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19614,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.5458,"phase_name":"approach_to_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":466.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_contact","tcp_end":[0.49846,0.13945,0.12877],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09779,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":155.0,"n_steps_budget":600.0,"object_pos_end":[0.50099,0.11606,0.03382],"object_pos_start":[0.50094,0.11605,0.03385],"object_to_goal_dist_end":0.19616,"object_to_goal_dist_start":0.19614,"object_z_max":0.03403,"peak_contact_force":0.58902,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":155.0,"raw_peak_contact_force":0.62856,"subtask_id":"reach_contact","tcp_end":[0.49759,0.12791,0.08308],"tcp_start":[0.49846,0.13945,0.12877],"tcp_to_object_dist_end":0.05078,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":900.0,"object_pos_end":[0.50098,0.11604,0.03382],"object_pos_start":[0.50099,0.11606,0.03382],"object_to_goal_dist_end":0.19614,"object_to_goal_dist_start":0.19616,"object_z_max":0.03382,"peak_contact_force":0.51474,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":0.54975,"subtask_id":"push_channel","tcp_end":[0.49735,0.12762,0.08257],"tcp_start":[0.49743,0.12771,0.08272],"tcp_to_object_dist_end":0.05023,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":506.0,"n_steps_budget":600.0,"object_pos_end":[0.50094,0.11607,0.03393],"object_pos_start":[0.50093,0.11601,0.03382],"object_to_goal_dist_end":0.19617,"object_to_goal_dist_start":0.19611,"object_z_max":0.03397,"peak_contact_force":0.60741,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":506.0,"raw_peak_contact_force":0.65081,"tcp_end":[0.49826,0.13399,0.14371],"tcp_start":[0.49735,0.12762,0.08257],"tcp_to_object_dist_end":0.11126,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9697,"average_solve_count":66.0,"average_success_count":66.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_behind.approach_speed":0.1973,"descend_to_contact.descend_speed":0.10705,"push_along_channel.push_distance":0.08703,"push_along_channel.push_speed":0.18803,"retract_up.retract_speed":0.14465},"optimized_scores":{"best_composite_score":-0.19479,"best_fitness_score":0.11521,"best_task_score":0.00082},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":38.0,"contact_point_centroid":[0.47329,0.11993,0.05956],"force_p95":164.61833,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":168.0667,"mean_force":124.40747,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48923,0.07957,0.08575]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47104,0.12,0.0573],"force_p95":164.72928,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":164.72928,"mean_force":164.72928,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4914,0.08,0.08101]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.47143,0.11999,0.05885],"force_p95":44.709,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.41669,"mean_force":24.53211,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49029,0.08004,0.08325]},{"body_a":"peg","body_b":"channel_base_body","contact_count":520.0,"contact_point_centroid":[0.49554,0.06393,0.00937],"force_p95":0.58645,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.5619,"phase_index":0.0,"phase_name":"approach_to_behind","phase_type":"approach","tcp_position_centroid":[0.48459,0.14819,0.1999]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_to_behind","phase_type":"approach","tcp_position_centroid":[0.50365,0.21506,0.29251]},{"body_a":"peg","body_b":"channel_base_body","contact_count":504.0,"contact_point_centroid":[0.49508,0.0637,0.0094],"force_p95":0.55068,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55315,"mean_force":0.54523,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49066,0.08074,0.11191]},{"body_a":"peg","body_b":"channel_base_body","contact_count":197.0,"contact_point_centroid":[0.49482,0.0641,0.0094],"force_p95":0.55073,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5516,"mean_force":0.54557,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48438,0.08327,0.10248]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.47912,0.0565,0.0094],"force_p95":0.5509,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55124,"mean_force":0.5476,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49143,0.08006,0.08093]}],"total_contact_groups":8},"final_pose_error":0.01026,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4953,0.06367,0.03402],"final_tcp_position":[0.49227,0.08224,0.14418],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":168.0667,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":547.0,"n_steps_budget":690.0,"object_pos_end":[0.495,0.06405,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14427,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54603,"phase_name":"approach_to_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":548.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_contact","tcp_end":[0.47985,0.09034,0.12753],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":197.0,"n_steps_budget":600.0,"object_pos_end":[0.49485,0.06384,0.03398],"object_pos_start":[0.495,0.06405,0.03394],"object_to_goal_dist_end":0.14406,"object_to_goal_dist_start":0.14427,"object_z_max":0.03398,"peak_contact_force":98.33301,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":235.0,"raw_peak_contact_force":168.0667,"subtask_id":"reach_contact","tcp_end":[0.4914,0.08,0.08101],"tcp_start":[0.47985,0.09034,0.12753],"tcp_to_object_dist_end":0.04985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.49487,0.06377,0.03398],"object_pos_start":[0.49485,0.06384,0.03398],"object_to_goal_dist_end":0.14399,"object_to_goal_dist_start":0.14406,"object_z_max":0.03398,"peak_contact_force":0.54363,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":164.72928,"subtask_id":"push_channel","tcp_end":[0.49141,0.0801,0.08081],"tcp_start":[0.49144,0.08009,0.08087],"tcp_to_object_dist_end":0.04972,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":504.0,"n_steps_budget":600.0,"object_pos_end":[0.4953,0.06367,0.03402],"object_pos_start":[0.49495,0.06367,0.03398],"object_to_goal_dist_end":0.14387,"object_to_goal_dist_start":0.14388,"object_z_max":0.03402,"peak_contact_force":0.54604,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":521.0,"raw_peak_contact_force":76.41669,"tcp_end":[0.49227,0.08224,0.14418],"tcp_start":[0.49141,0.0801,0.08081],"tcp_to_object_dist_end":0.11176,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4466,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_behind.approach_speed":0.16803,"descend_to_contact.descend_speed":0.23486,"push_along_channel.push_distance":0.02009,"push_along_channel.push_speed":0.10259,"retract_up.retract_speed":0.02962},"optimized_scores":{"best_composite_score":-0.21948,"best_fitness_score":0.09052,"best_task_score":0.00049},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":137.0,"contact_point_centroid":[0.47238,0.11996,0.05998],"force_p95":184.83287,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":205.50007,"mean_force":144.88547,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48629,0.07907,0.08715]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.46775,0.11997,0.06],"force_p95":94.28864,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":95.87509,"mean_force":81.29838,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49171,0.08001,0.07858]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":52.0,"contact_point_centroid":[0.46934,0.11999,0.06],"force_p95":50.23437,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.04402,"mean_force":28.90661,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48987,0.08005,0.08239]},{"body_a":"peg","body_b":"channel_base_body","contact_count":566.0,"contact_point_centroid":[0.49437,0.05905,0.00935],"force_p95":0.5666,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57206,"phase_index":0.0,"phase_name":"approach_to_behind","phase_type":"approach","tcp_position_centroid":[0.47866,0.14631,0.20221]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_to_behind","phase_type":"approach","tcp_position_centroid":[0.50216,0.22042,0.28708]},{"body_a":"peg","body_b":"channel_base_body","contact_count":687.0,"contact_point_centroid":[0.49411,0.05897,0.0094],"force_p95":0.55052,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55392,"mean_force":0.54554,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49027,0.0785,0.11033]},{"body_a":"peg","body_b":"channel_base_body","contact_count":295.0,"contact_point_centroid":[0.4941,0.05897,0.00939],"force_p95":0.55019,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54604,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.4797,0.07977,0.0981]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.47955,0.04942,0.00939],"force_p95":0.54887,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5493,"mean_force":0.54556,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49171,0.08001,0.07858]}],"total_contact_groups":8},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49399,0.05871,0.03402],"final_tcp_position":[0.49144,0.07771,0.14433],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":205.50007,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":595.0,"n_steps_budget":840.0,"object_pos_end":[0.49399,0.05894,0.03387],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.1392,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54846,"phase_name":"approach_to_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":601.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_contact","tcp_end":[0.4667,0.08549,0.12728],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10087,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":295.0,"n_steps_budget":600.0,"object_pos_end":[0.49396,0.05892,0.03391],"object_pos_start":[0.49399,0.05894,0.03387],"object_to_goal_dist_end":0.13918,"object_to_goal_dist_start":0.1392,"object_z_max":0.03391,"peak_contact_force":127.69755,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":432.0,"raw_peak_contact_force":205.50007,"subtask_id":"reach_contact","tcp_end":[0.49168,0.07998,0.07863],"tcp_start":[0.4667,0.08549,0.12728],"tcp_to_object_dist_end":0.04949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.49398,0.05886,0.03391],"object_pos_start":[0.49396,0.05892,0.03391],"object_to_goal_dist_end":0.13913,"object_to_goal_dist_start":0.13918,"object_z_max":0.03391,"peak_contact_force":0.0,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":95.87509,"subtask_id":"push_channel","tcp_end":[0.49174,0.0801,0.07848],"tcp_start":[0.49173,0.08005,0.07853],"tcp_to_object_dist_end":0.04942,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":687.0,"n_steps_budget":1000.0,"object_pos_end":[0.49399,0.05871,0.03402],"object_pos_start":[0.49407,0.0588,0.03391],"object_to_goal_dist_end":0.13897,"object_to_goal_dist_start":0.13906,"object_z_max":0.03402,"peak_contact_force":0.54087,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":739.0,"raw_peak_contact_force":71.04402,"tcp_end":[0.49144,0.07771,0.14433],"tcp_start":[0.49174,0.0801,0.07848],"tcp_to_object_dist_end":0.11197,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```