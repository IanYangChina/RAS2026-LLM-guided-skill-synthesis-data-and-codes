## Search State

- **Seed**: 1
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → push | linear_cartesian | impedance_motion | position_control | impedance_control | pose_tolerance | time_limit | 6 | 0.1993 | 0.35 | ❌ rejected |
| 11 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1517 | 0.30 | ❌ rejected |
| 10 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0378 | 0.02 | ❌ rejected |
| 9 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 4 | 0.1220 | 0.00 | ❌ rejected |
| 8 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1661 | 0.41 | ✅ accepted |

**Proposal policy**: task_score is 0.35 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.199) — your mutation base

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

- **Composite score**: 0.199
- **task_score** (E): 0.350
- **fitness_score**: 0.499  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.2510 |
| push_1 | 1.00 | 0.1212 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.484, 0.113, 0.067) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 |
| push_1 | push | 1.00 / time_limit | (0.484, 0.113, 0.067)→(0.491, -0.005, 0.042) | (0.497, 0.080, 0.034)→(0.501, -0.001, 0.031) | 0.160→0.080 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.686
- alignment_error: None
- terminal_score: 0.686
- phase_score: 0.652
- phase_breakdown.reach_approach_score: 0.883
- phase_breakdown.push_to_goal_score: 0.553

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.666
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.686
- **Median Q (composite search score)**: 0.160
- **K-run variance**: 0.0151
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.230


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.07576,"average_solve_count":66.0,"average_success_count":66.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_lateral_x":0.00077,"approach_1.approach_speed":0.17247,"approach_1.approach_tolerance":0.00904,"push_1.push_distance":0.1928,"push_1.push_lateral_x":-0.00244,"push_1.push_speed":0.0636},"optimized_scores":{"best_composite_score":0.36552,"best_fitness_score":0.66552,"best_task_score":0.6859},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":988.0,"contact_point_centroid":[0.5018,0.06092,0.00867],"force_p95":62.89761,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.48902,"mean_force":24.1982,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49547,0.09557,0.05372]},{"body_a":"attachment","body_b":"peg","contact_count":577.0,"contact_point_centroid":[0.503,0.09816,0.05394],"force_p95":65.3714,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.06229,"mean_force":40.79834,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49608,0.10705,0.05627]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":55.0,"contact_point_centroid":[0.52506,-0.00304,0.02583],"force_p95":12.60153,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.26671,"mean_force":7.71003,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49444,0.05125,0.04541]},{"body_a":"peg","body_b":"channel_base_body","contact_count":843.0,"contact_point_centroid":[0.50093,0.11609,0.0094],"force_p95":0.61973,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55231,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49808,0.17336,0.18141]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47497,0.03882,0.06],"force_p95":0.62691,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63312,"mean_force":0.57102,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49563,0.09219,0.05322]}],"total_contact_groups":5},"final_pose_error":0.08987,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50507,0.00629,0.02541],"final_tcp_position":[0.49416,0.04239,0.04363],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"phases":[{"n_steps":859.0,"n_steps_budget":900.0,"object_pos_end":[0.50089,0.11596,0.03387],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19606,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_approach","tcp_end":[0.4978,0.14727,0.06522],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04441,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50507,0.00629,0.02541],"object_pos_start":[0.50089,0.11596,0.03387],"object_to_goal_dist_end":0.08767,"object_to_goal_dist_start":0.19606,"object_z_max":0.04077,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.49416,0.04239,0.04363],"tcp_start":[0.4978,0.14727,0.06522],"tcp_to_object_dist_end":0.04188,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.29032,"average_solve_count":62.0,"average_success_count":62.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_lateral_x":0.00777,"approach_1.approach_speed":0.21214,"approach_1.approach_tolerance":0.00947,"push_1.push_distance":0.18712,"push_1.push_lateral_x":0.0004,"push_1.push_speed":0.07616},"optimized_scores":{"best_composite_score":0.15979,"best_fitness_score":0.45979,"best_task_score":0.27668},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":158.0,"contact_point_centroid":[0.475,0.04847,0.05916],"force_p95":63.60115,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.62784,"mean_force":41.05987,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48502,0.04538,0.05411]},{"body_a":"peg","body_b":"channel_base_body","contact_count":994.0,"contact_point_centroid":[0.50187,0.02546,0.00917],"force_p95":62.11712,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.43199,"mean_force":18.30178,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4856,0.03902,0.05322]},{"body_a":"attachment","body_b":"peg","contact_count":766.0,"contact_point_centroid":[0.49541,0.02802,0.04796],"force_p95":62.31349,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.83421,"mean_force":26.99264,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48602,0.03217,0.05206]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":360.0,"contact_point_centroid":[0.52516,0.02519,0.05036],"force_p95":21.27564,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.68015,"mean_force":13.85367,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48487,0.04544,0.05398]},{"body_a":"peg","body_b":"channel_base_body","contact_count":719.0,"contact_point_centroid":[0.49529,0.06396,0.00938],"force_p95":0.56528,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55739,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49199,0.1489,0.18184]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49939,0.19879,0.2976]}],"total_contact_groups":6},"final_pose_error":0.07288,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49516,-0.00636,0.02627],"final_tcp_position":[0.49208,-0.0215,0.04538],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"phases":[{"n_steps":746.0,"n_steps_budget":780.0,"object_pos_end":[0.4949,0.06371,0.03398],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14393,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_approach","tcp_end":[0.48556,0.09843,0.06726],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04899,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49516,-0.00636,0.02627],"object_pos_start":[0.4949,0.06371,0.03398],"object_to_goal_dist_end":0.07506,"object_to_goal_dist_start":0.14393,"object_z_max":0.04031,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.49208,-0.0215,0.04538],"tcp_start":[0.48556,0.09843,0.06726],"tcp_to_object_dist_end":0.02457,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.30645,"average_solve_count":62.0,"average_success_count":62.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_lateral_x":0.00484,"approach_1.approach_speed":0.21657,"approach_1.approach_tolerance":0.01152,"push_1.push_distance":0.16399,"push_1.push_lateral_x":-0.00021,"push_1.push_speed":0.08643},"optimized_scores":{"best_composite_score":0.07268,"best_fitness_score":0.37268,"best_task_score":0.08679},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":755.0,"contact_point_centroid":[0.47498,0.04314,0.05721],"force_p95":208.18516,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":252.24427,"mean_force":119.46727,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47969,0.03618,0.05488]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.5313,-0.03995,0.05999],"force_p95":153.25262,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":157.74695,"mean_force":105.26404,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48622,-0.03359,0.03797]},{"body_a":"attachment","body_b":"peg","contact_count":744.0,"contact_point_centroid":[0.49279,0.01955,0.05],"force_p95":81.88606,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":103.7501,"mean_force":46.98221,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48206,0.02147,0.05176]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":659.0,"contact_point_centroid":[0.52587,0.00616,0.04337],"force_p95":70.63563,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.77217,"mean_force":44.53118,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48338,0.01462,0.05045]},{"body_a":"peg","body_b":"channel_base_body","contact_count":832.0,"contact_point_centroid":[0.50361,0.03345,0.00969],"force_p95":47.28765,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.15174,"mean_force":13.75469,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4782,0.04211,0.05594]},{"body_a":"peg","body_b":"channel_base_body","contact_count":717.0,"contact_point_centroid":[0.49433,0.05903,0.00936],"force_p95":0.55965,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56658,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48393,0.14643,0.18163]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4991,0.19845,0.29676]}],"total_contact_groups":7},"final_pose_error":0.03982,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50185,-0.00329,0.04019],"final_tcp_position":[0.48692,-0.03602,0.03786],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"phases":[{"n_steps":746.0,"n_steps_budget":780.0,"object_pos_end":[0.49398,0.05895,0.03389],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13922,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_approach","tcp_end":[0.46946,0.09376,0.06751],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05425,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50185,-0.00329,0.04019],"object_pos_start":[0.49398,0.05895,0.03389],"object_to_goal_dist_end":0.07673,"object_to_goal_dist_start":0.13922,"object_z_max":0.04045,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.48692,-0.03602,0.03786],"tcp_start":[0.46946,0.09376,0.06751],"tcp_to_object_dist_end":0.03605,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```