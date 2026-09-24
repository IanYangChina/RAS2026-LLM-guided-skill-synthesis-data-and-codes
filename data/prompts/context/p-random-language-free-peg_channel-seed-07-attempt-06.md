## Search State

- **Seed**: 7
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | descend → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2759 | 0.00 | ❌ rejected |
| 5 | descend → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.0821 | 0.24 | ❌ rejected |
| 4 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1314 | 0.26 | ❌ rejected |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0714 | 0.00 | ❌ rejected |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 4 | 0.1780 | 0.00 | ❌ rejected |

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

## Current Skill (Q=-0.276) — your mutation base

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

- **Composite score**: -0.276
- **task_score** (E): 0.003
- **fitness_score**: 0.054  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_to_peg | 1.00 | 1.00 | 0.1726 |
| approach_peg | 1.00 | 1.00 | 0.0972 |
| push_channel | 0.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_to_peg | descend | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.110, 0.155) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.540 | 2.732 |
| approach_peg | approach | 1.00 / step_budget | (0.505, 0.110, 0.155)→(0.500, 0.087, 0.061) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 1.333 | 97.580 | 97.664 |
| push_channel | push | 0.00 / guard_failure | (0.499, 0.085, 0.059)→(0.499, 0.085, 0.059) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 2.667 | 57.325 | 67.768 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.109
- phase_breakdown.pre_push_score: 0.194
- phase_breakdown.push_goal_score: 0.072

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.065
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.005
- **Median Q (composite search score)**: -0.281
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.364


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36607,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.04267,"approach_peg.lateral_x":0.00011,"approach_peg.lateral_y":-0.01491,"descend_to_peg.descent_speed":0.08309,"push_channel.push_speed":0.07244,"push_channel.push_stroke":0.15408},"optimized_scores":{"best_composite_score":-0.28063,"best_fitness_score":0.04937,"best_task_score":0.00469},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.49788,0.09843,0.00933],"force_p95":45.33232,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.68363,"mean_force":27.71005,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50044,0.10077,0.05946]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.51221,0.10108,0.05815],"force_p95":45.15019,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.07775,"mean_force":29.86925,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50037,0.10069,0.05932]},{"body_a":"peg","body_b":"channel_base_body","contact_count":299.0,"contact_point_centroid":[0.50359,0.11161,0.00934],"force_p95":0.68472,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.57088,"phase_index":0.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50275,0.15967,0.22374]},{"body_a":"peg","body_b":"channel_base_body","contact_count":199.0,"contact_point_centroid":[0.50335,0.11182,0.00942],"force_p95":0.59264,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64993,"mean_force":0.54313,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50311,0.11238,0.10953]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49992,0.19899,0.2986]}],"total_contact_groups":5},"final_pose_error":0.14306,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5036,0.11097,0.03409],"final_tcp_position":[0.49998,0.09946,0.05864],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":49.68363,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":321.0,"n_steps_budget":1000.0,"object_pos_end":[0.50369,0.11179,0.03386],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.54052,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":315.0,"raw_peak_contact_force":2.06328,"subtask_id":"pre_push","tcp_end":[0.50618,0.1226,0.15584],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":199.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11176,0.03385],"object_pos_start":[0.50369,0.11179,0.03386],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19192,"object_z_max":0.03389,"peak_contact_force":0.48684,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":199.0,"raw_peak_contact_force":0.64993,"subtask_id":"pre_push","tcp_end":[0.50119,0.10157,0.06083],"tcp_start":[0.50618,0.1226,0.15584],"tcp_to_object_dist_end":0.02895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":11.0,"n_steps_budget":1000.0,"object_pos_end":[0.50351,0.1112,0.03396],"object_pos_start":[0.50371,0.11176,0.03385],"object_to_goal_dist_end":0.19133,"object_to_goal_dist_start":0.19189,"object_z_max":0.03404,"peak_contact_force":23.02393,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":21.0,"raw_peak_contact_force":49.68363,"subtask_id":"push_goal","tcp_end":[0.49998,0.09946,0.05864],"tcp_start":[0.5,0.09963,0.05871],"tcp_to_object_dist_end":0.02755,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16667,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.08665,"approach_peg.lateral_x":-0.00795,"approach_peg.lateral_y":-0.01386,"descend_to_peg.descent_speed":0.0393,"push_channel.push_speed":0.07172,"push_channel.push_stroke":0.12885},"optimized_scores":{"best_composite_score":-0.28235,"best_fitness_score":0.04765,"best_task_score":0.00364},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.475,0.09917,0.05997],"force_p95":61.86615,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.09959,"mean_force":59.76513,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4835,0.10749,0.0587]},{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.48865,0.11135,0.00933],"force_p95":38.38025,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.36526,"mean_force":20.13856,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48381,0.10854,0.05948]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.49557,0.1089,0.05818],"force_p95":38.42541,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.70458,"mean_force":21.50064,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48374,0.10845,0.05934]},{"body_a":"peg","body_b":"channel_base_body","contact_count":300.0,"contact_point_centroid":[0.49644,0.11917,0.00943],"force_p95":0.64652,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56312,"phase_index":0.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49199,0.16314,0.22436]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49942,0.19866,0.29763]},{"body_a":"peg","body_b":"channel_base_body","contact_count":193.0,"contact_point_centroid":[0.49607,0.11907,0.00943],"force_p95":0.60012,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62754,"mean_force":0.54333,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48454,0.11953,0.1098]}],"total_contact_groups":6},"final_pose_error":0.1197,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49581,0.11825,0.03402],"final_tcp_position":[0.48349,0.1072,0.0586],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":62.09959,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.49599,0.11902,0.03417],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19915,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52957,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":324.0,"raw_peak_contact_force":2.24822,"subtask_id":"pre_push","tcp_end":[0.48563,0.12932,0.1571],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":193.0,"n_steps_budget":870.0,"object_pos_end":[0.49606,0.11905,0.03392],"object_pos_start":[0.49599,0.11902,0.03417],"object_to_goal_dist_end":0.19918,"object_to_goal_dist_start":0.19915,"object_z_max":0.03417,"peak_contact_force":0.53975,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":193.0,"raw_peak_contact_force":0.62754,"subtask_id":"pre_push","tcp_end":[0.48452,0.10936,0.06093],"tcp_start":[0.48563,0.12932,0.1571],"tcp_to_object_dist_end":0.03094,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":11.0,"n_steps_budget":1000.0,"object_pos_end":[0.49574,0.11847,0.03393],"object_pos_start":[0.49606,0.11905,0.03392],"object_to_goal_dist_end":0.19861,"object_to_goal_dist_start":0.19918,"object_z_max":0.03398,"peak_contact_force":57.43067,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":23.0,"raw_peak_contact_force":62.09959,"subtask_id":"push_goal","tcp_end":[0.48349,0.1072,0.0586],"tcp_start":[0.48349,0.10739,0.05866],"tcp_to_object_dist_end":0.02976,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.93529,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.05891,"approach_peg.lateral_x":0.00927,"approach_peg.lateral_y":-0.01966,"descend_to_peg.descent_speed":0.01898,"push_channel.push_speed":0.05493,"push_channel.push_stroke":0.117},"optimized_scores":{"best_composite_score":-0.26469,"best_fitness_score":0.06531,"best_task_score":0.00017},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52583,0.05004,0.05966],"force_p95":288.35378,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":291.71469,"mean_force":258.10559,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51396,0.05042,0.06108]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52532,0.04985,0.05995],"force_p95":91.06046,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.52006,"mean_force":32.25509,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51347,0.04986,0.05967]},{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.49501,0.05239,0.0094],"force_p95":44.33724,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.39747,"mean_force":23.00123,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51347,0.04986,0.05967]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.52272,0.05716,0.05852],"force_p95":45.04515,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.09696,"mean_force":29.02214,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51334,0.04976,0.05946]},{"body_a":"peg","body_b":"channel_base_body","contact_count":386.0,"contact_point_centroid":[0.50556,0.063,0.00935],"force_p95":0.58397,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.58161,"phase_index":0.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51161,0.136,0.22137]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.5,0.19718,0.29626]},{"body_a":"peg","body_b":"channel_base_body","contact_count":193.0,"contact_point_centroid":[0.50624,0.06305,0.00938],"force_p95":0.5514,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55402,"mean_force":0.54656,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51837,0.06417,0.10718]}],"total_contact_groups":7},"final_pose_error":0.10585,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50553,0.06288,0.03395],"final_tcp_position":[0.51289,0.04941,0.05898],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":291.71469,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":414.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.06303,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.55069,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":420.0,"raw_peak_contact_force":3.88411,"subtask_id":"pre_push","tcp_end":[0.52372,0.07725,0.15205],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":193.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,0.06295,0.03381],"object_pos_start":[0.50602,0.06303,0.0338],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14329,"object_z_max":0.03381,"peak_contact_force":291.71469,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":195.0,"raw_peak_contact_force":291.71469,"subtask_id":"pre_push","tcp_end":[0.51398,0.05026,0.06053],"tcp_start":[0.52372,0.07725,0.15205],"tcp_to_object_dist_end":0.03064,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":9.0,"n_steps_budget":1000.0,"object_pos_end":[0.50567,0.06292,0.03392],"object_pos_start":[0.50601,0.06295,0.03381],"object_to_goal_dist_end":0.14316,"object_to_goal_dist_start":0.14321,"object_z_max":0.03394,"peak_contact_force":91.52006,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":25.0,"raw_peak_contact_force":91.52006,"subtask_id":"push_goal","tcp_end":[0.51289,0.04941,0.05898],"tcp_start":[0.51299,0.04946,0.05907],"tcp_to_object_dist_end":0.02937,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```