## Search State

- **Seed**: 8
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → align → contact → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 12 | -0.1377 | 0.12 | ❌ rejected |
| 4 | approach → align → contact → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 12 | -0.0189 | 0.22 | ✅ accepted |
| 3 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.4630 | 0.18 | ✅ accepted |
| 2 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.0326 | 0.00 | ❌ rejected |
| 1 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | -0.0488 | 0.15 | ✅ accepted |

**Proposal policy**: task_score is 0.12 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.138) — your mutation base

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

- **Composite score**: -0.138
- **task_score** (E): 0.120
- **fitness_score**: 0.272  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.660

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_prepush | 1.00 | 1.00 | 0.1959 |
| align_tool | 1.00 | 1.00 | 0.0247 |
| contact_engage | 1.00 | 1.00 | 0.0844 |
| push_channel | 0.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_prepush | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.115, 0.127) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.532 | 3.526 |
| align_tool | align | 1.00 / step_budget | (0.513, 0.115, 0.127)→(0.504, 0.137, 0.122) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.555 | 0.586 |
| contact_engage | contact | 1.00 / force_exceeded | (0.504, 0.137, 0.122)→(0.499, 0.106, 0.045) | (0.503, 0.080, 0.034)→(0.503, 0.077, 0.036) | 0.160→0.157 | 1.00 / 2.333 | 11.331 | 12.822 |
| push_channel | push | 0.00 / guard_failure | (0.496, 0.038, 0.041)→(0.496, 0.038, 0.041) | (0.503, 0.077, 0.036)→(0.499, 0.010, 0.038) | 0.157→0.094 | 1.00 / 2.667 | 20.329 | 46.008 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.873
- alignment_error: None
- force_efficiency: 0.209
- terminal_score: 0.130
- phase_score: 0.704
- phase_breakdown.pre_contact_score: 0.190
- phase_breakdown.push_progress_score: 0.925

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.475
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.130
- **Median Q (composite search score)**: -0.205
- **K-run variance**: 0.0213
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.317


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":54.0,"average_success_count":54.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_tool.align_speed":0.08594,"approach_prepush.approach_speed":0.24097,"approach_prepush.approach_tolerance":0.02204,"contact_engage.contact_force_threshold":5.71891,"contact_engage.contact_speed":0.12454,"push_channel.push_distance":0.17893,"push_channel.push_force_guard_threshold":34.58046,"push_channel.push_pose_tolerance":0.01953,"push_channel.push_speed":0.07581,"push_channel.retry_offset_x":0.0064,"push_channel.retry_offset_y":-0.01195,"push_channel.retry_offset_z":0.00155},"optimized_scores":{"best_composite_score":-0.27268,"best_fitness_score":0.13732,"best_task_score":0.12146},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47493,0.11999,0.04806],"force_p95":55.90338,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":58.56758,"mean_force":26.28028,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48574,0.12156,0.04325]},{"body_a":"peg","body_b":"channel_base_body","contact_count":67.0,"contact_point_centroid":[0.49441,0.09511,0.00991],"force_p95":30.68312,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.60655,"mean_force":22.31424,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48639,0.1334,0.04407]},{"body_a":"attachment","body_b":"peg","contact_count":62.0,"contact_point_centroid":[0.49061,0.12178,0.04272],"force_p95":30.41337,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.27384,"mean_force":23.74043,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48632,0.13262,0.04399]},{"body_a":"peg","body_b":"channel_base_body","contact_count":472.0,"contact_point_centroid":[0.49661,0.11687,0.00952],"force_p95":0.62225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.43964,"mean_force":0.65712,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.47936,0.15824,0.08396]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.49216,0.13508,0.05676],"force_p95":8.62375,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.16007,"mean_force":4.60225,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.48664,0.14633,0.05138]},{"body_a":"peg","body_b":"channel_base_body","contact_count":442.0,"contact_point_centroid":[0.49629,0.11912,0.0094],"force_p95":0.61955,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55895,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.49115,0.17488,0.21011]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.49939,0.19885,0.2967]},{"body_a":"peg","body_b":"channel_base_body","contact_count":307.0,"contact_point_centroid":[0.49598,0.11921,0.00946],"force_p95":0.59987,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64701,"mean_force":0.53871,"phase_index":1.0,"phase_name":"align_tool","phase_type":"align","tcp_position_centroid":[0.47751,0.16271,0.12504]}],"total_contact_groups":8},"final_pose_error":0.15568,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49665,0.0934,0.03981],"final_tcp_position":[0.48574,0.12105,0.04316],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":58.56758,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":467.0,"n_steps_budget":600.0,"object_pos_end":[0.49604,0.11913,0.03395],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19926,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.51129,"phase_name":"approach_prepush","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":466.0,"raw_peak_contact_force":2.24822,"subtask_id":"pre_contact","tcp_end":[0.4842,0.15204,0.1293],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10157,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":307.0,"n_steps_budget":600.0,"object_pos_end":[0.49606,0.11915,0.03392],"object_pos_start":[0.49604,0.11913,0.03395],"object_to_goal_dist_end":0.19929,"object_to_goal_dist_start":0.19926,"object_z_max":0.03408,"peak_contact_force":0.57166,"phase_name":"align_tool","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":307.0,"raw_peak_contact_force":0.64701,"subtask_id":"pre_contact","tcp_end":[0.47361,0.17247,0.12438],"tcp_start":[0.4842,0.15204,0.1293],"tcp_to_object_dist_end":0.10737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":472.0,"n_steps_budget":600.0,"object_pos_end":[0.49625,0.11641,0.03621],"object_pos_start":[0.49606,0.11915,0.03392],"object_to_goal_dist_end":0.19648,"object_to_goal_dist_start":0.19929,"object_z_max":0.03621,"peak_contact_force":7.58076,"phase_name":"contact_engage","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":486.0,"raw_peak_contact_force":11.43964,"subtask_id":"pre_contact","tcp_end":[0.48795,0.14433,0.04587],"tcp_start":[0.47361,0.17247,0.12438],"tcp_to_object_dist_end":0.03069,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":67.0,"n_steps_budget":1000.0,"object_pos_end":[0.4963,0.09399,0.03982],"object_pos_start":[0.49625,0.11641,0.03621],"object_to_goal_dist_end":0.17403,"object_to_goal_dist_start":0.19648,"object_z_max":0.03983,"peak_contact_force":40.80624,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":133.0,"raw_peak_contact_force":58.56758,"subtask_id":"push_progress","tcp_end":[0.48574,0.12105,0.04316],"tcp_start":[0.48574,0.12121,0.04321],"tcp_to_object_dist_end":0.02924,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5443,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_tool.align_speed":0.36236,"approach_prepush.approach_speed":0.42368,"approach_prepush.approach_tolerance":0.0195,"contact_engage.contact_force_threshold":13.87687,"contact_engage.contact_speed":0.17455,"push_channel.push_distance":0.20438,"push_channel.push_force_guard_threshold":39.02845,"push_channel.push_pose_tolerance":0.0096,"push_channel.push_speed":0.02294,"push_channel.retry_offset_x":-0.00024,"push_channel.retry_offset_y":-0.01172,"push_channel.retry_offset_z":-0.00159},"optimized_scores":{"best_composite_score":-0.20509,"best_fitness_score":0.20491,"best_task_score":0.10885},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":128.0,"contact_point_centroid":[0.50435,0.03131,0.00986],"force_p95":37.60472,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.91889,"mean_force":26.60164,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50201,0.07015,0.04315]},{"body_a":"attachment","body_b":"peg","contact_count":126.0,"contact_point_centroid":[0.50408,0.05836,0.04265],"force_p95":37.22776,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.52462,"mean_force":26.65309,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50198,0.06984,0.04312]},{"body_a":"peg","body_b":"channel_base_body","contact_count":385.0,"contact_point_centroid":[0.50584,0.06141,0.0094],"force_p95":0.55393,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.6807,"mean_force":0.70475,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.50868,0.10621,0.08241]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.505,0.07973,0.04976],"force_p95":12.69074,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.49811,"mean_force":7.35631,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.50434,0.09169,0.04974]},{"body_a":"peg","body_b":"channel_base_body","contact_count":520.0,"contact_point_centroid":[0.50578,0.063,0.00936],"force_p95":0.56846,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57257,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.51179,0.14782,0.20877]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.50003,0.19759,0.29572]},{"body_a":"peg","body_b":"channel_base_body","contact_count":321.0,"contact_point_centroid":[0.50598,0.06292,0.00938],"force_p95":0.55136,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54657,"phase_index":1.0,"phase_name":"align_tool","phase_type":"align","tcp_position_centroid":[0.51863,0.11164,0.12181]}],"total_contact_groups":7},"final_pose_error":0.16298,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50583,0.01839,0.04011],"final_tcp_position":[0.5017,0.04836,0.04256],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":39.91889,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":548.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.06294,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54018,"phase_name":"approach_prepush","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":554.0,"raw_peak_contact_force":3.88411,"subtask_id":"pre_contact","tcp_end":[0.52434,0.09934,0.12651],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":321.0,"n_steps_budget":600.0,"object_pos_end":[0.50595,0.06295,0.03381],"object_pos_start":[0.50599,0.06294,0.03381],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":0.54576,"phase_name":"align_tool","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":321.0,"raw_peak_contact_force":0.55501,"subtask_id":"pre_contact","tcp_end":[0.51579,0.12221,0.12109],"tcp_start":[0.52434,0.09934,0.12651],"tcp_to_object_dist_end":0.10596,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":385.0,"n_steps_budget":600.0,"object_pos_end":[0.50571,0.06061,0.03588],"object_pos_start":[0.50595,0.06295,0.03381],"object_to_goal_dist_end":0.14079,"object_to_goal_dist_start":0.14321,"object_z_max":0.03589,"peak_contact_force":14.6807,"phase_name":"contact_engage","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":394.0,"raw_peak_contact_force":14.6807,"subtask_id":"pre_contact","tcp_end":[0.50384,0.0898,0.04547],"tcp_start":[0.51579,0.12221,0.12109],"tcp_to_object_dist_end":0.03078,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":128.0,"n_steps_budget":1000.0,"object_pos_end":[0.50579,0.01897,0.04011],"object_pos_start":[0.50571,0.06061,0.03588],"object_to_goal_dist_end":0.09914,"object_to_goal_dist_start":0.14079,"object_z_max":0.04011,"peak_contact_force":13.71292,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":254.0,"raw_peak_contact_force":39.91889,"subtask_id":"push_progress","tcp_end":[0.5017,0.04836,0.04256],"tcp_start":[0.50172,0.04848,0.04261],"tcp_to_object_dist_end":0.02977,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42857,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_tool.align_speed":0.22921,"approach_prepush.approach_speed":0.18347,"approach_prepush.approach_tolerance":0.02544,"contact_engage.contact_force_threshold":10.02636,"contact_engage.contact_speed":0.12586,"push_channel.push_distance":0.17792,"push_channel.push_force_guard_threshold":34.45588,"push_channel.push_pose_tolerance":0.02208,"push_channel.push_speed":0.04049,"push_channel.retry_offset_x":0.01048,"push_channel.retry_offset_y":-0.00781,"push_channel.retry_offset_z":-0.0069},"optimized_scores":{"best_composite_score":0.06478,"best_fitness_score":0.47478,"best_task_score":0.13035},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":218.0,"contact_point_centroid":[0.50446,0.01165,0.04482],"force_p95":22.49103,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.53883,"mean_force":5.14233,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50169,0.02326,0.03926]},{"body_a":"peg","body_b":"channel_base_body","contact_count":164.0,"contact_point_centroid":[0.50501,-0.03235,0.00962],"force_p95":24.34249,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.51516,"mean_force":6.88659,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50156,0.00963,0.03908]},{"body_a":"peg","body_b":"channel_base_body","contact_count":13.0,"contact_point_centroid":[0.49407,-0.10055,0.05017],"force_p95":23.42439,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.85056,"mean_force":4.3713,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50112,-0.05324,0.03845]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":142.0,"contact_point_centroid":[0.52516,0.00174,0.02693],"force_p95":9.20525,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.81323,"mean_force":1.65283,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50172,0.03094,0.03931]},{"body_a":"peg","body_b":"channel_base_body","contact_count":378.0,"contact_point_centroid":[0.50574,0.05478,0.00941],"force_p95":0.55353,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.34597,"mean_force":0.69242,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.51272,0.09986,0.0809]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50589,0.07324,0.04885],"force_p95":11.83279,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.23934,"mean_force":6.75019,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.50591,0.08519,0.04869]},{"body_a":"peg","body_b":"channel_base_body","contact_count":574.0,"contact_point_centroid":[0.50585,0.05664,0.00935],"force_p95":0.60289,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.57429,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.51531,0.14387,0.20721]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_prepush","phase_type":"approach","tcp_position_centroid":[0.50017,0.19727,0.29521]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":20.0,"contact_point_centroid":[0.47474,-0.07225,0.03772],"force_p95":1.40137,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.55345,"mean_force":0.49411,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50115,-0.04321,0.0385]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.5251,0.05127,0.06],"force_p95":0.60504,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60504,"mean_force":0.60504,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.50492,0.08285,0.04354]},{"body_a":"peg","body_b":"channel_base_body","contact_count":329.0,"contact_point_centroid":[0.50613,0.05647,0.00938],"force_p95":0.55186,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55559,"mean_force":0.54652,"phase_index":1.0,"phase_name":"align_tool","phase_type":"align","tcp_position_centroid":[0.52528,0.10552,0.12051]}],"total_contact_groups":11},"final_pose_error":0.04034,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49345,-0.08301,0.03287],"final_tcp_position":[0.50101,-0.05532,0.03833],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":39.53883,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":603.0,"n_steps_budget":750.0,"object_pos_end":[0.50617,0.05664,0.0338],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13692,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54532,"phase_name":"approach_prepush","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":611.0,"raw_peak_contact_force":4.44541,"subtask_id":"pre_contact","tcp_end":[0.53092,0.09277,0.12529],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10144,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":329.0,"n_steps_budget":600.0,"object_pos_end":[0.50609,0.05667,0.03382],"object_pos_start":[0.50617,0.05664,0.0338],"object_to_goal_dist_end":0.13695,"object_to_goal_dist_start":0.13692,"object_z_max":0.03382,"peak_contact_force":0.54729,"phase_name":"align_tool","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":329.0,"raw_peak_contact_force":0.55559,"subtask_id":"pre_contact","tcp_end":[0.52256,0.11627,0.11978],"tcp_start":[0.53092,0.09277,0.12529],"tcp_to_object_dist_end":0.10588,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":378.0,"n_steps_budget":600.0,"object_pos_end":[0.50671,0.05364,0.03628],"object_pos_start":[0.50609,0.05667,0.03382],"object_to_goal_dist_end":0.13386,"object_to_goal_dist_start":0.13695,"object_z_max":0.03627,"peak_contact_force":11.73019,"phase_name":"contact_engage","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":388.0,"raw_peak_contact_force":12.34597,"subtask_id":"pre_contact","tcp_end":[0.50488,0.08276,0.04334],"tcp_start":[0.52256,0.11627,0.11978],"tcp_to_object_dist_end":0.03002,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":368.0,"n_steps_budget":1000.0,"object_pos_end":[0.49367,-0.08307,0.0328],"object_pos_start":[0.50671,0.05364,0.03628],"object_to_goal_dist_end":0.01007,"object_to_goal_dist_start":0.13386,"object_z_max":0.03991,"peak_contact_force":6.46927,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":557.0,"raw_peak_contact_force":39.53883,"subtask_id":"push_progress","tcp_end":[0.50101,-0.05532,0.03833],"tcp_start":[0.50106,-0.05518,0.03839],"tcp_to_object_dist_end":0.02924,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```