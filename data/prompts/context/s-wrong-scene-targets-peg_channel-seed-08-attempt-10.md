## Search State

- **Seed**: 8
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → align → descend → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.2013 | 0.30 | ✅ accepted |
| 9 | approach → align → descend → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.3108 | 0.18 | ❌ rejected |
| 8 | approach → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 10 | -0.5354 | 0.00 | ❌ rejected |
| 7 | approach → align → contact → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.1385 | 0.01 | ❌ rejected |
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 11 | -0.1959 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.48615778212844485, -0.04101785253296597, 0.04]
- Frozen task target: [0.5, 0.2, 0.3]
- Goal object position: (0.5, 0.2, 0.3)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48615778212844485, -0.04101785253296597, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.48615778212844485, 0.11898214746703403, 0.04)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.48615778212844485, 0.11898214746703403, 0.04]
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
  frozen_object_starts: {'peg': [0.48615778212844485, -0.04101785253296597, 0.04]}
  frozen_targets: {'channel_exit': [0.5, 0.2, 0.3]}
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
| `object` | offset from object initial position (0.48615778212844485, -0.04101785253296597, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.2, 0.3) | final destination targets |
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

## Current Skill (Q=-0.201) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.08
  weight: 0.3
- id: push_progress
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_prepush
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.08
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: pre_contact
- id: align_tool
  type: align
  generator: joint_interpolation
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_contact
- id: descend_to_peg
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: pre_contact
- id: push_channel
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
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.2
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_force_guard_threshold:
      type: scalar
      range:
      - 25.0
      - 40.0
      default: 35.0
      binds_to:
      - path: guards.push_force_limit.threshold
        mode: replace
    push_pose_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.12
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    retry_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: retry.offset.x
        mode: replace
    retry_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.0
      default: -0.005
      binds_to:
      - path: retry.offset.y
        mode: replace
    retry_offset_z:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: retry.offset.z
        mode: replace
  guards:
  - id: push_force_limit
    when: during_phase
    predicate: force_below
    threshold: 35.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.005
    - 0.0
  subtask_id: push_progress

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_prepush** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.08], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **align_tool** (`align`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **push_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.18, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_force_guard_threshold: status=consumed; consumers=guards.push_force_limit.threshold (replace)
    - push_pose_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - retry_offset_x: status=consumed; consumers=retry.offset.x (replace)
    - retry_offset_y: status=consumed; consumers=retry.offset.y (replace)
    - retry_offset_z: status=consumed; consumers=retry.offset.z (replace)
  - guards:
    - id=push_force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=35.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.005, 0.0]

## Design Metrics

