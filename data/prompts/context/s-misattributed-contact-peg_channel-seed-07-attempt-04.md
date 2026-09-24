## Search State

- **Seed**: 7
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.0296 | 0.24 | ❌ rejected |
| 3 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1314 | 0.00 | ❌ rejected |
| 2 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.0772 | 0.10 | ❌ rejected |
| 1 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1314 | 0.26 | ❌ rejected |
| 0 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1315 | 0.26 | ✅ accepted |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`
- Frozen object start: [0.5100076373283734, 0.11177710407756605, 0.04]
- Frozen task target: [0.5100076373283734, -0.04822289592243395, 0.04]
- Goal object position: (0.5100076373283734, -0.04822289592243395, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5100076373283734, 0.11177710407756605, 0.04)
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
  frozen_object_start: [0.51, 0.1118, 0.04]
  frozen_task_target: [0.51, -0.0482, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5100076373283734, 0.11177710407756605, 0.04]}
  frozen_targets: {'channel_exit': [0.5100076373283734, -0.04822289592243395, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415

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
| `object` | offset from object initial position (0.5100076373283734, 0.11177710407756605, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5100076373283734, -0.04822289592243395, 0.04) | final destination targets |
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

## Current Skill (Q=-0.030) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: insert_1
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: pose_tolerance
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
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
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

```

## Design Metrics

