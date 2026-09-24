## Search State

- **Seed**: 7
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.1370 | 0.30 | ❌ rejected |
| 6 | align → approach → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2459 | 0.00 | ❌ rejected |
| 5 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | -0.2272 | 0.00 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | -0.1136 | 0.00 | ❌ rejected |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | -0.1686 | 0.00 | ❌ rejected |

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

## Current Skill (Q=0.137) — your mutation base

```yaml
skill: peg_channel
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: admittance_control
  termination: force_exceeded
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
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
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.137
- **task_score** (E): 0.298
- **fitness_score**: 0.410  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.1731 |
| approach_1 | 1.00 | 1.00 | 0.1051 |
| contact_1 | 0.67 | 1.00 | 0.0009 |
| push_1 | 1.00 | 1.00 | 0.0973 |
| retract_1 | 1.00 | 1.00 | 0.0805 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.123, 0.147) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.534 | 2.732 |
| approach_1 | approach | 1.00 / step_budget | (0.505, 0.123, 0.147)→(0.505, 0.123, 0.043) | (0.502, 0.098, 0.034)→(0.502, 0.086, 0.028) | 0.178→0.167 | 1.00 / 2.000 | 80.320 | 229.215 |
| contact_1 | contact | 0.67 / force_exceeded | (0.505, 0.123, 0.043)→(0.505, 0.123, 0.043) | (0.502, 0.086, 0.028)→(0.502, 0.087, 0.028) | 0.167→0.167 | 1.00 / 2.000 | 77.001 | 78.840 |
| push_1 | push | 1.00 / time_limit | (0.505, 0.123, 0.043)→(0.502, 0.026, 0.041) | (0.502, 0.087, 0.028)→(0.494, 0.032, 0.031) | 0.167→0.113 | 1.00 / 2.333 | 27.254 | 107.171 |
| retract_1 | retract | 1.00 / step_budget | (0.502, 0.026, 0.041)→(0.499, 0.026, 0.121) | (0.494, 0.032, 0.031)→(0.501, 0.024, 0.031) | 0.113→0.105 | 1.00 / 1.000 | 0.629 | 42.862 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.390
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.390
- phase_score: 0.397
- phase_breakdown.reach_prepush_score: 0.821
- phase_breakdown.push_through_score: 0.216

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.523
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.390
- **Median Q (composite search score)**: 0.124
- **K-run variance**: 0.0026
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.325


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.70892,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.speed":0.09823,"approach_1.speed":0.01992,"contact_1.contact_force_threshold":3.81832,"contact_1.speed":0.01957,"push_1.push_distance":0.10042,"push_1.speed":0.02444,"retract_1.speed":0.08116},"optimized_scores":{"best_composite_score":0.20448,"best_fitness_score":0.39448,"best_task_score":0.39033},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50863,0.11545,0.00866],"force_p95":169.8327,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":182.65961,"mean_force":57.67563,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50456,0.13482,0.07857]},{"body_a":"attachment","body_b":"peg","contact_count":479.0,"contact_point_centroid":[0.51429,0.12689,0.05288],"force_p95":175.68778,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":182.26186,"mean_force":119.31904,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50703,0.13573,0.05169]},{"body_a":"attachment","body_b":"peg","contact_count":1000.0,"contact_point_centroid":[0.51441,0.09887,0.05314],"force_p95":143.90409,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":149.49157,"mean_force":125.75807,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51234,0.1027,0.05093]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.51106,0.09383,0.00785],"force_p95":140.87851,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":145.57727,"mean_force":123.76349,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51234,0.1027,0.05093]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":660.0,"contact_point_centroid":[0.52501,0.09562,0.06],"force_p95":108.93083,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":135.08189,"mean_force":60.41844,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51217,0.09674,0.05096]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52126,0.11934,0.00697],"force_p95":123.96501,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":123.96501,"mean_force":123.96501,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51031,0.13866,0.04706]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51536,0.12851,0.04958],"force_p95":123.20125,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":123.20125,"mean_force":123.20125,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51031,0.13866,0.04706]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":79.0,"contact_point_centroid":[0.47411,0.07583,0.05766],"force_p95":106.23645,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":120.44198,"mean_force":37.24252,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51113,0.05689,0.06248]},{"body_a":"attachment","body_b":"peg","contact_count":70.0,"contact_point_centroid":[0.50339,0.06455,0.06197],"force_p95":89.76561,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":100.31538,"mean_force":35.0688,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51124,0.05687,0.06083]},{"body_a":"peg","body_b":"channel_base_body","contact_count":183.0,"contact_point_centroid":[0.4964,0.06951,0.00957],"force_p95":21.57153,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":81.33646,"mean_force":4.34873,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50923,0.05771,0.09577]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":408.0,"contact_point_centroid":[0.47452,0.08055,0.01436],"force_p95":32.00352,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.76535,"mean_force":19.59313,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5117,0.07682,0.05038]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":48.0,"contact_point_centroid":[0.52502,0.1157,0.05593],"force_p95":6.33986,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.94662,"mean_force":4.26743,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51412,0.13453,0.05184]},{"body_a":"peg","body_b":"channel_base_body","contact_count":490.0,"contact_point_centroid":[0.50359,0.11166,0.00938],"force_p95":0.61584,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55952,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50241,0.16722,0.22054]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.52515,0.0588,0.03577],"force_p95":1.37319,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.37969,"mean_force":0.68469,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5099,0.05718,0.08717]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49982,0.19922,0.29884]}],"total_contact_groups":15},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50639,0.04932,0.03445],"final_tcp_position":[0.50854,0.05804,0.13062],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":182.65961,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":512.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11173,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.53731,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":506.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_prepush","tcp_end":[0.50627,0.1365,0.14793],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11682,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50574,0.11541,0.03028],"object_pos_start":[0.50375,0.11173,0.0338],"object_to_goal_dist_end":0.19573,"object_to_goal_dist_start":0.19187,"object_z_max":0.03412,"peak_contact_force":104.96107,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1479.0,"raw_peak_contact_force":182.65961,"subtask_id":"reach_prepush","tcp_end":[0.51031,0.13866,0.04706],"tcp_start":[0.50627,0.1365,0.14793],"tcp_to_object_dist_end":0.02903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50574,0.11542,0.03028],"object_pos_start":[0.50574,0.11541,0.03028],"object_to_goal_dist_end":0.19575,"object_to_goal_dist_start":0.19573,"object_z_max":0.03028,"peak_contact_force":123.96501,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":123.96501,"subtask_id":"reach_prepush","tcp_end":[0.51032,0.13869,0.04706],"tcp_start":[0.51031,0.13866,0.04706],"tcp_to_object_dist_end":0.02905,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49181,0.07299,0.03052],"object_pos_start":[0.50574,0.11542,0.03028],"object_to_goal_dist_end":0.1535,"object_to_goal_dist_start":0.19575,"object_z_max":0.03219,"peak_contact_force":79.79423,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3116.0,"raw_peak_contact_force":149.49157,"subtask_id":"push_through","tcp_end":[0.51157,0.05848,0.05014],"tcp_start":[0.51032,0.13869,0.04706],"tcp_to_object_dist_end":0.0314,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":246.0,"n_steps_budget":780.0,"object_pos_end":[0.50639,0.04932,0.03445],"object_pos_start":[0.49181,0.07299,0.03052],"object_to_goal_dist_end":0.1296,"object_to_goal_dist_start":0.1535,"object_z_max":0.04487,"peak_contact_force":0.78569,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":349.0,"raw_peak_contact_force":120.44198,"tcp_end":[0.50854,0.05804,0.13062],"tcp_start":[0.51157,0.05848,0.05014],"tcp_to_object_dist_end":0.0966,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46835,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.speed":0.07771,"approach_1.speed":0.04698,"contact_1.contact_force_threshold":2.64983,"contact_1.speed":0.0135,"push_1.push_distance":0.16648,"push_1.speed":0.03235,"retract_1.speed":0.087},"optimized_scores":{"best_composite_score":0.12363,"best_fitness_score":0.31363,"best_task_score":0.23153},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":277.0,"contact_point_centroid":[0.5006,0.13426,0.0513],"force_p95":174.39426,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":188.96203,"mean_force":104.07406,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49494,0.14361,0.0504]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50681,0.09468,0.00759],"force_p95":158.06072,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":163.54953,"mean_force":118.15022,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50503,0.09816,0.04854]},{"body_a":"attachment","body_b":"peg","contact_count":893.0,"contact_point_centroid":[0.51096,0.10304,0.05127],"force_p95":157.8727,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":163.0244,"mean_force":134.42365,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50566,0.10452,0.04936]},{"body_a":"peg","body_b":"channel_base_body","contact_count":822.0,"contact_point_centroid":[0.49799,0.11918,0.00886],"force_p95":126.02441,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":159.22334,"mean_force":31.52808,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48878,0.14184,0.08525]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50248,0.13808,0.046],"force_p95":106.31851,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":106.31851,"mean_force":106.31851,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49966,0.1484,0.04359]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51724,0.11863,0.00702],"force_p95":73.85414,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.85414,"mean_force":73.85414,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49966,0.1484,0.04359]},{"body_a":"peg","body_b":"world","contact_count":114.0,"contact_point_centroid":[0.49934,0.13012,-0.00036],"force_p95":49.84442,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.35472,"mean_force":31.74723,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49795,0.14613,0.04597]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":415.0,"contact_point_centroid":[0.47467,0.08054,0.01565],"force_p95":31.57857,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.96998,"mean_force":13.28219,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50522,0.06486,0.04775]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.50048,0.12896,-0.00065],"force_p95":35.63637,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.63637,"mean_force":35.63637,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49966,0.1484,0.04359]},{"body_a":"peg","body_b":"world","contact_count":82.0,"contact_point_centroid":[0.5008,0.12854,-0.00025],"force_p95":28.07919,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.28636,"mean_force":16.86105,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50077,0.1489,0.04556]},{"body_a":"peg","body_b":"channel_base_body","contact_count":478.0,"contact_point_centroid":[0.4962,0.11912,0.00945],"force_p95":0.61743,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55399,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49134,0.17056,0.22063]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49948,0.19895,0.29783]},{"body_a":"peg","body_b":"channel_base_body","contact_count":247.0,"contact_point_centroid":[0.49368,0.07829,0.00941],"force_p95":0.60524,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64964,"mean_force":0.54619,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49401,0.03829,0.07782]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":91.0,"contact_point_centroid":[0.47498,0.07832,0.05882],"force_p95":0.10666,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12674,"mean_force":0.02252,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49404,0.0383,0.07645]}],"total_contact_groups":14},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49301,0.07834,0.03378],"final_tcp_position":[0.49378,0.03835,0.11917],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":188.96203,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":503.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.11923,0.03388],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19936,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52045,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":502.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_prepush","tcp_end":[0.48454,0.14327,0.14872],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11789,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":822.0,"n_steps_budget":1000.0,"object_pos_end":[0.50047,0.12303,0.02893],"object_pos_start":[0.49603,0.11923,0.03388],"object_to_goal_dist_end":0.20333,"object_to_goal_dist_start":0.19936,"object_z_max":0.03404,"peak_contact_force":134.74804,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1213.0,"raw_peak_contact_force":188.96203,"subtask_id":"reach_prepush","tcp_end":[0.49966,0.1484,0.04359],"tcp_start":[0.48454,0.14327,0.14872],"tcp_to_object_dist_end":0.02932,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50045,0.12303,0.02893],"object_pos_start":[0.50047,0.12303,0.02893],"object_to_goal_dist_end":0.20334,"object_to_goal_dist_start":0.20333,"object_z_max":0.02893,"peak_contact_force":106.31851,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":106.31851,"subtask_id":"reach_prepush","tcp_end":[0.49964,0.14845,0.04357],"tcp_start":[0.49966,0.1484,0.04359],"tcp_to_object_dist_end":0.02934,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49299,0.07828,0.03424],"object_pos_start":[0.50045,0.12303,0.02893],"object_to_goal_dist_end":0.15854,"object_to_goal_dist_start":0.20334,"object_z_max":0.03436,"peak_contact_force":0.55744,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2390.0,"raw_peak_contact_force":163.54953,"subtask_id":"push_through","tcp_end":[0.49685,0.03866,0.03888],"tcp_start":[0.49964,0.14845,0.04357],"tcp_to_object_dist_end":0.04007,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":247.0,"n_steps_budget":720.0,"object_pos_end":[0.49301,0.07834,0.03378],"object_pos_start":[0.49299,0.07828,0.03424],"object_to_goal_dist_end":0.15862,"object_to_goal_dist_start":0.15854,"object_z_max":0.03424,"peak_contact_force":0.52225,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":338.0,"raw_peak_contact_force":0.64964,"tcp_end":[0.49378,0.03835,0.11917],"tcp_start":[0.49685,0.03866,0.03888],"tcp_to_object_dist_end":0.09429,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14286,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.speed":0.11332,"approach_1.speed":0.03724,"contact_1.contact_force_threshold":2.71414,"contact_1.speed":0.01363,"push_1.push_distance":0.19989,"push_1.speed":0.02051,"retract_1.speed":0.1074},"optimized_scores":{"best_composite_score":0.0829,"best_fitness_score":0.5229,"best_task_score":0.27213},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":73.0,"contact_point_centroid":[0.52506,0.08502,0.05999],"force_p95":260.73187,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.02361,"mean_force":189.14911,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51216,0.0851,0.05288]},{"body_a":"peg","body_b":"channel_base_body","contact_count":642.0,"contact_point_centroid":[0.50932,0.06542,0.00916],"force_p95":123.16418,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":128.74682,"mean_force":31.95227,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51358,0.08617,0.08577]},{"body_a":"attachment","body_b":"peg","contact_count":198.0,"contact_point_centroid":[0.51836,0.07614,0.05539],"force_p95":125.39213,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":128.27146,"mean_force":102.53727,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51073,0.08484,0.05462]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":113.0,"contact_point_centroid":[0.52516,0.06062,0.05406],"force_p95":6.67128,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.94139,"mean_force":3.00861,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51021,0.08468,0.05302]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49723,-0.01017,0.0089],"force_p95":2.08474,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.47065,"mean_force":0.94132,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49963,0.03155,0.03289]},{"body_a":"attachment","body_b":"peg","contact_count":570.0,"contact_point_centroid":[0.49744,0.00676,0.0333],"force_p95":3.04787,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.09413,"mean_force":0.98132,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4993,0.01855,0.0328]},{"body_a":"peg","body_b":"channel_base_body","contact_count":242.0,"contact_point_centroid":[0.5004,-0.057,0.00827],"force_p95":0.68647,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.49567,"mean_force":0.67834,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49608,-0.01896,0.07232]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":88.0,"contact_point_centroid":[0.47499,-0.03362,0.02617],"force_p95":6.55315,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.37903,"mean_force":3.52874,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49949,0.02619,0.03285]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52502,-0.03438,0.02427],"force_p95":7.2008,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.22969,"mean_force":2.65763,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49572,-0.0189,0.1039]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.49983,0.01648,0.00767],"force_p95":1.32938,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.23616,"mean_force":1.0139,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50462,0.08314,0.03773]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52501,0.04069,0.02425],"force_p95":5.04613,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.74506,"mean_force":2.10725,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50473,0.08324,0.03785]},{"body_a":"peg","body_b":"channel_base_body","contact_count":602.0,"contact_point_centroid":[0.50579,0.06295,0.00936],"force_p95":0.56295,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56904,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51191,0.14265,0.21783]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49994,0.19772,0.29656]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":12.0,"contact_point_centroid":[0.47478,0.01591,0.05111],"force_p95":1.75112,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.93897,"mean_force":0.7799,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50809,0.08428,0.04491]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47497,-0.07912,0.02724],"force_p95":1.89686,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92727,"mean_force":0.87537,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49809,-0.01913,0.03365]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.49768,-0.03087,0.03365],"force_p95":1.32796,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.38316,"mean_force":0.83117,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49888,-0.01895,0.03312]}],"total_contact_groups":16},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50434,-0.0571,0.0244],"final_tcp_position":[0.49584,-0.0189,0.11357],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":316.02361,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":630.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.06297,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14322,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54319,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":636.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_prepush","tcp_end":[0.52466,0.08981,0.14493],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11584,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":679.0,"n_steps_budget":1000.0,"object_pos_end":[0.50075,0.01992,0.02533],"object_pos_start":[0.50594,0.06297,0.03381],"object_to_goal_dist_end":0.10099,"object_to_goal_dist_start":0.14322,"object_z_max":0.04229,"peak_contact_force":1.25027,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1038.0,"raw_peak_contact_force":316.02361,"subtask_id":"reach_prepush","tcp_end":[0.50546,0.08342,0.03872],"tcp_start":[0.52466,0.08981,0.14493],"tcp_to_object_dist_end":0.06507,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50055,0.02127,0.02349],"object_pos_start":[0.50075,0.01992,0.02533],"object_to_goal_dist_end":0.10261,"object_to_goal_dist_start":0.10099,"object_z_max":0.02533,"peak_contact_force":0.71822,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":24.0,"raw_peak_contact_force":6.23616,"subtask_id":"reach_prepush","tcp_end":[0.50393,0.08264,0.03691],"tcp_start":[0.50546,0.08342,0.03872],"tcp_to_object_dist_end":0.06291,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49576,-0.05577,0.02735],"object_pos_start":[0.50055,0.02127,0.02349],"object_to_goal_dist_end":0.02766,"object_to_goal_dist_start":0.10261,"object_z_max":0.02736,"peak_contact_force":1.40984,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1658.0,"raw_peak_contact_force":8.47065,"subtask_id":"push_through","tcp_end":[0.49889,-0.01892,0.03313],"tcp_start":[0.50393,0.08264,0.03691],"tcp_to_object_dist_end":0.03743,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":242.0,"n_steps_budget":600.0,"object_pos_end":[0.50434,-0.0571,0.0244],"object_pos_start":[0.49576,-0.05577,0.02735],"object_to_goal_dist_end":0.02804,"object_to_goal_dist_start":0.02766,"object_z_max":0.02735,"peak_contact_force":0.57883,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":258.0,"raw_peak_contact_force":7.49567,"tcp_end":[0.49584,-0.0189,0.11357],"tcp_start":[0.49889,-0.01892,0.03313],"tcp_to_object_dist_end":0.09738,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```