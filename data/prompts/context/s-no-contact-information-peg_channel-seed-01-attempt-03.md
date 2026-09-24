## Search State

- **Seed**: 1
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 3 | 0.2813 | 0.03 | ❌ rejected |
| 2 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1153 | 0.34 | ✅ accepted |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.0494 | 0.19 | ❌ rejected |
| 0 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1472 | 0.30 | ✅ accepted |

**Proposal policy**: task_score is 0.03 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.281) — your mutation base

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

- **Composite score**: 0.281
- **task_score** (E): 0.033
- **fitness_score**: 0.158  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach | 1.00 | 0.2350 |
| descend | 1.00 | 0.0382 |
| push | 1.00 | 0.0411 |
| retract | 1.00 | 0.0404 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.481, 0.086, 0.097) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 |
| descend | descend | 1.00 / force_exceeded | (0.481, 0.086, 0.097)→(0.487, 0.081, 0.060) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 |
| push | push | 1.00 / time_limit | (0.487, 0.081, 0.060)→(0.511, 0.092, 0.055) | (0.497, 0.080, 0.034)→(0.497, 0.065, 0.027) | 0.160→0.146 |
| retract | retract | 1.00 / step_budget | (0.511, 0.092, 0.055)→(0.509, 0.091, 0.095) | (0.497, 0.065, 0.027)→(0.497, 0.065, 0.027) | 0.146→0.146 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.210
- alignment_error: None
- terminal_score: 0.048
- phase_score: 0.358
- phase_breakdown.push_to_goal_score: 0.242

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.234
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.048
- **Median Q (composite search score)**: 0.262
- **K-run variance**: 0.0031
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.253


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66667,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.10516,"descend.descent_force_threshold":19.84554,"push.retry_offset_x":0.00059},"optimized_scores":{"best_composite_score":0.26177,"best_fitness_score":0.13843,"best_task_score":0.04695},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":26.0,"contact_point_centroid":[0.52707,0.11736,0.05952],"force_p95":757.00777,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":842.74426,"mean_force":435.29906,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51938,0.10973,0.0627]},{"body_a":"attachment","body_b":"peg","contact_count":905.0,"contact_point_centroid":[0.50275,0.09329,0.05374],"force_p95":190.16329,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":409.57468,"mean_force":136.03775,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50333,0.08711,0.06273]},{"body_a":"peg","body_b":"channel_base_body","contact_count":932.0,"contact_point_centroid":[0.50093,0.09273,0.00806],"force_p95":193.62422,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":342.71075,"mean_force":132.17474,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50385,0.08777,0.06277]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":691.0,"contact_point_centroid":[0.46892,0.11994,0.06],"force_p95":223.21902,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":251.96108,"mean_force":196.94153,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50307,0.08335,0.06301]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.46827,0.11995,0.06],"force_p95":133.41925,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":137.64206,"mean_force":81.22793,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50662,0.08764,0.06377]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":24.0,"contact_point_centroid":[0.52672,0.11213,0.0568],"force_p95":105.92376,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":110.7628,"mean_force":24.44555,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51743,0.1087,0.06099]},{"body_a":"attachment","body_b":"peg","contact_count":52.0,"contact_point_centroid":[0.50459,0.09379,0.0567],"force_p95":81.85245,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":103.83392,"mean_force":23.48697,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.5062,0.08767,0.06724]},{"body_a":"peg","body_b":"channel_base_body","contact_count":302.0,"contact_point_centroid":[0.49435,0.1037,0.0094],"force_p95":39.49998,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":96.92444,"mean_force":4.75734,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50496,0.08699,0.08407]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":375.0,"contact_point_centroid":[0.47462,0.10662,0.01225],"force_p95":53.01612,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":66.70917,"mean_force":15.74391,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50319,0.08886,0.06249]},{"body_a":"peg","body_b":"channel_base_body","contact_count":214.0,"contact_point_centroid":[0.50109,0.11614,0.00942],"force_p95":0.61271,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.77777,"mean_force":0.68503,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49584,0.11841,0.0784]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50785,0.11558,0.05879],"force_p95":30.32017,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.32017,"mean_force":30.32017,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49605,0.11693,0.06047]},{"body_a":"peg","body_b":"link7","contact_count":30.0,"contact_point_centroid":[0.48874,0.12493,0.05895],"force_p95":13.12537,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.44336,"mean_force":2.10926,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50562,0.08726,0.0713]},{"body_a":"peg","body_b":"link7","contact_count":672.0,"contact_point_centroid":[0.4911,0.12249,0.05654],"force_p95":7.58647,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.16117,"mean_force":3.23117,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50302,0.08329,0.063]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.52533,0.11987,0.06],"force_p95":0.0,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":9.89816,"mean_force":0.39593,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49962,0.07944,0.06315]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":151.0,"contact_point_centroid":[0.47495,0.10743,0.04164],"force_p95":7.47601,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.6564,"mean_force":1.5979,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50528,0.08716,0.07972]},{"body_a":"peg","body_b":"channel_base_body","contact_count":650.0,"contact_point_centroid":[0.5009,0.11597,0.00941],"force_p95":0.61522,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55354,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49798,0.15936,0.19603]}],"total_contact_groups":16},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49305,0.10735,0.03382],"final_tcp_position":[0.50457,0.08684,0.10399],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"phases":[{"n_steps":666.0,"n_steps_budget":1000.0,"object_pos_end":[0.50098,0.11607,0.03399],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19617,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_pre_contact","tcp_end":[0.49763,0.12039,0.09808],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06432,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":214.0,"n_steps_budget":600.0,"object_pos_end":[0.50103,0.11628,0.03386],"object_pos_start":[0.50098,0.11607,0.03399],"object_to_goal_dist_end":0.19638,"object_to_goal_dist_start":0.19617,"object_z_max":0.03399,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.49607,0.11692,0.06031],"tcp_start":[0.49763,0.12039,0.09808],"tcp_to_object_dist_end":0.02692,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":932.0,"n_steps_budget":990.0,"object_pos_end":[0.49295,0.1075,0.03171],"object_pos_start":[0.50103,0.11628,0.03386],"object_to_goal_dist_end":0.18782,"object_to_goal_dist_start":0.19638,"object_z_max":0.0355,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.50663,0.08762,0.06368],"tcp_start":[0.49607,0.11692,0.06031],"tcp_to_object_dist_end":0.04006,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":302.0,"n_steps_budget":600.0,"object_pos_end":[0.49305,0.10735,0.03382],"object_pos_start":[0.49295,0.1075,0.03171],"object_to_goal_dist_end":0.18758,"object_to_goal_dist_start":0.18782,"object_z_max":0.03471,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.50457,0.08684,0.10399],"tcp_start":[0.50663,0.08762,0.06368],"tcp_to_object_dist_end":0.07401,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68696,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.10866,"descend.descent_force_threshold":15.97419,"push.retry_offset_x":0.00059},"optimized_scores":{"best_composite_score":0.22494,"best_fitness_score":0.10161,"best_task_score":0.00438},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":817.0,"contact_point_centroid":[0.47414,0.11989,0.05997],"force_p95":523.40988,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":579.18475,"mean_force":383.10088,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51221,0.08659,0.05585]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":539.0,"contact_point_centroid":[0.52508,0.09054,0.0574],"force_p95":346.31107,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":410.8916,"mean_force":278.34595,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51349,0.08771,0.05705]},{"body_a":"attachment","body_b":"peg","contact_count":478.0,"contact_point_centroid":[0.50166,0.08299,0.05159],"force_p95":246.39495,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":355.78609,"mean_force":55.90841,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50978,0.08293,0.05379]},{"body_a":"peg","body_b":"channel_base_body","contact_count":912.0,"contact_point_centroid":[0.49772,0.05272,0.00885],"force_p95":219.98927,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":355.70375,"mean_force":28.16397,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51159,0.08567,0.05557]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.47145,0.11993,0.05999],"force_p95":303.11252,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":307.44873,"mean_force":174.83836,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51375,0.09243,0.05849]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52502,0.09647,0.05871],"force_p95":250.45308,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":252.21283,"mean_force":133.83393,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51376,0.0924,0.05847]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":74.0,"contact_point_centroid":[0.47441,0.06158,0.02457],"force_p95":99.46962,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":107.23423,"mean_force":66.31927,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5052,0.08726,0.04615]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":12.0,"contact_point_centroid":[0.52571,0.05845,0.05561],"force_p95":64.35571,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":64.39897,"mean_force":48.60135,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50622,0.05711,0.05874]},{"body_a":"peg","body_b":"channel_base_body","contact_count":301.0,"contact_point_centroid":[0.49489,0.06374,0.0094],"force_p95":0.55087,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.51877,"mean_force":0.64628,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.48095,0.06813,0.07653]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.49683,0.06597,0.05897],"force_p95":15.92252,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.99996,"mean_force":15.22554,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.48496,0.06622,0.06067]},{"body_a":"peg","body_b":"channel_base_body","contact_count":732.0,"contact_point_centroid":[0.49541,0.06384,0.00938],"force_p95":0.56511,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55718,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48822,0.13306,0.19348]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49933,0.19823,0.29725]},{"body_a":"peg","body_b":"channel_base_body","contact_count":312.0,"contact_point_centroid":[0.49618,0.06263,0.00809],"force_p95":0.64666,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.89852,"mean_force":0.60433,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51203,0.09178,0.07821]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.525,0.11985,0.05994],"force_p95":0.0,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50237,0.08363,0.04113]}],"total_contact_groups":14},"final_pose_error":0.00992,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49525,0.06276,0.02415],"final_tcp_position":[0.5118,0.09165,0.09874],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"phases":[{"n_steps":759.0,"n_steps_budget":1000.0,"object_pos_end":[0.49519,0.0641,0.03398],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14431,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_pre_contact","tcp_end":[0.47875,0.07066,0.09689],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06535,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":301.0,"n_steps_budget":600.0,"object_pos_end":[0.49541,0.06384,0.03403],"object_pos_start":[0.49519,0.0641,0.03398],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14431,"object_z_max":0.03402,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.485,0.06621,0.06057],"tcp_start":[0.47875,0.07066,0.09689],"tcp_to_object_dist_end":0.02861,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":932.0,"n_steps_budget":990.0,"object_pos_end":[0.49702,0.06272,0.02436],"object_pos_start":[0.49541,0.06384,0.03403],"object_to_goal_dist_end":0.14361,"object_to_goal_dist_start":0.14404,"object_z_max":0.03671,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.51381,0.09238,0.05843],"tcp_start":[0.485,0.06621,0.06057],"tcp_to_object_dist_end":0.04819,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":312.0,"n_steps_budget":600.0,"object_pos_end":[0.49525,0.06276,0.02415],"object_pos_start":[0.49702,0.06272,0.02436],"object_to_goal_dist_end":0.14372,"object_to_goal_dist_start":0.14361,"object_z_max":0.02452,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.5118,0.09165,0.09874],"tcp_start":[0.51381,0.09238,0.05843],"tcp_to_object_dist_end":0.08168,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72807,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.11584,"descend.descent_force_threshold":27.01483,"push.retry_offset_x":0.00157},"optimized_scores":{"best_composite_score":0.35713,"best_fitness_score":0.23379,"best_task_score":0.04752},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":817.0,"contact_point_centroid":[0.47429,0.11989,0.05999],"force_p95":614.63706,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":700.27975,"mean_force":398.0517,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51265,0.0918,0.0404]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":576.0,"contact_point_centroid":[0.52506,0.09599,0.04215],"force_p95":425.36567,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":501.79675,"mean_force":279.41612,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51366,0.09256,0.0414]},{"body_a":"attachment","body_b":"peg","contact_count":126.0,"contact_point_centroid":[0.50436,0.07961,0.05231],"force_p95":303.08636,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":351.43888,"mean_force":203.10273,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50459,0.08257,0.04571]},{"body_a":"peg","body_b":"channel_base_body","contact_count":898.0,"contact_point_centroid":[0.49935,0.03053,0.00802],"force_p95":227.79097,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":351.35821,"mean_force":28.19795,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51194,0.09051,0.04165]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.47225,0.11991,0.06],"force_p95":322.87516,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":334.71206,"mean_force":207.28677,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51401,0.09669,0.0421]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52504,0.10124,0.04303],"force_p95":245.10146,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":253.78137,"mean_force":141.24967,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51401,0.09669,0.0421]},{"body_a":"world","body_b":"link7","contact_count":106.0,"contact_point_centroid":[0.48795,0.1573,-1e-05],"force_p95":162.77272,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":163.61971,"mean_force":128.05894,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51392,0.09611,0.0417]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.48723,0.15729,-0.0],"force_p95":131.13839,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":131.13839,"mean_force":131.13839,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51404,0.09666,0.042]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":43.0,"contact_point_centroid":[0.47453,0.0516,0.02378],"force_p95":87.06699,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":90.24899,"mean_force":63.13413,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50499,0.09474,0.03522]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.52516,0.05896,0.04085],"force_p95":38.941,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.56116,"mean_force":15.80752,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50946,0.07803,0.04584]},{"body_a":"peg","body_b":"channel_base_body","contact_count":339.0,"contact_point_centroid":[0.49434,0.05905,0.00939],"force_p95":0.55067,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.35551,"mean_force":0.86907,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.47134,0.06323,0.07676]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.49099,0.05993,0.05882],"force_p95":28.24977,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.03438,"mean_force":18.34613,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.47918,0.06113,0.06044]},{"body_a":"peg","body_b":"channel_base_body","contact_count":313.0,"contact_point_centroid":[0.50262,0.02439,0.00803],"force_p95":0.72632,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.82658,"mean_force":0.67913,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51219,0.09601,0.06182]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.525,0.04662,0.02417],"force_p95":6.51925,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.59176,"mean_force":3.79178,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51202,0.09588,0.05589]},{"body_a":"peg","body_b":"channel_base_body","contact_count":736.0,"contact_point_centroid":[0.49428,0.05902,0.00936],"force_p95":0.55961,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56606,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48132,0.13035,0.1931]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49896,0.19764,0.29624]}],"total_contact_groups":16},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50153,0.02542,0.0241],"final_tcp_position":[0.51194,0.09587,0.08233],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"phases":[{"n_steps":765.0,"n_steps_budget":1000.0,"object_pos_end":[0.49401,0.05886,0.03389],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13913,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_pre_contact","tcp_end":[0.46543,0.06583,0.09682],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06947,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.49416,0.05916,0.03395],"object_pos_start":[0.49401,0.05886,0.03389],"object_to_goal_dist_end":0.13941,"object_to_goal_dist_start":0.13913,"object_z_max":0.03396,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.47939,0.06107,0.06021],"tcp_start":[0.46543,0.06583,0.09682],"tcp_to_object_dist_end":0.03019,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":932.0,"n_steps_budget":990.0,"object_pos_end":[0.50229,0.02445,0.0241],"object_pos_start":[0.49416,0.05916,0.03395],"object_to_goal_dist_end":0.10568,"object_to_goal_dist_start":0.13941,"object_z_max":0.03906,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.51404,0.09666,0.042],"tcp_start":[0.47939,0.06107,0.06021],"tcp_to_object_dist_end":0.07532,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":313.0,"n_steps_budget":600.0,"object_pos_end":[0.50153,0.02542,0.0241],"object_pos_start":[0.50229,0.02445,0.0241],"object_to_goal_dist_end":0.10662,"object_to_goal_dist_start":0.10568,"object_z_max":0.0243,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.51194,0.09587,0.08233],"tcp_start":[0.51404,0.09666,0.042],"tcp_to_object_dist_end":0.09199,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```