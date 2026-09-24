## Search State

- **Seed**: 1
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.3281 | 0.22 | ❌ rejected |
| 9 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.0181 | 0.00 | ❌ rejected |
| 8 | approach → descend → contact → push | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.0318 | 0.01 | ❌ rejected |
| 7 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.5374 | 0.40 | ✅ accepted |
| 6 | approach → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0851 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.328) — your mutation base

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

- **Composite score**: 0.328
- **task_score** (E): 0.217
- **fitness_score**: 0.388  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2023 |
| descend_1 | 1.00 | 1.00 | 0.0872 |
| contact_1 | 1.00 | 1.00 | 0.0000 |
| push_1 | 1.00 | 1.00 | 0.1266 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.481, 0.087, 0.135) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.546 | 2.857 |
| descend_1 | descend | 1.00 / step_budget | (0.481, 0.087, 0.135)→(0.498, 0.081, 0.051) | (0.497, 0.080, 0.034)→(0.501, 0.079, 0.026) | 0.160→0.160 | 1.00 / 2.000 | 179.134 | 207.003 |
| contact_1 | contact | 1.00 / force_exceeded | (0.498, 0.081, 0.051)→(0.498, 0.081, 0.050) | (0.501, 0.079, 0.026)→(0.501, 0.079, 0.026) | 0.160→0.160 | 1.00 / 2.000 | 105.474 | 105.474 |
| push_1 | push | 1.00 / step_budget | (0.498, 0.081, 0.050)→(0.494, -0.045, 0.046) | (0.501, 0.079, 0.026)→(0.497, 0.027, 0.024) | 0.160→0.109 | 1.00 / 1.000 | 0.615 | 168.555 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.313
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.313
- phase_score: 0.485
- phase_breakdown.reach_contact_score: 0.806
- phase_breakdown.push_through_score: 0.254
- phase_breakdown.reach_approach_score: 0.855

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.416
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.313
- **Median Q (composite search score)**: 0.340
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.307


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06593,"average_solve_count":182.0,"average_success_count":182.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08774,"contact_1.contact_force":6.06841,"descend_1.descend_z_offset":0.00393,"push_1.push_distance":0.17559,"push_1.push_speed":0.01568},"optimized_scores":{"best_composite_score":0.35587,"best_fitness_score":0.41587,"best_task_score":0.31282},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":316.0,"contact_point_centroid":[0.50422,0.11654,0.0089],"force_p95":197.61737,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":228.04117,"mean_force":40.85898,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49728,0.11847,0.08682]},{"body_a":"attachment","body_b":"peg","contact_count":91.0,"contact_point_centroid":[0.51121,0.11746,0.05303],"force_p95":210.2436,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":227.20724,"mean_force":140.01893,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50022,0.11724,0.05566]},{"body_a":"peg","body_b":"channel_base_body","contact_count":442.0,"contact_point_centroid":[0.50546,0.08375,0.0084],"force_p95":157.38421,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":169.38606,"mean_force":54.72886,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50494,0.04592,0.04995]},{"body_a":"attachment","body_b":"peg","contact_count":233.0,"contact_point_centroid":[0.51595,0.09123,0.05251],"force_p95":160.80585,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":168.55381,"mean_force":102.40715,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50808,0.08573,0.05364]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.5215,0.12,0.006],"force_p95":117.81092,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.81092,"mean_force":117.81092,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50447,0.11773,0.05007]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51551,0.11777,0.04869],"force_p95":117.3676,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":117.3676,"mean_force":117.3676,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50447,0.11773,0.05007]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":91.0,"contact_point_centroid":[0.52503,0.0913,0.05155],"force_p95":16.50961,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.0605,"mean_force":12.73136,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50822,0.07126,0.05391]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47491,0.08904,0.02705],"force_p95":2.41468,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.87004,"mean_force":0.7614,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50205,0.02674,0.04643]},{"body_a":"peg","body_b":"channel_base_body","contact_count":549.0,"contact_point_centroid":[0.50097,0.11597,0.00938],"force_p95":0.60772,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55836,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49804,0.15997,0.21503]}],"total_contact_groups":9},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50452,0.06599,0.02451],"final_tcp_position":[0.50064,-0.03917,0.04505],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":228.04117,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":565.0,"n_steps_budget":1000.0,"object_pos_end":[0.50094,0.11612,0.03389],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19622,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.54624,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":549.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_approach","tcp_end":[0.49771,0.12138,0.13527],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10157,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":316.0,"n_steps_budget":630.0,"object_pos_end":[0.50405,0.11638,0.02707],"object_pos_start":[0.50094,0.11612,0.03389],"object_to_goal_dist_end":0.19685,"object_to_goal_dist_start":0.19622,"object_z_max":0.03401,"peak_contact_force":210.04036,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":407.0,"raw_peak_contact_force":228.04117,"tcp_end":[0.50447,0.11773,0.05007],"tcp_start":[0.49771,0.12138,0.13527],"tcp_to_object_dist_end":0.02304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50398,0.11637,0.02701],"object_pos_start":[0.50405,0.11638,0.02707],"object_to_goal_dist_end":0.19684,"object_to_goal_dist_start":0.19685,"object_z_max":0.02707,"peak_contact_force":117.81092,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":117.81092,"subtask_id":"reach_contact","tcp_end":[0.50445,0.11772,0.05004],"tcp_start":[0.50447,0.11773,0.05007],"tcp_to_object_dist_end":0.02307,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":447.0,"n_steps_budget":1000.0,"object_pos_end":[0.50452,0.06599,0.02451],"object_pos_start":[0.50398,0.11637,0.02701],"object_to_goal_dist_end":0.14687,"object_to_goal_dist_start":0.19684,"object_z_max":0.03952,"peak_contact_force":0.51069,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":776.0,"raw_peak_contact_force":169.38606,"subtask_id":"push_through","tcp_end":[0.50064,-0.03917,0.04505],"tcp_start":[0.50445,0.11772,0.05004],"tcp_to_object_dist_end":0.10721,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40602,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08822,"contact_1.contact_force":6.68488,"descend_1.descend_z_offset":0.00822,"push_1.push_distance":0.12373,"push_1.push_speed":0.03794},"optimized_scores":{"best_composite_score":0.34026,"best_fitness_score":0.40026,"best_task_score":0.22709},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":308.0,"contact_point_centroid":[0.49723,0.06376,0.00903],"force_p95":151.44123,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":185.98464,"mean_force":27.10427,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48371,0.0678,0.08937]},{"body_a":"attachment","body_b":"peg","contact_count":71.0,"contact_point_centroid":[0.50118,0.0656,0.05399],"force_p95":168.3215,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":185.38561,"mean_force":115.21328,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49037,0.06543,0.05752]},{"body_a":"peg","body_b":"channel_base_body","contact_count":290.0,"contact_point_centroid":[0.50172,0.03514,0.00846],"force_p95":147.05873,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":155.83918,"mean_force":77.79455,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49656,0.01895,0.05364]},{"body_a":"attachment","body_b":"peg","contact_count":225.0,"contact_point_centroid":[0.50594,0.03617,0.05313],"force_p95":148.07578,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":155.35496,"mean_force":99.65709,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49765,0.03131,0.05491]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49666,0.0811,0.00611],"force_p95":92.3603,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":92.3603,"mean_force":92.3603,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49449,0.06516,0.05214]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50534,0.06524,0.04963],"force_p95":91.65599,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.65599,"mean_force":91.65599,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49449,0.06516,0.05214]},{"body_a":"peg","body_b":"channel_base_body","contact_count":648.0,"contact_point_centroid":[0.49543,0.06396,0.00937],"force_p95":0.56738,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55868,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48832,0.13351,0.21252]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49922,0.19799,0.29732]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47499,0.0359,0.02787],"force_p95":0.89105,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.91939,"mean_force":0.49244,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49227,-0.02604,0.04878]}],"total_contact_groups":9},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49334,0.01125,0.02438],"final_tcp_position":[0.49147,-0.03953,0.04796],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":185.98464,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":675.0,"n_steps_budget":1000.0,"object_pos_end":[0.49491,0.064,0.03396],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14422,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54602,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":676.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_approach","tcp_end":[0.47891,0.07156,0.13394],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":308.0,"n_steps_budget":600.0,"object_pos_end":[0.49865,0.06335,0.02727],"object_pos_start":[0.49491,0.064,0.03396],"object_to_goal_dist_end":0.14392,"object_to_goal_dist_start":0.14422,"object_z_max":0.034,"peak_contact_force":164.316,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":379.0,"raw_peak_contact_force":185.98464,"tcp_end":[0.49449,0.06516,0.05214],"tcp_start":[0.47891,0.07156,0.13394],"tcp_to_object_dist_end":0.02528,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.4986,0.06332,0.02723],"object_pos_start":[0.49865,0.06335,0.02727],"object_to_goal_dist_end":0.1439,"object_to_goal_dist_start":0.14392,"object_z_max":0.02727,"peak_contact_force":92.3603,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":92.3603,"subtask_id":"reach_contact","tcp_end":[0.4945,0.06514,0.05209],"tcp_start":[0.49449,0.06516,0.05214],"tcp_to_object_dist_end":0.02526,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":296.0,"n_steps_budget":1000.0,"object_pos_end":[0.49334,0.01125,0.02438],"object_pos_start":[0.4986,0.06332,0.02723],"object_to_goal_dist_end":0.09281,"object_to_goal_dist_start":0.1439,"object_z_max":0.03949,"peak_contact_force":0.59661,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":519.0,"raw_peak_contact_force":155.83918,"subtask_id":"push_through","tcp_end":[0.49147,-0.03953,0.04796],"tcp_start":[0.4945,0.06514,0.05209],"tcp_to_object_dist_end":0.05602,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45312,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09141,"contact_1.contact_force":8.59826,"descend_1.descend_z_offset":0.00491,"push_1.push_distance":0.13664,"push_1.push_speed":0.04713},"optimized_scores":{"best_composite_score":0.28805,"best_fitness_score":0.34805,"best_task_score":0.11182},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":361.0,"contact_point_centroid":[0.4964,0.05908,0.00881],"force_p95":161.37613,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":206.98252,"mean_force":32.5255,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47661,0.06284,0.08852]},{"body_a":"attachment","body_b":"peg","contact_count":94.0,"contact_point_centroid":[0.49869,0.06063,0.05248],"force_p95":196.15109,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":206.29317,"mean_force":122.79099,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48791,0.06046,0.05589]},{"body_a":"peg","body_b":"channel_base_body","contact_count":327.0,"contact_point_centroid":[0.50172,0.02731,0.00809],"force_p95":169.70689,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":180.43919,"mean_force":82.83153,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49652,0.0074,0.05107]},{"body_a":"attachment","body_b":"peg","contact_count":234.0,"contact_point_centroid":[0.50667,0.02985,0.05148],"force_p95":171.2117,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":179.91389,"mean_force":114.92763,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49824,0.0253,0.05301]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50747,0.07387,0.00503],"force_p95":106.25057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.25057,"mean_force":106.25057,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49419,0.06004,0.0493]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50503,0.06011,0.04712],"force_p95":105.52182,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":105.52182,"mean_force":105.52182,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49419,0.06004,0.0493]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47495,-0.00618,0.02664],"force_p95":5.51754,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.54622,"mean_force":3.261,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49212,-0.03393,0.04612]},{"body_a":"peg","body_b":"channel_base_body","contact_count":653.0,"contact_point_centroid":[0.49426,0.05897,0.00936],"force_p95":0.56099,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.5686,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48149,0.13089,0.21386]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49882,0.19735,0.29643]}],"total_contact_groups":9},"final_pose_error":0.01968,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49389,0.00509,0.02408],"final_tcp_position":[0.49087,-0.05775,0.04484],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":206.98252,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":682.0,"n_steps_budget":1000.0,"object_pos_end":[0.49412,0.05882,0.03389],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13908,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54457,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":688.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_approach","tcp_end":[0.46572,0.06685,0.13703],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10728,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":361.0,"n_steps_budget":660.0,"object_pos_end":[0.49934,0.05795,0.02512],"object_pos_start":[0.49412,0.05882,0.03389],"object_to_goal_dist_end":0.13875,"object_to_goal_dist_start":0.13908,"object_z_max":0.03392,"peak_contact_force":163.04655,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":455.0,"raw_peak_contact_force":206.98252,"tcp_end":[0.49419,0.06004,0.0493],"tcp_start":[0.46572,0.06685,0.13703],"tcp_to_object_dist_end":0.02481,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49928,0.05791,0.02508],"object_pos_start":[0.49934,0.05795,0.02512],"object_to_goal_dist_end":0.13871,"object_to_goal_dist_start":0.13875,"object_z_max":0.02512,"peak_contact_force":106.25057,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":106.25057,"subtask_id":"reach_contact","tcp_end":[0.4942,0.06,0.04926],"tcp_start":[0.49419,0.06004,0.0493],"tcp_to_object_dist_end":0.0248,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":333.0,"n_steps_budget":1000.0,"object_pos_end":[0.49389,0.00509,0.02408],"object_pos_start":[0.49928,0.05791,0.02508],"object_to_goal_dist_end":0.08678,"object_to_goal_dist_start":0.13871,"object_z_max":0.03927,"peak_contact_force":0.73744,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":572.0,"raw_peak_contact_force":180.43919,"subtask_id":"push_through","tcp_end":[0.49087,-0.05775,0.04484],"tcp_start":[0.4942,0.06,0.04926],"tcp_to_object_dist_end":0.06625,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```