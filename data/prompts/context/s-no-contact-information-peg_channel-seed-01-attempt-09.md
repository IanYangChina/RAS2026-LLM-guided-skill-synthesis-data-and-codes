## Search State

- **Seed**: 1
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 4 | 0.1220 | 0.00 | ❌ rejected |
| 8 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1661 | 0.41 | ✅ accepted |
| 7 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1659 | 0.40 | ❌ rejected |
| 6 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 3 | 0.2378 | 0.24 | ❌ rejected |
| 5 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1208 | 0.32 | ❌ rejected |

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

## Current Skill (Q=0.122) — your mutation base

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

- **Composite score**: 0.122
- **task_score** (E): 0.001
- **fitness_score**: 0.241  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_0 | 1.00 | 0.1458 |
| align_1 | 1.00 | 0.1196 |
| push_1 | 0.33 | 0.0584 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_0 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.483, 0.096, 0.201) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 |
| align_1 | align | 1.00 / step_budget | (0.483, 0.096, 0.201)→(0.487, 0.081, 0.083) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 |
| push_1 | push | 0.33 / step_budget | (0.492, 0.030, 0.068)→(0.492, -0.023, 0.045) | (0.497, 0.080, 0.034)→(0.497, 0.079, 0.034) | 0.160→0.160 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.003
- alignment_error: None
- terminal_score: 0.001
- phase_score: 0.369
- phase_breakdown.reach_above_peg_score: 0.671
- phase_breakdown.push_through_channel_score: 0.004

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.251
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: 0.021
- **K-run variance**: 0.0206
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.359


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":78.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00344,"approach_0.approach_speed":0.40249,"push_1.force_threshold":24.08925,"push_1.push_distance":0.13633},"optimized_scores":{"best_composite_score":0.02085,"best_fitness_score":0.25085,"best_task_score":0.0005},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":207.0,"contact_point_centroid":[0.50107,0.11607,0.0093],"force_p95":0.84866,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.58474,"phase_index":0.0,"phase_name":"approach_0","phase_type":"approach","tcp_position_centroid":[0.49898,0.16367,0.24914]},{"body_a":"peg","body_b":"channel_base_body","contact_count":842.0,"contact_point_centroid":[0.50093,0.11603,0.00942],"force_p95":0.61064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65113,"mean_force":0.54216,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49684,0.05188,0.05729]},{"body_a":"peg","body_b":"channel_base_body","contact_count":382.0,"contact_point_centroid":[0.50087,0.11599,0.00941],"force_p95":0.60666,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64276,"mean_force":0.54411,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49867,0.12318,0.14309]}],"total_contact_groups":3},"final_pose_error":0.00784,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50098,0.11596,0.03389],"final_tcp_position":[0.4964,-0.01381,0.03557],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"phases":[{"n_steps":223.0,"n_steps_budget":600.0,"object_pos_end":[0.50094,0.11607,0.03386],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19617,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"phase_name":"approach_0","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_above_peg","tcp_end":[0.49881,0.12995,0.2041],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17082,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":382.0,"n_steps_budget":840.0,"object_pos_end":[0.50095,0.11614,0.03382],"object_pos_start":[0.50094,0.11607,0.03386],"object_to_goal_dist_end":0.19624,"object_to_goal_dist_start":0.19617,"object_z_max":0.03393,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"contact_peg","tcp_end":[0.50044,0.11677,0.08278],"tcp_start":[0.49881,0.12995,0.2041],"tcp_to_object_dist_end":0.04896,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":842.0,"n_steps_budget":900.0,"object_pos_end":[0.50098,0.11596,0.03389],"object_pos_start":[0.50095,0.11614,0.03382],"object_to_goal_dist_end":0.19606,"object_to_goal_dist_start":0.19624,"object_z_max":0.03402,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_through_channel","tcp_end":[0.4964,-0.01381,0.03557],"tcp_start":[0.50044,0.11677,0.08278],"tcp_to_object_dist_end":0.12986,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.08434,"average_solve_count":83.0,"average_success_count":83.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.01,"approach_0.approach_speed":0.33465,"push_1.force_threshold":14.19276,"push_1.push_distance":0.16625},"optimized_scores":{"best_composite_score":0.02019,"best_fitness_score":0.25019,"best_task_score":0.00073},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.49942,-0.10008,0.065],"force_p95":74.5145,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.03248,"mean_force":60.85271,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49539,-0.08793,0.03958]},{"body_a":"peg","body_b":"channel_base_body","contact_count":263.0,"contact_point_centroid":[0.49595,0.06382,0.00934],"force_p95":0.68255,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.57765,"phase_index":0.0,"phase_name":"approach_0","phase_type":"approach","tcp_position_centroid":[0.48963,0.13633,0.2448]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_0","phase_type":"approach","tcp_position_centroid":[0.49901,0.19586,0.29626]},{"body_a":"peg","body_b":"channel_base_body","contact_count":978.0,"contact_point_centroid":[0.49498,0.06384,0.0094],"force_p95":0.55075,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55403,"mean_force":0.5452,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48676,-0.0107,0.05956]},{"body_a":"peg","body_b":"channel_base_body","contact_count":381.0,"contact_point_centroid":[0.49512,0.06388,0.0094],"force_p95":0.55024,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55295,"mean_force":0.54574,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48052,0.07325,0.14115]}],"total_contact_groups":5},"final_pose_error":0.0149,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49534,0.06369,0.03403],"final_tcp_position":[0.49541,-0.08807,0.03953],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"phases":[{"n_steps":290.0,"n_steps_budget":600.0,"object_pos_end":[0.49515,0.06403,0.03391],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14424,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"phase_name":"approach_0","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_above_peg","tcp_end":[0.48143,0.08117,0.19974],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16728,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":381.0,"n_steps_budget":810.0,"object_pos_end":[0.49514,0.0641,0.03396],"object_pos_start":[0.49515,0.06403,0.03391],"object_to_goal_dist_end":0.1443,"object_to_goal_dist_start":0.14424,"object_z_max":0.03396,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"contact_peg","tcp_end":[0.48148,0.06541,0.08295],"tcp_start":[0.48143,0.08117,0.19974],"tcp_to_object_dist_end":0.05088,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":978.0,"n_steps_budget":1000.0,"object_pos_end":[0.49528,0.06364,0.03403],"object_pos_start":[0.49514,0.0641,0.03396],"object_to_goal_dist_end":0.14384,"object_to_goal_dist_start":0.1443,"object_z_max":0.03404,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_through_channel","tcp_end":[0.49541,-0.08807,0.03953],"tcp_start":[0.4954,-0.088,0.03956],"tcp_to_object_dist_end":0.15181,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.17241,"average_solve_count":58.0,"average_success_count":58.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00997,"approach_0.approach_speed":0.49268,"push_1.force_threshold":31.45492,"push_1.push_distance":0.06741},"optimized_scores":{"best_composite_score":0.32491,"best_fitness_score":0.22158,"best_task_score":0.00099},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":243.0,"contact_point_centroid":[0.49371,0.05844,0.00939],"force_p95":0.55173,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.10568,"mean_force":1.20156,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47988,0.0465,0.0698]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.49168,0.0406,0.05872],"force_p95":27.30618,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.72052,"mean_force":15.94207,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48274,0.03273,0.05997]},{"body_a":"peg","body_b":"channel_base_body","contact_count":268.0,"contact_point_centroid":[0.49454,0.05907,0.00932],"force_p95":0.65931,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.60076,"phase_index":0.0,"phase_name":"approach_0","phase_type":"approach","tcp_position_centroid":[0.48294,0.1333,0.24426]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_0","phase_type":"approach","tcp_position_centroid":[0.49806,0.1943,0.29475]},{"body_a":"peg","body_b":"channel_base_body","contact_count":397.0,"contact_point_centroid":[0.49424,0.059,0.00939],"force_p95":0.55035,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55326,"mean_force":0.54619,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47321,0.06825,0.14056]}],"total_contact_groups":5},"final_pose_error":0.04852,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49412,0.05846,0.03423],"final_tcp_position":[0.48299,0.03218,0.05971],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"phases":[{"n_steps":297.0,"n_steps_budget":600.0,"object_pos_end":[0.49407,0.05888,0.03384],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"phase_name":"approach_0","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_above_peg","tcp_end":[0.46914,0.07635,0.19952],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16845,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":397.0,"n_steps_budget":810.0,"object_pos_end":[0.49399,0.059,0.03389],"object_pos_start":[0.49407,0.05888,0.03384],"object_to_goal_dist_end":0.13926,"object_to_goal_dist_start":0.13914,"object_z_max":0.03389,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"contact_peg","tcp_end":[0.47932,0.06023,0.08229],"tcp_start":[0.46914,0.07635,0.19952],"tcp_to_object_dist_end":0.05059,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":243.0,"n_steps_budget":600.0,"object_pos_end":[0.49412,0.05846,0.03423],"object_pos_start":[0.49399,0.059,0.03389],"object_to_goal_dist_end":0.13871,"object_to_goal_dist_start":0.13926,"object_z_max":0.03419,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_through_channel","tcp_end":[0.48299,0.03218,0.05971],"tcp_start":[0.47932,0.06023,0.08229],"tcp_to_object_dist_end":0.03826,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```