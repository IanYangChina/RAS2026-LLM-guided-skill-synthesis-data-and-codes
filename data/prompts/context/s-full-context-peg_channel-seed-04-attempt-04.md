## Search State

- **Seed**: 4
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2053 | 0.07 | ❌ rejected |
| 3 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3041 | 0.61 | ✅ accepted |
| 2 | approach → push | linear_cartesian | impedance_motion | position_control | impedance_control | pose_tolerance | force_exceeded | 3 | 0.0071 | 0.00 | ❌ rejected |
| 1 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3025 | 0.60 | ❌ rejected |
| 0 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3038 | 0.61 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`
- Frozen object start: [0.5354444884457894, 0.08090620422514894, 0.04]
- Frozen task target: [0.5354444884457894, -0.07909379577485107, 0.04]
- Goal object position: (0.5354444884457894, -0.07909379577485107, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5354444884457894, 0.08090620422514894, 0.04)
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
  frozen_object_start: [0.5354, 0.0809, 0.04]
  frozen_task_target: [0.5354, -0.0791, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5354444884457894, 0.08090620422514894, 0.04]}
  frozen_targets: {'channel_exit': [0.5354444884457894, -0.07909379577485107, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c

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
| `object` | offset from object initial position (0.5354444884457894, 0.08090620422514894, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5354444884457894, -0.07909379577485107, 0.04) | final destination targets |
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

## Current Skill (Q=-0.205) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  parameters:
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
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0

```

## Design Metrics

