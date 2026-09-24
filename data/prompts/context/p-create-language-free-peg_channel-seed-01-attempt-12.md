## Search State

- **Seed**: 1
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.3806 | 0.33 | ❌ rejected |
| 11 | approach → descend → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0381 | 0.07 | ❌ rejected |
| 10 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.3281 | 0.22 | ❌ rejected |
| 9 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.0181 | 0.00 | ❌ rejected |
| 8 | approach → descend → contact → push | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.0318 | 0.01 | ❌ rejected |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.381) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_approach
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.1
  weight: 0.2
- id: reach_descend
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.0
  weight: 0.2
- id: reach_goal
  target_entity: object
  metric: goal_progress
  weight: 0.6
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.1
    tolerance: 0.01
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_approach
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.01
  parameters:
    descend_height:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_descend
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    offset_along_axis:
      distance: 0.02
      axis: channel_axis
      mode: add_to_offset
      sign: positive
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: reach_goal
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
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.12
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
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.1], tolerance=0.01
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - parameter_bindings:
    - descend_height: status=consumed; consumers=target.offset.z (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], offset_along_axis={axis=channel_axis, distance=0.02, mode=add_to_offset, sign=positive}
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.381
- **task_score** (E): 0.327
- **fitness_score**: 0.574  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1701 |
| descend_1 | 1.00 | 0.33 | 0.1128 |
| contact_1 | 0.67 | 1.00 | 0.0104 |
| push_1 | 1.00 | 1.00 | 0.1219 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.481, 0.107, 0.161) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.556 | 2.857 |
| descend_1 | descend | 1.00 / step_budget | (0.481, 0.107, 0.161)→(0.494, 0.101, 0.050) | (0.497, 0.080, 0.034)→(0.501, 0.059, 0.038) | 0.160→0.139 | 0.33 / 0.667 | 18.183 | 149.536 |
| contact_1 | contact | 0.67 / force_exceeded | (0.494, 0.101, 0.050)→(0.492, 0.091, 0.047) | (0.501, 0.059, 0.038)→(0.502, 0.053, 0.032) | 0.139→0.134 | 1.00 / 1.333 | 10.754 | 11.815 |
| push_1 | push | 1.00 / step_budget | (0.492, 0.091, 0.047)→(0.491, -0.031, 0.044) | (0.502, 0.053, 0.032)→(0.502, -0.039, 0.028) | 0.134→0.048 | 1.00 / 3.333 | 103.542 | 135.189 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.888
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.343
- phase_score: 0.856
- phase_breakdown.reach_goal_score: 0.889
- phase_breakdown.reach_descend_score: 0.760
- phase_breakdown.reach_approach_score: 0.852

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.651
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.478
- **Median Q (composite search score)**: 0.407
- **K-run variance**: 0.0204
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.384


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2875,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11559,"contact_1.contact_force":8.21407,"descend_1.descend_height":0.01587,"push_1.push_distance":0.15204,"push_1.push_speed":0.03014,"push_1.retry_offset_x":0.00596},"optimized_scores":{"best_composite_score":0.40708,"best_fitness_score":0.51708,"best_task_score":0.47828},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":381.0,"contact_point_centroid":[0.50439,0.07833,0.009],"force_p95":88.83668,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":89.69552,"mean_force":61.17877,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49819,0.0776,0.05923]},{"body_a":"attachment","body_b":"peg","contact_count":336.0,"contact_point_centroid":[0.50766,0.08908,0.05684],"force_p95":88.3933,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":89.21431,"mean_force":68.85114,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49852,0.08573,0.05967]},{"body_a":"peg","body_b":"channel_base_body","contact_count":330.0,"contact_point_centroid":[0.50134,0.11623,0.00941],"force_p95":50.94512,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":86.74504,"mean_force":4.35671,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49641,0.13809,0.11055]},{"body_a":"attachment","body_b":"peg","contact_count":18.0,"contact_point_centroid":[0.50791,0.13356,0.05735],"force_p95":85.54462,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":86.18928,"mean_force":70.01311,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49716,0.1362,0.06115]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50853,0.13433,0.05577],"force_p95":29.52315,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.52315,"mean_force":29.52315,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49772,0.1367,0.05915]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51824,0.11993,0.0089],"force_p95":29.45503,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.45503,"mean_force":29.45503,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49772,0.1367,0.05915]},{"body_a":"peg","body_b":"channel_base_body","contact_count":440.0,"contact_point_centroid":[0.50098,0.11603,0.00937],"force_p95":0.62076,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56217,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4982,0.16991,0.22946]}],"total_contact_groups":7},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49659,0.03951,0.02636],"final_tcp_position":[0.49478,0.00398,0.05498],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":89.69552,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":456.0,"n_steps_budget":990.0,"object_pos_end":[0.50091,0.11603,0.03386],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19613,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.5708,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":440.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_approach","tcp_end":[0.49795,0.14099,0.16357],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13212,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":330.0,"n_steps_budget":720.0,"object_pos_end":[0.50127,0.11651,0.03307],"object_pos_start":[0.50091,0.11603,0.03386],"object_to_goal_dist_end":0.19663,"object_to_goal_dist_start":0.19613,"object_z_max":0.03392,"peak_contact_force":54.54964,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":348.0,"raw_peak_contact_force":86.74504,"subtask_id":"reach_descend","tcp_end":[0.49772,0.1367,0.05915],"tcp_start":[0.49795,0.14099,0.16357],"tcp_to_object_dist_end":0.03317,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50117,0.11649,0.03295],"object_pos_start":[0.50127,0.11651,0.03307],"object_to_goal_dist_end":0.19662,"object_to_goal_dist_start":0.19663,"object_z_max":0.03307,"peak_contact_force":29.52315,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":29.52315,"subtask_id":"reach_goal","tcp_end":[0.49767,0.13671,0.05903],"tcp_start":[0.49772,0.1367,0.05915],"tcp_to_object_dist_end":0.03319,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":387.0,"n_steps_budget":1000.0,"object_pos_end":[0.49659,0.03951,0.02636],"object_pos_start":[0.50117,0.11649,0.03295],"object_to_goal_dist_end":0.12034,"object_to_goal_dist_start":0.19662,"object_z_max":0.0399,"peak_contact_force":1.22274,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":717.0,"raw_peak_contact_force":89.69552,"subtask_id":"reach_goal","tcp_end":[0.49478,0.00398,0.05498],"tcp_start":[0.49767,0.13671,0.05903],"tcp_to_object_dist_end":0.04566,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36486,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11337,"contact_1.contact_force":2.06285,"descend_1.descend_height":0.00335,"push_1.push_distance":0.15652,"push_1.push_speed":0.0408,"push_1.retry_offset_x":0.00926},"optimized_scores":{"best_composite_score":0.54058,"best_fitness_score":0.65058,"best_task_score":0.34283},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":395.0,"contact_point_centroid":[0.49642,0.06436,0.00925],"force_p95":129.89804,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":181.75689,"mean_force":17.63787,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48398,0.08787,0.10062]},{"body_a":"attachment","body_b":"peg","contact_count":63.0,"contact_point_centroid":[0.49943,0.08003,0.05574],"force_p95":156.77185,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":181.14346,"mean_force":107.32134,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49065,0.08584,0.05819]},{"body_a":"attachment","body_b":"peg","contact_count":374.0,"contact_point_centroid":[0.49202,-0.02609,0.04357],"force_p95":143.99403,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":145.54166,"mean_force":54.85529,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48791,-0.01534,0.0404]},{"body_a":"peg","body_b":"channel_base_body","contact_count":159.0,"contact_point_centroid":[0.49188,-0.10198,0.03573],"force_p95":139.08983,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":141.0746,"mean_force":110.74017,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48802,-0.04623,0.04008]},{"body_a":"peg","body_b":"channel_base_body","contact_count":370.0,"contact_point_centroid":[0.50516,-0.05656,0.00948],"force_p95":22.81971,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.88019,"mean_force":9.05959,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48816,-0.00259,0.0407]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":248.0,"contact_point_centroid":[0.52517,-0.07629,0.02797],"force_p95":21.66241,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.85265,"mean_force":10.19328,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.488,-0.02196,0.04034]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":23.0,"contact_point_centroid":[0.47466,0.04034,0.02411],"force_p95":9.54929,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.97329,"mean_force":2.89431,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48928,0.07088,0.04242]},{"body_a":"peg","body_b":"channel_base_body","contact_count":542.0,"contact_point_centroid":[0.4955,0.06397,0.00937],"force_p95":0.58344,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56124,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48855,0.14374,0.22542]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52507,0.0084,0.04723],"force_p95":2.08273,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.08273,"mean_force":2.08273,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49163,0.08452,0.0453]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49918,0.198,0.29732]}],"total_contact_groups":10},"final_pose_error":0.02371,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50497,-0.07828,0.0292],"final_tcp_position":[0.48792,-0.04941,0.03939],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":181.75689,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":569.0,"n_steps_budget":1000.0,"object_pos_end":[0.49492,0.06399,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14421,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54743,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":570.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_approach","tcp_end":[0.47936,0.09169,0.15931],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":400.0,"n_steps_budget":780.0,"object_pos_end":[0.50153,0.03844,0.04147],"object_pos_start":[0.49492,0.06399,0.03394],"object_to_goal_dist_end":0.11846,"object_to_goal_dist_start":0.14421,"object_z_max":0.04141,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":458.0,"raw_peak_contact_force":181.75689,"subtask_id":"reach_descend","tcp_end":[0.49281,0.08535,0.04668],"tcp_start":[0.47936,0.09169,0.15931],"tcp_to_object_dist_end":0.04799,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":11.0,"n_steps_budget":600.0,"object_pos_end":[0.5033,0.02795,0.03952],"object_pos_start":[0.50153,0.03844,0.04147],"object_to_goal_dist_end":0.108,"object_to_goal_dist_start":0.11846,"object_z_max":0.04149,"peak_contact_force":2.08273,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":2.08273,"subtask_id":"reach_goal","tcp_end":[0.49155,0.08441,0.04522],"tcp_start":[0.49281,0.08535,0.04668],"tcp_to_object_dist_end":0.05796,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":488.0,"n_steps_budget":1000.0,"object_pos_end":[0.50497,-0.07828,0.0292],"object_pos_start":[0.5033,0.02795,0.03952],"object_to_goal_dist_end":0.01201,"object_to_goal_dist_start":0.108,"object_z_max":0.03952,"peak_contact_force":145.41733,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1174.0,"raw_peak_contact_force":145.54166,"subtask_id":"reach_goal","tcp_end":[0.48792,-0.04941,0.03939],"tcp_start":[0.49155,0.08441,0.04522],"tcp_to_object_dist_end":0.03504,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31073,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11473,"contact_1.contact_force":8.27822,"descend_1.descend_height":1e-05,"push_1.push_distance":0.14795,"push_1.push_speed":0.03226,"push_1.retry_offset_x":0.00977},"optimized_scores":{"best_composite_score":0.19414,"best_fitness_score":0.55414,"best_task_score":0.15861},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":423.0,"contact_point_centroid":[0.49565,0.05993,0.00921],"force_p95":128.04876,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":180.10639,"mean_force":18.76285,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47627,0.083,0.10069]},{"body_a":"attachment","body_b":"peg","contact_count":69.0,"contact_point_centroid":[0.49652,0.07595,0.05547],"force_p95":152.04219,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":179.57356,"mean_force":111.80446,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48719,0.08083,0.05809]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":842.0,"contact_point_centroid":[0.53293,-0.03061,0.05998],"force_p95":155.35017,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":170.33001,"mean_force":119.48816,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4879,-0.02654,0.03772]},{"body_a":"attachment","body_b":"peg","contact_count":861.0,"contact_point_centroid":[0.49285,-0.03789,0.04233],"force_p95":111.29676,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":139.16414,"mean_force":67.64296,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48792,-0.02752,0.03773]},{"body_a":"peg","body_b":"channel_base_body","contact_count":585.0,"contact_point_centroid":[0.4923,-0.10178,0.03576],"force_p95":109.24565,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":118.05738,"mean_force":92.03325,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4884,-0.0449,0.03759]},{"body_a":"peg","body_b":"channel_base_body","contact_count":945.0,"contact_point_centroid":[0.50584,-0.07358,0.00969],"force_p95":21.83103,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.7333,"mean_force":8.32661,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48782,-0.02409,0.03775]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":646.0,"contact_point_centroid":[0.52527,-0.08681,0.02781],"force_p95":16.98792,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.68755,"mean_force":11.54903,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48817,-0.03402,0.03766]},{"body_a":"peg","body_b":"channel_base_body","contact_count":551.0,"contact_point_centroid":[0.49434,0.05904,0.00935],"force_p95":0.56809,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57277,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48177,0.14112,0.22584]},{"body_a":"peg","body_b":"channel_base_body","contact_count":459.0,"contact_point_centroid":[0.50128,0.01114,0.00827],"force_p95":0.85912,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83908,"mean_force":0.62366,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48657,0.06424,0.03845]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49874,0.19736,0.29644]}],"total_contact_groups":10},"final_pose_error":0.04924,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50551,-0.07764,0.02915],"final_tcp_position":[0.48946,-0.04687,0.03744],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":180.10639,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":580.0,"n_steps_budget":1000.0,"object_pos_end":[0.49402,0.05888,0.03387],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.55099,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":586.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_approach","tcp_end":[0.46629,0.08691,0.1605],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13262,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":438.0,"n_steps_budget":810.0,"object_pos_end":[0.5005,0.02229,0.04041],"object_pos_start":[0.49402,0.05888,0.03387],"object_to_goal_dist_end":0.10229,"object_to_goal_dist_start":0.13914,"object_z_max":0.04169,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":492.0,"raw_peak_contact_force":180.10639,"subtask_id":"reach_descend","tcp_end":[0.49042,0.08004,0.04291],"tcp_start":[0.46629,0.08691,0.1605],"tcp_to_object_dist_end":0.05867,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":476.0,"n_steps_budget":600.0,"object_pos_end":[0.50099,0.01541,0.02416],"object_pos_start":[0.5005,0.02229,0.04041],"object_to_goal_dist_end":0.09672,"object_to_goal_dist_start":0.10229,"object_z_max":0.04041,"peak_contact_force":0.65659,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":459.0,"raw_peak_contact_force":3.83908,"subtask_id":"reach_goal","tcp_end":[0.48629,0.05195,0.03815],"tcp_start":[0.49042,0.08004,0.04291],"tcp_to_object_dist_end":0.0418,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50551,-0.07764,0.02915],"object_pos_start":[0.50099,0.01541,0.02416],"object_to_goal_dist_end":0.0124,"object_to_goal_dist_start":0.09672,"object_z_max":0.03047,"peak_contact_force":163.98653,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3879.0,"raw_peak_contact_force":170.33001,"subtask_id":"reach_goal","tcp_end":[0.48946,-0.04687,0.03744],"tcp_start":[0.48629,0.05195,0.03815],"tcp_to_object_dist_end":0.03569,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```