- **Composite score**: -0.201
- **task_score** (E): 0.298
- **fitness_score**: 0.459  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.660

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_prepush | 1.00 | 1.00 | 0.1955 |
| align_tool | 1.00 | 1.00 | 0.0246 |
| descend_to_peg | 1.00 | 1.00 | 0.0886 |
| push_channel | 0.33 | 1.00 | 0.0461 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_prepush | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.115, 0.127) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.530 | 3.526 |
| align_tool | align | 1.00 / step_budget | (0.513, 0.115, 0.127)→(0.504, 0.137, 0.122) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.554 | 0.585 |
| descend_to_peg | descend | 1.00 / step_budget | (0.504, 0.137, 0.122)→(0.499, 0.104, 0.041) | (0.503, 0.080, 0.034)→(0.502, 0.075, 0.036) | 0.160→0.155 | 1.00 / 1.667 | 5.762 | 19.440 |
| push_channel | push | 0.33 / guard_failure | (0.497, 0.044, 0.038)→(0.496, -0.002, 0.037) | (0.502, 0.075, 0.036)→(0.502, -0.033, 0.038) | 0.155→0.051 | 1.00 / 2.333 | 4.965 | 38.516 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.892
- alignment_error: None
- force_efficiency: 0.328
- terminal_score: 0.366
- phase_score: 0.720
- phase_breakdown.pre_contact_score: 0.192
- phase_breakdown.push_progress_score: 0.947

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.578
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.366
- **Median Q (composite search score)**: -0.134
- **K-run variance**: 0.0179
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.215


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
{"anchors":[{"name":"object","value":[0.48616,-0.04102,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,-0.04102,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73239,"average_solve_count":71.0,"average_success_count":71.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_tool.align_speed":0.26617,"approach_prepush.approach_speed":0.39409,"approach_prepush.approach_tolerance":0.01406,"descend_to_peg.descend_speed":0.08561,"descend_to_peg.descend_tolerance":0.01651,"push_channel.push_distance":0.14361,"push_channel.push_force_guard_threshold":35.21767,"push_channel.push_pose_tolerance":0.01981,"push_channel.push_speed":0.05902,"push_channel.retry_offset_x":-0.00058,"push_channel.retry_offset_y":-0.01359,"push_channel.retry_offset_z":0.0011},"optimized_scores":{"best_composite_score":-0.38817,"best_fitness_score":0.27183,"best_task_score":0.31151},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47499,0.09659,0.04087],"force_p95":44.12212,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":46.08834,"mean_force":26.42617,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48597,0.09635,0.03604]},{"body_a":"peg","body_b":"channel_base_body","contact_count":57.0,"contact_point_centroid":[0.5015,0.07472,0.00934],"force_p95":24.04064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.99221,"mean_force":4.75193,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48662,0.11425,0.03692]},{"body_a":"attachment","body_b":"peg","contact_count":60.0,"contact_point_centroid":[0.49261,0.11539,0.04508],"force_p95":23.91837,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.39833,"mean_force":3.88503,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48727,0.12661,0.0378]},{"body_a":"peg","body_b":"channel_base_body","contact_count":316.0,"contact_point_centroid":[0.49657,0.11616,0.00948],"force_p95":0.64979,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.35541,"mean_force":0.97897,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48018,0.15758,0.0821]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.49211,0.13314,0.04915],"force_p95":16.01562,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.05921,"mean_force":10.42044,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48795,0.14455,0.04643]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47496,0.10926,0.06],"force_p95":3.05172,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.34502,"mean_force":1.36354,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48924,0.1423,0.04017]},{"body_a":"peg","body_b":"channel_base_body","contact_count":442.0,"contact_point_centroid":[0.49629,0.11912,0.0094],"force_p95":0.61955,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55895,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.49115,0.17488,0.21011]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.49939,0.19885,0.2967]},{"body_a":"peg","body_b":"channel_base_body","contact_count":307.0,"contact_point_centroid":[0.49598,0.11921,0.00946],"force_p95":0.59987,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64701,"mean_force":0.53871,"phase_index":1.0,"phase_name":"align_tool","phase_type":"align","tcp_position_centroid":[0.47751,0.16271,0.12504]}],"total_contact_groups":9},"final_pose_error":0.09711,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4939,0.06182,0.03708],"final_tcp_position":[0.48598,0.09579,0.03598],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":46.08834,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":467.0,"n_steps_budget":600.0,"object_pos_end":[0.49604,0.11913,0.03395],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19926,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.51129,"phase_name":"approach_prepush","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":466.0,"raw_peak_contact_force":2.24822,"subtask_id":"pre_contact","tcp_end":[0.4842,0.15204,0.1293],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10157,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":307.0,"n_steps_budget":600.0,"object_pos_end":[0.49606,0.11915,0.03392],"object_pos_start":[0.49604,0.11913,0.03395],"object_to_goal_dist_end":0.19929,"object_to_goal_dist_start":0.19926,"object_z_max":0.03408,"peak_contact_force":0.57166,"phase_name":"align_tool","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":307.0,"raw_peak_contact_force":0.64701,"subtask_id":"pre_contact","tcp_end":[0.47361,0.17247,0.12438],"tcp_start":[0.4842,0.15204,0.1293],"tcp_to_object_dist_end":0.10737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":316.0,"n_steps_budget":750.0,"object_pos_end":[0.49441,0.11361,0.03766],"object_pos_start":[0.49606,0.11915,0.03392],"object_to_goal_dist_end":0.19371,"object_to_goal_dist_start":0.19929,"object_z_max":0.03771,"peak_contact_force":16.35541,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":330.0,"raw_peak_contact_force":16.35541,"subtask_id":"pre_contact","tcp_end":[0.48939,0.14245,0.04048],"tcp_start":[0.47361,0.17247,0.12438],"tcp_to_object_dist_end":0.02941,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.49445,0.06247,0.03676],"object_pos_start":[0.49441,0.11361,0.03766],"object_to_goal_dist_end":0.14262,"object_to_goal_dist_start":0.19371,"object_z_max":0.03849,"peak_contact_force":0.0,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":122.0,"raw_peak_contact_force":46.08834,"subtask_id":"push_progress","tcp_end":[0.48598,0.09579,0.03598],"tcp_start":[0.48597,0.09601,0.03603],"tcp_to_object_dist_end":0.03439,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,-0.09705,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,-0.09705,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26016,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_tool.align_speed":0.33372,"approach_prepush.approach_speed":0.33311,"approach_prepush.approach_tolerance":0.01118,"descend_to_peg.descend_speed":0.05989,"descend_to_peg.descend_tolerance":0.01265,"push_channel.push_distance":0.15657,"push_channel.push_force_guard_threshold":37.33083,"push_channel.push_pose_tolerance":0.02478,"push_channel.push_speed":0.04612,"push_channel.retry_offset_x":-0.0014,"push_channel.retry_offset_y":-0.01116,"push_channel.retry_offset_z":7e-05},"optimized_scores":{"best_composite_score":-0.08151,"best_fitness_score":0.57849,"best_task_score":0.36552},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":150.0,"contact_point_centroid":[0.50342,0.01305,0.04406],"force_p95":23.85691,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.59117,"mean_force":5.03156,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50031,0.0246,0.03768]},{"body_a":"peg","body_b":"channel_base_body","contact_count":179.0,"contact_point_centroid":[0.50302,-0.02034,0.00954],"force_p95":18.00958,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.56508,"mean_force":4.08964,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50018,0.01898,0.0375]},{"body_a":"peg","body_b":"channel_base_body","contact_count":10.0,"contact_point_centroid":[0.50592,-0.10047,0.05922],"force_p95":24.42763,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.7473,"mean_force":9.68453,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49974,-0.04739,0.03689]},{"body_a":"peg","body_b":"channel_base_body","contact_count":283.0,"contact_point_centroid":[0.50597,0.06095,0.00941],"force_p95":0.60453,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.33683,"mean_force":1.01742,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50895,0.1062,0.08246]},{"body_a":"attachment","body_b":"peg","contact_count":15.0,"contact_point_centroid":[0.50512,0.07818,0.04575],"force_p95":18.5405,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.95275,"mean_force":9.01406,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50403,0.09007,0.04595]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":73.0,"contact_point_centroid":[0.52514,0.01251,0.02813],"force_p95":7.04598,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.37965,"mean_force":1.40261,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50074,0.04194,0.03825]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.52518,0.05932,0.04059],"force_p95":2.87279,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.60849,"mean_force":0.94786,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50383,0.08933,0.04423]},{"body_a":"peg","body_b":"channel_base_body","contact_count":520.0,"contact_point_centroid":[0.50578,0.063,0.00936],"force_p95":0.56846,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57257,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.51179,0.14782,0.20877]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.50003,0.19759,0.29572]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":32.0,"contact_point_centroid":[0.47454,-0.03088,0.03889],"force_p95":0.76478,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.8869,"mean_force":0.37028,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49978,0.00054,0.03698]},{"body_a":"peg","body_b":"channel_base_body","contact_count":321.0,"contact_point_centroid":[0.50598,0.06292,0.00938],"force_p95":0.55136,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54657,"phase_index":1.0,"phase_name":"align_tool","phase_type":"align","tcp_position_centroid":[0.51863,0.11164,0.12181]}],"total_contact_groups":11},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50677,-0.07984,0.03715],"final_tcp_position":[0.49971,-0.04936,0.03685],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":33.59117,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":548.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.06294,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54018,"phase_name":"approach_prepush","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":554.0,"raw_peak_contact_force":3.88411,"subtask_id":"pre_contact","tcp_end":[0.52434,0.09934,0.12651],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":321.0,"n_steps_budget":600.0,"object_pos_end":[0.50595,0.06295,0.03381],"object_pos_start":[0.50599,0.06294,0.03381],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":0.54576,"phase_name":"align_tool","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":321.0,"raw_peak_contact_force":0.55501,"subtask_id":"pre_contact","tcp_end":[0.51579,0.12221,0.12109],"tcp_start":[0.52434,0.09934,0.12651],"tcp_to_object_dist_end":0.10596,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":289.0,"n_steps_budget":1000.0,"object_pos_end":[0.50646,0.05859,0.03572],"object_pos_start":[0.50595,0.06295,0.03381],"object_to_goal_dist_end":0.13881,"object_to_goal_dist_start":0.14321,"object_z_max":0.03627,"peak_contact_force":0.7975,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":313.0,"raw_peak_contact_force":21.33683,"subtask_id":"pre_contact","tcp_end":[0.50352,0.08827,0.04178],"tcp_start":[0.51579,0.12221,0.12109],"tcp_to_object_dist_end":0.03043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":361.0,"n_steps_budget":1000.0,"object_pos_end":[0.50677,-0.07984,0.03715],"object_pos_start":[0.50646,0.05859,0.03572],"object_to_goal_dist_end":0.00735,"object_to_goal_dist_start":0.13881,"object_z_max":0.04173,"peak_contact_force":0.9048,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":444.0,"raw_peak_contact_force":33.59117,"subtask_id":"push_progress","tcp_end":[0.49971,-0.04936,0.03685],"tcp_start":[0.50352,0.08827,0.04178],"tcp_to_object_dist_end":0.03129,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,-0.10339,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,-0.10339,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64706,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_tool.align_speed":0.31968,"approach_prepush.approach_speed":0.29876,"approach_prepush.approach_tolerance":0.01324,"descend_to_peg.descend_speed":0.04961,"descend_to_peg.descend_tolerance":0.017,"push_channel.push_distance":0.16055,"push_channel.push_force_guard_threshold":32.05885,"push_channel.push_pose_tolerance":0.01879,"push_channel.push_speed":0.08438,"push_channel.retry_offset_x":0.00277,"push_channel.retry_offset_y":-0.01329,"push_channel.retry_offset_z":-0.00181},"optimized_scores":{"best_composite_score":-0.13426,"best_fitness_score":0.52574,"best_task_score":0.21616},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":6.0,"contact_point_centroid":[0.50879,-0.1003,0.06215],"force_p95":34.90511,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.86856,"mean_force":22.83881,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.501,-0.05177,0.03691]},{"body_a":"attachment","body_b":"peg","contact_count":147.0,"contact_point_centroid":[0.50073,0.00364,0.04081],"force_p95":22.86206,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.99844,"mean_force":4.48386,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50152,0.01514,0.03761]},{"body_a":"peg","body_b":"channel_base_body","contact_count":148.0,"contact_point_centroid":[0.49676,-0.01862,0.00942],"force_p95":20.7054,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.28413,"mean_force":4.12429,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50165,0.02,0.03779]},{"body_a":"peg","body_b":"channel_base_body","contact_count":282.0,"contact_point_centroid":[0.50588,0.05475,0.00939],"force_p95":0.59757,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.62904,"mean_force":1.19297,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51303,0.10049,0.08248]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.50556,0.07184,0.04547],"force_p95":20.21427,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.42564,"mean_force":9.9009,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.5054,0.08376,0.04537]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":29.0,"contact_point_centroid":[0.52573,-0.06777,0.03076],"force_p95":9.35393,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.99143,"mean_force":1.841,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50104,-0.03548,0.03698]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":84.0,"contact_point_centroid":[0.47478,-0.00318,0.0331],"force_p95":2.02623,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.38845,"mean_force":0.88088,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50154,0.02775,0.03762]},{"body_a":"peg","body_b":"channel_base_body","contact_count":520.0,"contact_point_centroid":[0.50582,0.05661,0.00935],"force_p95":0.60102,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.57712,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.51508,0.14481,0.20872]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.50018,0.19729,0.29533]},{"body_a":"peg","body_b":"channel_base_body","contact_count":318.0,"contact_point_centroid":[0.50614,0.05661,0.00938],"force_p95":0.55076,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55367,"mean_force":0.54675,"phase_index":1.0,"phase_name":"align_tool","phase_type":"align","tcp_position_centroid":[0.52514,0.10596,0.12166]}],"total_contact_groups":10},"final_pose_error":0.02631,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50364,-0.08255,0.03846],"final_tcp_position":[0.50087,-0.05279,0.03678],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":35.86856,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":549.0,"n_steps_budget":600.0,"object_pos_end":[0.50613,0.05663,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.53944,"phase_name":"approach_prepush","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":557.0,"raw_peak_contact_force":4.44541,"subtask_id":"pre_contact","tcp_end":[0.53072,0.09347,0.12642],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":318.0,"n_steps_budget":600.0,"object_pos_end":[0.50613,0.05663,0.03378],"object_pos_start":[0.50613,0.05663,0.03378],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.13691,"object_z_max":0.03378,"peak_contact_force":0.54515,"phase_name":"align_tool","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":318.0,"raw_peak_contact_force":0.55367,"subtask_id":"pre_contact","tcp_end":[0.5224,0.11671,0.12091],"tcp_start":[0.53072,0.09347,0.12642],"tcp_to_object_dist_end":0.10708,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":289.0,"n_steps_budget":1000.0,"object_pos_end":[0.50457,0.05223,0.03591],"object_pos_start":[0.50613,0.05663,0.03378],"object_to_goal_dist_end":0.13238,"object_to_goal_dist_start":0.13691,"object_z_max":0.03626,"peak_contact_force":0.13232,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":301.0,"raw_peak_contact_force":20.62904,"subtask_id":"pre_contact","tcp_end":[0.50474,0.08223,0.04182],"tcp_start":[0.5224,0.11671,0.12091],"tcp_to_object_dist_end":0.03057,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.50369,-0.08194,0.0386],"object_pos_start":[0.50457,0.05223,0.03591],"object_to_goal_dist_end":0.0044,"object_to_goal_dist_start":0.13238,"object_z_max":0.04356,"peak_contact_force":13.99143,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":414.0,"raw_peak_contact_force":35.86856,"subtask_id":"push_progress","tcp_end":[0.50087,-0.05279,0.03678],"tcp_start":[0.50093,-0.05259,0.03684],"tcp_to_object_dist_end":0.02935,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```