## Search State

- **Seed**: 1
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1659 | 0.40 | ❌ rejected |
| 6 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 3 | 0.2378 | 0.24 | ❌ rejected |
| 5 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1208 | 0.32 | ❌ rejected |
| 4 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1680 | 0.40 | ✅ accepted |
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 3 | 0.2813 | 0.03 | ❌ rejected |

**Proposal policy**: task_score is 0.40 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.166) — your mutation base

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

- **Composite score**: 0.166
- **task_score** (E): 0.395
- **fitness_score**: 0.376  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| rotate_1 | 1.00 | 0.1730 |
| align_1 | 1.00 | 0.1462 |
| push_1 | 0.33 | 0.1269 |
| align_2 | 1.00 | 0.0069 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| rotate_1 | rotate | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.497, 0.075, 0.180) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.075, 0.180)→(0.494, 0.118, 0.043) | (0.497, 0.080, 0.034)→(0.497, 0.084, 0.033) | 0.160→0.164 |
| push_1 | push | 0.33 / step_budget | (0.494, 0.118, 0.043)→(0.497, -0.009, 0.040) | (0.497, 0.084, 0.033)→(0.504, -0.020, 0.025) | 0.164→0.071 |
| align_2 | align | 1.00 / step_budget | (0.497, -0.009, 0.040)→(0.500, -0.004, 0.039) | (0.504, -0.020, 0.025)→(0.496, -0.021, 0.028) | 0.071→0.065 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.812
- alignment_error: None
- terminal_score: 0.602
- phase_score: 0.466
- phase_breakdown.push_score: 0.766
- phase_breakdown.approach_score: 0.035

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.520
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.602
- **Median Q (composite search score)**: 0.219
- **K-run variance**: 0.0209
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.714


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29464,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00583,"align_2.lateral_offset_x":0.00273,"push_1.push_distance":0.02082},"optimized_scores":{"best_composite_score":-0.0317,"best_fitness_score":0.1783,"best_task_score":0.29366},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52502,0.12,0.05999],"force_p95":199.04195,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":205.44009,"mean_force":67.11936,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50778,0.1218,0.04941]},{"body_a":"peg","body_b":"channel_base_body","contact_count":456.0,"contact_point_centroid":[0.50776,0.11559,0.0074],"force_p95":194.30677,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":195.89105,"mean_force":131.05822,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50318,0.14272,0.04694]},{"body_a":"attachment","body_b":"peg","contact_count":431.0,"contact_point_centroid":[0.50968,0.13588,0.04673],"force_p95":193.8333,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":195.46711,"mean_force":142.89205,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50309,0.14411,0.047]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.50657,0.13982,0.05102],"force_p95":119.53343,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.43451,"mean_force":83.80714,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49846,0.14657,0.05326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":563.0,"contact_point_centroid":[0.50214,0.1166,0.00925],"force_p95":94.17839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.99062,"mean_force":15.43742,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49609,0.11288,0.10781]},{"body_a":"peg","body_b":"world","contact_count":174.0,"contact_point_centroid":[0.50196,0.12509,-0.00017],"force_p95":19.83953,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.74864,"mean_force":14.07926,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50038,0.15464,0.04467]},{"body_a":"peg","body_b":"world","contact_count":28.0,"contact_point_centroid":[0.50222,0.12719,-0.0003],"force_p95":37.33342,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.90411,"mean_force":28.00895,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49992,0.15488,0.04587]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47456,0.08747,0.05662],"force_p95":2.82842,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.03518,"mean_force":1.48577,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50648,0.12023,0.04793]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50098,0.11602,0.0094],"force_p95":0.60736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55146,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49749,0.13563,0.23636]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52517,0.05179,0.04927],"force_p95":1.4955,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.50973,"mean_force":1.37526,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50091,0.11578,0.04121]},{"body_a":"peg","body_b":"channel_base_body","contact_count":12.0,"contact_point_centroid":[0.49994,0.08203,0.00994],"force_p95":0.95119,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.01016,"mean_force":0.55977,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50152,0.11565,0.04183]}],"total_contact_groups":11},"final_pose_error":0.00508,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50323,0.06905,0.03778],"final_tcp_position":[0.50069,0.11587,0.04101],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11601,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15182,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.50228,0.12805,0.02979],"object_pos_start":[0.50092,0.11601,0.03383],"object_to_goal_dist_end":0.20832,"object_to_goal_dist_start":0.19611,"object_z_max":0.0342,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.50029,0.1577,0.04359],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03276,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":456.0,"n_steps_budget":600.0,"object_pos_end":[0.4986,0.08049,0.04082],"object_pos_start":[0.50228,0.12805,0.02979],"object_to_goal_dist_end":0.1605,"object_to_goal_dist_start":0.20832,"object_z_max":0.04077,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.50266,0.1162,0.04324],"tcp_start":[0.50029,0.1577,0.04359],"tcp_to_object_dist_end":0.03602,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50323,0.06905,0.03778],"object_pos_start":[0.4986,0.08049,0.04082],"object_to_goal_dist_end":0.1491,"object_to_goal_dist_start":0.1605,"object_z_max":0.04084,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.50069,0.11587,0.04101],"tcp_start":[0.50266,0.1162,0.04324],"tcp_to_object_dist_end":0.047,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75397,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00796,"align_2.lateral_offset_x":0.00601,"push_1.push_distance":0.19876},"optimized_scores":{"best_composite_score":0.31048,"best_fitness_score":0.52048,"best_task_score":0.60152},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":328.0,"contact_point_centroid":[0.52506,-0.06285,0.05997],"force_p95":264.04135,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":340.19558,"mean_force":214.48745,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50054,-0.06265,0.03728]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":377.0,"contact_point_centroid":[0.54524,-0.05947,0.05994],"force_p95":298.73748,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":323.57976,"mean_force":233.05971,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50024,-0.06294,0.03719]},{"body_a":"channel_base_body","body_b":"link7","contact_count":37.0,"contact_point_centroid":[0.53868,-0.10001,0.06496],"force_p95":211.62611,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":225.12047,"mean_force":106.25265,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49603,-0.06645,0.03706]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":300.0,"contact_point_centroid":[0.5345,-0.00795,0.05999],"force_p95":165.19235,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":222.50268,"mean_force":101.57168,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48914,-0.00333,0.03819]},{"body_a":"attachment","body_b":"peg","contact_count":913.0,"contact_point_centroid":[0.49789,0.00678,0.03581],"force_p95":117.70598,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":136.66725,"mean_force":70.00002,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48937,0.01195,0.03808]},{"body_a":"peg","body_b":"channel_base_body","contact_count":453.0,"contact_point_centroid":[0.49661,-0.06374,0.0063],"force_p95":122.66538,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":133.17519,"mean_force":64.81916,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49977,-0.0634,0.03716]},{"body_a":"attachment","body_b":"peg","contact_count":450.0,"contact_point_centroid":[0.50274,-0.06545,0.03656],"force_p95":122.17742,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":132.82156,"mean_force":67.57031,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49977,-0.0634,0.03717]},{"body_a":"peg","body_b":"channel_base_body","contact_count":975.0,"contact_point_centroid":[0.50836,-0.00525,0.009],"force_p95":91.50122,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":128.06199,"mean_force":43.23885,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48936,0.01664,0.03818]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":859.0,"contact_point_centroid":[0.52615,-0.00493,0.02702],"force_p95":97.54178,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":112.13373,"mean_force":56.44719,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48944,0.00738,0.03806]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":30.0,"contact_point_centroid":[0.52502,-0.07346,0.01603],"force_p95":35.24681,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.70501,"mean_force":28.23548,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49525,-0.0673,0.03739]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":286.0,"contact_point_centroid":[0.4745,-0.08273,0.02306],"force_p95":36.81626,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.21918,"mean_force":27.65618,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50047,-0.06259,0.0374]},{"body_a":"peg","body_b":"link7","contact_count":365.0,"contact_point_centroid":[0.5202,0.01244,0.06766],"force_p95":24.68807,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.77871,"mean_force":12.68315,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48922,0.03707,0.03792]},{"body_a":"peg","body_b":"world","contact_count":81.0,"contact_point_centroid":[0.50894,-0.0634,-0.00072],"force_p95":12.06858,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.51119,"mean_force":1.20179,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49219,-0.05943,0.03791]},{"body_a":"peg","body_b":"world","contact_count":122.0,"contact_point_centroid":[0.5055,-0.06341,-0.00129],"force_p95":8.53784,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.79859,"mean_force":1.67088,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49766,-0.06542,0.03687]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.49527,0.06395,0.00938],"force_p95":0.55699,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55424,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49748,0.13493,0.23568]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49942,0.19831,0.29814]}],"total_contact_groups":17},"final_pose_error":0.04065,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49192,-0.06597,0.02363],"final_tcp_position":[0.50019,-0.06214,0.03842],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06382,0.03401],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14649,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":447.0,"n_steps_budget":930.0,"object_pos_end":[0.49519,0.06359,0.03403],"object_pos_start":[0.49482,0.06382,0.03401],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14404,"object_z_max":0.03403,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.4911,0.10042,0.04259],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03803,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50718,-0.06844,0.0168],"object_pos_start":[0.49519,0.06359,0.03403],"object_to_goal_dist_end":0.0269,"object_to_goal_dist_start":0.14379,"object_z_max":0.03979,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49423,-0.0681,0.03819],"tcp_start":[0.4911,0.10042,0.04259],"tcp_to_object_dist_end":0.02501,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":453.0,"n_steps_budget":600.0,"object_pos_end":[0.49192,-0.06597,0.02363],"object_pos_start":[0.50718,-0.06844,0.0168],"object_to_goal_dist_end":0.02302,"object_to_goal_dist_start":0.0269,"object_z_max":0.0237,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.50019,-0.06214,0.03842],"tcp_start":[0.49423,-0.0681,0.03819],"tcp_to_object_dist_end":0.01737,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75397,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00099,"align_2.lateral_offset_x":-0.00367,"push_1.push_distance":0.19665},"optimized_scores":{"best_composite_score":0.21907,"best_fitness_score":0.42907,"best_task_score":0.29124},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":434.0,"contact_point_centroid":[0.54307,-0.10001,0.06495],"force_p95":283.30126,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":295.32651,"mean_force":219.93329,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50035,-0.06786,0.03725]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":349.0,"contact_point_centroid":[0.52505,-0.06747,0.05998],"force_p95":245.85587,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":288.33732,"mean_force":200.29834,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50073,-0.06732,0.03723]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":339.0,"contact_point_centroid":[0.53416,-0.00893,0.05999],"force_p95":168.13078,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":219.74619,"mean_force":101.69542,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48879,-0.00432,0.03822]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":75.0,"contact_point_centroid":[0.54576,-0.06353,0.05999],"force_p95":124.77692,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":154.37708,"mean_force":91.60346,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.5004,-0.06684,0.03798]},{"body_a":"peg","body_b":"channel_base_body","contact_count":458.0,"contact_point_centroid":[0.49448,-0.07071,0.00632],"force_p95":77.82694,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":148.17552,"mean_force":36.84796,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50017,-0.06811,0.03729]},{"body_a":"attachment","body_b":"peg","contact_count":420.0,"contact_point_centroid":[0.50104,-0.07213,0.0372],"force_p95":75.05845,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":142.14023,"mean_force":37.53562,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50012,-0.06816,0.0373]},{"body_a":"attachment","body_b":"peg","contact_count":881.0,"contact_point_centroid":[0.49767,-0.00081,0.03499],"force_p95":117.23296,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":134.38772,"mean_force":71.47198,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4892,0.00373,0.03813]},{"body_a":"peg","body_b":"channel_base_body","contact_count":969.0,"contact_point_centroid":[0.50766,-0.00938,0.00894],"force_p95":95.20114,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":118.45976,"mean_force":40.81241,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48912,0.01062,0.03822]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":839.0,"contact_point_centroid":[0.52617,-0.01102,0.02401],"force_p95":97.1418,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.96668,"mean_force":57.58735,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48926,8e-05,0.03811]},{"body_a":"channel_base_body","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.53637,-0.1,0.065],"force_p95":91.25932,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.15372,"mean_force":53.80535,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49353,-0.07012,0.03802]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.52503,-0.04607,0.01677],"force_p95":43.15136,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.58079,"mean_force":28.70483,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49588,-0.07374,0.03826]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":348.0,"contact_point_centroid":[0.47412,-0.07273,0.02227],"force_p95":42.81886,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.7851,"mean_force":25.93166,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50073,-0.06732,0.03723]},{"body_a":"peg","body_b":"world","contact_count":89.0,"contact_point_centroid":[0.50865,-0.06834,-0.00064],"force_p95":5.12802,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.50934,"mean_force":1.05264,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49261,-0.06559,0.03791]},{"body_a":"peg","body_b":"link7","contact_count":194.0,"contact_point_centroid":[0.51689,0.01007,0.06913],"force_p95":8.99658,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.50485,"mean_force":6.69783,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48886,0.03688,0.03796]},{"body_a":"peg","body_b":"world","contact_count":99.0,"contact_point_centroid":[0.50552,-0.07105,-0.00102],"force_p95":4.59773,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.49056,"mean_force":0.80444,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49811,-0.0709,0.03755]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.49432,0.05896,0.00937],"force_p95":0.55417,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56118,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49747,0.13481,0.23556]}],"total_contact_groups":18},"final_pose_error":0.04184,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49169,-0.06667,0.02322],"final_tcp_position":[0.50032,-0.06676,0.03823],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49409,0.05914,0.03393],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.1394,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14702,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":443.0,"n_steps_budget":930.0,"object_pos_end":[0.49439,0.05889,0.034],"object_pos_start":[0.49409,0.05914,0.03393],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.1394,"object_z_max":0.034,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.49044,0.0962,0.04256],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03848,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50687,-0.07107,0.0174],"object_pos_start":[0.49439,0.05889,0.034],"object_to_goal_dist_end":0.02525,"object_to_goal_dist_start":0.13914,"object_z_max":0.04018,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.495,-0.07428,0.03864],"tcp_start":[0.49044,0.0962,0.04256],"tcp_to_object_dist_end":0.02454,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":458.0,"n_steps_budget":600.0,"object_pos_end":[0.49169,-0.06667,0.02322],"object_pos_start":[0.50687,-0.07107,0.0174],"object_to_goal_dist_end":0.02298,"object_to_goal_dist_start":0.02525,"object_z_max":0.02354,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.50032,-0.06676,0.03823],"tcp_start":[0.495,-0.07428,0.03864],"tcp_to_object_dist_end":0.01731,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```