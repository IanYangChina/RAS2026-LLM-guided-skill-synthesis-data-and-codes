## Search State

- **Seed**: 1
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.5374 | 0.40 | ✅ accepted |
| 6 | approach → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0851 | 0.00 | ❌ rejected |
| 5 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.2667 | 0.00 | ❌ rejected |
| 4 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | -0.0335 | 0.10 | ❌ rejected |
| 3 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.2538 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.40 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.537) — your mutation base

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

- **Composite score**: 0.537
- **task_score** (E): 0.398
- **fitness_score**: 0.597  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1844 |
| descend_1 | 1.00 | 1.00 | 0.0976 |
| contact_1 | 1.00 | 1.00 | 0.0151 |
| push_1 | 1.00 | 1.00 | 0.1162 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.481, 0.106, 0.145) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.554 | 2.857 |
| descend_1 | descend | 1.00 / step_budget | (0.481, 0.106, 0.145)→(0.493, 0.101, 0.048) | (0.497, 0.080, 0.034)→(0.501, 0.060, 0.037) | 0.160→0.140 | 1.00 / 1.333 | 32.727 | 158.446 |
| contact_1 | contact | 1.00 / force_exceeded | (0.493, 0.101, 0.048)→(0.494, 0.087, 0.044) | (0.501, 0.060, 0.037)→(0.500, 0.047, 0.027) | 0.140→0.128 | 1.00 / 2.333 | 43.548 | 43.548 |
| push_1 | push | 1.00 / step_budget | (0.494, 0.087, 0.044)→(0.494, -0.029, 0.042) | (0.500, 0.047, 0.027)→(0.498, -0.038, 0.028) | 0.128→0.048 | 1.00 / 3.333 | 88.886 | 136.008 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.894
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.536
- phase_score: 0.810
- phase_breakdown.reach_goal_score: 0.865
- phase_breakdown.reach_descend_score: 0.768
- phase_breakdown.reach_approach_score: 0.687

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.700
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.536
- **Median Q (composite search score)**: 0.509
- **K-run variance**: 0.0057
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.248


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.93296,"average_solve_count":179.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08974,"contact_1.contact_force":7.27863,"descend_1.descend_height":0.01435,"push_1.push_distance":0.15491,"push_1.push_speed":0.02339},"optimized_scores":{"best_composite_score":0.46242,"best_fitness_score":0.52242,"best_task_score":0.47842},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":261.0,"contact_point_centroid":[0.50179,0.11643,0.00939],"force_p95":92.12345,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":107.7502,"mean_force":8.44608,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49631,0.13781,0.09669]},{"body_a":"attachment","body_b":"peg","contact_count":26.0,"contact_point_centroid":[0.50792,0.13378,0.05667],"force_p95":97.361,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":107.0383,"mean_force":79.42137,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49722,0.13664,0.06023]},{"body_a":"peg","body_b":"channel_base_body","contact_count":403.0,"contact_point_centroid":[0.50506,0.079,0.00885],"force_p95":96.65358,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":99.22539,"mean_force":66.66584,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49901,0.07719,0.05818]},{"body_a":"attachment","body_b":"peg","contact_count":354.0,"contact_point_centroid":[0.50857,0.08895,0.056],"force_p95":96.29154,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":98.92648,"mean_force":75.37055,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49939,0.08582,0.05868]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.4889,0.11987,0.0086],"force_p95":86.31101,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":86.31101,"mean_force":86.31101,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49812,0.13749,0.05761]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50884,0.13485,0.05449],"force_p95":85.83536,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.83536,"mean_force":85.83536,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49812,0.13749,0.05761]},{"body_a":"peg","body_b":"channel_base_body","contact_count":511.0,"contact_point_centroid":[0.501,0.11606,0.00937],"force_p95":0.61898,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55965,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49808,0.16953,0.21671]}],"total_contact_groups":7},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49604,0.03949,0.02624],"final_tcp_position":[0.49521,0.00199,0.05349],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":107.7502,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":527.0,"n_steps_budget":1000.0,"object_pos_end":[0.50087,0.11612,0.03382],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19622,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.56843,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":511.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_approach","tcp_end":[0.49776,0.14024,0.13818],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":261.0,"n_steps_budget":600.0,"object_pos_end":[0.50145,0.11662,0.03261],"object_pos_start":[0.50087,0.11612,0.03382],"object_to_goal_dist_end":0.19676,"object_to_goal_dist_start":0.19622,"object_z_max":0.03397,"peak_contact_force":97.47555,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":287.0,"raw_peak_contact_force":107.7502,"subtask_id":"reach_descend","tcp_end":[0.49812,0.13749,0.05761],"tcp_start":[0.49776,0.14024,0.13818],"tcp_to_object_dist_end":0.03274,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50138,0.11663,0.0326],"object_pos_start":[0.50145,0.11662,0.03261],"object_to_goal_dist_end":0.19677,"object_to_goal_dist_start":0.19676,"object_z_max":0.03261,"peak_contact_force":86.31101,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":86.31101,"subtask_id":"reach_goal","tcp_end":[0.49811,0.13753,0.05754],"tcp_start":[0.49812,0.13749,0.05761],"tcp_to_object_dist_end":0.03271,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.49604,0.03949,0.02624],"object_pos_start":[0.50138,0.11663,0.0326],"object_to_goal_dist_end":0.12035,"object_to_goal_dist_start":0.19677,"object_z_max":0.03984,"peak_contact_force":0.74677,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":757.0,"raw_peak_contact_force":99.22539,"subtask_id":"reach_goal","tcp_end":[0.49521,0.00199,0.05349],"tcp_start":[0.49811,0.13753,0.05754],"tcp_to_object_dist_end":0.04636,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39568,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11107,"contact_1.contact_force":8.9567,"descend_1.descend_height":0.00238,"push_1.push_distance":0.13477,"push_1.push_speed":0.04912},"optimized_scores":{"best_composite_score":0.64044,"best_fitness_score":0.70044,"best_task_score":0.53618},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":389.0,"contact_point_centroid":[0.4968,0.06461,0.00925],"force_p95":138.32269,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":187.4505,"mean_force":18.87263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48394,0.08773,0.09935]},{"body_a":"attachment","body_b":"peg","contact_count":63.0,"contact_point_centroid":[0.49964,0.08037,0.05567],"force_p95":161.91865,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":186.84066,"mean_force":113.31504,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49054,0.08573,0.05823]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":594.0,"contact_point_centroid":[0.54264,-0.02195,0.05998],"force_p95":154.12752,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":164.44638,"mean_force":120.65509,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49801,-0.0202,0.03673]},{"body_a":"attachment","body_b":"peg","contact_count":492.0,"contact_point_centroid":[0.50229,-0.03809,0.04412],"force_p95":104.50576,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":123.8975,"mean_force":59.90802,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49821,-0.02726,0.03668]},{"body_a":"peg","body_b":"channel_base_body","contact_count":329.0,"contact_point_centroid":[0.50128,-0.10171,0.04305],"force_p95":104.60972,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":123.2009,"mean_force":87.17023,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49869,-0.0447,0.03653]},{"body_a":"peg","body_b":"channel_base_body","contact_count":672.0,"contact_point_centroid":[0.49933,-0.06288,0.00959],"force_p95":12.96372,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.20682,"mean_force":2.59059,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49788,-0.01542,0.03678]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54147,0.04726,0.06],"force_p95":22.08894,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":22.08894,"mean_force":22.08894,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49645,0.04901,0.03704]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.4749,-0.08189,0.02749],"force_p95":11.91456,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.46935,"mean_force":3.82843,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49775,-0.03476,0.03675]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":54.0,"contact_point_centroid":[0.52505,-0.04404,0.02651],"force_p95":9.03833,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.0212,"mean_force":3.98526,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49712,0.01579,0.03701]},{"body_a":"peg","body_b":"channel_base_body","contact_count":419.0,"contact_point_centroid":[0.50206,0.01573,0.00829],"force_p95":0.89922,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.44134,"mean_force":0.71689,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49307,0.06591,0.03929]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52505,-0.00244,0.03034],"force_p95":6.66132,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.22628,"mean_force":2.08803,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49348,0.06609,0.03981]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.50078,0.03825,0.04285],"force_p95":4.13151,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.18921,"mean_force":1.47539,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4962,0.05008,0.03716]},{"body_a":"peg","body_b":"channel_base_body","contact_count":546.0,"contact_point_centroid":[0.49537,0.06399,0.00937],"force_p95":0.58292,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56114,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48854,0.14377,0.22436]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52523,0.02719,0.05656],"force_p95":1.49947,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.60895,"mean_force":0.83603,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49298,0.08521,0.04712]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49918,0.198,0.29729]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":14.0,"contact_point_centroid":[0.47484,0.03636,0.02767],"force_p95":0.90071,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.93685,"mean_force":0.49874,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49094,0.08014,0.04195]}],"total_contact_groups":16},"final_pose_error":0.0397,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49615,-0.07917,0.02799],"final_tcp_position":[0.49934,-0.04625,0.03644],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":187.4505,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":1000.0,"object_pos_end":[0.49492,0.06375,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14397,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55002,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":574.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_approach","tcp_end":[0.47932,0.09157,0.15703],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":397.0,"n_steps_budget":780.0,"object_pos_end":[0.50296,0.03888,0.04082],"object_pos_start":[0.49492,0.06375,0.03394],"object_to_goal_dist_end":0.11892,"object_to_goal_dist_start":0.14397,"object_z_max":0.04111,"peak_contact_force":0.33351,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":460.0,"raw_peak_contact_force":187.4505,"subtask_id":"reach_descend","tcp_end":[0.49274,0.085,0.04575],"tcp_start":[0.47932,0.09157,0.15703],"tcp_to_object_dist_end":0.0475,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":429.0,"n_steps_budget":600.0,"object_pos_end":[0.50375,0.01224,0.0253],"object_pos_start":[0.50296,0.03888,0.04082],"object_to_goal_dist_end":0.09348,"object_to_goal_dist_start":0.11892,"object_z_max":0.04082,"peak_contact_force":22.08894,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":469.0,"raw_peak_contact_force":22.08894,"subtask_id":"reach_goal","tcp_end":[0.49648,0.04893,0.03704],"tcp_start":[0.49274,0.085,0.04575],"tcp_to_object_dist_end":0.0392,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":733.0,"n_steps_budget":1000.0,"object_pos_end":[0.49615,-0.07917,0.02799],"object_pos_start":[0.50375,0.01224,0.0253],"object_to_goal_dist_end":0.01264,"object_to_goal_dist_start":0.09348,"object_z_max":0.02954,"peak_contact_force":158.44587,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2151.0,"raw_peak_contact_force":164.44638,"subtask_id":"reach_goal","tcp_end":[0.49934,-0.04625,0.03644],"tcp_start":[0.49648,0.04893,0.03704],"tcp_to_object_dist_end":0.03414,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33742,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0927,"contact_1.contact_force":7.71211,"descend_1.descend_height":3e-05,"push_1.push_distance":0.14118,"push_1.push_speed":0.03104},"optimized_scores":{"best_composite_score":0.50935,"best_fitness_score":0.56935,"best_task_score":0.17915},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":356.0,"contact_point_centroid":[0.49576,0.05848,0.00928],"force_p95":120.81452,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":180.13701,"mean_force":15.17676,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47564,0.08279,0.09003]},{"body_a":"attachment","body_b":"peg","contact_count":51.0,"contact_point_centroid":[0.49364,0.07586,0.05636],"force_p95":157.23877,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":179.64417,"mean_force":102.31148,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4844,0.08103,0.05927]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":563.0,"contact_point_centroid":[0.53286,-0.00277,0.05998],"force_p95":135.91565,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":144.35144,"mean_force":115.32339,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48762,3e-05,0.03785]},{"body_a":"attachment","body_b":"peg","contact_count":456.0,"contact_point_centroid":[0.49468,-0.02621,0.04468],"force_p95":90.6993,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":125.5166,"mean_force":36.01238,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48786,-0.0153,0.03783]},{"body_a":"peg","body_b":"channel_base_body","contact_count":207.0,"contact_point_centroid":[0.49207,-0.10121,0.03259],"force_p95":86.50467,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":103.30934,"mean_force":65.97471,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48828,-0.0413,0.03765]},{"body_a":"peg","body_b":"channel_base_body","contact_count":683.0,"contact_point_centroid":[0.50318,-0.04421,0.00934],"force_p95":24.24749,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.08347,"mean_force":7.14935,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48759,0.00225,0.03786]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53197,0.07341,0.06],"force_p95":22.24512,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":22.24512,"mean_force":22.24512,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48652,0.07362,0.03783]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":335.0,"contact_point_centroid":[0.5252,-0.07564,0.02781],"force_p95":17.68056,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.70248,"mean_force":9.67986,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48798,-0.02253,0.03778]},{"body_a":"peg","body_b":"channel_base_body","contact_count":597.0,"contact_point_centroid":[0.49441,0.05902,0.00936],"force_p95":0.56412,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57071,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48161,0.14087,0.21494]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49879,0.19752,0.29627]},{"body_a":"peg","body_b":"channel_base_body","contact_count":59.0,"contact_point_centroid":[0.49488,0.01385,0.00873],"force_p95":2.01084,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.57068,"mean_force":0.70432,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48699,0.07664,0.03928]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47496,0.03605,0.02812],"force_p95":1.15899,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.64505,"mean_force":0.61028,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48703,0.0776,0.03961]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52527,0.01839,0.05424],"force_p95":1.29032,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.41869,"mean_force":0.7022,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48811,0.08045,0.04708]}],"total_contact_groups":13},"final_pose_error":0.02353,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5026,-0.07445,0.03052],"final_tcp_position":[0.48848,-0.04421,0.03756],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":180.13701,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":626.0,"n_steps_budget":1000.0,"object_pos_end":[0.49402,0.05904,0.03388],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.1393,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54246,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":632.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_approach","tcp_end":[0.46596,0.08628,0.1392],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11235,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":365.0,"n_steps_budget":690.0,"object_pos_end":[0.4996,0.02568,0.03745],"object_pos_start":[0.49402,0.05904,0.03388],"object_to_goal_dist_end":0.10571,"object_to_goal_dist_start":0.1393,"object_z_max":0.04064,"peak_contact_force":0.37197,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":418.0,"raw_peak_contact_force":180.13701,"subtask_id":"reach_descend","tcp_end":[0.48853,0.07984,0.04203],"tcp_start":[0.46596,0.08628,0.1392],"tcp_to_object_dist_end":0.05547,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":66.0,"n_steps_budget":600.0,"object_pos_end":[0.49485,0.01232,0.02424],"object_pos_start":[0.4996,0.02568,0.03745],"object_to_goal_dist_end":0.0938,"object_to_goal_dist_start":0.10571,"object_z_max":0.03745,"peak_contact_force":22.24512,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":71.0,"raw_peak_contact_force":22.24512,"subtask_id":"reach_goal","tcp_end":[0.48652,0.07352,0.0378],"tcp_start":[0.48853,0.07984,0.04203],"tcp_to_object_dist_end":0.06324,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":734.0,"n_steps_budget":1000.0,"object_pos_end":[0.5026,-0.07445,0.03052],"object_pos_start":[0.49485,0.01232,0.02424],"object_to_goal_dist_end":0.01129,"object_to_goal_dist_start":0.0938,"object_z_max":0.03064,"peak_contact_force":107.4643,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2244.0,"raw_peak_contact_force":144.35144,"subtask_id":"reach_goal","tcp_end":[0.48848,-0.04421,0.03756],"tcp_start":[0.48652,0.07352,0.0378],"tcp_to_object_dist_end":0.03411,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```