- **Composite score**: -0.205
- **task_score** (E): 0.068
- **fitness_score**: 0.155  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1652 |
| descend | 1.00 | 1.00 | 0.0908 |
| push_channel | 0.00 | 1.00 | 0.0530 |
| retract | 0.00 | 1.00 | 0.0118 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.517, 0.166, 0.141) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.164 | 1.00 / 1.000 | 0.542 | 3.242 |
| descend | descend | 1.00 / step_budget | (0.517, 0.166, 0.141)→(0.504, 0.134, 0.057) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.164→0.165 | 1.00 / 2.000 | 282.304 | 310.055 |
| push_channel | push | 0.00 / step_budget | (0.504, 0.134, 0.057)→(0.509, 0.082, 0.052) | (0.505, 0.084, 0.034)→(0.506, 0.063, 0.036) | 0.165→0.143 | 1.00 / 3.333 | 219.325 | 590.886 |
| retract | retract | 0.00 / step_budget | (0.509, 0.082, 0.052)→(0.510, 0.086, 0.041) | (0.506, 0.063, 0.036)→(0.506, 0.063, 0.034) | 0.143→0.143 | 1.00 / 3.000 | 114.371 | 397.471 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.260
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.139
- phase_score: 0.214
- phase_breakdown.reach_push_score: 0.039
- phase_breakdown.reach_approach_score: 0.912

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.184
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.139
- **Median Q (composite search score)**: -0.219
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.220


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `424e8a040c59c1e1e42822c1022320b6050001458f7b9b4937cb9238911ce80b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `72d2436204c0f1ee3bbdbdfe3e5489661153a48f95d8f0dc3b73e6ce1e1e081b`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56069,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height_offset_z":0.0928,"approach.approach_speed":0.15736,"descend.descend_speed":0.04315,"push_channel.push_distance_m":0.181,"push_channel.push_speed":0.03194,"retract.retract_speed":0.15795},"optimized_scores":{"best_composite_score":-0.21902,"best_fitness_score":0.14098,"best_task_score":0.03716},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":666.0,"contact_point_centroid":[0.47497,0.11995,0.0535],"force_p95":377.22021,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":476.64373,"mean_force":224.02563,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51094,0.07989,0.05287]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":999.0,"contact_point_centroid":[0.47497,0.11995,0.05956],"force_p95":294.77933,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":456.32085,"mean_force":229.07909,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.5131,0.08299,0.04522]},{"body_a":"world","body_b":"link7","contact_count":85.0,"contact_point_centroid":[0.51028,0.19059,-0.00029],"force_p95":283.01544,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":291.50861,"mean_force":248.19403,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50818,0.12972,0.05499]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":83.0,"contact_point_centroid":[0.52504,0.08168,0.05121],"force_p95":225.12447,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":251.08149,"mean_force":154.63023,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51314,0.0805,0.05116]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":923.0,"contact_point_centroid":[0.52502,0.08427,0.04533],"force_p95":164.54376,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":245.27616,"mean_force":128.56506,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51311,0.08307,0.04504]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":154.0,"contact_point_centroid":[0.52501,0.11987,0.02956],"force_p95":172.00209,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":212.31186,"mean_force":134.56391,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5081,0.0797,0.05533]},{"body_a":"world","body_b":"link7","contact_count":145.0,"contact_point_centroid":[0.51007,0.16766,-1e-05],"force_p95":130.62365,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":138.12032,"mean_force":118.04367,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50761,0.10731,0.0561]},{"body_a":"attachment","body_b":"peg","contact_count":807.0,"contact_point_centroid":[0.50625,0.08023,0.04369],"force_p95":3.71079,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.42665,"mean_force":1.50782,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5103,0.08042,0.05346]},{"body_a":"peg","body_b":"channel_base_body","contact_count":994.0,"contact_point_centroid":[0.5074,0.05303,0.00989],"force_p95":3.13072,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.23179,"mean_force":1.54925,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50989,0.08564,0.05387]},{"body_a":"peg","body_b":"channel_base_body","contact_count":529.0,"contact_point_centroid":[0.5057,0.08092,0.00936],"force_p95":0.55815,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57561,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50938,0.18597,0.21289]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50334,0.22184,0.28706]},{"body_a":"attachment","body_b":"peg","contact_count":278.0,"contact_point_centroid":[0.50627,0.07954,0.05846],"force_p95":1.33859,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.09419,"mean_force":0.74127,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51312,0.08138,0.04882]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50678,0.05694,0.00956],"force_p95":1.31196,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.0657,"mean_force":0.70077,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.5131,0.08299,0.04523]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":274.0,"contact_point_centroid":[0.52501,0.0617,0.05756],"force_p95":0.33675,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.23057,"mean_force":0.0585,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.5131,0.08292,0.04537]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":470.0,"contact_point_centroid":[0.52501,0.05995,0.05639],"force_p95":0.35713,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.81118,"mean_force":0.18338,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51075,0.08012,0.05303]},{"body_a":"peg","body_b":"channel_base_body","contact_count":352.0,"contact_point_centroid":[0.50593,0.08079,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55007,"mean_force":0.54677,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.51652,0.14224,0.08743]}],"total_contact_groups":16},"final_pose_error":0.25894,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50698,0.06169,0.03377],"final_tcp_position":[0.51308,0.08469,0.04137],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":476.64373,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":558.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54457,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":565.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_approach","tcp_end":[0.53009,0.1626,0.14078],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13679,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":352.0,"n_steps_budget":750.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":270.02558,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":437.0,"raw_peak_contact_force":291.50861,"tcp_end":[0.50769,0.13054,0.05636],"tcp_start":[0.53009,0.1626,0.14078],"tcp_to_object_dist_end":0.05457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.507,0.06252,0.03571],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.14276,"object_to_goal_dist_start":0.16113,"object_z_max":0.03821,"peak_contact_force":431.88502,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3319.0,"raw_peak_contact_force":476.64373,"subtask_id":"reach_push","tcp_end":[0.51315,0.08063,0.05107],"tcp_start":[0.50769,0.13054,0.05636],"tcp_to_object_dist_end":0.02453,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50698,0.06169,0.03377],"object_pos_start":[0.507,0.06252,0.03571],"object_to_goal_dist_end":0.142,"object_to_goal_dist_start":0.14276,"object_z_max":0.03571,"peak_contact_force":0.0,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3474.0,"raw_peak_contact_force":456.32085,"tcp_end":[0.51308,0.08469,0.04137],"tcp_start":[0.51315,0.08063,0.05107],"tcp_to_object_dist_end":0.02497,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `54762c1e743ba455eff3c9979c2b42f5642abe1893e28eae37dc231d7efcd4e4`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53073,"average_solve_count":179.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height_offset_z":0.09031,"approach.approach_speed":0.16151,"descend.descend_speed":0.06496,"push_channel.push_distance_m":0.20357,"push_channel.push_speed":0.03095,"retract.retract_speed":0.14684},"optimized_scores":{"best_composite_score":-0.17635,"best_fitness_score":0.18365,"best_task_score":0.13877},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":199.0,"contact_point_centroid":[0.50789,0.17835,-1e-05],"force_p95":138.61446,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":578.63243,"mean_force":135.13753,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50543,0.11821,0.05632]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":52.0,"contact_point_centroid":[0.52501,0.11969,0.03152],"force_p95":522.31554,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":568.62155,"mean_force":150.53852,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50592,0.07978,0.05601]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":694.0,"contact_point_centroid":[0.47496,0.11994,0.05363],"force_p95":224.06995,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":302.12946,"mean_force":208.16031,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50897,0.08069,0.05364]},{"body_a":"world","body_b":"link7","contact_count":84.0,"contact_point_centroid":[0.50813,0.21392,-0.00028],"force_p95":274.88292,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":295.01476,"mean_force":244.688,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50601,0.15318,0.05515]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":998.0,"contact_point_centroid":[0.47497,0.11995,0.05956],"force_p95":245.82263,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":275.30233,"mean_force":208.34557,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.513,0.08352,0.04436]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":770.0,"contact_point_centroid":[0.52502,0.0852,0.04356],"force_p95":135.64642,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":145.22673,"mean_force":118.96819,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51311,0.08397,0.04321]},{"body_a":"attachment","body_b":"peg","contact_count":772.0,"contact_point_centroid":[0.50639,0.08393,0.04245],"force_p95":29.97133,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.86388,"mean_force":3.73901,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50832,0.08398,0.05414]},{"body_a":"peg","body_b":"channel_base_body","contact_count":990.0,"contact_point_centroid":[0.50673,0.06368,0.00987],"force_p95":28.08914,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.63103,"mean_force":3.30934,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50791,0.0919,0.05445]},{"body_a":"attachment","body_b":"peg","contact_count":982.0,"contact_point_centroid":[0.50677,0.08067,0.05068],"force_p95":1.13443,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.16118,"mean_force":0.63251,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.513,0.08354,0.04432]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50854,0.04853,0.00998],"force_p95":1.52165,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.6654,"mean_force":0.99064,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.513,0.08352,0.04438]},{"body_a":"peg","body_b":"channel_base_body","contact_count":506.0,"contact_point_centroid":[0.50563,0.10471,0.00937],"force_p95":0.57747,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56868,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50454,0.19649,0.21156]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.5042,0.21902,0.2903]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":398.0,"contact_point_centroid":[0.52501,0.05505,0.06],"force_p95":0.60847,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.84394,"mean_force":0.23987,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50887,0.08067,0.05372]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":268.0,"contact_point_centroid":[0.52501,0.06129,0.06],"force_p95":0.25204,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66602,"mean_force":0.09922,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51296,0.08323,0.04511]},{"body_a":"peg","body_b":"channel_base_body","contact_count":342.0,"contact_point_centroid":[0.50594,0.10447,0.00939],"force_p95":0.57566,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57647,"mean_force":0.54634,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.5111,0.16492,0.08669]}],"total_contact_groups":15},"final_pose_error":0.25982,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50684,0.06303,0.03546],"final_tcp_position":[0.51309,0.08524,0.04048],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":578.63243,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":533.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.1046,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.53607,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":538.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_approach","tcp_end":[0.51995,0.18431,0.13896],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13267,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":342.0,"n_steps_budget":720.0,"object_pos_end":[0.50584,0.10459,0.03384],"object_pos_start":[0.50599,0.1046,0.03384],"object_to_goal_dist_end":0.18479,"object_to_goal_dist_start":0.1848,"object_z_max":0.03384,"peak_contact_force":269.76074,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":426.0,"raw_peak_contact_force":295.01476,"tcp_end":[0.50565,0.15411,0.05659],"tcp_start":[0.51995,0.18431,0.13896],"tcp_to_object_dist_end":0.0545,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50668,0.06348,0.03865],"object_pos_start":[0.50584,0.10459,0.03384],"object_to_goal_dist_end":0.14364,"object_to_goal_dist_start":0.18479,"object_z_max":0.04002,"peak_contact_force":225.10613,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3105.0,"raw_peak_contact_force":578.63243,"subtask_id":"reach_push","tcp_end":[0.51191,0.08158,0.05127],"tcp_start":[0.50565,0.15411,0.05659],"tcp_to_object_dist_end":0.02267,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50684,0.06303,0.03546],"object_pos_start":[0.50668,0.06348,0.03865],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14364,"object_z_max":0.03865,"peak_contact_force":168.59484,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4018.0,"raw_peak_contact_force":275.30233,"tcp_end":[0.51309,0.08524,0.04048],"tcp_start":[0.51191,0.08158,0.05127],"tcp_to_object_dist_end":0.02361,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b230a5798f38c3fb8968a6bc74f96ee85fe7026f3170cf8216fc868a1c5c570f`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58434,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height_offset_z":0.09304,"approach.approach_speed":0.14779,"descend.descend_speed":0.06543,"push_channel.push_distance_m":0.19294,"push_channel.push_speed":0.02682,"retract.retract_speed":0.13961},"optimized_scores":{"best_composite_score":-0.22052,"best_fitness_score":0.13948,"best_task_score":0.02872},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":302.0,"contact_point_centroid":[0.49978,0.15104,-1e-05],"force_p95":132.05412,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":717.38247,"mean_force":92.83774,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50089,0.08968,0.05491]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":834.0,"contact_point_centroid":[0.46968,0.11991,0.04818],"force_p95":243.19505,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":672.40327,"mean_force":214.67032,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50102,0.08173,0.05458]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":999.0,"contact_point_centroid":[0.46827,0.11995,0.05996],"force_p95":180.07169,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":460.78979,"mean_force":175.07727,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50212,0.08574,0.04554]},{"body_a":"world","body_b":"link7","contact_count":86.0,"contact_point_centroid":[0.50149,0.17734,-0.00028],"force_p95":326.14606,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":343.64214,"mean_force":279.57935,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49946,0.117,0.05557]},{"body_a":"world","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.49793,0.14643,-2e-05],"force_p95":244.75656,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":245.59596,"mean_force":123.03327,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.5022,0.08342,0.05298]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.52504,0.11966,0.03873],"force_p95":196.08043,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":198.35842,"mean_force":55.43816,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49942,0.07988,0.05707]},{"body_a":"attachment","body_b":"peg","contact_count":218.0,"contact_point_centroid":[0.50282,0.08084,0.04446],"force_p95":11.16618,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.7804,"mean_force":2.50645,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49998,0.08104,0.0561]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50443,0.05976,0.00952],"force_p95":1.35342,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.6289,"mean_force":1.04122,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50073,0.0849,0.05504]},{"body_a":"peg","body_b":"channel_base_body","contact_count":516.0,"contact_point_centroid":[0.50308,0.0675,0.00934],"force_p95":0.55678,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56331,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49545,0.18163,0.21439]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50354,0.06293,0.00937],"force_p95":0.64051,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64624,"mean_force":0.54651,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50212,0.08574,0.04554]},{"body_a":"peg","body_b":"channel_base_body","contact_count":371.0,"contact_point_centroid":[0.50309,0.06737,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55092,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49923,0.12957,0.0883]}],"total_contact_groups":11},"final_pose_error":0.26202,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50357,0.06287,0.03378],"final_tcp_position":[0.50295,0.08791,0.04027],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":717.38247,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":532.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54533,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":516.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_approach","tcp_end":[0.50047,0.1504,0.142],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13638,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":371.0,"n_steps_budget":750.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":307.12579,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":457.0,"raw_peak_contact_force":343.64214,"tcp_end":[0.49924,0.11844,0.05748],"tcp_start":[0.50047,0.1504,0.142],"tcp_to_object_dist_end":0.05637,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50356,0.06283,0.03377],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14301,"object_to_goal_dist_start":0.14759,"object_z_max":0.03707,"peak_contact_force":0.98316,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2387.0,"raw_peak_contact_force":717.38247,"subtask_id":"reach_push","tcp_end":[0.50222,0.08337,0.05303],"tcp_start":[0.49924,0.11844,0.05748],"tcp_to_object_dist_end":0.02819,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50357,0.06287,0.03378],"object_pos_start":[0.50356,0.06283,0.03377],"object_to_goal_dist_end":0.14305,"object_to_goal_dist_start":0.14301,"object_z_max":0.03379,"peak_contact_force":174.51878,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2005.0,"raw_peak_contact_force":460.78979,"tcp_end":[0.50295,0.08791,0.04027],"tcp_start":[0.50222,0.08337,0.05303],"tcp_to_object_dist_end":0.02588,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```