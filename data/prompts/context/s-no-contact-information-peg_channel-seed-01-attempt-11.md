## Search State

- **Seed**: 1
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1517 | 0.30 | ❌ rejected |
| 10 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0378 | 0.02 | ❌ rejected |
| 9 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 4 | 0.1220 | 0.00 | ❌ rejected |
| 8 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1661 | 0.41 | ✅ accepted |
| 7 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1659 | 0.40 | ❌ rejected |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.152) — your mutation base

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

- **Composite score**: 0.152
- **task_score** (E): 0.305
- **fitness_score**: 0.362  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| rotate_1 | 1.00 | 0.1730 |
| align_1 | 1.00 | 0.1462 |
| push_1 | 0.00 | 0.1693 |
| align_2 | 1.00 | 0.0394 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| rotate_1 | rotate | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.497, 0.075, 0.180) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.075, 0.180)→(0.494, 0.118, 0.043) | (0.497, 0.080, 0.034)→(0.497, 0.084, 0.033) | 0.160→0.164 |
| push_1 | push | 0.00 / step_budget | (0.494, 0.118, 0.043)→(0.496, -0.051, 0.038) | (0.497, 0.084, 0.033)→(0.502, -0.023, 0.022) | 0.164→0.069 |
| align_2 | align | 1.00 / step_budget | (0.496, -0.051, 0.038)→(0.500, -0.013, 0.038) | (0.502, -0.023, 0.022)→(0.493, -0.006, 0.027) | 0.069→0.081 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.840
- alignment_error: None
- terminal_score: 0.614
- phase_score: 0.478
- phase_breakdown.push_score: 0.785
- phase_breakdown.approach_score: 0.034

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.532
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.614
- **Median Q (composite search score)**: 0.221
- **K-run variance**: 0.0304
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.446


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91111,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00726,"align_2.lateral_offset_x":-0.00994,"push_1.push_distance":0.19971},"optimized_scores":{"best_composite_score":-0.08801,"best_fitness_score":0.12199,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":611.0,"contact_point_centroid":[0.54311,0.03307,0.05998],"force_p95":184.94102,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":221.30613,"mean_force":142.99903,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49826,0.03568,0.03681]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49863,0.088,0.00786],"force_p95":186.13102,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":193.84105,"mean_force":87.56123,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.503,0.08081,0.0454]},{"body_a":"attachment","body_b":"peg","contact_count":696.0,"contact_point_centroid":[0.50833,0.10495,0.04973],"force_p95":189.08892,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":193.31091,"mean_force":134.42756,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50522,0.10867,0.04847]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":143.0,"contact_point_centroid":[0.52501,0.07354,0.06],"force_p95":144.3642,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":171.03818,"mean_force":77.51704,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50709,0.07352,0.04898]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.50657,0.13982,0.05102],"force_p95":119.53343,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.43451,"mean_force":83.80714,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49846,0.14657,0.05326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":563.0,"contact_point_centroid":[0.50214,0.1166,0.00925],"force_p95":94.17839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.99062,"mean_force":15.43742,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49609,0.11288,0.10781]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":535.0,"contact_point_centroid":[0.47371,0.07824,0.02992],"force_p95":79.15545,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.65657,"mean_force":34.31271,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5039,0.05847,0.04532]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":69.0,"contact_point_centroid":[0.54173,0.00017,0.06],"force_p95":61.99524,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.67358,"mean_force":45.25151,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49683,0.00441,0.03713]},{"body_a":"peg","body_b":"world","contact_count":122.0,"contact_point_centroid":[0.50193,0.12558,-0.00017],"force_p95":19.73105,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.74864,"mean_force":13.83474,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5003,0.15495,0.04487]},{"body_a":"peg","body_b":"world","contact_count":28.0,"contact_point_centroid":[0.50222,0.12719,-0.0003],"force_p95":37.33342,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.90411,"mean_force":28.00895,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49992,0.15488,0.04587]},{"body_a":"attachment","body_b":"peg","contact_count":82.0,"contact_point_centroid":[0.49728,0.0783,0.03734],"force_p95":19.90439,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.27803,"mean_force":2.4233,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49888,0.06666,0.03661]},{"body_a":"peg","body_b":"channel_base_body","contact_count":661.0,"contact_point_centroid":[0.49447,0.08514,0.00944],"force_p95":0.98991,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.34605,"mean_force":0.79947,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49822,0.03294,0.03683]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":263.0,"contact_point_centroid":[0.47488,0.08415,0.04692],"force_p95":0.51841,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.2361,"mean_force":0.21898,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49836,0.03907,0.03681]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50098,0.11602,0.0094],"force_p95":0.60736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55146,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49749,0.13563,0.23636]}],"total_contact_groups":14},"final_pose_error":0.02332,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49448,0.122,0.03514],"final_tcp_position":[0.49929,0.09198,0.03629],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11601,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15182,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.50228,0.12805,0.02979],"object_pos_start":[0.50092,0.11601,0.03383],"object_to_goal_dist_end":0.20832,"object_to_goal_dist_start":0.19611,"object_z_max":0.0342,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.50029,0.1577,0.04359],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03276,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49301,0.0743,0.03379],"object_pos_start":[0.50228,0.12805,0.02979],"object_to_goal_dist_end":0.15458,"object_to_goal_dist_start":0.20832,"object_z_max":0.03457,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49703,-0.01011,0.03709],"tcp_start":[0.50029,0.1577,0.04359],"tcp_to_object_dist_end":0.08457,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":722.0,"n_steps_budget":780.0,"object_pos_end":[0.49448,0.122,0.03514],"object_pos_start":[0.49301,0.0743,0.03379],"object_to_goal_dist_end":0.20213,"object_to_goal_dist_start":0.15458,"object_z_max":0.03778,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.49929,0.09198,0.03629],"tcp_start":[0.49703,-0.01011,0.03709],"tcp_to_object_dist_end":0.03042,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75397,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00094,"align_2.lateral_offset_x":0.0014,"push_1.push_distance":0.19792},"optimized_scores":{"best_composite_score":0.32204,"best_fitness_score":0.53204,"best_task_score":0.6136},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":344.0,"contact_point_centroid":[0.52507,-0.06432,0.05997],"force_p95":275.20591,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":374.43564,"mean_force":216.20229,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50056,-0.0641,0.03731]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":330.0,"contact_point_centroid":[0.54562,-0.0607,0.05994],"force_p95":297.35433,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":324.63225,"mean_force":237.01017,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50053,-0.06409,0.03734]},{"body_a":"channel_base_body","body_b":"link7","contact_count":90.0,"contact_point_centroid":[0.54032,-0.10001,0.06497],"force_p95":250.62677,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":265.22914,"mean_force":162.1028,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49775,-0.06752,0.03709]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":309.0,"contact_point_centroid":[0.53462,-0.00999,0.05999],"force_p95":167.34807,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":247.15649,"mean_force":100.9957,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48928,-0.00532,0.03817]},{"body_a":"attachment","body_b":"peg","contact_count":442.0,"contact_point_centroid":[0.5022,-0.06949,0.03713],"force_p95":125.75464,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":154.96522,"mean_force":66.02689,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49981,-0.06495,0.0373]},{"body_a":"peg","body_b":"channel_base_body","contact_count":455.0,"contact_point_centroid":[0.4962,-0.06565,0.00663],"force_p95":125.25012,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":139.01454,"mean_force":59.35584,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.4998,-0.06499,0.03728]},{"body_a":"attachment","body_b":"peg","contact_count":922.0,"contact_point_centroid":[0.49788,0.00609,0.036],"force_p95":118.93926,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":138.73133,"mean_force":69.02591,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48941,0.01148,0.03807]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50845,-0.00682,0.00907],"force_p95":93.31982,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":125.06298,"mean_force":43.13937,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4894,0.01582,0.03818]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":846.0,"contact_point_centroid":[0.52615,-0.00638,0.02726],"force_p95":97.18935,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":107.09058,"mean_force":57.02177,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4895,0.00565,0.03805]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":31.0,"contact_point_centroid":[0.52507,-0.09635,0.01649],"force_p95":48.74491,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.14488,"mean_force":31.02858,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49485,-0.06974,0.03783]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":295.0,"contact_point_centroid":[0.47463,-0.08465,0.02343],"force_p95":31.26942,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.01246,"mean_force":25.73558,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50046,-0.06403,0.03745]},{"body_a":"peg","body_b":"link7","contact_count":368.0,"contact_point_centroid":[0.52003,0.00922,0.06779],"force_p95":22.8559,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.26412,"mean_force":11.84131,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48937,0.03412,0.03791]},{"body_a":"peg","body_b":"world","contact_count":64.0,"contact_point_centroid":[0.50906,-0.06945,-0.00083],"force_p95":11.60453,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.1044,"mean_force":1.23912,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49206,-0.06259,0.03789]},{"body_a":"peg","body_b":"world","contact_count":105.0,"contact_point_centroid":[0.50565,-0.06525,-0.00123],"force_p95":7.81894,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.80597,"mean_force":1.37531,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49726,-0.06788,0.03722]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.49527,0.06395,0.00938],"force_p95":0.55699,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55424,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49748,0.13493,0.23568]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49942,0.19831,0.29814]}],"total_contact_groups":17},"final_pose_error":0.03911,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49222,-0.07057,0.02403],"final_tcp_position":[0.50018,-0.06358,0.03852],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06382,0.03401],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14649,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":447.0,"n_steps_budget":930.0,"object_pos_end":[0.49519,0.06359,0.03403],"object_pos_start":[0.49482,0.06382,0.03401],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14404,"object_z_max":0.03403,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.4911,0.10042,0.04259],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03803,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50745,-0.07188,0.01678],"object_pos_start":[0.49519,0.06359,0.03403],"object_to_goal_dist_end":0.0257,"object_to_goal_dist_start":0.14379,"object_z_max":0.0399,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.4939,-0.06969,0.0381],"tcp_start":[0.4911,0.10042,0.04259],"tcp_to_object_dist_end":0.02536,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.49222,-0.07057,0.02403],"object_pos_start":[0.50745,-0.07188,0.01678],"object_to_goal_dist_end":0.02011,"object_to_goal_dist_start":0.0257,"object_z_max":0.02403,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.50018,-0.06358,0.03852],"tcp_start":[0.4939,-0.06969,0.0381],"tcp_to_object_dist_end":0.01795,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75397,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00148,"align_2.lateral_offset_x":0.00917,"push_1.push_distance":0.18973},"optimized_scores":{"best_composite_score":0.22095,"best_fitness_score":0.43095,"best_task_score":0.30085},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":358.0,"contact_point_centroid":[0.52505,-0.06851,0.05997],"force_p95":264.92619,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":321.87576,"mean_force":216.86907,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50082,-0.06836,0.03746]},{"body_a":"channel_base_body","body_b":"link7","contact_count":413.0,"contact_point_centroid":[0.54322,-0.10001,0.06494],"force_p95":283.37381,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":291.96918,"mean_force":229.30166,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50044,-0.06881,0.03747]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":293.0,"contact_point_centroid":[0.53439,-0.00752,0.05999],"force_p95":164.06307,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":240.66468,"mean_force":100.31253,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48903,-0.00292,0.03817]},{"body_a":"attachment","body_b":"peg","contact_count":898.0,"contact_point_centroid":[0.49813,0.00145,0.03576],"force_p95":117.4438,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":135.51088,"mean_force":68.14311,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48946,0.00636,0.03811]},{"body_a":"peg","body_b":"channel_base_body","contact_count":968.0,"contact_point_centroid":[0.5079,-0.00945,0.00877],"force_p95":93.29461,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":128.54081,"mean_force":42.90966,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4894,0.01151,0.03821]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":808.0,"contact_point_centroid":[0.52609,-0.00632,0.02486],"force_p95":96.899,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":105.32864,"mean_force":55.66102,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48939,0.00347,0.03809]},{"body_a":"attachment","body_b":"peg","contact_count":432.0,"contact_point_centroid":[0.50132,-0.07136,0.03744],"force_p95":99.49211,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":101.73169,"mean_force":44.22282,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50035,-0.06898,0.03746]},{"body_a":"peg","body_b":"channel_base_body","contact_count":464.0,"contact_point_centroid":[0.49471,-0.06809,0.00652],"force_p95":89.66748,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.6947,"mean_force":41.42429,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50037,-0.06896,0.03745]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":369.0,"contact_point_centroid":[0.47433,-0.08223,0.02257],"force_p95":39.97419,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.89443,"mean_force":23.53826,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50083,-0.06839,0.03744]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":13.0,"contact_point_centroid":[0.52501,-0.04627,0.01557],"force_p95":29.09656,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.8659,"mean_force":23.32522,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49664,-0.07294,0.03795]},{"body_a":"peg","body_b":"link7","contact_count":272.0,"contact_point_centroid":[0.51846,0.0074,0.06847],"force_p95":21.7081,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.59851,"mean_force":10.59324,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48904,0.03317,0.03796]},{"body_a":"peg","body_b":"world","contact_count":120.0,"contact_point_centroid":[0.50814,-0.06606,-0.00078],"force_p95":1.75605,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.21478,"mean_force":0.8167,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49307,-0.0617,0.03814]},{"body_a":"peg","body_b":"world","contact_count":87.0,"contact_point_centroid":[0.50536,-0.07149,-0.00122],"force_p95":6.94894,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.66398,"mean_force":1.15668,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49836,-0.07139,0.03754]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.49432,0.05896,0.00937],"force_p95":0.55417,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56118,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49747,0.13481,0.23556]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49933,0.1979,0.29752]},{"body_a":"peg","body_b":"channel_base_body","contact_count":443.0,"contact_point_centroid":[0.49394,0.0588,0.0094],"force_p95":0.55052,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55295,"mean_force":0.54554,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49272,0.08527,0.11112]}],"total_contact_groups":16},"final_pose_error":0.0432,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49151,-0.06969,0.02262],"final_tcp_position":[0.50037,-0.06773,0.0384],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49409,0.05914,0.03393],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.1394,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14702,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":443.0,"n_steps_budget":930.0,"object_pos_end":[0.49439,0.05889,0.034],"object_pos_start":[0.49409,0.05914,0.03393],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.1394,"object_z_max":0.034,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.49044,0.0962,0.04256],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03848,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50691,-0.07138,0.01599],"object_pos_start":[0.49439,0.05889,0.034],"object_to_goal_dist_end":0.02643,"object_to_goal_dist_start":0.13914,"object_z_max":0.03992,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49563,-0.07345,0.03844],"tcp_start":[0.49044,0.0962,0.04256],"tcp_to_object_dist_end":0.02521,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":464.0,"n_steps_budget":600.0,"object_pos_end":[0.49151,-0.06969,0.02262],"object_pos_start":[0.50691,-0.07138,0.01599],"object_to_goal_dist_end":0.02192,"object_to_goal_dist_start":0.02643,"object_z_max":0.02356,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.50037,-0.06773,0.0384],"tcp_start":[0.49563,-0.07345,0.03844],"tcp_to_object_dist_end":0.0182,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```