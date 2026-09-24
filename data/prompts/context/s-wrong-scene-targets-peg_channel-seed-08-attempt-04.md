## Search State

- **Seed**: 8
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → align → contact → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 12 | -0.0189 | 0.22 | ✅ accepted |
| 3 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.4630 | 0.18 | ✅ accepted |
| 2 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.0326 | 0.00 | ❌ rejected |
| 1 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | -0.0488 | 0.15 | ✅ accepted |
| 0 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | 0.2633 | 0.00 | ✅ accepted |

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

## Current Skill (Q=-0.019) — your mutation base

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
- id: contact_engage
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 6.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
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
      - 20.0
      - 35.0
      default: 30.0
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
    threshold: 30.0
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
- **contact_engage** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
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
    - id=push_force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.005, 0.0]

## Design Metrics

- **Composite score**: -0.019
- **task_score** (E): 0.216
- **fitness_score**: 0.391  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.660

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_prepush | 1.00 | 1.00 | 0.1955 |
| align_tool | 1.00 | 1.00 | 0.0246 |
| contact_engage | 1.00 | 1.00 | 0.0864 |
| push_channel | 0.33 | 1.00 | 0.0381 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_prepush | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.115, 0.127) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.530 | 3.526 |
| align_tool | align | 1.00 / step_budget | (0.513, 0.115, 0.127)→(0.504, 0.137, 0.122) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.554 | 0.585 |
| contact_engage | contact | 1.00 / force_exceeded | (0.504, 0.137, 0.122)→(0.499, 0.105, 0.043) | (0.503, 0.080, 0.034)→(0.503, 0.076, 0.036) | 0.160→0.156 | 1.00 / 2.333 | 1304.701 | 12.128 |
| push_channel | push | 0.33 / guard_failure | (0.497, 0.050, 0.041)→(0.495, 0.012, 0.039) | (0.503, 0.076, 0.036)→(0.502, -0.017, 0.038) | 0.156→0.067 | 1.00 / 2.333 | 2.094 | 38.742 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.915
- alignment_error: None
- force_efficiency: 0.222
- terminal_score: 0.317
- phase_score: 0.728
- phase_breakdown.pre_contact_score: 0.196
- phase_breakdown.push_progress_score: 0.956

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.564
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.317
- **Median Q (composite search score)**: 0.064
- **K-run variance**: 0.0340
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.347


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0566,"average_solve_count":53.0,"average_success_count":53.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_tool.align_speed":0.3338,"approach_prepush.approach_speed":0.41394,"approach_prepush.approach_tolerance":0.01047,"contact_engage.contact_force_threshold":7.10275,"contact_engage.contact_speed":0.19256,"push_channel.push_distance":0.13648,"push_channel.push_force_guard_threshold":33.9815,"push_channel.push_pose_tolerance":0.00609,"push_channel.push_speed":0.07318,"push_channel.retry_offset_x":0.01003,"push_channel.retry_offset_y":-0.01177,"push_channel.retry_offset_z":-0.00983},"optimized_scores":{"best_composite_score":-0.27455,"best_fitness_score":0.13545,"best_task_score":0.11911},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47497,0.11999,0.04807],"force_p95":49.3933,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":54.24988,"mean_force":19.97799,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48573,0.12207,0.04327]},{"body_a":"peg","body_b":"channel_base_body","contact_count":65.0,"contact_point_centroid":[0.49446,0.09538,0.00992],"force_p95":30.75071,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.49147,"mean_force":22.22553,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48641,0.13382,0.04409]},{"body_a":"attachment","body_b":"peg","contact_count":60.0,"contact_point_centroid":[0.49062,0.12219,0.04273],"force_p95":30.40608,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.15812,"mean_force":23.71014,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48634,0.13304,0.04401]},{"body_a":"peg","body_b":"channel_base_body","contact_count":472.0,"contact_point_centroid":[0.49661,0.11687,0.00952],"force_p95":0.62225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.43964,"mean_force":0.65712,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.47936,0.15824,0.08396]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.49216,0.13508,0.05676],"force_p95":8.62375,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.16007,"mean_force":4.60225,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.48664,0.14633,0.05138]},{"body_a":"peg","body_b":"channel_base_body","contact_count":442.0,"contact_point_centroid":[0.49629,0.11912,0.0094],"force_p95":0.61955,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55895,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.49115,0.17488,0.21011]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.49939,0.19885,0.2967]},{"body_a":"peg","body_b":"channel_base_body","contact_count":307.0,"contact_point_centroid":[0.49598,0.11921,0.00946],"force_p95":0.59987,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64701,"mean_force":0.53871,"phase_index":1.0,"phase_name":"align_tool","phase_type":"align","tcp_position_centroid":[0.47751,0.16271,0.12504]}],"total_contact_groups":8},"final_pose_error":0.11381,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49659,0.09398,0.03981],"final_tcp_position":[0.48573,0.12161,0.0432],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":54.24988,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":467.0,"n_steps_budget":600.0,"object_pos_end":[0.49604,0.11913,0.03395],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19926,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.51129,"phase_name":"approach_prepush","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":466.0,"raw_peak_contact_force":2.24822,"subtask_id":"pre_contact","tcp_end":[0.4842,0.15204,0.1293],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10157,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":307.0,"n_steps_budget":600.0,"object_pos_end":[0.49606,0.11915,0.03392],"object_pos_start":[0.49604,0.11913,0.03395],"object_to_goal_dist_end":0.19929,"object_to_goal_dist_start":0.19926,"object_z_max":0.03408,"peak_contact_force":0.57166,"phase_name":"align_tool","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":307.0,"raw_peak_contact_force":0.64701,"subtask_id":"pre_contact","tcp_end":[0.47361,0.17247,0.12438],"tcp_start":[0.4842,0.15204,0.1293],"tcp_to_object_dist_end":0.10737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":472.0,"n_steps_budget":600.0,"object_pos_end":[0.49625,0.11641,0.03621],"object_pos_start":[0.49606,0.11915,0.03392],"object_to_goal_dist_end":0.19648,"object_to_goal_dist_start":0.19929,"object_z_max":0.03621,"peak_contact_force":7.58076,"phase_name":"contact_engage","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":486.0,"raw_peak_contact_force":11.43964,"subtask_id":"pre_contact","tcp_end":[0.48795,0.14433,0.04587],"tcp_start":[0.47361,0.17247,0.12438],"tcp_to_object_dist_end":0.03069,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":65.0,"n_steps_budget":1000.0,"object_pos_end":[0.49636,0.09443,0.03982],"object_pos_start":[0.49625,0.11641,0.03621],"object_to_goal_dist_end":0.17446,"object_to_goal_dist_start":0.19648,"object_z_max":0.03982,"peak_contact_force":5.6841,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":128.0,"raw_peak_contact_force":54.24988,"subtask_id":"push_progress","tcp_end":[0.48573,0.12161,0.0432],"tcp_start":[0.48571,0.12179,0.04325],"tcp_to_object_dist_end":0.02938,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.05063,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_tool.align_speed":0.42575,"approach_prepush.approach_speed":0.33069,"approach_prepush.approach_tolerance":0.01556,"contact_engage.contact_force_threshold":13.07889,"contact_engage.contact_speed":0.08728,"push_channel.push_distance":0.16254,"push_channel.push_force_guard_threshold":33.51732,"push_channel.push_pose_tolerance":0.01744,"push_channel.push_speed":0.09861,"push_channel.retry_offset_x":0.00464,"push_channel.retry_offset_y":-0.00976,"push_channel.retry_offset_z":0.00139},"optimized_scores":{"best_composite_score":0.15369,"best_fitness_score":0.56369,"best_task_score":0.31747},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":172.0,"contact_point_centroid":[0.50317,0.01262,0.04457],"force_p95":19.70402,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.87636,"mean_force":3.98411,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50055,0.0242,0.03906]},{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.50428,-0.10055,0.04284],"force_p95":33.31857,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.29726,"mean_force":8.21547,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4999,-0.05273,0.03814]},{"body_a":"peg","body_b":"channel_base_body","contact_count":159.0,"contact_point_centroid":[0.50508,-0.02671,0.0096],"force_p95":19.0976,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.59508,"mean_force":4.45292,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50031,0.01194,0.03873]},{"body_a":"peg","body_b":"channel_base_body","contact_count":409.0,"contact_point_centroid":[0.50599,0.06089,0.00942],"force_p95":0.55416,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.44904,"mean_force":0.69433,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.50853,0.10568,0.0812]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.50505,0.07971,0.04983],"force_p95":11.30507,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.15608,"mean_force":6.13099,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.50435,0.09166,0.04968]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":41.0,"contact_point_centroid":[0.52529,-0.00104,0.02074],"force_p95":0.88748,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.45154,"mean_force":0.89207,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50058,0.02884,0.03908]},{"body_a":"peg","body_b":"channel_base_body","contact_count":520.0,"contact_point_centroid":[0.50578,0.063,0.00936],"force_p95":0.56846,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57257,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.51179,0.14782,0.20877]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.50003,0.19759,0.29572]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":32.0,"contact_point_centroid":[0.47449,-0.03612,0.04008],"force_p95":1.20389,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.47967,"mean_force":0.4781,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49994,-0.00532,0.03823]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":13.0,"contact_point_centroid":[0.52512,0.06019,0.05936],"force_p95":0.55746,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5604,"mean_force":0.20167,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.5042,0.09102,0.04822]},{"body_a":"peg","body_b":"channel_base_body","contact_count":321.0,"contact_point_centroid":[0.50598,0.06292,0.00938],"force_p95":0.55136,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54657,"phase_index":1.0,"phase_name":"align_tool","phase_type":"align","tcp_position_centroid":[0.51863,0.11164,0.12181]}],"total_contact_groups":11},"final_pose_error":0.02007,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50344,-0.08353,0.03625],"final_tcp_position":[0.49982,-0.05475,0.03806],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":38.87636,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":548.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.06294,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54018,"phase_name":"approach_prepush","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":554.0,"raw_peak_contact_force":3.88411,"subtask_id":"pre_contact","tcp_end":[0.52434,0.09934,0.12651],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":321.0,"n_steps_budget":600.0,"object_pos_end":[0.50595,0.06295,0.03381],"object_pos_start":[0.50599,0.06294,0.03381],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":0.54576,"phase_name":"align_tool","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":321.0,"raw_peak_contact_force":0.55501,"subtask_id":"pre_contact","tcp_end":[0.51579,0.12221,0.12109],"tcp_start":[0.52434,0.09934,0.12651],"tcp_to_object_dist_end":0.10596,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":409.0,"n_steps_budget":720.0,"object_pos_end":[0.50679,0.0595,0.03642],"object_pos_start":[0.50595,0.06295,0.03381],"object_to_goal_dist_end":0.13971,"object_to_goal_dist_start":0.14321,"object_z_max":0.03642,"peak_contact_force":13.24316,"phase_name":"contact_engage","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":433.0,"raw_peak_contact_force":14.44904,"subtask_id":"pre_contact","tcp_end":[0.50359,0.08871,0.04301],"tcp_start":[0.51579,0.12221,0.12109],"tcp_to_object_dist_end":0.03011,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":350.0,"n_steps_budget":1000.0,"object_pos_end":[0.50351,-0.0834,0.03619],"object_pos_start":[0.50679,0.0595,0.03642],"object_to_goal_dist_end":0.0062,"object_to_goal_dist_start":0.13971,"object_z_max":0.04199,"peak_contact_force":0.47373,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":415.0,"raw_peak_contact_force":38.87636,"subtask_id":"push_progress","tcp_end":[0.49982,-0.05475,0.03806],"tcp_start":[0.49986,-0.05457,0.0381],"tcp_to_object_dist_end":0.02895,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2541,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_tool.align_speed":0.36621,"approach_prepush.approach_speed":0.2833,"approach_prepush.approach_tolerance":0.01069,"contact_engage.contact_force_threshold":12.81928,"contact_engage.contact_speed":0.03505,"push_channel.push_distance":0.13268,"push_channel.push_force_guard_threshold":30.09292,"push_channel.push_pose_tolerance":0.01702,"push_channel.push_speed":0.05733,"push_channel.retry_offset_x":0.01403,"push_channel.retry_offset_y":-0.00954,"push_channel.retry_offset_z":-0.00181},"optimized_scores":{"best_composite_score":0.0642,"best_fitness_score":0.4742,"best_task_score":0.21024},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":202.0,"contact_point_centroid":[0.50535,0.01509,0.04606],"force_p95":18.9827,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.10023,"mean_force":4.51473,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5013,0.02672,0.03727]},{"body_a":"peg","body_b":"channel_base_body","contact_count":117.0,"contact_point_centroid":[0.50458,-0.01846,0.0098],"force_p95":19.67669,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.04435,"mean_force":7.73895,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50136,0.02742,0.03735]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":123.0,"contact_point_centroid":[0.52513,-0.00275,0.02459],"force_p95":4.22815,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.27194,"mean_force":1.06551,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50111,0.02655,0.03702]},{"body_a":"peg","body_b":"channel_base_body","contact_count":445.0,"contact_point_centroid":[0.50596,0.05466,0.00941],"force_p95":0.55024,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.49477,"mean_force":0.73549,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.5125,0.09996,0.08119]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.5057,0.07178,0.04536],"force_p95":9.45073,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.15624,"mean_force":4.59086,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.50523,0.08367,0.04538]},{"body_a":"peg","body_b":"channel_base_body","contact_count":520.0,"contact_point_centroid":[0.50582,0.05661,0.00935],"force_p95":0.60102,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.57712,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.51508,0.14481,0.20872]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.50018,0.19729,0.29533]},{"body_a":"peg","body_b":"channel_base_body","contact_count":318.0,"contact_point_centroid":[0.50614,0.05661,0.00938],"force_p95":0.55076,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55367,"mean_force":0.54675,"phase_index":1.0,"phase_name":"align_tool","phase_type":"align","tcp_position_centroid":[0.52514,0.10596,0.12166]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52513,0.05459,0.05939],"force_p95":0.29532,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29901,"mean_force":0.17763,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.50585,0.08511,0.04859]}],"total_contact_groups":9},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50635,-0.06155,0.03667],"final_tcp_position":[0.50076,-0.032,0.03652],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":3893.28022,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":549.0,"n_steps_budget":600.0,"object_pos_end":[0.50613,0.05663,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.53944,"phase_name":"approach_prepush","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":557.0,"raw_peak_contact_force":4.44541,"subtask_id":"pre_contact","tcp_end":[0.53072,0.09347,0.12642],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":318.0,"n_steps_budget":600.0,"object_pos_end":[0.50613,0.05663,0.03378],"object_pos_start":[0.50613,0.05663,0.03378],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.13691,"object_z_max":0.03378,"peak_contact_force":0.54515,"phase_name":"align_tool","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":318.0,"raw_peak_contact_force":0.55367,"subtask_id":"pre_contact","tcp_end":[0.5224,0.11671,0.12091],"tcp_start":[0.53072,0.09347,0.12642],"tcp_to_object_dist_end":0.10708,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":455.0,"n_steps_budget":1000.0,"object_pos_end":[0.5069,0.05233,0.03558],"object_pos_start":[0.50613,0.05663,0.03378],"object_to_goal_dist_end":0.13258,"object_to_goal_dist_start":0.13691,"object_z_max":0.03636,"peak_contact_force":3893.28022,"phase_name":"contact_engage","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":473.0,"raw_peak_contact_force":10.49477,"subtask_id":"pre_contact","tcp_end":[0.50443,0.08182,0.04128],"tcp_start":[0.5224,0.11671,0.12091],"tcp_to_object_dist_end":0.03013,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.50635,-0.06155,0.03667],"object_pos_start":[0.5069,0.05233,0.03558],"object_to_goal_dist_end":0.01979,"object_to_goal_dist_start":0.13258,"object_z_max":0.03712,"peak_contact_force":0.12476,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":442.0,"raw_peak_contact_force":23.10023,"subtask_id":"push_progress","tcp_end":[0.50076,-0.032,0.03652],"tcp_start":[0.50443,0.08182,0.04128],"tcp_to_object_dist_end":0.03008,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```