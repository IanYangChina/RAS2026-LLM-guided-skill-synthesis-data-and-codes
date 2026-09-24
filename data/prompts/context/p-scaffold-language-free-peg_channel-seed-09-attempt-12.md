## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → align → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.0437 | 0.12 | ❌ rejected |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | 0.3691 | 0.18 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | 0.0845 | 0.12 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | 0.3782 | 0.23 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.2691 | 0.03 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`
- Frozen object start: [0.5296199363176067, 0.06294537672700443, 0.04]
- Frozen task target: [0.5296199363176067, -0.09705462327299558, 0.04]
- Goal object position: (0.5296199363176067, -0.09705462327299558, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5296199363176067, 0.06294537672700443, 0.04)
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
  frozen_object_start: [0.5296, 0.0629, 0.04]
  frozen_task_target: [0.5296, -0.0971, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5296199363176067, 0.06294537672700443, 0.04]}
  frozen_targets: {'channel_exit': [0.5296199363176067, -0.09705462327299558, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9

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
| `object` | offset from object initial position (0.5296199363176067, 0.06294537672700443, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5296199363176067, -0.09705462327299558, 0.04) | final destination targets |
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

## Current Skill (Q=-0.044) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.05
  weight: 0.3
- id: push_through_channel
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_peg
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
    - 0.06
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
    lateral_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_peg
- id: contact_peg
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
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: peg_contact
    when: after_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.005
    - 0.0
- id: push_along_channel
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
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
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_through_channel
- id: retract_from_channel
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.06, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - lateral_offset: status=consumed; consumers=target.offset.x (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=peg_contact, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.005, 0.0]
- **push_along_channel** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_from_channel** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.044
- **task_score** (E): 0.116
- **fitness_score**: 0.296  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.590

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2154 |
| align_tool | 1.00 | 1.00 | 0.0260 |
| contact_peg | 1.00 | 1.00 | 0.0449 |
| push_along_channel | 1.00 | 1.00 | 0.0148 |
| retract_from_channel | 1.00 | 1.00 | 0.0925 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.511, 0.130, 0.099) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.555 | 4.034 |
| align_tool | align | 1.00 / step_budget | (0.511, 0.130, 0.099)→(0.508, 0.127, 0.082) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.543 | 827.962 |
| contact_peg | contact | 1.00 / force_exceeded | (0.508, 0.127, 0.082)→(0.502, 0.094, 0.052) | (0.502, 0.067, 0.034)→(0.502, 0.066, 0.035) | 0.147→0.146 | 1.00 / 2.000 | 67.179 | 67.179 |
| push_along_channel | push | 1.00 / time_limit | (0.502, 0.094, 0.052)→(0.509, 0.082, 0.051) | (0.502, 0.066, 0.035)→(0.504, 0.017, 0.031) | 0.146→0.099 | 1.00 / 3.667 | 427.803 | 892.958 |
| retract_from_channel | retract | 1.00 / step_budget | (0.509, 0.082, 0.051)→(0.507, 0.081, 0.143) | (0.504, 0.017, 0.031)→(0.502, 0.017, 0.031) | 0.099→0.099 | 1.00 / 1.000 | 0.569 | 626.151 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.894
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.332
- phase_score: 0.769
- phase_breakdown.push_through_channel_score: 0.854
- phase_breakdown.reach_peg_score: 0.572

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.594
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.332
- **Median Q (composite search score)**: -0.182
- **K-run variance**: 0.0445
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.338


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `bf8103833c1e96f48e87b3ce39b3b3bf17e268470bd7b5c037546fb78b5150b8`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `98954a34ee744fa939070f7dadee8a411de43cdcfeddcf3b4bfc5c3a4c536020`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25434,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_tool.align_speed":0.04823,"approach_peg.approach_height":0.04523,"approach_peg.lateral_offset":-0.00147,"approach_peg.speed":0.0704,"contact_peg.contact_force":12.76679,"push_along_channel.push_distance":0.18996,"push_along_channel.push_speed":0.04854,"push_along_channel.push_time_limit":4.34104,"retract_from_channel.retract_height":0.08033,"retract_from_channel.speed":0.04696},"optimized_scores":{"best_composite_score":-0.18175,"best_fitness_score":0.15825,"best_task_score":0.01653},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":38.0,"contact_point_centroid":[0.5494,0.11962,0.0586],"force_p95":1034.4928,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1198.55159,"mean_force":385.88389,"phase_index":1.0,"phase_name":"align_tool","phase_type":"align","tcp_position_centroid":[0.53897,0.11606,0.06027]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":125.0,"contact_point_centroid":[0.47499,0.11999,0.05844],"force_p95":528.23314,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":737.95141,"mean_force":89.04786,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.51157,0.08178,0.05755]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":448.0,"contact_point_centroid":[0.47495,0.11992,0.05509],"force_p95":494.04183,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":557.7274,"mean_force":373.19126,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51289,0.07977,0.05162]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.52509,0.08198,0.05103],"force_p95":405.68902,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":437.80879,"mean_force":245.68253,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.51325,0.08077,0.05097]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":287.0,"contact_point_centroid":[0.52509,0.08115,0.05147],"force_p95":333.17225,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":365.11883,"mean_force":293.06189,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51323,0.08005,0.05143]},{"body_a":"world","body_b":"link7","contact_count":989.0,"contact_point_centroid":[0.50602,0.14613,-4e-05],"force_p95":231.26046,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":326.99385,"mean_force":161.43533,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51101,0.08244,0.052]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":237.0,"contact_point_centroid":[0.525,0.11993,0.06],"force_p95":306.73461,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":322.24088,"mean_force":153.29065,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51127,0.0792,0.05209]},{"body_a":"world","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.50622,0.14509,-3e-05],"force_p95":169.88795,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":170.93806,"mean_force":151.38764,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.51324,0.08064,0.05088]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50424,0.15485,-0.0],"force_p95":49.27982,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.27982,"mean_force":49.27982,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50594,0.09024,0.05119]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50574,0.05832,0.0094],"force_p95":0.58723,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.37408,"mean_force":0.60297,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51101,0.08251,0.05201]},{"body_a":"attachment","body_b":"peg","contact_count":23.0,"contact_point_centroid":[0.50544,0.07982,0.05748],"force_p95":4.51678,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.052,"mean_force":2.49579,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5104,0.08002,0.05222]},{"body_a":"peg","body_b":"channel_base_body","contact_count":694.0,"contact_point_centroid":[0.50576,0.06295,0.00936],"force_p95":0.5598,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56606,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51093,0.16192,0.19163]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49988,0.19857,0.29634]},{"body_a":"peg","body_b":"channel_base_body","contact_count":630.0,"contact_point_centroid":[0.50594,0.05614,0.00939],"force_p95":0.5552,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57013,"mean_force":0.54651,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.51099,0.0804,0.08403]},{"body_a":"peg","body_b":"channel_base_body","contact_count":233.0,"contact_point_centroid":[0.50611,0.06281,0.00938],"force_p95":0.55187,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55424,"mean_force":0.54655,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50807,0.10661,0.06411]},{"body_a":"peg","body_b":"channel_base_body","contact_count":194.0,"contact_point_centroid":[0.50607,0.06324,0.00938],"force_p95":0.55268,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55422,"mean_force":0.54657,"phase_index":1.0,"phase_name":"align_tool","phase_type":"align","tcp_position_centroid":[0.52467,0.11951,0.06907]}],"total_contact_groups":17},"final_pose_error":0.00991,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50591,0.0562,0.03378],"final_tcp_position":[0.511,0.07981,0.12153],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":1198.55159,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":722.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.06303,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54754,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":728.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_peg","tcp_end":[0.523,0.12674,0.09291],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08855,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":194.0,"n_steps_budget":600.0,"object_pos_end":[0.50603,0.06298,0.03381],"object_pos_start":[0.50595,0.06303,0.0338],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.14329,"object_z_max":0.03381,"peak_contact_force":0.54454,"phase_name":"align_tool","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":232.0,"raw_peak_contact_force":1198.55159,"tcp_end":[0.51174,0.12224,0.07885],"tcp_start":[0.523,0.12674,0.09291],"tcp_to_object_dist_end":0.07466,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":233.0,"n_steps_budget":600.0,"object_pos_end":[0.50595,0.06295,0.03381],"object_pos_start":[0.50603,0.06298,0.03381],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14324,"object_z_max":0.03381,"peak_contact_force":49.27982,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":234.0,"raw_peak_contact_force":49.27982,"tcp_end":[0.50593,0.09013,0.0511],"tcp_start":[0.51174,0.12224,0.07885],"tcp_to_object_dist_end":0.03221,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5058,0.05619,0.03388],"object_pos_start":[0.50595,0.06295,0.03381],"object_to_goal_dist_end":0.13645,"object_to_goal_dist_start":0.14321,"object_z_max":0.0363,"peak_contact_force":463.27512,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2987.0,"raw_peak_contact_force":557.7274,"subtask_id":"push_through_channel","tcp_end":[0.51326,0.08066,0.05081],"tcp_start":[0.50593,0.09013,0.0511],"tcp_to_object_dist_end":0.03068,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":630.0,"n_steps_budget":1000.0,"object_pos_end":[0.50591,0.0562,0.03378],"object_pos_start":[0.5058,0.05619,0.03388],"object_to_goal_dist_end":0.13647,"object_to_goal_dist_start":0.13645,"object_z_max":0.03388,"peak_contact_force":0.54325,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":777.0,"raw_peak_contact_force":737.95141,"tcp_end":[0.511,0.07981,0.12153],"tcp_start":[0.51326,0.08066,0.05081],"tcp_to_object_dist_end":0.09102,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `cae0d95026bac46aa2e5d95cffd531753a79751757c4f25fa56c1ec6e19c2175`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.03629,"average_solve_count":248.0,"average_success_count":248.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_tool.align_speed":0.05961,"approach_peg.approach_height":0.04192,"approach_peg.lateral_offset":0.00598,"approach_peg.speed":0.04415,"contact_peg.contact_force":8.41679,"push_along_channel.push_distance":0.15545,"push_along_channel.push_speed":0.0537,"push_along_channel.push_time_limit":2.5385,"retract_from_channel.retract_height":0.12385,"retract_from_channel.speed":0.03687},"optimized_scores":{"best_composite_score":-0.20377,"best_fitness_score":0.13623,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":56.0,"contact_point_centroid":[0.55357,0.11351,0.05891],"force_p95":1024.63954,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1284.77199,"mean_force":340.7697,"phase_index":1.0,"phase_name":"align_tool","phase_type":"align","tcp_position_centroid":[0.55574,0.10479,0.06426]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":119.0,"contact_point_centroid":[0.47499,0.11998,0.0581],"force_p95":530.19509,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":673.97366,"mean_force":94.67438,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.51165,0.082,0.05703]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":498.0,"contact_point_centroid":[0.47495,0.11992,0.05467],"force_p95":513.5957,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":564.07725,"mean_force":417.2057,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51317,0.07993,0.05128]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.52509,0.08231,0.05053],"force_p95":388.82104,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":423.97533,"mean_force":245.23479,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.51325,0.08104,0.05046]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":305.0,"contact_point_centroid":[0.525,0.11994,0.06],"force_p95":336.33663,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":384.62875,"mean_force":164.97918,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51162,0.0792,0.05227]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":415.0,"contact_point_centroid":[0.5251,0.08121,0.05118],"force_p95":340.05198,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":367.95471,"mean_force":304.57769,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51326,0.0801,0.05113]},{"body_a":"world","body_b":"link7","contact_count":976.0,"contact_point_centroid":[0.50647,0.14388,-5e-05],"force_p95":195.20748,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":363.37429,"mean_force":157.83942,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51173,0.08082,0.05194]},{"body_a":"world","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.50545,0.14125,-3e-05],"force_p95":180.64315,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":184.17474,"mean_force":156.86025,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.51326,0.08093,0.05035]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50561,0.14922,-4e-05],"force_p95":141.0466,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":141.0466,"mean_force":141.0466,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50774,0.08605,0.05288]},{"body_a":"peg","body_b":"channel_base_body","contact_count":771.0,"contact_point_centroid":[0.50592,0.05663,0.00936],"force_p95":0.60168,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56714,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51782,0.15876,0.18958]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49996,0.1985,0.29629]},{"body_a":"peg","body_b":"channel_base_body","contact_count":225.0,"contact_point_centroid":[0.50613,0.0565,0.00938],"force_p95":0.60881,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62363,"mean_force":0.54642,"phase_index":1.0,"phase_name":"align_tool","phase_type":"align","tcp_position_centroid":[0.53876,0.11043,0.07248]},{"body_a":"peg","body_b":"channel_base_body","contact_count":217.0,"contact_point_centroid":[0.50611,0.0568,0.00938],"force_p95":0.5542,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55965,"mean_force":0.54665,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51055,0.10137,0.06501]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50612,0.05658,0.00939],"force_p95":0.55298,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55686,"mean_force":0.5464,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51174,0.0808,0.05194]},{"body_a":"peg","body_b":"channel_base_body","contact_count":978.0,"contact_point_centroid":[0.50615,0.05658,0.00939],"force_p95":0.55162,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55442,"mean_force":0.54633,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.51109,0.08052,0.10442]}],"total_contact_groups":15},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50603,0.05667,0.03386],"final_tcp_position":[0.51131,0.08035,0.16443],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":1284.77199,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":800.0,"n_steps_budget":1000.0,"object_pos_end":[0.50615,0.0566,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.58341,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":808.0,"raw_peak_contact_force":4.44541,"subtask_id":"reach_peg","tcp_end":[0.5365,0.12048,0.08868],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":225.0,"n_steps_budget":600.0,"object_pos_end":[0.50611,0.05664,0.03379],"object_pos_start":[0.50615,0.0566,0.03377],"object_to_goal_dist_end":0.13692,"object_to_goal_dist_start":0.13688,"object_z_max":0.03379,"peak_contact_force":0.54124,"phase_name":"align_tool","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":281.0,"raw_peak_contact_force":1284.77199,"tcp_end":[0.51463,0.11573,0.07879],"tcp_start":[0.5365,0.12048,0.08868],"tcp_to_object_dist_end":0.07476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":217.0,"n_steps_budget":600.0,"object_pos_end":[0.50617,0.05664,0.03381],"object_pos_start":[0.50611,0.05664,0.03379],"object_to_goal_dist_end":0.13692,"object_to_goal_dist_start":0.13692,"object_z_max":0.03381,"peak_contact_force":141.0466,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":218.0,"raw_peak_contact_force":141.0466,"tcp_end":[0.50773,0.08596,0.05279],"tcp_start":[0.51463,0.11573,0.07879],"tcp_to_object_dist_end":0.03496,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.0567,0.03384],"object_pos_start":[0.50617,0.05664,0.03381],"object_to_goal_dist_end":0.13697,"object_to_goal_dist_start":0.13692,"object_z_max":0.03384,"peak_contact_force":562.95084,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3194.0,"raw_peak_contact_force":564.07725,"subtask_id":"push_through_channel","tcp_end":[0.51329,0.08094,0.0503],"tcp_start":[0.50773,0.08596,0.05279],"tcp_to_object_dist_end":0.03017,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":978.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.05667,0.03386],"object_pos_start":[0.50611,0.0567,0.03384],"object_to_goal_dist_end":0.13694,"object_to_goal_dist_start":0.13697,"object_z_max":0.03386,"peak_contact_force":0.54665,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1120.0,"raw_peak_contact_force":673.97366,"tcp_end":[0.51131,0.08035,0.16443],"tcp_start":[0.51329,0.08094,0.0503],"tcp_to_object_dist_end":0.13281,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fd7ada9a67242f1adcdb6e23860d1223cdc8a17daf859e94e1687ff0564d9575`; realized-scene SHA-256: `8df62a5afc1e0110114ab6e06b493b5783d0c746729f7f7f1f2cb046babeda91`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47029,0.07994,0.04]},{"name":"goal","value":[0.47029,-0.08006,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,0.07994,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.47029,-0.08006,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.49673,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_tool.align_speed":0.06628,"approach_peg.approach_height":0.0651,"approach_peg.lateral_offset":0.00434,"approach_peg.speed":0.08969,"contact_peg.contact_force":8.86517,"push_along_channel.push_distance":0.13788,"push_along_channel.push_speed":0.05326,"push_along_channel.push_time_limit":2.31979,"retract_from_channel.retract_height":0.10241,"retract_from_channel.speed":0.06027},"optimized_scores":{"best_composite_score":0.25447,"best_fitness_score":0.59447,"best_task_score":0.33234},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.53692,0.11983,0.05971],"force_p95":801.50398,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1557.06926,"mean_force":534.30945,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50101,0.09525,0.03446]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52555,0.10103,0.0599],"force_p95":1140.8168,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1147.15208,"mean_force":1001.76081,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50941,0.0924,0.03605]},{"body_a":"world","body_b":"link7","contact_count":883.0,"contact_point_centroid":[0.49019,0.15012,-8e-05],"force_p95":306.39882,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":651.4082,"mean_force":226.02758,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49725,0.08624,0.05101]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.47495,0.09285,0.03222],"force_p95":493.16503,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":504.4131,"mean_force":296.58412,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48682,0.09157,0.03183]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":476.0,"contact_point_centroid":[0.46721,0.11992,0.06],"force_p95":350.31629,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":477.45458,"mean_force":266.46688,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49953,0.0822,0.05185]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.46547,0.11999,0.06],"force_p95":298.54745,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":466.52775,"mean_force":53.72381,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.50007,0.0837,0.05914]},{"body_a":"world","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.4912,0.14693,-5e-05],"force_p95":383.75063,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":411.31782,"mean_force":254.35557,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.50161,0.08371,0.05179]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49442,0.09202,0.05354],"force_p95":98.3753,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":98.62664,"mean_force":80.58616,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4938,0.10383,0.05191]},{"body_a":"peg","body_b":"channel_base_body","contact_count":939.0,"contact_point_centroid":[0.50283,-0.06027,0.00814],"force_p95":0.74536,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":97.08633,"mean_force":0.91056,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49718,0.08684,0.0505]},{"body_a":"peg","body_b":"channel_base_body","contact_count":365.0,"contact_point_centroid":[0.49404,0.07844,0.00939],"force_p95":0.60399,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.21095,"mean_force":0.66114,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48613,0.12622,0.05577]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.49282,0.09623,0.05566],"force_p95":9.8802,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.08789,"mean_force":5.13876,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.4917,0.10806,0.05428]},{"body_a":"peg","body_b":"channel_base_body","contact_count":693.0,"contact_point_centroid":[0.49589,-0.06326,0.00809],"force_p95":0.69261,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.54725,"mean_force":0.6384,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49958,0.08309,0.09688]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.525,-0.08648,0.02431],"force_p95":8.11442,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.28221,"mean_force":3.39975,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49628,0.08804,0.05209]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47499,-0.03923,0.02424],"force_p95":8.13048,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.15517,"mean_force":2.49386,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49948,0.08288,0.10596]},{"body_a":"peg","body_b":"channel_base_body","contact_count":565.0,"contact_point_centroid":[0.49414,0.07995,0.00937],"force_p95":0.58913,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.5691,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48556,0.17043,0.20264]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49908,0.19857,0.29597]}],"total_contact_groups":17},"final_pose_error":0.0099,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49507,-0.06303,0.02416],"final_tcp_position":[0.49972,0.08313,0.14441],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":1557.06926,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":593.0,"n_steps_budget":1000.0,"object_pos_end":[0.4938,0.07996,0.03377],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.1602,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.53311,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":600.0,"raw_peak_contact_force":3.77147,"subtask_id":"reach_peg","tcp_end":[0.47342,0.14327,0.1143],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.49382,0.07993,0.03378],"object_pos_start":[0.4938,0.07996,0.03377],"object_to_goal_dist_end":0.16017,"object_to_goal_dist_start":0.1602,"object_z_max":0.03378,"peak_contact_force":0.54207,"phase_name":"align_tool","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":20.0,"raw_peak_contact_force":0.56107,"tcp_end":[0.49732,0.14298,0.08873],"tcp_start":[0.47342,0.14327,0.1143],"tcp_to_object_dist_end":0.08371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":365.0,"n_steps_budget":600.0,"object_pos_end":[0.49348,0.07775,0.03591],"object_pos_start":[0.49382,0.07993,0.03378],"object_to_goal_dist_end":0.15794,"object_to_goal_dist_start":0.16017,"object_z_max":0.03583,"peak_contact_force":11.21095,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":374.0,"raw_peak_contact_force":11.21095,"tcp_end":[0.49161,0.10616,0.05266],"tcp_start":[0.49732,0.14298,0.08873],"tcp_to_object_dist_end":0.03303,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49954,-0.06316,0.02415],"object_pos_start":[0.49348,0.07775,0.03591],"object_to_goal_dist_end":0.02313,"object_to_goal_dist_start":0.15794,"object_z_max":0.04467,"peak_contact_force":257.18215,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2345.0,"raw_peak_contact_force":1557.06926,"subtask_id":"push_through_channel","tcp_end":[0.50162,0.08371,0.05169],"tcp_start":[0.49161,0.10616,0.05266],"tcp_to_object_dist_end":0.14944,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":693.0,"n_steps_budget":1000.0,"object_pos_end":[0.49507,-0.06303,0.02416],"object_pos_start":[0.49954,-0.06316,0.02415],"object_to_goal_dist_end":0.02373,"object_to_goal_dist_start":0.02313,"object_z_max":0.02449,"peak_contact_force":0.61592,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":753.0,"raw_peak_contact_force":466.52775,"tcp_end":[0.49972,0.08313,0.14441],"tcp_start":[0.50162,0.08371,0.05169],"tcp_to_object_dist_end":0.18932,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```