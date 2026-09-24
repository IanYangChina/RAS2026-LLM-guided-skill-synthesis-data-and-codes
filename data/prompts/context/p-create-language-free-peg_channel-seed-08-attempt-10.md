## Search State

- **Seed**: 8
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | descend → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1612 | 0.43 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | -0.0476 | 0.00 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0242 | 0.26 | ❌ rejected |
| 7 | approach → descend → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1268 | 0.30 | ❌ rejected |
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.0101 | 0.16 | ❌ rejected |

**Proposal policy**: task_score is 0.43 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`
- Frozen object start: [0.48615778212844485, 0.11898214746703403, 0.04]
- Frozen task target: [0.48615778212844485, -0.04101785253296597, 0.04]
- Goal object position: (0.48615778212844485, -0.04101785253296597, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48615778212844485, 0.11898214746703403, 0.04)
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
  frozen_object_start: [0.4862, 0.119, 0.04]
  frozen_task_target: [0.4862, -0.041, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48615778212844485, 0.11898214746703403, 0.04]}
  frozen_targets: {'channel_exit': [0.48615778212844485, -0.04101785253296597, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e

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
| `object` | offset from object initial position (0.48615778212844485, 0.11898214746703403, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48615778212844485, -0.04101785253296597, 0.04) | final destination targets |
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

## Current Skill (Q=0.161) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.025
  - 0.0
  weight: 0.3
- id: push_complete
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
    - 0.05
    - 0.06
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_contact
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.025
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  subtask_id: pre_contact
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
      - 0.09
      - 0.18
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_complete
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
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.06], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.025, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.161
- **task_score** (E): 0.432
- **fitness_score**: 0.571  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_to_push_height | 1.00 | 1.00 | 0.2509 |
| align_behind_peg | 1.00 | 0.67 | 0.1049 |
| push_through_channel | 0.33 | 1.00 | 0.0483 |
| retract_after_push | 1.00 | 1.00 | 0.1384 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_to_push_height | descend | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.198, 0.049) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.547 | 3.526 |
| align_behind_peg | align | 1.00 / step_budget | (0.496, 0.198, 0.049)→(0.499, 0.095, 0.030) | (0.503, 0.080, 0.034)→(0.502, 0.066, 0.035) | 0.160→0.146 | 0.67 / 1.333 | 2.341 | 9.939 |
| push_through_channel | push | 0.33 / guard_failure | (0.496, 0.013, 0.027)→(0.495, -0.035, 0.026) | (0.502, 0.066, 0.035)→(0.505, -0.064, 0.036) | 0.146→0.020 | 1.00 / 1.667 | 31.059 | 64.680 |
| retract_after_push | retract | 1.00 / step_budget | (0.495, -0.035, 0.026)→(0.492, -0.035, 0.164) | (0.505, -0.064, 0.036)→(0.504, -0.066, 0.034) | 0.020→0.021 | 1.00 / 1.000 | 0.543 | 128.758 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.976
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.678
- phase_score: 0.590
- phase_breakdown.pre_contact_score: 0.176
- phase_breakdown.push_complete_score: 0.767

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.625
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.678
- **Median Q (composite search score)**: 0.159
- **K-run variance**: 0.0018
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.194


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a8ce855c7f52ba2d198de8387bdd2f3b869655c206850d620daaec6ac6f298cd`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `79b30dd7102e96fb2fa0880d3932c959e04a6f943c7e87b878f77a0e54f87a94`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83453,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_peg.align_speed":0.07016,"descend_to_push_height.descend_speed":0.11498,"push_through_channel.force_limit":41.00306,"push_through_channel.push_distance":0.16362,"push_through_channel.push_speed":0.08235,"push_through_channel.retry_offset_x":-0.00149,"retract_after_push.retract_speed":0.1104},"optimized_scores":{"best_composite_score":0.215,"best_fitness_score":0.625,"best_task_score":0.67759},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":111.0,"contact_point_centroid":[0.47499,-0.00892,0.04552],"force_p95":188.96226,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":252.01632,"mean_force":91.51255,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.48682,-0.00891,0.04357]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":103.0,"contact_point_centroid":[0.47465,0.07256,0.03478],"force_p95":25.0976,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.65665,"mean_force":5.51209,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49014,0.10248,0.02805]},{"body_a":"attachment","body_b":"peg","contact_count":283.0,"contact_point_centroid":[0.49328,0.05297,0.04907],"force_p95":19.85012,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.32119,"mean_force":2.81811,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48935,0.06458,0.02705]},{"body_a":"peg","body_b":"channel_base_body","contact_count":147.0,"contact_point_centroid":[0.49687,0.02193,0.00968],"force_p95":6.47871,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.22132,"mean_force":2.43934,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48934,0.06275,0.02704]},{"body_a":"peg","body_b":"channel_base_body","contact_count":342.0,"contact_point_centroid":[0.49606,0.1164,0.0095],"force_p95":1.32193,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.44554,"mean_force":0.69292,"phase_index":1.0,"phase_name":"align_behind_peg","phase_type":"align","tcp_position_centroid":[0.49285,0.16779,0.03838]},{"body_a":"attachment","body_b":"peg","contact_count":53.0,"contact_point_centroid":[0.49459,0.13115,0.04504],"force_p95":3.99375,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.0424,"mean_force":1.08019,"phase_index":1.0,"phase_name":"align_behind_peg","phase_type":"align","tcp_position_centroid":[0.49228,0.14301,0.03238]},{"body_a":"peg","body_b":"channel_base_body","contact_count":728.0,"contact_point_centroid":[0.49619,0.11913,0.00943],"force_p95":0.61762,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.551,"phase_index":0.0,"phase_name":"descend_to_push_height","phase_type":"descend","tcp_position_centroid":[0.49732,0.19862,0.17023]},{"body_a":"peg","body_b":"channel_base_body","contact_count":793.0,"contact_point_centroid":[0.49928,-0.03876,0.00947],"force_p95":0.6238,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.97467,"mean_force":0.54092,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.48599,-0.00877,0.09439]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"descend_to_push_height","phase_type":"descend","tcp_position_centroid":[0.49968,0.19958,0.29754]},{"body_a":"attachment","body_b":"peg","contact_count":47.0,"contact_point_centroid":[0.49318,-0.02023,0.06008],"force_p95":0.43247,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.84269,"mean_force":0.20461,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.48683,-0.00893,0.04137]}],"total_contact_groups":10},"final_pose_error":0.01194,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49845,-0.03715,0.03429],"final_tcp_position":[0.48591,-0.00869,0.16481],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":252.01632,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":753.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.11964,0.03401],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19977,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.56061,"phase_name":"descend_to_push_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":752.0,"raw_peak_contact_force":2.24822,"subtask_id":"pre_contact","tcp_end":[0.49628,0.19824,0.04931],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08008,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":364.0,"n_steps_budget":660.0,"object_pos_end":[0.49338,0.10579,0.03465],"object_pos_start":[0.49603,0.11964,0.03401],"object_to_goal_dist_end":0.18599,"object_to_goal_dist_start":0.19977,"object_z_max":0.03593,"peak_contact_force":1.39826,"phase_name":"align_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":395.0,"raw_peak_contact_force":8.44554,"subtask_id":"pre_contact","tcp_end":[0.49224,0.1358,0.0308],"tcp_start":[0.49628,0.19824,0.04931],"tcp_to_object_dist_end":0.03028,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":350.0,"n_steps_budget":1000.0,"object_pos_end":[0.50186,-0.03691,0.03626],"object_pos_start":[0.49338,0.10579,0.03465],"object_to_goal_dist_end":0.04329,"object_to_goal_dist_start":0.18599,"object_z_max":0.03716,"peak_contact_force":1.07835,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":533.0,"raw_peak_contact_force":33.65665,"subtask_id":"push_complete","tcp_end":[0.48879,-0.00875,0.02639],"tcp_start":[0.49224,0.1358,0.0308],"tcp_to_object_dist_end":0.03258,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":793.0,"n_steps_budget":870.0,"object_pos_end":[0.49845,-0.03715,0.03429],"object_pos_start":[0.50186,-0.03691,0.03626],"object_to_goal_dist_end":0.04325,"object_to_goal_dist_start":0.04329,"object_z_max":0.03672,"peak_contact_force":0.54074,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":951.0,"raw_peak_contact_force":252.01632,"tcp_end":[0.48591,-0.00869,0.16481],"tcp_start":[0.48879,-0.00875,0.02639],"tcp_to_object_dist_end":0.13417,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50556,"average_solve_count":180.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_peg.align_speed":0.07071,"descend_to_push_height.descend_speed":0.12817,"push_through_channel.force_limit":41.895,"push_through_channel.push_distance":0.1605,"push_through_channel.push_speed":0.04186,"push_through_channel.retry_offset_x":0.00115,"retract_after_push.retract_speed":0.11212},"optimized_scores":{"best_composite_score":0.15853,"best_fitness_score":0.56853,"best_task_score":0.3698},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.55385,-0.1,0.06496],"force_p95":77.7068,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.31266,"mean_force":63.09262,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49787,-0.0479,0.02516]},{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.55355,-0.10001,0.06494],"force_p95":67.6377,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":68.32736,"mean_force":62.63475,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49789,-0.04842,0.02518]},{"body_a":"attachment","body_b":"peg","contact_count":282.0,"contact_point_centroid":[0.50393,0.00402,0.04767],"force_p95":31.30137,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.96442,"mean_force":7.77525,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49835,0.01566,0.02586]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":255.0,"contact_point_centroid":[0.52525,-0.01728,0.03612],"force_p95":28.9026,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.95974,"mean_force":5.85417,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49822,0.01167,0.02572]},{"body_a":"peg","body_b":"channel_base_body","contact_count":116.0,"contact_point_centroid":[0.50701,-0.02596,0.00989],"force_p95":21.26536,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.57536,"mean_force":8.99841,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4984,0.01975,0.02595]},{"body_a":"attachment","body_b":"peg","contact_count":86.0,"contact_point_centroid":[0.50483,0.0736,0.04718],"force_p95":9.4381,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.73182,"mean_force":3.72864,"phase_index":1.0,"phase_name":"align_behind_peg","phase_type":"align","tcp_position_centroid":[0.50106,0.08548,0.03071]},{"body_a":"peg","body_b":"channel_base_body","contact_count":748.0,"contact_point_centroid":[0.50602,0.06078,0.00943],"force_p95":5.4755,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.20336,"mean_force":0.93548,"phase_index":1.0,"phase_name":"align_behind_peg","phase_type":"align","tcp_position_centroid":[0.49722,0.13817,0.03747]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":60.0,"contact_point_centroid":[0.52505,0.05569,0.02533],"force_p95":3.67973,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.75458,"mean_force":1.39673,"phase_index":1.0,"phase_name":"align_behind_peg","phase_type":"align","tcp_position_centroid":[0.5011,0.08497,0.03065]},{"body_a":"peg","body_b":"channel_base_body","contact_count":714.0,"contact_point_centroid":[0.50578,0.06295,0.00936],"force_p95":0.55928,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56551,"phase_index":0.0,"phase_name":"descend_to_push_height","phase_type":"descend","tcp_position_centroid":[0.49734,0.19862,0.16984]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"descend_to_push_height","phase_type":"descend","tcp_position_centroid":[0.49958,0.19954,0.29591]},{"body_a":"peg","body_b":"channel_base_body","contact_count":759.0,"contact_point_centroid":[0.50675,-0.0808,0.0094],"force_p95":0.56683,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.14045,"mean_force":0.54989,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.4947,-0.04805,0.09322]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.52503,-0.08015,0.04695],"force_p95":0.54876,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60209,"mean_force":0.12218,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49667,-0.04847,0.02851]},{"body_a":"peg","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.52312,-0.0203,0.0619],"force_p95":0.01309,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.01824,"mean_force":0.00262,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49789,0.00107,0.02526]}],"total_contact_groups":13},"final_pose_error":0.0124,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5069,-0.08054,0.0338],"final_tcp_position":[0.49498,-0.04803,0.16311],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":79.31266,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":742.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.06302,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54587,"phase_name":"descend_to_push_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":748.0,"raw_peak_contact_force":3.88411,"subtask_id":"pre_contact","tcp_end":[0.49627,0.19824,0.04956],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13647,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":784.0,"n_steps_budget":1000.0,"object_pos_end":[0.50687,0.04898,0.03522],"object_pos_start":[0.50595,0.06302,0.03381],"object_to_goal_dist_end":0.12925,"object_to_goal_dist_start":0.14328,"object_z_max":0.03566,"peak_contact_force":5.62449,"phase_name":"align_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":894.0,"raw_peak_contact_force":11.73182,"subtask_id":"pre_contact","tcp_end":[0.50164,0.07846,0.02988],"tcp_start":[0.49627,0.19824,0.04956],"tcp_to_object_dist_end":0.03041,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":345.0,"n_steps_budget":1000.0,"object_pos_end":[0.507,-0.07768,0.03573],"object_pos_start":[0.50687,0.04898,0.03522],"object_to_goal_dist_end":0.00852,"object_to_goal_dist_start":0.12925,"object_z_max":0.03656,"peak_contact_force":46.71117,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":665.0,"raw_peak_contact_force":79.31266,"subtask_id":"push_complete","tcp_end":[0.49788,-0.04829,0.02516],"tcp_start":[0.49787,-0.04814,0.02516],"tcp_to_object_dist_end":0.03254,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":763.0,"n_steps_budget":840.0,"object_pos_end":[0.5069,-0.08054,0.0338],"object_pos_start":[0.50702,-0.0783,0.0356],"object_to_goal_dist_end":0.0093,"object_to_goal_dist_start":0.00846,"object_z_max":0.0356,"peak_contact_force":0.54711,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":782.0,"raw_peak_contact_force":68.32736,"tcp_end":[0.49498,-0.04803,0.16311],"tcp_start":[0.49788,-0.04829,0.02516],"tcp_to_object_dist_end":0.13386,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71598,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_peg.align_speed":0.08335,"descend_to_push_height.descend_speed":0.09309,"push_through_channel.force_limit":35.06869,"push_through_channel.push_distance":0.15765,"push_through_channel.push_speed":0.06212,"push_through_channel.retry_offset_x":-0.00083,"retract_after_push.retract_speed":0.1012},"optimized_scores":{"best_composite_score":0.11,"best_fitness_score":0.52,"best_task_score":0.24718},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.55462,-0.1,0.06499],"force_p95":79.51542,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":81.07062,"mean_force":63.99253,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49817,-0.04696,0.0251]},{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.55432,-0.1,0.06499],"force_p95":65.44651,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":65.92941,"mean_force":60.80164,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49823,-0.04755,0.02515]},{"body_a":"attachment","body_b":"peg","contact_count":210.0,"contact_point_centroid":[0.50366,-0.00445,0.04419],"force_p95":23.42806,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.23113,"mean_force":5.55252,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49858,0.00721,0.02574]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":182.0,"contact_point_centroid":[0.52525,-0.00325,0.02985],"force_p95":23.84846,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.22136,"mean_force":3.66203,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49885,0.02583,0.02611]},{"body_a":"peg","body_b":"channel_base_body","contact_count":108.0,"contact_point_centroid":[0.5048,-0.02918,0.00986],"force_p95":17.89962,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.81594,"mean_force":6.40806,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49874,0.01506,0.02594]},{"body_a":"peg","body_b":"channel_base_body","contact_count":774.0,"contact_point_centroid":[0.50632,0.0547,0.00942],"force_p95":1.40552,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.63935,"mean_force":0.6893,"phase_index":1.0,"phase_name":"align_behind_peg","phase_type":"align","tcp_position_centroid":[0.49732,0.13473,0.03738]},{"body_a":"attachment","body_b":"peg","contact_count":80.0,"contact_point_centroid":[0.50435,0.06767,0.04391],"force_p95":6.20407,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.15986,"mean_force":1.46995,"phase_index":1.0,"phase_name":"align_behind_peg","phase_type":"align","tcp_position_centroid":[0.50124,0.07956,0.03066]},{"body_a":"peg","body_b":"channel_base_body","contact_count":738.0,"contact_point_centroid":[0.50595,0.05665,0.00936],"force_p95":0.60101,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56814,"phase_index":0.0,"phase_name":"descend_to_push_height","phase_type":"descend","tcp_position_centroid":[0.49728,0.1986,0.1697]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"descend_to_push_height","phase_type":"descend","tcp_position_centroid":[0.49952,0.19951,0.29543]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":31.0,"contact_point_centroid":[0.52511,-0.08033,0.05932],"force_p95":1.9557,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.02625,"mean_force":0.47408,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49595,-0.04748,0.0337]},{"body_a":"peg","body_b":"channel_base_body","contact_count":10.0,"contact_point_centroid":[0.50718,-0.10008,0.059],"force_p95":1.89448,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.91343,"mean_force":1.19853,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49704,-0.04775,0.02829]},{"body_a":"peg","body_b":"channel_base_body","contact_count":840.0,"contact_point_centroid":[0.5064,-0.07993,0.0094],"force_p95":0.59712,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.85493,"mean_force":0.54842,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49499,-0.04717,0.09407]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52507,0.04246,0.05976],"force_p95":0.20859,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21413,"mean_force":0.11227,"phase_index":1.0,"phase_name":"align_behind_peg","phase_type":"align","tcp_position_centroid":[0.50175,0.07269,0.02984]},{"body_a":"peg","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52258,-0.05254,0.06178],"force_p95":0.10872,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11305,"mean_force":0.07573,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49811,-0.03038,0.02509]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50358,-0.05956,0.05488],"force_p95":0.04748,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.04816,"mean_force":0.0413,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49822,-0.04749,0.02513]}],"total_contact_groups":15},"final_pose_error":0.01171,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50675,-0.07958,0.0338],"final_tcp_position":[0.49527,-0.04715,0.16379],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":81.07062,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":767.0,"n_steps_budget":1000.0,"object_pos_end":[0.50615,0.05659,0.03379],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.53589,"phase_name":"descend_to_push_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":775.0,"raw_peak_contact_force":4.44541,"subtask_id":"pre_contact","tcp_end":[0.49623,0.19822,0.0495],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":807.0,"n_steps_budget":990.0,"object_pos_end":[0.50656,0.04205,0.03535],"object_pos_start":[0.50615,0.05659,0.03379],"object_to_goal_dist_end":0.12231,"object_to_goal_dist_start":0.13687,"object_z_max":0.03575,"peak_contact_force":0.0,"phase_name":"align_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":860.0,"raw_peak_contact_force":9.63935,"subtask_id":"pre_contact","tcp_end":[0.5018,0.0719,0.02975],"tcp_start":[0.49623,0.19822,0.0495],"tcp_to_object_dist_end":0.03075,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":312.0,"n_steps_budget":1000.0,"object_pos_end":[0.50509,-0.07634,0.03586],"object_pos_start":[0.50656,0.04205,0.03535],"object_to_goal_dist_end":0.00751,"object_to_goal_dist_start":0.12231,"object_z_max":0.03663,"peak_contact_force":45.38835,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":506.0,"raw_peak_contact_force":81.07062,"subtask_id":"push_complete","tcp_end":[0.49821,-0.04741,0.02512],"tcp_start":[0.49819,-0.04724,0.02512],"tcp_to_object_dist_end":0.03161,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.50675,-0.07958,0.0338],"object_pos_start":[0.50508,-0.07702,0.03591],"object_to_goal_dist_end":0.00918,"object_to_goal_dist_start":0.00717,"object_z_max":0.03591,"peak_contact_force":0.54208,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":886.0,"raw_peak_contact_force":65.92941,"tcp_end":[0.49527,-0.04715,0.16379],"tcp_start":[0.49821,-0.04741,0.02512],"tcp_to_object_dist_end":0.13447,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```