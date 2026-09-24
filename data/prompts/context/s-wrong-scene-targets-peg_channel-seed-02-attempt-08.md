## Search State

- **Seed**: 2
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.0814 | 0.13 | ❌ rejected |
| 7 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.1029 | 0.13 | ❌ rejected |
| 6 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.1029 | 0.13 | ❌ rejected |
| 5 | align → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | -0.0688 | 0.00 | ❌ rejected |
| 4 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.1029 | 0.13 | ❌ rejected |

**Proposal policy**: task_score is 0.13 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`
- Frozen object start: [0.48092897073994534, -0.09612070852687013, 0.04]
- Frozen task target: [0.5, 0.2, 0.3]
- Goal object position: (0.5, 0.2, 0.3)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48092897073994534, -0.09612070852687013, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.48092897073994534, 0.06387929147312987, 0.04)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.48092897073994534, 0.06387929147312987, 0.04]
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
  frozen_object_start: [0.4809, 0.0639, 0.04]
  frozen_task_target: [0.4809, -0.0961, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48092897073994534, -0.09612070852687013, 0.04]}
  frozen_targets: {'channel_exit': [0.5, 0.2, 0.3]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7

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
| `object` | offset from object initial position (0.48092897073994534, -0.09612070852687013, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.2, 0.3) | final destination targets |
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

## Current Skill (Q=0.081) — your mutation base

```yaml
skill: peg_channel
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: align_2
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: pull_1
  type: pull
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: 0.081
- **task_score** (E): 0.125
- **fitness_score**: 0.341  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2022 |
| align_orientation | 0.00 | 1.00 | 0.0234 |
| contact_peg | 1.00 | 1.00 | 0.0606 |
| push_through_channel | 0.00 | 1.00 | 0.1603 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.492, 0.076, 0.143) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.548 | 3.659 |
| align_orientation | align | 0.00 / step_budget | (0.492, 0.076, 0.143)→(0.493, 0.075, 0.120) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.548 | 0.551 |
| contact_peg | contact | 1.00 / force_exceeded | (0.493, 0.075, 0.120)→(0.493, 0.070, 0.061) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.000 | 19.292 | 19.292 |
| push_through_channel | push | 0.00 / step_budget | (0.493, 0.070, 0.061)→(0.508, -0.087, 0.036) | (0.498, 0.068, 0.034)→(0.500, 0.016, 0.024) | 0.148→0.098 | 1.00 / 2.667 | 114.189 | 766.457 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.347
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.188
- phase_score: 0.511
- phase_breakdown.push_through_score: 0.377
- phase_breakdown.reach_peg_score: 0.824

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.382
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.188
- **Median Q (composite search score)**: 0.076
- **K-run variance**: 0.0010
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.290


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6269840a353345700ffa70ea476a3ad730b138bf2ec3c52304c054f0e194e023`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a2936262b79fcd5a49fda15d77b54223f43c58bfee2e71dc505f8a2f79369706`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,-0.09612,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,-0.09612,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.00877,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_orientation.fine_orientation_tol":0.06872,"align_orientation.lateral_offset":0.00408,"approach_peg.approach_height":0.08946,"approach_peg.approach_speed":0.27159,"contact_peg.contact_speed":0.05294,"contact_peg.probe_force":12.7476,"push_through_channel.pose_tolerance_push":0.03325,"push_through_channel.push_distance":0.12195,"push_through_channel.push_speed":0.11479},"optimized_scores":{"best_composite_score":0.122,"best_fitness_score":0.382,"best_task_score":0.18802},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":415.0,"contact_point_centroid":[0.50724,-0.10028,0.065],"force_p95":580.17708,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":926.29025,"mean_force":271.46231,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50213,-0.08834,0.03927]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":130.0,"contact_point_centroid":[0.52509,-0.08826,0.05998],"force_p95":836.75117,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":909.39257,"mean_force":299.42944,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50824,-0.08803,0.03668]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47495,0.07109,0.05979],"force_p95":381.77003,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":400.8739,"mean_force":264.71297,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48662,0.07192,0.05756]},{"body_a":"peg","body_b":"channel_base_body","contact_count":686.0,"contact_point_centroid":[0.49671,0.01712,0.00822],"force_p95":150.34075,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":227.33637,"mean_force":23.73067,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49773,-0.05361,0.04462]},{"body_a":"attachment","body_b":"peg","contact_count":143.0,"contact_point_centroid":[0.49913,0.04718,0.05637],"force_p95":175.76293,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":226.99859,"mean_force":111.0343,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48998,0.04322,0.05666]},{"body_a":"peg","body_b":"channel_base_body","contact_count":397.0,"contact_point_centroid":[0.49507,0.06361,0.0094],"force_p95":0.55065,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.98879,"mean_force":0.60702,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48158,0.06965,0.08623]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49794,0.06578,0.05897],"force_p95":24.51618,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.51618,"mean_force":24.51618,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.4862,0.06711,0.06104]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47499,0.02127,0.0593],"force_p95":14.03546,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.04394,"mean_force":11.56945,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4921,0.00567,0.05584]},{"body_a":"peg","body_b":"channel_base_body","contact_count":522.0,"contact_point_centroid":[0.4955,0.06398,0.00937],"force_p95":0.58586,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56184,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48863,0.1341,0.21392]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49923,0.19768,0.29692]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.49554,0.06361,0.00939],"force_p95":0.55036,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55088,"mean_force":0.54557,"phase_index":1.0,"phase_name":"align_orientation","phase_type":"align","tcp_position_centroid":[0.47934,0.07444,0.12993]}],"total_contact_groups":11},"final_pose_error":0.11477,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49818,0.00837,0.02412],"final_tcp_position":[0.50787,-0.08751,0.03638],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":926.29025,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":549.0,"n_steps_budget":600.0,"object_pos_end":[0.49491,0.06396,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14418,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54492,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":550.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_peg","tcp_end":[0.47929,0.07234,0.13624],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.49492,0.06399,0.03394],"object_pos_start":[0.49491,0.06396,0.03394],"object_to_goal_dist_end":0.14421,"object_to_goal_dist_start":0.14418,"object_z_max":0.03394,"peak_contact_force":0.54743,"phase_name":"align_orientation","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":20.0,"raw_peak_contact_force":0.55088,"subtask_id":"reach_peg","tcp_end":[0.48101,0.07354,0.11944],"tcp_start":[0.47929,0.07234,0.13624],"tcp_to_object_dist_end":0.08715,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":397.0,"n_steps_budget":1000.0,"object_pos_end":[0.49533,0.06402,0.03401],"object_pos_start":[0.49492,0.06399,0.03394],"object_to_goal_dist_end":0.14422,"object_to_goal_dist_start":0.14421,"object_z_max":0.03401,"peak_contact_force":24.98879,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":398.0,"raw_peak_contact_force":24.98879,"tcp_end":[0.48623,0.06709,0.06091],"tcp_start":[0.48101,0.07354,0.11944],"tcp_to_object_dist_end":0.02857,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":695.0,"n_steps_budget":1000.0,"object_pos_end":[0.49818,0.00837,0.02412],"object_pos_start":[0.49533,0.06402,0.03401],"object_to_goal_dist_end":0.08981,"object_to_goal_dist_start":0.14422,"object_z_max":0.03994,"peak_contact_force":0.95079,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1383.0,"raw_peak_contact_force":926.29025,"subtask_id":"push_through","tcp_end":[0.50787,-0.08751,0.03638],"tcp_start":[0.48623,0.06709,0.06091],"tcp_to_object_dist_end":0.09715,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,-0.10106,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,-0.10106,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_orientation.fine_orientation_tol":0.05595,"align_orientation.lateral_offset":-0.00653,"approach_peg.approach_height":0.10309,"approach_peg.approach_speed":0.28491,"contact_peg.contact_speed":0.04968,"contact_peg.probe_force":12.84251,"push_through_channel.pose_tolerance_push":0.02767,"push_through_channel.push_distance":0.1695,"push_through_channel.push_speed":0.11774},"optimized_scores":{"best_composite_score":0.07614,"best_fitness_score":0.33614,"best_task_score":0.09374},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":43.0,"contact_point_centroid":[0.47497,0.02918,0.05851],"force_p95":493.08531,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":500.56153,"mean_force":284.68164,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48378,0.03508,0.0572]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":670.0,"contact_point_centroid":[0.50575,-0.10022,0.065],"force_p95":298.8251,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":331.04027,"mean_force":229.54065,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50202,-0.08784,0.03899]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":238.0,"contact_point_centroid":[0.52504,-0.08797,0.05999],"force_p95":281.66695,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":308.23614,"mean_force":170.81733,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5092,-0.08711,0.03508]},{"body_a":"peg","body_b":"channel_base_body","contact_count":991.0,"contact_point_centroid":[0.49545,0.01656,0.00828],"force_p95":93.67404,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":198.43241,"mean_force":11.31429,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49703,-0.06103,0.04391]},{"body_a":"attachment","body_b":"peg","contact_count":142.0,"contact_point_centroid":[0.49324,0.04891,0.05804],"force_p95":145.7222,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":197.5467,"mean_force":75.74614,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48419,0.04398,0.05873]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":42.0,"contact_point_centroid":[0.47491,0.03825,0.05991],"force_p95":27.88558,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.93461,"mean_force":23.38472,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48659,0.02363,0.05845]},{"body_a":"peg","body_b":"channel_base_body","contact_count":468.0,"contact_point_centroid":[0.49405,0.05892,0.00939],"force_p95":0.55024,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.02803,"mean_force":0.59965,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.47549,0.06153,0.086]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.49412,0.06105,0.05888],"force_p95":13.42593,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.51818,"mean_force":12.59567,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48234,0.06023,0.06096]},{"body_a":"peg","body_b":"channel_base_body","contact_count":519.0,"contact_point_centroid":[0.49435,0.05904,0.00935],"force_p95":0.57019,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.5744,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48186,0.13139,0.22013]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49873,0.19675,0.29592]},{"body_a":"peg","body_b":"channel_base_body","contact_count":32.0,"contact_point_centroid":[0.49418,0.05897,0.00939],"force_p95":0.54968,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55099,"mean_force":0.54625,"phase_index":1.0,"phase_name":"align_orientation","phase_type":"align","tcp_position_centroid":[0.46851,0.06662,0.13645]}],"total_contact_groups":11},"final_pose_error":0.16376,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49565,0.00966,0.02413],"final_tcp_position":[0.50872,-0.0861,0.03357],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":500.56153,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":548.0,"n_steps_budget":600.0,"object_pos_end":[0.49403,0.05888,0.03387],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.5504,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":554.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_peg","tcp_end":[0.46627,0.06775,0.14914],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":32.0,"n_steps_budget":600.0,"object_pos_end":[0.49402,0.05888,0.03387],"object_pos_start":[0.49403,0.05888,0.03387],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.13914,"object_z_max":0.03387,"peak_contact_force":0.55099,"phase_name":"align_orientation","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":32.0,"raw_peak_contact_force":0.55099,"subtask_id":"reach_peg","tcp_end":[0.47261,0.06337,0.11716],"tcp_start":[0.46627,0.06775,0.14914],"tcp_to_object_dist_end":0.08611,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":468.0,"n_steps_budget":1000.0,"object_pos_end":[0.49403,0.05877,0.03394],"object_pos_start":[0.49402,0.05888,0.03387],"object_to_goal_dist_end":0.13903,"object_to_goal_dist_start":0.13914,"object_z_max":0.03393,"peak_contact_force":14.02803,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":470.0,"raw_peak_contact_force":14.02803,"tcp_end":[0.48239,0.06023,0.06084],"tcp_start":[0.47261,0.06337,0.11716],"tcp_to_object_dist_end":0.02935,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49565,0.00966,0.02413],"object_pos_start":[0.49403,0.05877,0.03394],"object_to_goal_dist_end":0.09115,"object_to_goal_dist_start":0.13903,"object_z_max":0.04061,"peak_contact_force":202.485,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2126.0,"raw_peak_contact_force":500.56153,"subtask_id":"push_through","tcp_end":[0.50872,-0.0861,0.03357],"tcp_start":[0.48239,0.06023,0.06084],"tcp_to_object_dist_end":0.0971,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,-0.07909,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,-0.07909,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.98462,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_orientation.fine_orientation_tol":0.07542,"align_orientation.lateral_offset":0.00866,"approach_peg.approach_height":0.09821,"approach_peg.approach_speed":0.21482,"contact_peg.contact_speed":0.05338,"contact_peg.probe_force":13.91087,"push_through_channel.pose_tolerance_push":0.05437,"push_through_channel.push_distance":0.13749,"push_through_channel.push_speed":0.10021},"optimized_scores":{"best_composite_score":0.04616,"best_fitness_score":0.30616,"best_task_score":0.09384},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":444.0,"contact_point_centroid":[0.51298,-0.10021,0.065],"force_p95":504.20297,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":872.51915,"mean_force":255.45067,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50727,-0.08803,0.04035]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":317.0,"contact_point_centroid":[0.52505,-0.07894,0.05999],"force_p95":575.64171,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":854.34523,"mean_force":207.74661,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50824,-0.07856,0.04041]},{"body_a":"attachment","body_b":"peg","contact_count":101.0,"contact_point_centroid":[0.51796,0.06706,0.05655],"force_p95":190.72065,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":238.554,"mean_force":122.10645,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51128,0.06074,0.05619]},{"body_a":"peg","body_b":"channel_base_body","contact_count":637.0,"contact_point_centroid":[0.50472,0.03681,0.00815],"force_p95":157.07918,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":222.32437,"mean_force":19.90637,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50776,-0.05817,0.04397]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":40.0,"contact_point_centroid":[0.5252,0.05105,0.04455],"force_p95":45.61771,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.6881,"mean_force":18.21217,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50982,0.0173,0.05064]},{"body_a":"peg","body_b":"channel_base_body","contact_count":231.0,"contact_point_centroid":[0.50584,0.08079,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.858,"mean_force":0.62604,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51453,0.08405,0.08448]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.52105,0.08164,0.05877],"force_p95":18.44157,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.44157,"mean_force":18.44157,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50931,0.08289,0.06088]},{"body_a":"peg","body_b":"channel_base_body","contact_count":516.0,"contact_point_centroid":[0.50566,0.0809,0.00936],"force_p95":0.55893,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57634,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5148,0.14172,0.21701]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50025,0.19703,0.29554]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47494,0.00842,0.03095],"force_p95":1.67893,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.73029,"mean_force":1.30013,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50812,-0.0064,0.05169]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.50752,0.08093,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55007,"mean_force":0.54663,"phase_index":1.0,"phase_name":"align_orientation","phase_type":"align","tcp_position_centroid":[0.52819,0.08981,0.13611]}],"total_contact_groups":11},"final_pose_error":0.13042,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5062,0.03044,0.02413],"final_tcp_position":[0.50722,-0.0873,0.03744],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":872.51915,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":545.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.55007,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":552.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.53001,0.08821,0.14359],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11265,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54611,"phase_name":"align_orientation","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":20.0,"raw_peak_contact_force":0.55007,"subtask_id":"reach_peg","tcp_end":[0.52582,0.08813,0.12372],"tcp_start":[0.53001,0.08821,0.14359],"tcp_to_object_dist_end":0.09239,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":231.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03377],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":18.858,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":232.0,"raw_peak_contact_force":18.858,"tcp_end":[0.50928,0.08287,0.06068],"tcp_start":[0.52582,0.08813,0.12372],"tcp_to_object_dist_end":0.02718,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":646.0,"n_steps_budget":1000.0,"object_pos_end":[0.5062,0.03044,0.02413],"object_pos_start":[0.50597,0.0809,0.03377],"object_to_goal_dist_end":0.11175,"object_to_goal_dist_start":0.16113,"object_z_max":0.03863,"peak_contact_force":139.13072,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1542.0,"raw_peak_contact_force":872.51915,"subtask_id":"push_through","tcp_end":[0.50722,-0.0873,0.03744],"tcp_start":[0.50928,0.08287,0.06068],"tcp_to_object_dist_end":0.11849,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```