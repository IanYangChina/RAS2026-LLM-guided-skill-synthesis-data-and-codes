## Search State

- **Seed**: 1
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → push | linear_cartesian | impedance_motion | position_control | impedance_control | pose_tolerance | time_limit | 6 | 0.0151 | 0.15 | ❌ rejected |
| 12 | approach → push | linear_cartesian | impedance_motion | position_control | impedance_control | pose_tolerance | time_limit | 6 | 0.1993 | 0.35 | ❌ rejected |
| 11 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1517 | 0.30 | ❌ rejected |
| 10 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0378 | 0.02 | ❌ rejected |
| 9 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 4 | 0.1220 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.15 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.015) — your mutation base

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

- **Composite score**: 0.015
- **task_score** (E): 0.145
- **fitness_score**: 0.315  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.2440 |
| push_1 | 1.00 | 0.1461 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.483, 0.104, 0.078) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 |
| push_1 | push | 1.00 / time_limit | (0.483, 0.104, 0.078)→(0.491, -0.037, 0.042) | (0.497, 0.080, 0.034)→(0.502, 0.038, 0.024) | 0.160→0.120 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.261
- alignment_error: None
- terminal_score: 0.261
- phase_score: 0.397
- phase_breakdown.reach_approach_score: 0.835
- phase_breakdown.push_to_goal_score: 0.209

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.343
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.261
- **Median Q (composite search score)**: 0.014
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.349


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93182,"average_solve_count":88.0,"average_success_count":88.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_lateral_x":0.00549,"approach_1.approach_speed":0.09345,"approach_1.approach_tolerance":0.01962,"push_1.push_distance":0.16668,"push_1.push_lateral_x":0.00574,"push_1.push_speed":0.11716},"optimized_scores":{"best_composite_score":0.04265,"best_fitness_score":0.34265,"best_task_score":0.26131},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":104.0,"contact_point_centroid":[0.54542,-0.02224,0.05993],"force_p95":305.8,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":353.01838,"mean_force":225.47204,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50063,-0.01684,0.03701]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":172.0,"contact_point_centroid":[0.52505,-0.01504,0.05997],"force_p95":288.73428,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":313.9319,"mean_force":183.29211,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50089,-0.01499,0.03733]},{"body_a":"peg","body_b":"channel_base_body","contact_count":991.0,"contact_point_centroid":[0.5024,0.09212,0.00896],"force_p95":18.33441,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.00175,"mean_force":2.5151,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50056,0.05072,0.05321]},{"body_a":"attachment","body_b":"peg","contact_count":200.0,"contact_point_centroid":[0.50693,0.08221,0.05628],"force_p95":20.83802,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.3882,"mean_force":9.76371,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5006,0.0736,0.05895]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.525,0.05111,0.0242],"force_p95":6.44433,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.5006,"mean_force":2.21181,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50079,0.03192,0.04845]},{"body_a":"peg","body_b":"channel_base_body","contact_count":690.0,"contact_point_centroid":[0.50097,0.11601,0.0094],"force_p95":0.61264,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.5539,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5004,0.1688,0.18662]}],"total_contact_groups":6},"final_pose_error":0.03335,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50357,0.07423,0.02413],"final_tcp_position":[0.50049,-0.01809,0.03748],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"phases":[{"n_steps":706.0,"n_steps_budget":1000.0,"object_pos_end":[0.50095,0.11602,0.03395],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19612,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_approach","tcp_end":[0.50242,0.13884,0.07846],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05003,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":996.0,"n_steps_budget":1000.0,"object_pos_end":[0.50357,0.07423,0.02413],"object_pos_start":[0.50095,0.11602,0.03395],"object_to_goal_dist_end":0.15508,"object_to_goal_dist_start":0.19612,"object_z_max":0.04076,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.50049,-0.01809,0.03748],"tcp_start":[0.50242,0.13884,0.07846],"tcp_to_object_dist_end":0.09333,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93939,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_lateral_x":0.00034,"approach_1.approach_speed":0.08422,"approach_1.approach_tolerance":0.01103,"push_1.push_distance":0.17993,"push_1.push_lateral_x":-0.009,"push_1.push_speed":0.10562},"optimized_scores":{"best_composite_score":0.01415,"best_fitness_score":0.31415,"best_task_score":0.12017},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":451.0,"contact_point_centroid":[0.47498,-0.02705,0.05532],"force_p95":124.53017,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":165.11135,"mean_force":89.05142,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48403,-0.02544,0.05071]},{"body_a":"peg","body_b":"channel_base_body","contact_count":995.0,"contact_point_centroid":[0.49944,0.04124,0.00897],"force_p95":29.85635,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.47717,"mean_force":4.41371,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48088,0.00911,0.05756]},{"body_a":"attachment","body_b":"peg","contact_count":228.0,"contact_point_centroid":[0.48597,0.03421,0.05737],"force_p95":32.03156,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.94343,"mean_force":16.86927,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47824,0.02732,0.06111]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52503,-0.002,0.0243],"force_p95":6.81708,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.93396,"mean_force":1.79777,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48562,-0.02357,0.05204]},{"body_a":"peg","body_b":"channel_base_body","contact_count":756.0,"contact_point_centroid":[0.49541,0.06387,0.00938],"force_p95":0.56441,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55679,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48825,0.14298,0.18421]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49931,0.19852,0.29725]}],"total_contact_groups":6},"final_pose_error":0.04329,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50121,0.02259,0.02404],"final_tcp_position":[0.48571,-0.07284,0.03931],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"phases":[{"n_steps":783.0,"n_steps_budget":1000.0,"object_pos_end":[0.4951,0.06412,0.03398],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14433,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_approach","tcp_end":[0.47867,0.08941,0.07766],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05307,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50121,0.02259,0.02404],"object_pos_start":[0.4951,0.06412,0.03398],"object_to_goal_dist_end":0.10383,"object_to_goal_dist_start":0.14433,"object_z_max":0.04069,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.48571,-0.07284,0.03931],"tcp_start":[0.47867,0.08941,0.07766],"tcp_to_object_dist_end":0.09788,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.14062,"average_solve_count":64.0,"average_success_count":64.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_lateral_x":0.00191,"approach_1.approach_speed":0.19688,"approach_1.approach_tolerance":0.01025,"push_1.push_distance":0.14573,"push_1.push_lateral_x":8e-05,"push_1.push_speed":0.06942},"optimized_scores":{"best_composite_score":-0.01148,"best_fitness_score":0.28852,"best_task_score":0.05407},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":389.0,"contact_point_centroid":[0.47499,0.00586,0.05926],"force_p95":132.32447,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":171.63837,"mean_force":90.08169,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48122,0.00428,0.05606]},{"body_a":"peg","body_b":"channel_base_body","contact_count":995.0,"contact_point_centroid":[0.49781,0.04538,0.00951],"force_p95":45.51997,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.26812,"mean_force":11.14612,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47434,0.03182,0.06189]},{"body_a":"attachment","body_b":"peg","contact_count":481.0,"contact_point_centroid":[0.48338,0.03092,0.05648],"force_p95":46.23613,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.84161,"mean_force":22.04147,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47549,0.0244,0.06032]},{"body_a":"peg","body_b":"channel_base_body","contact_count":654.0,"contact_point_centroid":[0.49426,0.05895,0.00936],"force_p95":0.56097,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56857,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48212,0.13993,0.18301]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49887,0.19751,0.29518]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52501,0.04451,0.02678],"force_p95":2.03404,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.05649,"mean_force":1.2671,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4857,-0.0091,0.05339]}],"total_contact_groups":6},"final_pose_error":0.07006,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50268,0.01854,0.02416],"final_tcp_position":[0.48564,-0.01891,0.04838],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"phases":[{"n_steps":683.0,"n_steps_budget":840.0,"object_pos_end":[0.49417,0.05883,0.03389],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13908,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_approach","tcp_end":[0.46689,0.0847,0.07775],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05777,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50268,0.01854,0.02416],"object_pos_start":[0.49417,0.05883,0.03389],"object_to_goal_dist_end":0.09984,"object_to_goal_dist_start":0.13908,"object_z_max":0.04069,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.48564,-0.01891,0.04838],"tcp_start":[0.46689,0.0847,0.07775],"tcp_to_object_dist_end":0.04775,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```