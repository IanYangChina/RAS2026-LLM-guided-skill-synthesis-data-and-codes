## Search State

- **Seed**: 7
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.0157 | 0.00 | ❌ rejected |
| 7 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.1370 | 0.30 | ❌ rejected |
| 6 | align → approach → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2459 | 0.00 | ❌ rejected |
| 5 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | -0.2272 | 0.00 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | -0.1136 | 0.00 | ❌ rejected |

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

## Current Skill (Q=0.016) — your mutation base

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

- **Composite score**: 0.016
- **task_score** (E): 0.000
- **fitness_score**: 0.176  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_tcp | 1.00 | 1.00 | 0.1725 |
| descend_to_contact | 1.00 | 1.00 | 0.0883 |
| push_along_channel | 0.33 | 1.00 | 0.0695 |
| retract_after_push | 1.00 | 1.00 | 0.0803 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_tcp | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.110, 0.155) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.540 | 2.732 |
| descend_to_contact | descend | 1.00 / force_exceeded | (0.505, 0.110, 0.155)→(0.499, 0.101, 0.068) | (0.502, 0.098, 0.034)→(0.502, 0.102, 0.033) | 0.178→0.183 | 1.00 / 2.000 | 15.281 | 14.419 |
| push_along_channel | push | 0.33 / guard_failure | (0.499, 0.101, 0.067)→(0.501, 0.035, 0.053) | (0.502, 0.102, 0.033)→(0.504, 0.112, 0.027) | 0.183→0.192 | 1.00 / 1.667 | 117.692 | 118.428 |
| retract_after_push | retract | 1.00 / step_budget | (0.501, 0.035, 0.053)→(0.499, 0.034, 0.133) | (0.504, 0.112, 0.027)→(0.506, 0.112, 0.027) | 0.193→0.193 | 1.00 / 1.000 | 0.534 | 49.863 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.935
- terminal_score: 0.000
- phase_score: 0.679
- phase_breakdown.reach_prepush_score: 0.315
- phase_breakdown.push_through_score: 0.922

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.408
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.096
- **K-run variance**: 0.0269
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at lower bound**: descend_to_contact.contact_force_threshold
- **Final σ (mean)**: 0.266


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53913,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_tcp.speed":0.12739,"descend_to_contact.contact_force_threshold":5.57107,"descend_to_contact.speed":0.03302,"push_along_channel.force_limit_guard":30.70036,"push_along_channel.push_distance":-0.03181,"push_along_channel.speed":0.01616,"retract_after_push.speed":0.14458},"optimized_scores":{"best_composite_score":-0.10457,"best_fitness_score":0.05543,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.51081,0.12,0.00939],"force_p95":165.0732,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":168.5148,"mean_force":117.31365,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5008,0.11412,0.06024]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.5126,0.11291,0.05867],"force_p95":164.90519,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":168.33482,"mean_force":117.01786,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5008,0.11412,0.06024]},{"body_a":"peg","body_b":"channel_base_body","contact_count":250.0,"contact_point_centroid":[0.50171,0.11248,0.0094],"force_p95":0.76074,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":71.96936,"mean_force":1.53074,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49811,0.11479,0.09814]},{"body_a":"attachment","body_b":"peg","contact_count":18.0,"contact_point_centroid":[0.5112,0.11298,0.05873],"force_p95":56.94793,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":71.21224,"mean_force":13.73891,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49965,0.11538,0.05999]},{"body_a":"peg","body_b":"channel_base_body","contact_count":520.0,"contact_point_centroid":[0.50368,0.11159,0.00943],"force_p95":0.59406,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.18163,"mean_force":0.58996,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.5022,0.11789,0.10687]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51253,0.1133,0.05888],"force_p95":24.66209,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.66209,"mean_force":24.66209,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50067,0.11375,0.06061]},{"body_a":"peg","body_b":"channel_base_body","contact_count":289.0,"contact_point_centroid":[0.50348,0.11172,0.00934],"force_p95":0.68765,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.57164,"phase_index":0.0,"phase_name":"align_tcp","phase_type":"align","tcp_position_centroid":[0.5028,0.15955,0.22351]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_tcp","phase_type":"align","tcp_position_centroid":[0.49992,0.19885,0.29833]}],"total_contact_groups":8},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50329,0.11225,0.03386],"final_tcp_position":[0.49802,0.11472,0.13998],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":168.5148,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":311.0,"n_steps_budget":900.0,"object_pos_end":[0.50371,0.11176,0.03396],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.54338,"phase_name":"align_tcp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":305.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_prepush","tcp_end":[0.50622,0.12263,0.15589],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12244,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":520.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11177,0.0339],"object_pos_start":[0.50371,0.11176,0.03396],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19189,"object_z_max":0.03403,"peak_contact_force":25.18163,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":521.0,"raw_peak_contact_force":25.18163,"subtask_id":"reach_prepush","tcp_end":[0.50067,0.11373,0.06045],"tcp_start":[0.50622,0.12263,0.15589],"tcp_to_object_dist_end":0.0268,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.5038,0.11193,0.0339],"object_pos_start":[0.50372,0.11177,0.0339],"object_to_goal_dist_end":0.19207,"object_to_goal_dist_start":0.1919,"object_z_max":0.0339,"peak_contact_force":168.5148,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":168.5148,"subtask_id":"push_through","tcp_end":[0.50087,0.11539,0.05974],"tcp_start":[0.50089,0.11459,0.06001],"tcp_to_object_dist_end":0.02623,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":250.0,"n_steps_budget":600.0,"object_pos_end":[0.50329,0.11225,0.03386],"object_pos_start":[0.50379,0.11263,0.03385],"object_to_goal_dist_end":0.19238,"object_to_goal_dist_start":0.19276,"object_z_max":0.03486,"peak_contact_force":0.53266,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":268.0,"raw_peak_contact_force":71.96936,"tcp_end":[0.49802,0.11472,0.13998],"tcp_start":[0.50087,0.11539,0.05974],"tcp_to_object_dist_end":0.10628,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.99587,"average_solve_count":242.0,"average_success_count":242.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_tcp.speed":0.14902,"descend_to_contact.contact_force_threshold":2.00033,"descend_to_contact.speed":0.01818,"push_along_channel.force_limit_guard":30.82389,"push_along_channel.push_distance":-0.01904,"push_along_channel.speed":0.03583,"retract_after_push.speed":0.11472},"optimized_scores":{"best_composite_score":0.24755,"best_fitness_score":0.40755,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"world","contact_count":558.0,"contact_point_centroid":[0.49797,0.15837,-0.00189],"force_p95":0.77114,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98088,"mean_force":0.61328,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48937,0.02837,0.0588]},{"body_a":"peg","body_b":"channel_base_body","contact_count":269.0,"contact_point_centroid":[0.49644,0.119,0.00938],"force_p95":0.64709,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.57054,"phase_index":0.0,"phase_name":"align_tcp","phase_type":"align","tcp_position_centroid":[0.49213,0.16266,0.22338]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_tcp","phase_type":"align","tcp_position_centroid":[0.49946,0.19809,0.29642]},{"body_a":"peg","body_b":"world","contact_count":228.0,"contact_point_centroid":[0.50592,0.16024,-0.00203],"force_p95":0.77048,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77049,"mean_force":0.60577,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.4938,-0.07932,0.07836]},{"body_a":"peg","body_b":"channel_base_body","contact_count":480.0,"contact_point_centroid":[0.49603,0.11964,0.00945],"force_p95":0.57952,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65319,"mean_force":0.53608,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48573,0.12567,0.11828]},{"body_a":"peg","body_b":"channel_base_body","contact_count":6.0,"contact_point_centroid":[0.47818,0.11986,0.00979],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48767,0.12415,0.08143]}],"total_contact_groups":6},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50946,0.16028,0.01405],"final_tcp_position":[0.49367,-0.07924,0.11979],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":3.23853,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":294.0,"n_steps_budget":780.0,"object_pos_end":[0.49604,0.11908,0.03397],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19921,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52289,"phase_name":"align_tcp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":293.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_prepush","tcp_end":[0.48582,0.12932,0.15706],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":480.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.13258,0.03071],"object_pos_start":[0.49604,0.11908,0.03397],"object_to_goal_dist_end":0.21282,"object_to_goal_dist_start":0.19921,"object_z_max":0.03403,"peak_contact_force":3.23853,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":480.0,"raw_peak_contact_force":0.65319,"subtask_id":"reach_prepush","tcp_end":[0.48815,0.12266,0.08236],"tcp_start":[0.48582,0.12932,0.15706],"tcp_to_object_dist_end":0.05318,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":567.0,"n_steps_budget":1000.0,"object_pos_end":[0.5028,0.16029,0.01404],"object_pos_start":[0.49601,0.13258,0.03071],"object_to_goal_dist_end":0.2417,"object_to_goal_dist_start":0.21282,"object_z_max":0.03071,"peak_contact_force":0.77043,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":564.0,"raw_peak_contact_force":2.98088,"subtask_id":"push_through","tcp_end":[0.49601,-0.07946,0.03953],"tcp_start":[0.48815,0.12266,0.08236],"tcp_to_object_dist_end":0.24119,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":228.0,"n_steps_budget":600.0,"object_pos_end":[0.50946,0.16028,0.01405],"object_pos_start":[0.5028,0.16029,0.01404],"object_to_goal_dist_end":0.24186,"object_to_goal_dist_start":0.2417,"object_z_max":0.01405,"peak_contact_force":0.52475,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":228.0,"raw_peak_contact_force":0.77049,"tcp_end":[0.49367,-0.07924,0.11979],"tcp_start":[0.49601,-0.07946,0.03953],"tcp_to_object_dist_end":0.26229,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57391,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_tcp.speed":0.12901,"descend_to_contact.contact_force_threshold":4.26033,"descend_to_contact.speed":0.03469,"push_along_channel.force_limit_guard":28.23803,"push_along_channel.push_distance":-0.01341,"push_along_channel.speed":0.03268,"retract_after_push.speed":0.15701},"optimized_scores":{"best_composite_score":-0.09602,"best_fitness_score":0.06398,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.51335,0.0784,0.00935],"force_p95":180.35663,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":183.78943,"mean_force":138.42515,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50715,0.06659,0.06016]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.51892,0.06517,0.0586],"force_p95":179.8755,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":183.29726,"mean_force":137.744,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50715,0.06659,0.06016]},{"body_a":"peg","body_b":"channel_base_body","contact_count":251.0,"contact_point_centroid":[0.50508,0.06398,0.00937],"force_p95":0.71599,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.84786,"mean_force":1.07173,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.5046,0.06735,0.09796]},{"body_a":"attachment","body_b":"peg","contact_count":16.0,"contact_point_centroid":[0.51787,0.0661,0.05833],"force_p95":37.44352,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":76.20291,"mean_force":8.36694,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50622,0.06773,0.05958]},{"body_a":"peg","body_b":"channel_base_body","contact_count":464.0,"contact_point_centroid":[0.50587,0.06297,0.00938],"force_p95":0.55161,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.42225,"mean_force":0.58294,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51433,0.07163,0.10544]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51884,0.06558,0.05881],"force_p95":16.97868,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.97868,"mean_force":16.97868,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50699,0.06627,0.06056]},{"body_a":"peg","body_b":"channel_base_body","contact_count":351.0,"contact_point_centroid":[0.50568,0.06297,0.00934],"force_p95":0.59723,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.58511,"phase_index":0.0,"phase_name":"align_tcp","phase_type":"align","tcp_position_centroid":[0.51192,0.13514,0.22038]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"align_tcp","phase_type":"align","tcp_position_centroid":[0.50039,0.19603,0.29488]}],"total_contact_groups":8},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50552,0.06359,0.03392],"final_tcp_position":[0.50455,0.06732,0.13994],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":183.78943,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":379.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.06295,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.55423,"phase_name":"align_tcp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":385.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_prepush","tcp_end":[0.5238,0.07728,0.15209],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12048,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":464.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.06304,0.0338],"object_pos_start":[0.50596,0.06295,0.03381],"object_to_goal_dist_end":0.1433,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":17.42225,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":465.0,"raw_peak_contact_force":17.42225,"subtask_id":"reach_prepush","tcp_end":[0.50697,0.06625,0.06038],"tcp_start":[0.5238,0.07728,0.15209],"tcp_to_object_dist_end":0.02679,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.5061,0.06319,0.03388],"object_pos_start":[0.50597,0.06304,0.0338],"object_to_goal_dist_end":0.14345,"object_to_goal_dist_start":0.1433,"object_z_max":0.03397,"peak_contact_force":183.78943,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":183.78943,"subtask_id":"push_through","tcp_end":[0.50746,0.06773,0.05969],"tcp_start":[0.50732,0.06701,0.05994],"tcp_to_object_dist_end":0.02625,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":251.0,"n_steps_budget":600.0,"object_pos_end":[0.50552,0.06359,0.03392],"object_pos_start":[0.5063,0.06381,0.03409],"object_to_goal_dist_end":0.14383,"object_to_goal_dist_start":0.14407,"object_z_max":0.03411,"peak_contact_force":0.54496,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":267.0,"raw_peak_contact_force":76.84786,"tcp_end":[0.50455,0.06732,0.13994],"tcp_start":[0.50746,0.06773,0.05969],"tcp_to_object_dist_end":0.10609,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```