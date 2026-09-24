## Search State

- **Seed**: 1
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0075 | 0.00 | ❌ rejected |
| 12 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.3806 | 0.33 | ❌ rejected |
| 11 | approach → descend → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0381 | 0.07 | ❌ rejected |
| 10 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.3281 | 0.22 | ❌ rejected |
| 9 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.0181 | 0.00 | ❌ rejected |

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

## Current Skill (Q=0.007) — your mutation base

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

- **Composite score**: 0.007
- **task_score** (E): 0.000
- **fitness_score**: 0.201  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1851 |
| descend_1 | 1.00 | 1.00 | 0.0970 |
| contact_1 | 0.67 | 1.00 | 0.0082 |
| push_1 | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.481, 0.115, 0.138) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.540 | 2.857 |
| descend_1 | descend | 1.00 / step_budget | (0.481, 0.115, 0.138)→(0.491, 0.110, 0.043) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.667 | 1.466 | 96.463 |
| contact_1 | contact | 0.67 / force_exceeded | (0.491, 0.110, 0.043)→(0.488, 0.115, 0.039) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.667 | 5.918 | 6.946 |
| push_1 | push | 0.00 / guard_failure | (0.487, 0.122, 0.037)→(0.487, 0.122, 0.037) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.667 | 34.639 | 59.775 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.338
- phase_breakdown.reach_goal_score: 0.000
- phase_breakdown.reach_descend_score: 0.841
- phase_breakdown.reach_approach_score: 0.847

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.217
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: 0.072
- **K-run variance**: 0.0113
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.297


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14545,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09177,"contact_1.contact_force":3.89489,"descend_1.descend_height":8e-05,"push_1.push_distance":0.17101,"push_1.push_speed":0.02528,"push_1.retry_offset_x":0.01388},"optimized_scores":{"best_composite_score":-0.14276,"best_fitness_score":0.21724,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.55327,0.12,0.05999],"force_p95":74.00382,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.4086,"mean_force":65.01612,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48991,0.17677,0.03388]},{"body_a":"peg","body_b":"channel_base_body","contact_count":305.0,"contact_point_centroid":[0.50103,0.11467,0.00942],"force_p95":0.62713,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.40973,"mean_force":0.583,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49619,0.14726,0.09165]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50029,0.13383,0.05636],"force_p95":3.57246,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.1781,"mean_force":1.86051,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49659,0.14575,0.04903]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.50159,0.13476,0.05698],"force_p95":1.53416,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.63956,"mean_force":0.40335,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49458,0.14645,0.04024]},{"body_a":"peg","body_b":"channel_base_body","contact_count":426.0,"contact_point_centroid":[0.50104,0.11514,0.00943],"force_p95":0.61712,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.30575,"mean_force":0.54753,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49299,0.15186,0.03827]},{"body_a":"peg","body_b":"channel_base_body","contact_count":493.0,"contact_point_centroid":[0.50096,0.11598,0.00938],"force_p95":0.62118,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55939,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4981,0.17421,0.21787]},{"body_a":"peg","body_b":"channel_base_body","contact_count":66.0,"contact_point_centroid":[0.50102,0.11591,0.00945],"force_p95":0.59644,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64992,"mean_force":0.5381,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4911,0.16578,0.03548]}],"total_contact_groups":7},"final_pose_error":0.15143,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50097,0.11638,0.0341],"final_tcp_position":[0.48988,0.17724,0.0339],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":75.4086,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":509.0,"n_steps_budget":1000.0,"object_pos_end":[0.50096,0.11614,0.03404],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19623,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.52478,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":493.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_approach","tcp_end":[0.49779,0.14955,0.1405],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11162,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":305.0,"n_steps_budget":690.0,"object_pos_end":[0.50044,0.11575,0.0342],"object_pos_start":[0.50096,0.11614,0.03404],"object_to_goal_dist_end":0.19583,"object_to_goal_dist_start":0.19623,"object_z_max":0.0342,"peak_contact_force":2.45845,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":313.0,"raw_peak_contact_force":4.40973,"subtask_id":"reach_descend","tcp_end":[0.49666,0.14553,0.04293],"tcp_start":[0.49779,0.14955,0.1405],"tcp_to_object_dist_end":0.03127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.50097,0.1162,0.03387],"object_pos_start":[0.50044,0.11575,0.0342],"object_to_goal_dist_end":0.1963,"object_to_goal_dist_start":0.19583,"object_z_max":0.03498,"peak_contact_force":0.5549,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":440.0,"raw_peak_contact_force":3.63956,"subtask_id":"reach_goal","tcp_end":[0.49258,0.15759,0.03774],"tcp_start":[0.49666,0.14553,0.04293],"tcp_to_object_dist_end":0.04241,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":66.0,"n_steps_budget":1000.0,"object_pos_end":[0.50095,0.11636,0.03407],"object_pos_start":[0.50097,0.1162,0.03387],"object_to_goal_dist_end":0.19645,"object_to_goal_dist_start":0.1963,"object_z_max":0.03409,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":69.0,"raw_peak_contact_force":75.4086,"subtask_id":"reach_goal","tcp_end":[0.48988,0.17724,0.0339],"tcp_start":[0.4899,0.17704,0.03388],"tcp_to_object_dist_end":0.06188,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51948,"average_solve_count":77.0,"average_success_count":77.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08821,"contact_1.contact_force":2.7975,"descend_1.descend_height":3e-05,"push_1.push_distance":0.18482,"push_1.push_speed":0.02203,"push_1.retry_offset_x":0.00841},"optimized_scores":{"best_composite_score":0.09262,"best_fitness_score":0.20262,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53114,0.09902,0.05998],"force_p95":67.99833,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":68.13681,"mean_force":66.63921,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48581,0.0979,0.03758]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53116,0.09896,0.05999],"force_p95":7.90225,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7.90225,"mean_force":7.90225,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48583,0.09785,0.0376]},{"body_a":"peg","body_b":"channel_base_body","contact_count":574.0,"contact_point_centroid":[0.49535,0.0638,0.00937],"force_p95":0.57968,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56036,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48846,0.14848,0.2134]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49922,0.19824,0.29716]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.49492,0.08199,0.05287],"force_p95":0.85049,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.97817,"mean_force":0.30385,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48923,0.09385,0.04153]},{"body_a":"peg","body_b":"channel_base_body","contact_count":91.0,"contact_point_centroid":[0.49432,0.06439,0.00937],"force_p95":0.6617,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.81731,"mean_force":0.54672,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48701,0.09584,0.03894]},{"body_a":"peg","body_b":"channel_base_body","contact_count":316.0,"contact_point_centroid":[0.49526,0.06376,0.0094],"force_p95":0.551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59376,"mean_force":0.54607,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48308,0.09703,0.08825]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49085,0.04727,0.00938],"force_p95":0.55376,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55481,"mean_force":0.54461,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48581,0.0979,0.03758]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49462,0.0824,0.0588],"force_p95":0.26088,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26088,"mean_force":0.26088,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48864,0.09425,0.04697]}],"total_contact_groups":9},"final_pose_error":0.18476,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49539,0.06397,0.03386],"final_tcp_position":[0.4858,0.09794,0.03756],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":68.13681,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":601.0,"n_steps_budget":1000.0,"object_pos_end":[0.49529,0.06379,0.03395],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.144,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54803,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":602.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_approach","tcp_end":[0.47912,0.1005,0.13534],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":316.0,"n_steps_budget":660.0,"object_pos_end":[0.49533,0.06397,0.03396],"object_pos_start":[0.49529,0.06379,0.03395],"object_to_goal_dist_end":0.14417,"object_to_goal_dist_start":0.144,"object_z_max":0.034,"peak_contact_force":1.3892,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":317.0,"raw_peak_contact_force":0.59376,"subtask_id":"reach_descend","tcp_end":[0.4894,0.0939,0.04181],"tcp_start":[0.47912,0.1005,0.13534],"tcp_to_object_dist_end":0.03151,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":91.0,"n_steps_budget":600.0,"object_pos_end":[0.49527,0.06397,0.03386],"object_pos_start":[0.49533,0.06397,0.03396],"object_to_goal_dist_end":0.14418,"object_to_goal_dist_start":0.14417,"object_z_max":0.03396,"peak_contact_force":7.90225,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":96.0,"raw_peak_contact_force":7.90225,"subtask_id":"reach_goal","tcp_end":[0.48582,0.09788,0.03759],"tcp_start":[0.4894,0.0939,0.04181],"tcp_to_object_dist_end":0.03539,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.4953,0.06395,0.03386],"object_pos_start":[0.49527,0.06397,0.03386],"object_to_goal_dist_end":0.14416,"object_to_goal_dist_start":0.14418,"object_z_max":0.03386,"peak_contact_force":68.13681,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":68.13681,"subtask_id":"reach_goal","tcp_end":[0.4858,0.09794,0.03756],"tcp_start":[0.4858,0.09793,0.03757],"tcp_to_object_dist_end":0.03549,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56579,"average_solve_count":76.0,"average_success_count":76.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0925,"contact_1.contact_force":3.24426,"descend_1.descend_height":0.00188,"push_1.push_distance":0.15711,"push_1.push_speed":0.01643,"push_1.retry_offset_x":0.00892},"optimized_scores":{"best_composite_score":0.0725,"best_fitness_score":0.1825,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.47486,0.0935,0.05963],"force_p95":280.97544,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":284.3859,"mean_force":162.91607,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48476,0.08997,0.05457]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47496,0.09096,0.0458],"force_p95":35.59091,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.77945,"mean_force":33.51539,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48568,0.09089,0.04048]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.09088,0.04588],"force_p95":9.29638,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":9.29638,"mean_force":9.29638,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48573,0.09081,0.04056]},{"body_a":"peg","body_b":"channel_base_body","contact_count":573.0,"contact_point_centroid":[0.49433,0.05889,0.00936],"force_p95":0.56629,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57173,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4817,0.14591,0.2152]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49879,0.19764,0.2962]},{"body_a":"peg","body_b":"channel_base_body","contact_count":354.0,"contact_point_centroid":[0.49417,0.05892,0.00939],"force_p95":0.55016,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54601,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4756,0.0923,0.09021]},{"body_a":"peg","body_b":"channel_base_body","contact_count":36.0,"contact_point_centroid":[0.49295,0.05959,0.00939],"force_p95":0.54984,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5505,"mean_force":0.54559,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48668,0.08979,0.04163]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50967,0.05128,0.00939],"force_p95":0.54956,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54961,"mean_force":0.54896,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48568,0.09089,0.04048]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49391,0.07727,0.05557],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48747,0.08909,0.04255]}],"total_contact_groups":9},"final_pose_error":0.15703,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49431,0.05899,0.03393],"final_tcp_position":[0.48564,0.09093,0.0404],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":284.3859,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":602.0,"n_steps_budget":1000.0,"object_pos_end":[0.49425,0.05892,0.03388],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13918,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54868,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":608.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_approach","tcp_end":[0.46607,0.0959,0.13949],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1154,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":354.0,"n_steps_budget":690.0,"object_pos_end":[0.49431,0.05898,0.03392],"object_pos_start":[0.49425,0.05892,0.03388],"object_to_goal_dist_end":0.13923,"object_to_goal_dist_start":0.13918,"object_z_max":0.03392,"peak_contact_force":0.54999,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":367.0,"raw_peak_contact_force":284.3859,"subtask_id":"reach_descend","tcp_end":[0.488,0.08924,0.04328],"tcp_start":[0.46607,0.0959,0.13949],"tcp_to_object_dist_end":0.03229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":36.0,"n_steps_budget":600.0,"object_pos_end":[0.49426,0.05883,0.03393],"object_pos_start":[0.49431,0.05898,0.03392],"object_to_goal_dist_end":0.13908,"object_to_goal_dist_start":0.13923,"object_z_max":0.03393,"peak_contact_force":9.29638,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":40.0,"raw_peak_contact_force":9.29638,"subtask_id":"reach_goal","tcp_end":[0.4857,0.09086,0.04052],"tcp_start":[0.488,0.08924,0.04328],"tcp_to_object_dist_end":0.0338,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49429,0.05887,0.03393],"object_pos_start":[0.49426,0.05883,0.03393],"object_to_goal_dist_end":0.13912,"object_to_goal_dist_start":0.13908,"object_z_max":0.03393,"peak_contact_force":35.77945,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":35.77945,"subtask_id":"reach_goal","tcp_end":[0.48564,0.09093,0.0404],"tcp_start":[0.48566,0.09092,0.04044],"tcp_to_object_dist_end":0.03383,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```