- **Composite score**: -0.030
- **task_score** (E): 0.238
- **fitness_score**: 0.250  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2567 |
| push_channel | 0.33 | 1.00 | 0.0391 |
| retract_upward | 1.00 | 1.00 | 0.1218 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.504, 0.133, 0.054) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.667 | 18.307 | 49.484 |
| push_channel | push | 0.33 / guard_failure | (0.503, 0.126, 0.053)→(0.502, 0.087, 0.051) | (0.502, 0.098, 0.034)→(0.500, 0.066, 0.033) | 0.178→0.146 | 1.00 / 1.000 | 0.624 | 87.867 |
| retract_upward | retract | 1.00 / step_budget | (0.502, 0.087, 0.051)→(0.499, 0.086, 0.173) | (0.501, 0.066, 0.033)→(0.504, 0.054, 0.027) | 0.146→0.135 | 1.00 / 1.333 | 106.469 | 121.266 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.532
- alignment_error: None
- force_efficiency: 0.442
- terminal_score: 0.532
- phase_score: 0.329
- phase_breakdown.behind_peg_score: 0.822
- phase_breakdown.push_goal_score: 0.118

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.410
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.532
- **Median Q (composite search score)**: -0.053
- **K-run variance**: 0.0149
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.226


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40136,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.11537,"push_channel.push_distance":0.13198,"push_channel.push_speed":0.04105,"push_channel.push_tolerance":0.00776,"retract_upward.retract_speed":0.06595},"optimized_scores":{"best_composite_score":0.13027,"best_fitness_score":0.41027,"best_task_score":0.53192},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.4998,0.05822,0.00936],"force_p95":26.20575,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.89523,"mean_force":10.08065,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50226,0.0845,0.04435]},{"body_a":"attachment","body_b":"peg","contact_count":716.0,"contact_point_centroid":[0.50419,0.0882,0.044],"force_p95":26.07115,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.51294,"mean_force":13.39611,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50242,0.09978,0.04452]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50395,0.02722,0.00806],"force_p95":0.68548,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.9156,"mean_force":0.65852,"phase_index":2.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49796,0.0266,0.09782]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47497,0.05203,0.02431],"force_p95":9.44805,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.51542,"mean_force":2.96031,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50149,0.03861,0.04354]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.52501,0.01515,0.02426],"force_p95":9.38131,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.40551,"mean_force":3.28335,"phase_index":2.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49798,0.02663,0.12361]},{"body_a":"peg","body_b":"channel_base_body","contact_count":754.0,"contact_point_centroid":[0.5036,0.11168,0.00937],"force_p95":0.60833,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55527,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50202,0.171,0.17035]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49974,0.19941,0.29885]}],"total_contact_groups":7},"final_pose_error":0.04138,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50655,0.02667,0.02413],"final_tcp_position":[0.49819,0.02664,0.15225],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":27.89523,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":776.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11175,0.03384],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.58979,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1723.0,"raw_peak_contact_force":27.89523,"subtask_id":"behind_peg","tcp_end":[0.50558,0.14378,0.04849],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03527,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49566,0.02734,0.02414],"object_pos_start":[0.50373,0.11175,0.03384],"object_to_goal_dist_end":0.10859,"object_to_goal_dist_start":0.19188,"object_z_max":0.04047,"peak_contact_force":0.68361,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1018.0,"raw_peak_contact_force":9.9156,"subtask_id":"push_goal","tcp_end":[0.50143,0.02687,0.04351],"tcp_start":[0.50558,0.14378,0.04849],"tcp_to_object_dist_end":0.02021,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50655,0.02667,0.02413],"object_pos_start":[0.49566,0.02734,0.02414],"object_to_goal_dist_end":0.10804,"object_to_goal_dist_start":0.10859,"object_z_max":0.02465,"peak_contact_force":0.52755,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":770.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.49819,0.02664,0.15225],"tcp_start":[0.50143,0.02687,0.04351],"tcp_to_object_dist_end":0.1284,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79339,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.07267,"push_channel.push_distance":0.05777,"push_channel.push_speed":0.07119,"push_channel.push_tolerance":0.01917,"retract_upward.retract_speed":0.10422},"optimized_scores":{"best_composite_score":-0.05333,"best_fitness_score":0.22667,"best_task_score":0.18094},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":72.0,"contact_point_centroid":[0.47495,0.11993,0.05354],"force_p95":166.62861,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":186.11529,"mean_force":83.34965,"phase_index":2.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.47834,0.13102,0.05162]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47487,0.11982,0.04854],"force_p95":56.48167,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.26577,"mean_force":22.23018,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48034,0.12983,0.04558]},{"body_a":"peg","body_b":"channel_base_body","contact_count":51.0,"contact_point_centroid":[0.50151,0.10786,0.0095],"force_p95":11.60355,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.37234,"mean_force":1.98909,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48136,0.14256,0.047]},{"body_a":"attachment","body_b":"peg","contact_count":17.0,"contact_point_centroid":[0.48964,0.12695,0.04946],"force_p95":14.49203,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.73641,"mean_force":4.6452,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48079,0.13639,0.04624]},{"body_a":"peg","body_b":"channel_base_body","contact_count":811.0,"contact_point_centroid":[0.4995,0.07679,0.00847],"force_p95":0.74505,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.85489,"mean_force":0.61311,"phase_index":2.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.47722,0.129,0.11377]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":12.0,"contact_point_centroid":[0.47491,0.09297,0.02426],"force_p95":6.49823,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.71817,"mean_force":1.85527,"phase_index":2.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.47681,0.1286,0.08406]},{"body_a":"peg","body_b":"channel_base_body","contact_count":768.0,"contact_point_centroid":[0.49621,0.11905,0.00941],"force_p95":0.60932,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55205,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49059,0.17444,0.17053]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.525,0.06963,0.04914],"force_p95":1.36742,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.52205,"mean_force":0.68853,"phase_index":2.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.47635,0.13025,0.06589]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49948,0.19924,0.29772]}],"total_contact_groups":9},"final_pose_error":0.012,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50089,0.07189,0.02415],"final_tcp_position":[0.47759,0.1286,0.18382],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":186.11529,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":793.0,"n_steps_budget":1000.0,"object_pos_end":[0.49599,0.11918,0.03387],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19931,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.0,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":71.0,"raw_peak_contact_force":62.26577,"subtask_id":"behind_peg","tcp_end":[0.48313,0.15062,0.04915],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03725,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":59.0,"n_steps_budget":600.0,"object_pos_end":[0.49978,0.10764,0.04005],"object_pos_start":[0.49599,0.11918,0.03387],"object_to_goal_dist_end":0.18764,"object_to_goal_dist_start":0.19931,"object_z_max":0.0401,"peak_contact_force":0.64363,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":899.0,"raw_peak_contact_force":186.11529,"subtask_id":"push_goal","tcp_end":[0.48034,0.12932,0.04548],"tcp_start":[0.48034,0.12953,0.04554],"tcp_to_object_dist_end":0.02962,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":820.0,"n_steps_budget":900.0,"object_pos_end":[0.50089,0.07189,0.02415],"object_pos_start":[0.50001,0.10693,0.03983],"object_to_goal_dist_end":0.15272,"object_to_goal_dist_start":0.18693,"object_z_max":0.04079,"peak_contact_force":0.5966,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":792.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.47759,0.1286,0.18382],"tcp_start":[0.48034,0.12932,0.04548],"tcp_to_object_dist_end":0.17103,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83838,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.09961,"push_channel.push_distance":0.11425,"push_channel.push_speed":0.04241,"push_channel.push_tolerance":0.01128,"retract_upward.retract_speed":0.07208},"optimized_scores":{"best_composite_score":-0.16572,"best_fitness_score":0.11428,"best_task_score":0.00012},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":115.0,"contact_point_centroid":[0.53491,0.1037,0.05978],"force_p95":346.34011,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":359.48773,"mean_force":318.3367,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52378,0.10378,0.06404]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.53567,0.10371,0.05995],"force_p95":65.89089,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":67.57028,"mean_force":58.79422,"phase_index":2.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.52463,0.10372,0.06461]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.53557,0.10371,0.05993],"force_p95":57.99808,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":58.29025,"mean_force":55.99696,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.52453,0.10372,0.06457]},{"body_a":"peg","body_b":"channel_base_body","contact_count":892.0,"contact_point_centroid":[0.50585,0.06296,0.00937],"force_p95":0.55578,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56173,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51234,0.1444,0.16235]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.4998,0.19833,0.29608]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50605,0.06298,0.00938],"force_p95":0.55181,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54651,"phase_index":2.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.52133,0.10306,0.12345]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49092,0.06826,0.00939],"force_p95":0.5486,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54877,"mean_force":0.54575,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.52453,0.10372,0.06457]}],"total_contact_groups":7},"final_pose_error":0.0318,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50594,0.0629,0.03385],"final_tcp_position":[0.52166,0.10313,0.18292],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":359.48773,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":920.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.06297,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":54.33206,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6.0,"raw_peak_contact_force":58.29025,"subtask_id":"behind_peg","tcp_end":[0.52448,0.10371,0.06456],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05431,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.063,0.03381],"object_pos_start":[0.50594,0.06297,0.03381],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14323,"object_z_max":0.03381,"peak_contact_force":0.54444,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1004.0,"raw_peak_contact_force":67.57028,"subtask_id":"push_goal","tcp_end":[0.5246,0.10373,0.06458],"tcp_start":[0.52457,0.10372,0.06457],"tcp_to_object_dist_end":0.05434,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.0629,0.03385],"object_pos_start":[0.50599,0.06303,0.03381],"object_to_goal_dist_end":0.14315,"object_to_goal_dist_start":0.14329,"object_z_max":0.03385,"peak_contact_force":318.28198,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1041.0,"raw_peak_contact_force":359.48773,"tcp_end":[0.52166,0.10313,0.18292],"tcp_start":[0.5246,0.10373,0.06458],"tcp_to_object_dist_end":0.1552,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```