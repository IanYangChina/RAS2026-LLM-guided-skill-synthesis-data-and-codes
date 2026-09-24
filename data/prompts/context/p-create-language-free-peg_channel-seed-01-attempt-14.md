## Search State

- **Seed**: 1
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 5 | -0.0359 | 0.03 | ❌ rejected |
| 13 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0075 | 0.00 | ❌ rejected |
| 12 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.3806 | 0.33 | ❌ rejected |
| 11 | approach → descend → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0381 | 0.07 | ❌ rejected |
| 10 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.3281 | 0.22 | ❌ rejected |

**Proposal policy**: task_score is 0.03 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.036) — your mutation base

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

- **Composite score**: -0.036
- **task_score** (E): 0.030
- **fitness_score**: 0.024  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1457 |
| align_1 | 0.00 | 1.00 | 0.0884 |
| contact_1 | 1.00 | 1.00 | 0.0001 |
| push_1 | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, 0.200, 0.300)→(0.527, 0.148, 0.243) | (0.483, 0.080, 0.040)→(0.498, 0.080, 0.035) | 0.161→0.160 | 1.00 / 2.667 | 547.560 | 2030.301 |
| align_1 | align | 0.00 / step_budget | (0.527, 0.148, 0.243)→(0.482, 0.075, 0.234) | (0.498, 0.080, 0.035)→(0.504, 0.061, 0.035) | 0.160→0.141 | 1.00 / 3.000 | 478.923 | 502.820 |
| contact_1 | contact | 1.00 / force_exceeded | (0.482, 0.075, 0.234)→(0.482, 0.075, 0.234) | (0.504, 0.061, 0.035)→(0.504, 0.061, 0.035) | 0.141→0.141 | 1.00 / 3.000 | 243.645 | 243.645 |
| push_1 | push | 0.00 / guard_failure | (0.482, 0.075, 0.234)→(0.482, 0.075, 0.234) | (0.504, 0.061, 0.035)→(0.504, 0.061, 0.035) | 0.141→0.141 | 1.00 / 3.000 | 94.216 | 104.759 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.154
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.052
- phase_score: 0.011
- phase_breakdown.reach_goal_score: 0.000
- phase_breakdown.reach_approach_score: 0.054

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.027
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.052
- **Median Q (composite search score)**: -0.037
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.386


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89474,"average_solve_count":76.0,"average_success_count":76.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_z":0.11054,"approach_1.approach_height":0.09797,"contact_1.contact_force":4.71254,"push_1.force_threshold":5.9793,"push_1.push_speed":0.03778},"optimized_scores":{"best_composite_score":-0.03759,"best_fitness_score":0.02241,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link6","contact_count":575.0,"contact_point_centroid":[0.5332,0.11054,0.05966],"force_p95":529.90517,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1395.21175,"mean_force":440.82685,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.59122,0.25988,0.18827]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":235.0,"contact_point_centroid":[0.47499,-0.01701,0.05997],"force_p95":180.17937,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":197.57321,"mean_force":134.67914,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.58222,0.14167,0.1612]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.47499,-0.03386,0.05998],"force_p95":183.26313,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":185.83428,"mean_force":166.4638,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.57528,0.12549,0.1644]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":578.0,"contact_point_centroid":[0.52704,0.06602,0.05998],"force_p95":160.00524,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":174.50541,"mean_force":130.378,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.612,0.22239,0.16457]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.47499,-0.03356,0.05998],"force_p95":143.75186,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":143.75186,"mean_force":143.75186,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.57525,0.12578,0.16453]},{"body_a":"peg","body_b":"channel_base_body","contact_count":647.0,"contact_point_centroid":[0.50117,0.11659,0.00941],"force_p95":0.74784,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.63899,"mean_force":0.68223,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.57689,0.25395,0.18726]},{"body_a":"peg","body_b":"link6","contact_count":42.0,"contact_point_centroid":[0.51649,0.116,0.05618],"force_p95":10.7233,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.22427,"mean_force":2.02774,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43255,0.26799,0.14112]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50059,0.11596,0.00943],"force_p95":0.60112,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6652,"mean_force":0.54178,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.60333,0.19892,0.16349]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.517,0.12,0.00946],"force_p95":0.60075,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60075,"mean_force":0.60075,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.57525,0.12578,0.16453]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50662,0.12,0.00945],"force_p95":0.57666,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57871,"mean_force":0.55289,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.57528,0.12549,0.1644]}],"total_contact_groups":10},"final_pose_error":0.23434,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50069,0.11619,0.03393],"final_tcp_position":[0.5753,0.12528,0.16431],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":1395.21175,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":663.0,"n_steps_budget":1000.0,"object_pos_end":[0.50071,0.11619,0.03403],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19628,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":393.09411,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1264.0,"raw_peak_contact_force":1395.21175,"subtask_id":"reach_approach","tcp_end":[0.63651,0.26806,0.1634],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.24134,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50072,0.11611,0.03394],"object_pos_start":[0.50071,0.11619,0.03403],"object_to_goal_dist_end":0.19621,"object_to_goal_dist_start":0.19628,"object_z_max":0.03403,"peak_contact_force":180.16667,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1813.0,"raw_peak_contact_force":197.57321,"subtask_id":"reach_approach","tcp_end":[0.57525,0.12578,0.16453],"tcp_start":[0.63651,0.26806,0.1634],"tcp_to_object_dist_end":0.15067,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":720.0,"object_pos_end":[0.50073,0.11614,0.03393],"object_pos_start":[0.50072,0.11611,0.03394],"object_to_goal_dist_end":0.19623,"object_to_goal_dist_start":0.19621,"object_z_max":0.03394,"peak_contact_force":143.75186,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":143.75186,"subtask_id":"reach_goal","tcp_end":[0.57527,0.12561,0.16446],"tcp_start":[0.57525,0.12578,0.16453],"tcp_to_object_dist_end":0.15061,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50072,0.11616,0.03393],"object_pos_start":[0.50073,0.11614,0.03393],"object_to_goal_dist_end":0.19625,"object_to_goal_dist_start":0.19623,"object_z_max":0.03393,"peak_contact_force":160.12281,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":185.83428,"subtask_id":"reach_goal","tcp_end":[0.5753,0.12528,0.16431],"tcp_start":[0.5753,0.12536,0.16435],"tcp_to_object_dist_end":0.15048,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.22222,"average_solve_count":72.0,"average_success_count":72.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_z":0.08463,"approach_1.approach_height":0.13999,"contact_1.contact_force":5.65632,"push_1.force_threshold":18.46125,"push_1.push_speed":0.02771},"optimized_scores":{"best_composite_score":-0.03278,"best_fitness_score":0.02722,"best_task_score":0.05169},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link6","contact_count":71.0,"contact_point_centroid":[0.4745,0.11398,0.05918],"force_p95":1100.52183,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1747.59769,"mean_force":393.37685,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46165,0.23587,0.21331]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":647.0,"contact_point_centroid":[0.52503,0.10689,0.05989],"force_p95":709.91166,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1501.50936,"mean_force":615.47857,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51375,0.17221,0.26472]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":999.0,"contact_point_centroid":[0.52503,0.08615,0.05993],"force_p95":643.65108,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":659.73566,"mean_force":577.32312,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45034,0.07793,0.27611]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.52504,0.0862,0.05994],"force_p95":290.52914,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":290.52914,"mean_force":290.52914,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.43528,0.05363,0.269]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":429.0,"contact_point_centroid":[0.475,0.09838,0.06],"force_p95":264.79944,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":282.69705,"mean_force":160.92109,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44666,0.07639,0.27508]},{"body_a":"peg","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.49799,0.06641,0.05881],"force_p95":33.00602,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":187.31278,"mean_force":20.44765,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45035,0.07794,0.27611]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50612,0.05418,0.00959],"force_p95":32.25555,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":186.64582,"mean_force":20.50485,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45035,0.07794,0.27611]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.52502,0.08641,0.05996],"force_p95":64.9387,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":65.53022,"mean_force":61.25938,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.43528,0.05381,0.26907]},{"body_a":"peg","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.49888,0.0548,0.0582],"force_p95":28.42895,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.56367,"mean_force":26.03889,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.43528,0.05381,0.26907]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49083,0.03619,0.00936],"force_p95":27.76607,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.95022,"mean_force":25.71313,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.43528,0.05381,0.26907]},{"body_a":"peg","body_b":"channel_base_body","contact_count":771.0,"contact_point_centroid":[0.4952,0.06393,0.00939],"force_p95":1.22665,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.29946,"mean_force":1.02968,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50194,0.18024,0.25168]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":385.0,"contact_point_centroid":[0.52532,0.04176,0.03367],"force_p95":9.6555,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.98604,"mean_force":6.27286,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.43889,0.06483,0.2717]},{"body_a":"peg","body_b":"link6","contact_count":34.0,"contact_point_centroid":[0.49749,0.08139,0.05901],"force_p95":12.82351,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.86672,"mean_force":10.83094,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47168,0.08913,0.28259]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.5254,0.03928,0.01],"force_p95":6.25704,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.32357,"mean_force":5.72546,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.43528,0.05381,0.26907]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50004,0.19477,0.28631]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52506,0.03428,0.00936],"force_p95":0.60374,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60374,"mean_force":0.60374,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.43528,0.05363,0.269]}],"total_contact_groups":18},"final_pose_error":0.24062,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50774,0.03926,0.03374],"final_tcp_position":[0.43529,0.05396,0.26912],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":1747.59769,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":798.0,"n_steps_budget":960.0,"object_pos_end":[0.49491,0.06328,0.03441],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14348,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":639.96504,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1551.0,"raw_peak_contact_force":1747.59769,"subtask_id":"reach_approach","tcp_end":[0.47131,0.09032,0.28253],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.25069,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50781,0.03929,0.03373],"object_pos_start":[0.49491,0.06328,0.03441],"object_to_goal_dist_end":0.11971,"object_to_goal_dist_start":0.14348,"object_z_max":0.03449,"peak_contact_force":627.13701,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3813.0,"raw_peak_contact_force":659.73566,"subtask_id":"reach_approach","tcp_end":[0.43528,0.05363,0.269],"tcp_start":[0.47131,0.09032,0.28253],"tcp_to_object_dist_end":0.24662,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50779,0.03928,0.03373],"object_pos_start":[0.50781,0.03929,0.03373],"object_to_goal_dist_end":0.1197,"object_to_goal_dist_start":0.11971,"object_z_max":0.03373,"peak_contact_force":290.52914,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":290.52914,"subtask_id":"reach_goal","tcp_end":[0.43528,0.05372,0.26904],"tcp_start":[0.43528,0.05363,0.269],"tcp_to_object_dist_end":0.24665,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50777,0.03927,0.03373],"object_pos_start":[0.50779,0.03928,0.03373],"object_to_goal_dist_end":0.11969,"object_to_goal_dist_start":0.1197,"object_z_max":0.03373,"peak_contact_force":59.61497,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":65.53022,"subtask_id":"reach_goal","tcp_end":[0.43529,0.05396,0.26912],"tcp_start":[0.43529,0.05389,0.2691],"tcp_to_object_dist_end":0.24674,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.17333,"average_solve_count":75.0,"average_success_count":75.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_z":0.10179,"approach_1.approach_height":0.13862,"contact_1.contact_force":5.87391,"push_1.force_threshold":13.53353,"push_1.push_speed":0.01651},"optimized_scores":{"best_composite_score":-0.03738,"best_fitness_score":0.02262,"best_task_score":0.03926},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link6","contact_count":128.0,"contact_point_centroid":[0.47453,0.10503,0.0593],"force_p95":729.3631,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2948.09251,"mean_force":373.42211,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48851,0.23625,0.21422]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":681.0,"contact_point_centroid":[0.52503,0.09568,0.05989],"force_p95":648.54087,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2890.29804,"mean_force":543.60775,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52356,0.17671,0.25655]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.52503,0.07543,0.05993],"force_p95":639.54541,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":651.15044,"mean_force":545.39697,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44942,0.07113,0.27608]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.52504,0.07203,0.05993],"force_p95":296.65285,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":296.65285,"mean_force":296.65285,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.43462,0.04623,0.26967]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":300.0,"contact_point_centroid":[0.475,0.08855,0.06],"force_p95":203.93744,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":252.25579,"mean_force":110.9765,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44155,0.06488,0.27357]},{"body_a":"peg","body_b":"channel_base_body","contact_count":829.0,"contact_point_centroid":[0.49639,0.0628,0.00938],"force_p95":46.41301,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":155.46323,"mean_force":11.81964,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51016,0.18511,0.244]},{"body_a":"peg","body_b":"link6","contact_count":236.0,"contact_point_centroid":[0.5003,0.08155,0.05754],"force_p95":66.14219,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":155.12269,"mean_force":39.60633,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48971,0.11235,0.28333]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.52502,0.07225,0.05996],"force_p95":62.72981,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.91169,"mean_force":61.42135,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.43464,0.04641,0.26974]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49979,0.05237,0.00948],"force_p95":50.49346,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.41785,"mean_force":39.10914,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44942,0.07113,0.27608]},{"body_a":"peg","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.4962,0.06137,0.05747],"force_p95":50.0195,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.94367,"mean_force":38.63191,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44942,0.07113,0.27608]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50209,0.03952,0.00956],"force_p95":30.70155,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.89858,"mean_force":29.43123,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.43464,0.04641,0.26974]},{"body_a":"peg","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.4984,0.04913,0.05745],"force_p95":30.23071,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.43147,"mean_force":28.94106,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.43464,0.04641,0.26974]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49798,0.19301,0.2776]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50218,0.03956,0.00955],"force_p95":0.78728,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.78728,"mean_force":0.78728,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.43462,0.04623,0.26967]},{"body_a":"peg","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.49834,0.04925,0.05735],"force_p95":0.29714,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29714,"mean_force":0.29714,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.43462,0.04623,0.26967]}],"total_contact_groups":15},"final_pose_error":0.23731,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50413,0.02739,0.0374],"final_tcp_position":[0.43464,0.04657,0.2698],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":2948.09251,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":858.0,"n_steps_budget":1000.0,"object_pos_end":[0.49718,0.05921,0.03784],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13926,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":609.6209,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1909.0,"raw_peak_contact_force":2948.09251,"subtask_id":"reach_approach","tcp_end":[0.47308,0.08632,0.28317],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.24799,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50415,0.0275,0.03738],"object_pos_start":[0.49718,0.05921,0.03784],"object_to_goal_dist_end":0.10761,"object_to_goal_dist_start":0.13926,"object_z_max":0.0379,"peak_contact_force":629.46602,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3300.0,"raw_peak_contact_force":651.15044,"subtask_id":"reach_approach","tcp_end":[0.43462,0.04623,0.26967],"tcp_start":[0.47308,0.08632,0.28317],"tcp_to_object_dist_end":0.2432,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50414,0.02747,0.03739],"object_pos_start":[0.50415,0.0275,0.03738],"object_to_goal_dist_end":0.10758,"object_to_goal_dist_start":0.10761,"object_z_max":0.03738,"peak_contact_force":296.65285,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":296.65285,"subtask_id":"reach_goal","tcp_end":[0.43463,0.04632,0.26971],"tcp_start":[0.43462,0.04623,0.26967],"tcp_to_object_dist_end":0.24323,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50414,0.02744,0.03739],"object_pos_start":[0.50414,0.02747,0.03739],"object_to_goal_dist_end":0.10755,"object_to_goal_dist_start":0.10758,"object_z_max":0.03739,"peak_contact_force":62.91169,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":62.91169,"subtask_id":"reach_goal","tcp_end":[0.43464,0.04657,0.2698],"tcp_start":[0.43464,0.0465,0.26977],"tcp_to_object_dist_end":0.24333,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```