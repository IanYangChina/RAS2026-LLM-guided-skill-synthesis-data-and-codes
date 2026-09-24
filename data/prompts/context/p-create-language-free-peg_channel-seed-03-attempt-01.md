## Search State

- **Seed**: 3
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.4166 | 0.12 | ✅ accepted |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.4151 | 0.11 | ✅ accepted |

**Proposal policy**: task_score is 0.12 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`
- Frozen object start: [0.46685193337148995, 0.058944840527687975, 0.04]
- Frozen task target: [0.46685193337148995, -0.10105515947231203, 0.04]
- Goal object position: (0.46685193337148995, -0.10105515947231203, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.46685193337148995, 0.058944840527687975, 0.04)
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
  frozen_object_start: [0.4669, 0.0589, 0.04]
  frozen_task_target: [0.4669, -0.1011, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.46685193337148995, 0.058944840527687975, 0.04]}
  frozen_targets: {'channel_exit': [0.46685193337148995, -0.10105515947231203, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834

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
| `object` | offset from object initial position (0.46685193337148995, 0.058944840527687975, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.46685193337148995, -0.10105515947231203, 0.04) | final destination targets |
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

## Current Skill (Q=0.417) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.025
  - 0.1
  weight: 0.3
- id: goal_push
  offset:
  - 0.0
  - 0.025
  - 0.0
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.025
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_contact
- id: descend_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.025
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.14
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: goal_push
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.025, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.025, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.417
- **task_score** (E): 0.115
- **fitness_score**: 0.477  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1847 |
| descend_1 | 1.00 | 1.00 | 0.0811 |
| push_1 | 1.00 | 1.00 | 0.1598 |
| retract_1 | 1.00 | 1.00 | 0.0804 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.117, 0.138) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.549 | 3.954 |
| descend_1 | contact | 1.00 / force_exceeded | (0.505, 0.117, 0.138)→(0.499, 0.109, 0.059) | (0.502, 0.081, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 2.000 | 48.265 | 48.265 |
| push_1 | push | 1.00 / step_budget | (0.499, 0.109, 0.059)→(0.498, -0.051, 0.056) | (0.502, 0.081, 0.034)→(0.498, 0.008, 0.024) | 0.162→0.090 | 1.00 / 1.333 | 33.992 | 93.934 |
| retract_1 | retract | 1.00 / step_budget | (0.498, -0.051, 0.056)→(0.495, -0.051, 0.136) | (0.498, 0.008, 0.024)→(0.498, 0.008, 0.024) | 0.090→0.090 | 1.00 / 1.000 | 0.568 | 34.967 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.530
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.145
- phase_score: 0.753
- phase_breakdown.pre_contact_score: 0.818
- phase_breakdown.goal_push_score: 0.725

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.510
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.145
- **Median Q (composite search score)**: 0.430
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.208


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `cc7283febf3c95cef1fde4c5a16cbcb134186cb6faf3a169717a9aa53375931d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `178d67757a065da6e29d31070e25f6065dc7e42bdbf58dfbff0deec513214033`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11373,"average_solve_count":255.0,"average_success_count":255.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0823,"approach_1.approach_speed":0.0331,"descend_1.contact_force":8.67228,"push_1.push_distance":0.16083,"push_1.push_speed":0.03476},"optimized_scores":{"best_composite_score":0.36985,"best_fitness_score":0.42985,"best_task_score":0.07346},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":375.0,"contact_point_centroid":[0.475,0.00874,0.05999],"force_p95":131.49899,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":141.62048,"mean_force":113.11659,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4842,0.01626,0.05871]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.07818,0.05998],"force_p95":102.96104,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":102.96104,"mean_force":102.96104,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.48326,0.08677,0.05881]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.475,-0.06106,0.05998],"force_p95":84.69803,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":87.02996,"mean_force":68.443,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48493,-0.0545,0.05857]},{"body_a":"peg","body_b":"channel_base_body","contact_count":546.0,"contact_point_centroid":[0.50099,0.02331,0.0087],"force_p95":1.11122,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.00662,"mean_force":1.08205,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48422,0.0156,0.05872]},{"body_a":"attachment","body_b":"peg","contact_count":35.0,"contact_point_centroid":[0.49052,0.06142,0.0581],"force_p95":25.72485,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.77422,"mean_force":7.62188,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4837,0.07073,0.05877]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":15.0,"contact_point_centroid":[0.47489,0.03401,0.0243],"force_p95":5.25524,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.70923,"mean_force":1.28897,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48403,0.03065,0.05876]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52525,0.02995,0.05298],"force_p95":1.22335,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.02112,"mean_force":0.41677,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48381,0.05697,0.05879]},{"body_a":"peg","body_b":"channel_base_body","contact_count":371.0,"contact_point_centroid":[0.49443,0.05887,0.00934],"force_p95":0.60191,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.58563,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48276,0.14573,0.21371]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49879,0.19736,0.29569]},{"body_a":"peg","body_b":"channel_base_body","contact_count":240.0,"contact_point_centroid":[0.49886,0.0138,0.00803],"force_p95":0.72557,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73806,"mean_force":0.6053,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48243,-0.05426,0.09795]},{"body_a":"peg","body_b":"channel_base_body","contact_count":479.0,"contact_point_centroid":[0.49412,0.05893,0.00939],"force_p95":0.5504,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54612,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.47433,0.09119,0.09666]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.03387,0.02415],"force_p95":0.4674,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4674,"mean_force":0.4674,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48198,-0.0541,0.12163]}],"total_contact_groups":12},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4988,0.01371,0.02415],"final_tcp_position":[0.48213,-0.0541,0.13892],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":141.62048,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":400.0,"n_steps_budget":1000.0,"object_pos_end":[0.49422,0.05892,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13918,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54871,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":406.0,"raw_peak_contact_force":4.20518,"subtask_id":"pre_contact","tcp_end":[0.46801,0.09615,0.13751],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":479.0,"n_steps_budget":690.0,"object_pos_end":[0.49429,0.0589,0.03391],"object_pos_start":[0.49422,0.05892,0.03385],"object_to_goal_dist_end":0.13916,"object_to_goal_dist_start":0.13918,"object_z_max":0.03391,"peak_contact_force":102.96104,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":480.0,"raw_peak_contact_force":102.96104,"tcp_end":[0.48332,0.08676,0.05866],"tcp_start":[0.46801,0.09615,0.13751],"tcp_to_object_dist_end":0.03884,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":557.0,"n_steps_budget":1000.0,"object_pos_end":[0.49971,0.01407,0.0241],"object_pos_start":[0.49429,0.0589,0.03391],"object_to_goal_dist_end":0.0954,"object_to_goal_dist_start":0.13916,"object_z_max":0.04064,"peak_contact_force":100.93192,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1003.0,"raw_peak_contact_force":141.62048,"subtask_id":"goal_push","tcp_end":[0.48495,-0.05436,0.05858],"tcp_start":[0.48332,0.08676,0.05866],"tcp_to_object_dist_end":0.07804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":240.0,"n_steps_budget":660.0,"object_pos_end":[0.4988,0.01371,0.02415],"object_pos_start":[0.49971,0.01407,0.0241],"object_to_goal_dist_end":0.09505,"object_to_goal_dist_start":0.0954,"object_z_max":0.02421,"peak_contact_force":0.65584,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":244.0,"raw_peak_contact_force":87.02996,"tcp_end":[0.48213,-0.0541,0.13892],"tcp_start":[0.48495,-0.05436,0.05858],"tcp_to_object_dist_end":0.13434,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.99643,"average_solve_count":280.0,"average_success_count":280.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08132,"approach_1.approach_speed":0.02949,"descend_1.contact_force":4.99508,"push_1.push_distance":0.17661,"push_1.push_speed":0.02752},"optimized_scores":{"best_composite_score":0.43027,"best_fitness_score":0.49027,"best_task_score":0.12796},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":461.0,"contact_point_centroid":[0.50839,0.03214,0.00941],"force_p95":69.84852,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.69498,"mean_force":47.68945,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50923,0.0363,0.05868]},{"body_a":"attachment","body_b":"peg","contact_count":394.0,"contact_point_centroid":[0.51489,0.05138,0.05943],"force_p95":69.50687,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.25282,"mean_force":55.26661,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50965,0.04824,0.05919]},{"body_a":"peg","body_b":"channel_base_body","contact_count":329.0,"contact_point_centroid":[0.50603,0.08085,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.61902,"mean_force":0.60778,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.51796,0.11186,0.0973]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51366,0.0971,0.05872],"force_p95":20.21734,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.21734,"mean_force":20.21734,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.50906,0.10815,0.05938]},{"body_a":"peg","body_b":"channel_base_body","contact_count":247.0,"contact_point_centroid":[0.49748,-0.00886,0.00808],"force_p95":0.79443,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.42033,"mean_force":0.63859,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50317,-0.04951,0.09395]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47495,0.01523,0.02435],"force_p95":5.12084,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.18561,"mean_force":1.22712,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50358,-0.0499,0.06621]},{"body_a":"peg","body_b":"channel_base_body","contact_count":359.0,"contact_point_centroid":[0.50552,0.08086,0.00935],"force_p95":0.5667,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.58926,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51418,0.15608,0.21332]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50023,0.19773,0.29548]}],"total_contact_groups":8},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50103,-0.00822,0.02414],"final_tcp_position":[0.50299,-0.04926,0.1352],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":70.69498,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":388.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54511,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":395.0,"raw_peak_contact_force":4.32595,"subtask_id":"pre_contact","tcp_end":[0.52858,0.11606,0.13654],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11094,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":329.0,"n_steps_budget":690.0,"object_pos_end":[0.50595,0.08088,0.03377],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.16111,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":20.61902,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":330.0,"raw_peak_contact_force":20.61902,"tcp_end":[0.50901,0.10813,0.05916],"tcp_start":[0.52858,0.11606,0.13654],"tcp_to_object_dist_end":0.03737,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":467.0,"n_steps_budget":1000.0,"object_pos_end":[0.4971,-0.00826,0.02384],"object_pos_start":[0.50595,0.08088,0.03377],"object_to_goal_dist_end":0.07359,"object_to_goal_dist_start":0.16111,"object_z_max":0.04012,"peak_contact_force":0.44368,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":855.0,"raw_peak_contact_force":70.69498,"subtask_id":"goal_push","tcp_end":[0.50596,-0.04948,0.05482],"tcp_start":[0.50901,0.10813,0.05916],"tcp_to_object_dist_end":0.05231,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":247.0,"n_steps_budget":630.0,"object_pos_end":[0.50103,-0.00822,0.02414],"object_pos_start":[0.4971,-0.00826,0.02384],"object_to_goal_dist_end":0.07352,"object_to_goal_dist_start":0.07359,"object_z_max":0.02468,"peak_contact_force":0.54617,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":256.0,"raw_peak_contact_force":8.42033,"tcp_end":[0.50299,-0.04926,0.1352],"tcp_start":[0.50596,-0.04948,0.05482],"tcp_to_object_dist_end":0.11842,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1,"average_solve_count":280.0,"average_success_count":280.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08326,"approach_1.approach_speed":0.01966,"descend_1.contact_force":4.93515,"push_1.push_distance":0.1997,"push_1.push_speed":0.02973},"optimized_scores":{"best_composite_score":0.44965,"best_fitness_score":0.50965,"best_task_score":0.14487},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":509.0,"contact_point_centroid":[0.50788,0.05233,0.00924],"force_p95":68.48317,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.4861,"mean_force":39.25342,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50537,0.04754,0.05835]},{"body_a":"attachment","body_b":"peg","contact_count":372.0,"contact_point_centroid":[0.51345,0.07685,0.05924],"force_p95":68.32859,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.00663,"mean_force":53.05549,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50619,0.07305,0.05937]},{"body_a":"peg","body_b":"channel_base_body","contact_count":354.0,"contact_point_centroid":[0.50576,0.10463,0.00939],"force_p95":0.57553,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.21503,"mean_force":0.60473,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.51122,0.13412,0.0992]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51277,0.12126,0.05878],"force_p95":20.79468,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.79468,"mean_force":20.79468,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.50593,0.13106,0.05977]},{"body_a":"peg","body_b":"channel_base_body","contact_count":247.0,"contact_point_centroid":[0.49406,0.01921,0.00814],"force_p95":0.73232,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.45101,"mean_force":0.70733,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49977,-0.04953,0.09411]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47499,0.04417,0.02428],"force_p95":8.95902,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.0296,"mean_force":2.99092,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4996,-0.04945,0.09336]},{"body_a":"peg","body_b":"channel_base_body","contact_count":328.0,"contact_point_centroid":[0.50553,0.10457,0.00936],"force_p95":0.60002,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.58082,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50899,0.16752,0.21584]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49998,0.19843,0.29625]}],"total_contact_groups":8},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49345,0.01979,0.0242],"final_tcp_position":[0.49959,-0.04928,0.13536],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":69.4861,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":355.0,"n_steps_budget":1000.0,"object_pos_end":[0.50584,0.1046,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55203,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":360.0,"raw_peak_contact_force":3.33087,"subtask_id":"pre_contact","tcp_end":[0.51862,0.13781,0.14052],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":354.0,"n_steps_budget":690.0,"object_pos_end":[0.50584,0.1047,0.03383],"object_pos_start":[0.50584,0.1046,0.03384],"object_to_goal_dist_end":0.18489,"object_to_goal_dist_start":0.1848,"object_z_max":0.03384,"peak_contact_force":21.21503,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":355.0,"raw_peak_contact_force":21.21503,"tcp_end":[0.50591,0.13104,0.05956],"tcp_start":[0.51862,0.13781,0.14052],"tcp_to_object_dist_end":0.03682,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":515.0,"n_steps_budget":1000.0,"object_pos_end":[0.49691,0.01938,0.02413],"object_pos_start":[0.50584,0.1047,0.03383],"object_to_goal_dist_end":0.10069,"object_to_goal_dist_start":0.18489,"object_z_max":0.04017,"peak_contact_force":0.59984,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":881.0,"raw_peak_contact_force":69.4861,"subtask_id":"goal_push","tcp_end":[0.50253,-0.04951,0.05491],"tcp_start":[0.50591,0.13104,0.05956],"tcp_to_object_dist_end":0.07566,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":247.0,"n_steps_budget":630.0,"object_pos_end":[0.49345,0.01979,0.0242],"object_pos_start":[0.49691,0.01938,0.02413],"object_to_goal_dist_end":0.10124,"object_to_goal_dist_start":0.10069,"object_z_max":0.02474,"peak_contact_force":0.5007,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":257.0,"raw_peak_contact_force":9.45101,"tcp_end":[0.49959,-0.04928,0.13536],"tcp_start":[0.50253,-0.04951,0.05491],"tcp_to_object_dist_end":0.13101,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```