## Search State

- **Seed**: 1
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6  | 0.1121 | 0.31 | ❌ rejected |
| 10 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3  | -0.0363 | 0.00 | ❌ rejected |
| 9 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5  | 0.0461 | 0.00 | ❌ rejected |
| 8 | approach → descend → contact → push | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5  | -0.1968 | 0.00 | ❌ rejected |
| 7 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5  | 0.0454 | 0.35 | ✅ accepted |

**Proposal policy**: task_score is 0.35 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.045) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_contact
  anchor: object
  offset:
  - -0.001
  - 0.03
  - 0.0
  weight: 0.3
- id: reach_goal
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
    - 0.12
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_contact
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
    - 0.03
    - 0.0
  parameters:
    descend_tolerance:
      type: scalar
      range:
      - 0.003
      - 0.01
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
  subtask_id: reach_contact
- id: push_1
  type: push
  generator: linear_cartesian
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
      distance: 0.18
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.22
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: guard_force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.12]
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0]
  - parameter_bindings:
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - lateral_offset_x: status=consumed; consumers=target.offset.x (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.18, mode=replace_offset_projection, sign=positive}
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=guard_force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.045
- **task_score** (E): 0.347
- **fitness_score**: 0.375  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1506 |
| descend_1 | 1.00 | 1.00 | 0.1294 |
| push_1 | 0.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.481, 0.135, 0.168) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.546 | 2.857 |
| descend_1 | descend | 1.00 / step_budget | (0.481, 0.135, 0.168)→(0.493, 0.111, 0.041) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.547 | 115.319 |
| push_1 | push | 0.00 / guard_failure | (0.490, 0.035, 0.038)→(0.490, 0.035, 0.038) | (0.497, 0.080, 0.034)→(0.500, 0.007, 0.037) | 0.160→0.090 | 1.00 / 2.000 | 50.954 | 80.198 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.172
- terminal_score: 0.971
- phase_score: 0.691
- phase_breakdown.reach_contact_score: 0.937
- phase_breakdown.reach_goal_score: 0.586

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.803
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.971
- **Median Q (composite search score)**: -0.143
- **K-run variance**: 0.0919
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.317


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28796,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07537,"descend_1.descend_tolerance":0.0099,"descend_1.lateral_offset_x":0.00577,"push_1.push_distance":0.21375,"push_1.push_speed":0.025,"push_1.push_tolerance":0.01442},"optimized_scores":{"best_composite_score":0.47316,"best_fitness_score":0.80316,"best_task_score":0.97127},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":532.0,"contact_point_centroid":[0.5027,0.02402,0.04113],"force_p95":17.70224,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.37984,"mean_force":5.51646,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49806,0.03552,0.03762]},{"body_a":"peg","body_b":"channel_base_body","contact_count":12.0,"contact_point_centroid":[0.50653,-0.10052,0.05971],"force_p95":35.86836,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.69859,"mean_force":24.19035,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49791,-0.05246,0.03741]},{"body_a":"peg","body_b":"channel_base_body","contact_count":371.0,"contact_point_centroid":[0.50575,0.00742,0.00985],"force_p95":15.73409,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.45575,"mean_force":7.17224,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49825,0.05056,0.03782]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":401.0,"contact_point_centroid":[0.52508,0.00273,0.02588],"force_p95":6.30543,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.10034,"mean_force":1.84305,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49796,0.03025,0.03751]},{"body_a":"peg","body_b":"channel_base_body","contact_count":401.0,"contact_point_centroid":[0.501,0.11602,0.00936],"force_p95":0.62384,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56391,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49825,0.18383,0.23262]},{"body_a":"peg","body_b":"channel_base_body","contact_count":403.0,"contact_point_centroid":[0.50085,0.11593,0.00944],"force_p95":0.59813,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64981,"mean_force":0.54094,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49885,0.1578,0.10539]}],"total_contact_groups":6},"final_pose_error":0.0146,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50653,-0.08152,0.03632],"final_tcp_position":[0.49781,-0.05349,0.03727],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":41.37984,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":417.0,"n_steps_budget":1000.0,"object_pos_end":[0.50093,0.11601,0.03389],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.1961,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.54807,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":401.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_contact","tcp_end":[0.49803,0.16855,0.16915],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14514,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":403.0,"n_steps_budget":870.0,"object_pos_end":[0.50091,0.11607,0.03391],"object_pos_start":[0.50093,0.11601,0.03389],"object_to_goal_dist_end":0.19616,"object_to_goal_dist_start":0.1961,"object_z_max":0.03415,"peak_contact_force":0.54775,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":403.0,"raw_peak_contact_force":0.64981,"subtask_id":"reach_contact","tcp_end":[0.50191,0.1472,0.04233],"tcp_start":[0.49803,0.16855,0.16915],"tcp_to_object_dist_end":0.03226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":762.0,"n_steps_budget":1000.0,"object_pos_end":[0.50659,-0.08139,0.03635],"object_pos_start":[0.50091,0.11607,0.03391],"object_to_goal_dist_end":0.00766,"object_to_goal_dist_start":0.19616,"object_z_max":0.03872,"peak_contact_force":1.44343,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1316.0,"raw_peak_contact_force":41.37984,"subtask_id":"reach_goal","tcp_end":[0.49781,-0.05349,0.03727],"tcp_start":[0.49785,-0.0534,0.03732],"tcp_to_object_dist_end":0.02927,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17308,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05576,"descend_1.descend_tolerance":0.00968,"descend_1.lateral_offset_x":0.00118,"push_1.push_distance":0.16693,"push_1.push_speed":0.06065,"push_1.push_tolerance":0.01159},"optimized_scores":{"best_composite_score":-0.14297,"best_fitness_score":0.18703,"best_task_score":0.06154},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53298,0.07514,0.06],"force_p95":133.71939,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":134.32252,"mean_force":101.99081,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48757,0.07527,0.03774]},{"body_a":"peg","body_b":"channel_base_body","contact_count":72.0,"contact_point_centroid":[0.49526,0.04465,0.00971],"force_p95":19.60393,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.051,"mean_force":7.96273,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48875,0.08678,0.03912]},{"body_a":"attachment","body_b":"peg","contact_count":72.0,"contact_point_centroid":[0.49272,0.07262,0.04198],"force_p95":19.07319,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.52638,"mean_force":7.52969,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48832,0.08419,0.03863]},{"body_a":"peg","body_b":"channel_base_body","contact_count":495.0,"contact_point_centroid":[0.4955,0.06378,0.00937],"force_p95":0.59558,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56272,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48876,0.15879,0.22986]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49921,0.19849,0.29758]},{"body_a":"peg","body_b":"channel_base_body","contact_count":432.0,"contact_point_centroid":[0.49497,0.06413,0.0094],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54548,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48412,0.10809,0.10389]}],"total_contact_groups":6},"final_pose_error":0.14622,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49767,0.04617,0.03753],"final_tcp_position":[0.48757,0.07495,0.03774],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":134.32252,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":522.0,"n_steps_budget":1000.0,"object_pos_end":[0.49526,0.06398,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14419,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54674,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":523.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_contact","tcp_end":[0.47969,0.1205,0.1672],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14559,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":432.0,"n_steps_budget":870.0,"object_pos_end":[0.49487,0.06372,0.03401],"object_pos_start":[0.49526,0.06398,0.03394],"object_to_goal_dist_end":0.14393,"object_to_goal_dist_start":0.14419,"object_z_max":0.03401,"peak_contact_force":0.54871,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":432.0,"raw_peak_contact_force":0.55289,"subtask_id":"reach_contact","tcp_end":[0.49092,0.09575,0.04169],"tcp_start":[0.47969,0.1205,0.1672],"tcp_to_object_dist_end":0.03317,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":96.0,"n_steps_budget":1000.0,"object_pos_end":[0.49757,0.04665,0.03762],"object_pos_start":[0.49487,0.06372,0.03401],"object_to_goal_dist_end":0.12669,"object_to_goal_dist_start":0.14393,"object_z_max":0.03762,"peak_contact_force":128.29117,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":147.0,"raw_peak_contact_force":134.32252,"subtask_id":"reach_goal","tcp_end":[0.48757,0.07495,0.03774],"tcp_start":[0.48757,0.07509,0.03774],"tcp_to_object_dist_end":0.03002,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17822,"average_solve_count":101.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05893,"descend_1.descend_tolerance":0.00834,"descend_1.lateral_offset_x":-0.00152,"push_1.push_distance":0.16179,"push_1.push_speed":0.05306,"push_1.push_tolerance":0.01785},"optimized_scores":{"best_composite_score":-0.1941,"best_fitness_score":0.1359,"best_task_score":0.00828},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":17.0,"contact_point_centroid":[0.47491,0.09831,0.05982],"force_p95":327.21449,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":344.75436,"mean_force":230.74026,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48459,0.09349,0.05494]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47497,0.08403,0.0433],"force_p95":60.91912,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":64.8908,"mean_force":34.37969,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48569,0.08396,0.03794]},{"body_a":"peg","body_b":"channel_base_body","contact_count":27.0,"contact_point_centroid":[0.49098,0.04937,0.00947],"force_p95":18.66194,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.5717,"mean_force":3.30945,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48633,0.08764,0.03872]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.4915,0.07454,0.0449],"force_p95":19.15719,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.34515,"mean_force":10.99124,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48596,0.08609,0.0383]},{"body_a":"peg","body_b":"channel_base_body","contact_count":508.0,"contact_point_centroid":[0.49434,0.05889,0.00935],"force_p95":0.57384,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.575,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48207,0.15621,0.2295]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49878,0.19798,0.29667]},{"body_a":"peg","body_b":"channel_base_body","contact_count":521.0,"contact_point_centroid":[0.49428,0.05898,0.00939],"force_p95":0.55015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54599,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47582,0.1028,0.10165]}],"total_contact_groups":7},"final_pose_error":0.15465,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49471,0.05479,0.03701],"final_tcp_position":[0.48568,0.08333,0.03783],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":344.75436,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":537.0,"n_steps_budget":1000.0,"object_pos_end":[0.49423,0.0589,0.03387],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13915,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54433,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":543.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_contact","tcp_end":[0.46674,0.11575,0.16701],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14736,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":521.0,"n_steps_budget":870.0,"object_pos_end":[0.49418,0.05915,0.03393],"object_pos_start":[0.49423,0.0589,0.03387],"object_to_goal_dist_end":0.1394,"object_to_goal_dist_start":0.13915,"object_z_max":0.03393,"peak_contact_force":0.54483,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":538.0,"raw_peak_contact_force":344.75436,"subtask_id":"reach_contact","tcp_end":[0.48743,0.0905,0.03999],"tcp_start":[0.46674,0.11575,0.16701],"tcp_to_object_dist_end":0.03264,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":27.0,"n_steps_budget":1000.0,"object_pos_end":[0.49455,0.05516,0.03662],"object_pos_start":[0.49418,0.05915,0.03393],"object_to_goal_dist_end":0.13531,"object_to_goal_dist_start":0.1394,"object_z_max":0.03682,"peak_contact_force":23.1284,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":38.0,"raw_peak_contact_force":64.8908,"subtask_id":"reach_goal","tcp_end":[0.48568,0.08333,0.03783],"tcp_start":[0.48568,0.08352,0.03788],"tcp_to_object_dist_end":0.02956,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```