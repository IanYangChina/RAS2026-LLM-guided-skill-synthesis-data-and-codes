## Search State

- **Seed**: 1
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0381 | 0.07 | ❌ rejected |
| 10 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.3281 | 0.22 | ❌ rejected |
| 9 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.0181 | 0.00 | ❌ rejected |
| 8 | approach → descend → contact → push | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.0318 | 0.01 | ❌ rejected |
| 7 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.5374 | 0.40 | ✅ accepted |

**Proposal policy**: task_score is 0.07 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.038) — your mutation base

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

- **Composite score**: 0.038
- **task_score** (E): 0.070
- **fitness_score**: 0.228  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1852 |
| descend_vertical | 1.00 | 1.00 | 0.0670 |
| align_side | 1.00 | 0.67 | 0.0406 |
| contact_1 | 1.00 | 1.00 | 0.0018 |
| push_1 | 0.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.481, 0.106, 0.144) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.532 | 2.857 |
| descend_vertical | descend | 1.00 / step_budget | (0.481, 0.106, 0.144)→(0.478, 0.105, 0.077) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.333 | 18.824 | 26.740 |
| align_side | align | 1.00 / step_budget | (0.478, 0.105, 0.077)→(0.493, 0.105, 0.042) | (0.497, 0.080, 0.034)→(0.499, 0.070, 0.036) | 0.160→0.150 | 0.67 / 1.667 | 67.923 | 220.679 |
| contact_1 | contact | 1.00 / force_exceeded | (0.493, 0.105, 0.042)→(0.493, 0.104, 0.041) | (0.499, 0.070, 0.036)→(0.498, 0.064, 0.031) | 0.150→0.144 | 1.00 / 2.333 | 44.260 | 40.709 |
| push_1 | push | 0.00 / guard_failure | (0.492, 0.101, 0.040)→(0.492, 0.101, 0.040) | (0.498, 0.064, 0.031)→(0.498, 0.061, 0.031) | 0.144→0.142 | 1.00 / 2.667 | 65.273 | 133.829 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.293
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.182
- phase_score: 0.326
- phase_breakdown.reach_goal_score: 0.003
- phase_breakdown.reach_align_score: 0.849
- phase_breakdown.reach_descend_score: 0.216
- phase_breakdown.reach_approach_score: 0.815

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.269
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.182
- **Median Q (composite search score)**: 0.021
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.318


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42683,"average_solve_count":82.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09036,"contact_1.contact_force":8.54067,"descend_vertical.descend_distance":0.0884,"push_1.force_guard_threshold":28.15193,"push_1.push_distance":0.1598,"push_1.push_speed":0.01459},"optimized_scores":{"best_composite_score":0.01456,"best_fitness_score":0.20456,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":275.0,"contact_point_centroid":[0.50753,0.13808,0.04735],"force_p95":181.71999,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":189.71528,"mean_force":137.08877,"phase_index":2.0,"phase_name":"align_side","phase_type":"align","tcp_position_centroid":[0.50012,0.14557,0.04825]},{"body_a":"peg","body_b":"channel_base_body","contact_count":275.0,"contact_point_centroid":[0.50712,0.11871,0.00723],"force_p95":171.14457,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":183.98612,"mean_force":129.21729,"phase_index":2.0,"phase_name":"align_side","phase_type":"align","tcp_position_centroid":[0.50012,0.14557,0.04825]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50936,0.14167,0.04291],"force_p95":124.06637,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":126.93908,"mean_force":107.05932,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5039,0.15029,0.0425]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49915,0.11796,0.00693],"force_p95":122.53815,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":126.25635,"mean_force":100.91179,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5039,0.15029,0.0425]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50938,0.14146,0.04292],"force_p95":113.61494,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":113.61494,"mean_force":113.61494,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50392,0.15012,0.0425]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51851,0.11795,0.00687],"force_p95":108.37435,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":108.37435,"mean_force":108.37435,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50392,0.15012,0.0425]},{"body_a":"peg","body_b":"channel_base_body","contact_count":250.0,"contact_point_centroid":[0.5012,0.11621,0.00942],"force_p95":38.13736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":79.11582,"mean_force":3.95339,"phase_index":1.0,"phase_name":"descend_vertical","phase_type":"descend","tcp_position_centroid":[0.49502,0.13939,0.09863]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.50419,0.13416,0.05765],"force_p95":74.98155,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":78.60542,"mean_force":61.00577,"phase_index":1.0,"phase_name":"descend_vertical","phase_type":"descend","tcp_position_centroid":[0.49435,0.13945,0.06119]},{"body_a":"peg","body_b":"world","contact_count":151.0,"contact_point_centroid":[0.50322,0.12388,-0.00013],"force_p95":28.03195,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.09568,"mean_force":17.62629,"phase_index":2.0,"phase_name":"align_side","phase_type":"align","tcp_position_centroid":[0.50231,0.14783,0.04493]},{"body_a":"peg","body_b":"world","contact_count":3.0,"contact_point_centroid":[0.50379,0.12243,-0.00022],"force_p95":12.02753,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.09383,"mean_force":8.53902,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5039,0.15029,0.0425]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.50384,0.12244,-0.00025],"force_p95":8.51394,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.51394,"mean_force":8.51394,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50392,0.15012,0.0425]},{"body_a":"peg","body_b":"channel_base_body","contact_count":510.0,"contact_point_centroid":[0.5009,0.11608,0.00938],"force_p95":0.61832,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55881,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49808,0.1695,0.21692]}],"total_contact_groups":12},"final_pose_error":0.16015,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50383,0.12146,0.03045],"final_tcp_position":[0.50395,0.15053,0.04256],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":189.71528,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":526.0,"n_steps_budget":1000.0,"object_pos_end":[0.50096,0.11611,0.03395],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19621,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.50534,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":510.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_approach","tcp_end":[0.49776,0.14018,0.13859],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":250.0,"n_steps_budget":600.0,"object_pos_end":[0.50096,0.11628,0.03315],"object_pos_start":[0.50096,0.11611,0.03395],"object_to_goal_dist_end":0.1964,"object_to_goal_dist_start":0.19621,"object_z_max":0.03395,"peak_contact_force":55.38101,"phase_name":"descend_vertical","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":264.0,"raw_peak_contact_force":79.11582,"subtask_id":"reach_descend","tcp_end":[0.49467,0.13987,0.05953],"tcp_start":[0.49776,0.14018,0.13859],"tcp_to_object_dist_end":0.03594,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":275.0,"n_steps_budget":600.0,"object_pos_end":[0.50384,0.12118,0.03028],"object_pos_start":[0.50096,0.11628,0.03315],"object_to_goal_dist_end":0.20145,"object_to_goal_dist_start":0.1964,"object_z_max":0.03315,"peak_contact_force":188.81859,"phase_name":"align_side","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":701.0,"raw_peak_contact_force":189.71528,"subtask_id":"reach_align","tcp_end":[0.50392,0.15012,0.0425],"tcp_start":[0.49467,0.13987,0.05953],"tcp_to_object_dist_end":0.03141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50381,0.12123,0.0303],"object_pos_start":[0.50384,0.12118,0.03028],"object_to_goal_dist_end":0.2015,"object_to_goal_dist_start":0.20145,"object_z_max":0.03028,"peak_contact_force":113.61494,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":113.61494,"subtask_id":"reach_goal","tcp_end":[0.50389,0.15018,0.04249],"tcp_start":[0.50392,0.15012,0.0425],"tcp_to_object_dist_end":0.03142,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50379,0.12131,0.03034],"object_pos_start":[0.50381,0.12123,0.0303],"object_to_goal_dist_end":0.20157,"object_to_goal_dist_start":0.2015,"object_z_max":0.03039,"peak_contact_force":96.02689,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":126.93908,"subtask_id":"reach_goal","tcp_end":[0.50395,0.15053,0.04256],"tcp_start":[0.50391,0.15041,0.04252],"tcp_to_object_dist_end":0.03168,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4433,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10057,"contact_1.contact_force":1.28495,"descend_vertical.descend_distance":0.05565,"push_1.force_guard_threshold":30.19308,"push_1.push_distance":0.18726,"push_1.push_speed":0.0268},"optimized_scores":{"best_composite_score":0.0785,"best_fitness_score":0.2685,"best_task_score":0.18247},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":225.0,"contact_point_centroid":[0.49783,0.06146,0.00932],"force_p95":99.27431,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":121.10607,"mean_force":16.09175,"phase_index":2.0,"phase_name":"align_side","phase_type":"align","tcp_position_centroid":[0.48132,0.0878,0.07075]},{"body_a":"attachment","body_b":"peg","contact_count":41.0,"contact_point_centroid":[0.49303,0.08065,0.05689],"force_p95":118.57814,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":120.58111,"mean_force":85.53787,"phase_index":2.0,"phase_name":"align_side","phase_type":"align","tcp_position_centroid":[0.48431,0.08684,0.05986]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53214,0.08038,0.05996],"force_p95":99.7656,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":99.79307,"mean_force":86.33454,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48671,0.08024,0.03769]},{"body_a":"peg","body_b":"channel_base_body","contact_count":30.0,"contact_point_centroid":[0.49727,0.04246,0.00997],"force_p95":0.50219,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.91289,"mean_force":0.46085,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48788,0.08319,0.03961]},{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.4975,-0.00694,0.00775],"force_p95":2.28246,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.46952,"mean_force":1.25316,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48699,0.08067,0.038]},{"body_a":"peg","body_b":"channel_base_body","contact_count":570.0,"contact_point_centroid":[0.4953,0.06391,0.00937],"force_p95":0.58008,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56048,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48847,0.14359,0.21911]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.5252,0.0339,0.05818],"force_p95":1.11564,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.19148,"mean_force":0.60384,"phase_index":2.0,"phase_name":"align_side","phase_type":"align","tcp_position_centroid":[0.48763,0.08612,0.04926]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4992,0.19808,0.29726]},{"body_a":"peg","body_b":"channel_base_body","contact_count":160.0,"contact_point_centroid":[0.49564,0.06345,0.0094],"force_p95":0.55083,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5516,"mean_force":0.54554,"phase_index":1.0,"phase_name":"descend_vertical","phase_type":"descend","tcp_position_centroid":[0.47696,0.09071,0.12412]}],"total_contact_groups":9},"final_pose_error":0.1862,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49543,0.01693,0.02441],"final_tcp_position":[0.48661,0.08004,0.03759],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":121.10607,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":597.0,"n_steps_budget":1000.0,"object_pos_end":[0.49508,0.06366,0.03395],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14387,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54286,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":598.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_approach","tcp_end":[0.4792,0.09126,0.14687],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":160.0,"n_steps_budget":600.0,"object_pos_end":[0.4953,0.06402,0.03398],"object_pos_start":[0.49508,0.06366,0.03395],"object_to_goal_dist_end":0.14422,"object_to_goal_dist_start":0.14387,"object_z_max":0.03398,"peak_contact_force":0.54478,"phase_name":"descend_vertical","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":160.0,"raw_peak_contact_force":0.5516,"subtask_id":"reach_descend","tcp_end":[0.47592,0.09065,0.10063],"tcp_start":[0.4792,0.09126,0.14687],"tcp_to_object_dist_end":0.07434,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":229.0,"n_steps_budget":600.0,"object_pos_end":[0.50017,0.03691,0.03982],"object_pos_start":[0.4953,0.06402,0.03398],"object_to_goal_dist_end":0.11691,"object_to_goal_dist_start":0.14422,"object_z_max":0.04085,"peak_contact_force":0.0,"phase_name":"align_side","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":274.0,"raw_peak_contact_force":121.10607,"subtask_id":"reach_align","tcp_end":[0.48892,0.08498,0.04136],"tcp_start":[0.47592,0.09065,0.10063],"tcp_to_object_dist_end":0.04939,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":39.0,"n_steps_budget":600.0,"object_pos_end":[0.49661,0.01723,0.02669],"object_pos_start":[0.50017,0.03691,0.03982],"object_to_goal_dist_end":0.0982,"object_to_goal_dist_start":0.11691,"object_z_max":0.03982,"peak_contact_force":2.91289,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":30.0,"raw_peak_contact_force":2.91289,"subtask_id":"reach_goal","tcp_end":[0.48728,0.0811,0.03836],"tcp_start":[0.48892,0.08498,0.04136],"tcp_to_object_dist_end":0.0656,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":11.0,"n_steps_budget":1000.0,"object_pos_end":[0.49567,0.0166,0.02464],"object_pos_start":[0.49661,0.01723,0.02669],"object_to_goal_dist_end":0.09791,"object_to_goal_dist_start":0.0982,"object_z_max":0.02669,"peak_contact_force":99.79307,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":14.0,"raw_peak_contact_force":99.79307,"subtask_id":"reach_goal","tcp_end":[0.48661,0.08004,0.03759],"tcp_start":[0.48666,0.08013,0.03764],"tcp_to_object_dist_end":0.06538,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09975,"contact_1.contact_force":1.71173,"descend_vertical.descend_distance":0.08471,"push_1.force_guard_threshold":22.42891,"push_1.push_distance":0.1511,"push_1.push_speed":0.04106},"optimized_scores":{"best_composite_score":0.0213,"best_fitness_score":0.2113,"best_task_score":0.02902},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":288.0,"contact_point_centroid":[0.47495,0.09317,0.05992],"force_p95":330.21954,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":351.21421,"mean_force":282.2841,"phase_index":2.0,"phase_name":"align_side","phase_type":"align","tcp_position_centroid":[0.4772,0.08478,0.05881]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53144,0.07353,0.05997],"force_p95":172.98286,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":174.75611,"mean_force":135.95436,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48557,0.07365,0.03865]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47497,0.07373,0.04422],"force_p95":60.90425,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.54607,"mean_force":37.89007,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48557,0.07365,0.03865]},{"body_a":"attachment","body_b":"peg","contact_count":76.0,"contact_point_centroid":[0.48922,0.0732,0.05794],"force_p95":16.39608,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.8766,"mean_force":4.83348,"phase_index":2.0,"phase_name":"align_side","phase_type":"align","tcp_position_centroid":[0.48252,0.08412,0.05426]},{"body_a":"peg","body_b":"channel_base_body","contact_count":373.0,"contact_point_centroid":[0.49836,0.05076,0.00965],"force_p95":3.34224,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.77289,"mean_force":1.46621,"phase_index":2.0,"phase_name":"align_side","phase_type":"align","tcp_position_centroid":[0.47717,0.08457,0.05822]},{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.49276,0.03646,0.0099],"force_p95":13.95243,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.09737,"mean_force":5.22366,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48659,0.07997,0.03987]},{"body_a":"attachment","body_b":"peg","contact_count":22.0,"contact_point_centroid":[0.49082,0.06603,0.04337],"force_p95":12.47426,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.26713,"mean_force":1.70736,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48619,0.07744,0.0394]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49128,0.03888,0.00995],"force_p95":5.59808,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.59808,"mean_force":5.59808,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4875,0.08114,0.04097]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.4901,0.0698,0.03978],"force_p95":5.4224,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.4224,"mean_force":5.4224,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4875,0.08114,0.04097]},{"body_a":"peg","body_b":"channel_base_body","contact_count":582.0,"contact_point_centroid":[0.49438,0.05904,0.00936],"force_p95":0.56582,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57134,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48166,0.14094,0.21842]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49878,0.19747,0.29632]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47498,0.04805,0.06],"force_p95":3.11073,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.20793,"mean_force":2.23594,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48668,0.07897,0.03996]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":23.0,"contact_point_centroid":[0.47472,0.04893,0.05999],"force_p95":0.62716,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.79802,"mean_force":0.25316,"phase_index":2.0,"phase_name":"align_side","phase_type":"align","tcp_position_centroid":[0.48677,0.08187,0.04496]},{"body_a":"peg","body_b":"channel_base_body","contact_count":247.0,"contact_point_centroid":[0.49388,0.05872,0.00939],"force_p95":0.55017,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54604,"phase_index":1.0,"phase_name":"descend_vertical","phase_type":"descend","tcp_position_centroid":[0.46346,0.08593,0.10851]}],"total_contact_groups":14},"final_pose_error":0.1431,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49521,0.04402,0.03633],"final_tcp_position":[0.48553,0.07307,0.0386],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":351.21421,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":611.0,"n_steps_budget":1000.0,"object_pos_end":[0.49399,0.05896,0.03388],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13922,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54639,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":617.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_approach","tcp_end":[0.46606,0.08648,0.14604],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11882,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":247.0,"n_steps_budget":600.0,"object_pos_end":[0.49418,0.0588,0.03391],"object_pos_start":[0.49399,0.05896,0.03388],"object_to_goal_dist_end":0.13906,"object_to_goal_dist_start":0.13922,"object_z_max":0.03391,"peak_contact_force":0.54507,"phase_name":"descend_vertical","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":247.0,"raw_peak_contact_force":0.55382,"subtask_id":"reach_descend","tcp_end":[0.46252,0.08585,0.07064],"tcp_start":[0.46606,0.08648,0.14604],"tcp_to_object_dist_end":0.05553,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":373.0,"n_steps_budget":600.0,"object_pos_end":[0.49367,0.05264,0.03736],"object_pos_start":[0.49418,0.0588,0.03391],"object_to_goal_dist_end":0.13281,"object_to_goal_dist_start":0.13906,"object_z_max":0.0377,"peak_contact_force":14.95105,"phase_name":"align_side","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":760.0,"raw_peak_contact_force":351.21421,"subtask_id":"reach_align","tcp_end":[0.4875,0.08114,0.04097],"tcp_start":[0.46252,0.08585,0.07064],"tcp_to_object_dist_end":0.02938,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49362,0.05253,0.0374],"object_pos_start":[0.49367,0.05264,0.03736],"object_to_goal_dist_end":0.13271,"object_to_goal_dist_start":0.13281,"object_z_max":0.03736,"peak_contact_force":16.25257,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":5.59808,"subtask_id":"reach_goal","tcp_end":[0.48745,0.0811,0.0408],"tcp_start":[0.4875,0.08114,0.04097],"tcp_to_object_dist_end":0.02942,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":29.0,"n_steps_budget":1000.0,"object_pos_end":[0.49499,0.045,0.03681],"object_pos_start":[0.49362,0.05253,0.0374],"object_to_goal_dist_end":0.12514,"object_to_goal_dist_start":0.13271,"object_z_max":0.03755,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":37.0,"raw_peak_contact_force":174.75611,"subtask_id":"reach_goal","tcp_end":[0.48553,0.07307,0.0386],"tcp_start":[0.48555,0.07332,0.03862],"tcp_to_object_dist_end":0.02967,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```