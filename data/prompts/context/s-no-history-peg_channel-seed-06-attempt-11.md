## Search State

- **Seed**: 6
- **Iteration**: 12 / 15

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
- Frozen realised-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`
- Frozen object start: [0.5030531481177555, 0.06746166958506708, 0.04]
- Frozen task target: [0.5030531481177555, -0.09253833041493292, 0.04]
- Goal object position: (0.5030531481177555, -0.09253833041493292, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5030531481177555, 0.06746166958506708, 0.04)
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
  frozen_object_start: [0.5031, 0.0675, 0.04]
  frozen_task_target: [0.5031, -0.0925, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5030531481177555, 0.06746166958506708, 0.04]}
  frozen_targets: {'channel_exit': [0.5030531481177555, -0.09253833041493292, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.872, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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
| `object` | offset from object initial position (0.5030531481177555, 0.06746166958506708, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5030531481177555, -0.09253833041493292, 0.04) | final destination targets |
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

## Current Skill (Q=0.396) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_high
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.08
  weight: 0.1
- id: descend_to_contact
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.0
  weight: 0.1
- id: align_at_channel
  anchor: object
  weight: 0.2
- id: push_through_channel
  metric: goal_progress
  weight: 0.6
phases:
- id: approach_high
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
    - 0.03
    - 0.08
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.07
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: approach_force_guard
    when: during_phase
    predicate: force_below
    threshold: 60.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: approach_high
- id: descend_to_peg
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.03
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 12.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.005
      - 0.04
      default: 0.015
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: descend_force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  subtask_id: descend_to_contact
- id: align_at_channel
  type: contact
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.02
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    align_force_threshold:
      type: scalar
      range:
      - 8.0
      - 25.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    align_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: align_force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  subtask_id: align_at_channel
- id: push_through
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
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
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.16
      default: 0.14
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_force_guard_threshold:
      type: scalar
      range:
      - 30.0
      - 60.0
      default: 45.0
      binds_to:
      - path: guards.push_force_guard.threshold
        mode: replace
    push_retry_offset_x:
      type: scalar
      range:
      - -0.015
      - 0.015
      default: -0.008
      binds_to:
      - path: retry.offset.x
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: push_force_guard
    when: during_phase
    predicate: force_below
    threshold: 45.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - -0.008
    - 0.0
    - 0.0
  subtask_id: push_through_channel
- id: retract_after_push
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
    - 0.05
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
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
- **approach_high** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.08], tolerance=0.02
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=approach_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=60.0
  - retries: max_attempts=1, strategy=reduce_speed
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.0]
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=descend_force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
- **align_at_channel** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.02, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - align_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - align_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=align_force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
- **push_through** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_force_guard_threshold: status=consumed; consumers=guards.push_force_guard.threshold (replace)
    - push_retry_offset_x: status=consumed; consumers=retry.offset.x (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=push_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=45.0
  - retries: max_attempts=2, strategy=offset_target, offset=[-0.008, 0.0, 0.0]
- **retract_after_push** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.396
- **task_score** (E): 0.859
- **fitness_score**: 0.870  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.067
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.1754 |
| descend_to_peg | 0.00 | 1.00 | 0.1015 |
| align_at_channel | 0.33 | 1.00 | 0.0257 |
| push_through | 0.67 | 1.00 | 0.1134 |
| retract_after_push | 1.00 | 1.00 | 0.0310 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.137, 0.138) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.529 | 2.127 |
| descend_to_peg | descend | 0.00 / step_budget | (0.497, 0.137, 0.138)→(0.497, 0.129, 0.037) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.179 | 1.00 / 1.000 | 0.483 | 3.415 |
| align_at_channel | contact | 0.33 / step_budget | (0.497, 0.129, 0.037)→(0.495, 0.104, 0.031) | (0.501, 0.099, 0.034)→(0.505, 0.076, 0.036) | 0.179→0.156 | 1.00 / 2.000 | 1307.646 | 8.218 |
| push_through | push | 0.67 / step_budget | (0.496, 0.060, 0.030)→(0.500, -0.053, 0.030) | (0.505, 0.076, 0.036)→(0.505, -0.082, 0.036) | 0.156→0.007 | 1.00 / 2.000 | 8.705 | 56.715 |
| retract_after_push | retract | 1.00 / step_budget | (0.500, -0.053, 0.030)→(0.496, -0.052, 0.061) | (0.504, -0.082, 0.036)→(0.503, -0.080, 0.042) | 0.007→0.008 | 1.00 / 1.667 | 12.083 | 23.671 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.867
- phase_breakdown.descend_to_contact_score: 0.814
- phase_breakdown.align_at_channel_score: 0.700
- phase_breakdown.approach_high_score: 0.675
- phase_breakdown.push_through_channel_score: 0.964

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.920
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.356
- **K-run variance**: 0.0187
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.311


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `080f370e6b427cbdf66706e7036a0e474f3967ccfc94f129756881a980a10a27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1f3f20d8b9dd2cb87de5d9f0723b4addbc88cdcf096cd2177633d23c0fa32881`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.58908,"average_solve_count":348.0,"average_success_count":348.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_channel.align_force_threshold":11.77069,"align_at_channel.align_speed":0.01068,"approach_high.approach_speed":0.06736,"descend_to_peg.contact_force_threshold":12.63381,"descend_to_peg.descend_speed":0.0115,"push_through.push_retry_offset_x":0.01147,"push_through.push_retry_offset_y":-0.00791,"push_through.push_speed":0.02229,"retract_after_push.retract_speed":0.05364},"optimized_scores":{"best_composite_score":0.35644,"best_fitness_score":0.89644,"best_task_score":0.92377},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":19.0,"contact_point_centroid":[0.50271,-0.10112,0.03776],"force_p95":50.60321,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.93944,"mean_force":24.20133,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49995,-0.0556,0.02946]},{"body_a":"attachment","body_b":"peg","contact_count":276.0,"contact_point_centroid":[0.50285,0.00114,0.04704],"force_p95":35.81209,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":76.43228,"mean_force":10.82055,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.4967,0.0125,0.02832]},{"body_a":"attachment","body_b":"peg","contact_count":120.0,"contact_point_centroid":[0.49999,-0.06749,0.05096],"force_p95":43.40138,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.26086,"mean_force":26.72798,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49688,-0.05647,0.04416]},{"body_a":"peg","body_b":"channel_base_body","contact_count":120.0,"contact_point_centroid":[0.50268,-0.10148,0.05028],"force_p95":43.89914,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.04396,"mean_force":26.60756,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49688,-0.05647,0.04416]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":255.0,"contact_point_centroid":[0.52539,-0.00927,0.03555],"force_p95":34.12993,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.03625,"mean_force":7.7215,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49626,0.01889,0.02808]},{"body_a":"peg","body_b":"channel_base_body","contact_count":121.0,"contact_point_centroid":[0.50665,-0.03562,0.00981],"force_p95":19.04327,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.02723,"mean_force":7.61997,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49706,0.00837,0.02857]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.5251,-0.08543,0.05976],"force_p95":9.87612,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.1024,"mean_force":6.26932,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49742,-0.05775,0.03896]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47486,-0.08601,0.02126],"force_p95":8.12317,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.58967,"mean_force":4.30941,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49787,-0.05817,0.03557]},{"body_a":"peg","body_b":"channel_base_body","contact_count":968.0,"contact_point_centroid":[0.50403,0.03835,0.00996],"force_p95":3.43945,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.28528,"mean_force":1.54716,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49635,0.08404,0.03147]},{"body_a":"attachment","body_b":"peg","contact_count":979.0,"contact_point_centroid":[0.50049,0.0722,0.03811],"force_p95":3.08399,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.98113,"mean_force":1.2177,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49632,0.08378,0.03139]},{"body_a":"peg","body_b":"channel_base_body","contact_count":380.0,"contact_point_centroid":[0.50304,0.06753,0.00932],"force_p95":0.61717,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56928,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49856,0.15705,0.21811]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51098,-0.08574,0.01],"force_p95":1.39554,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.39554,"mean_force":1.39554,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.4982,-0.0583,0.03295]},{"body_a":"peg","body_b":"channel_base_body","contact_count":640.0,"contact_point_centroid":[0.50309,0.06745,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55159,"mean_force":0.54664,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49815,0.10281,0.08453]}],"total_contact_groups":13},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.503,-0.08034,0.0516],"final_tcp_position":[0.49554,-0.05393,0.06047],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":76.93944,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":396.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54568,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":380.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_high","tcp_end":[0.50002,0.10866,0.13599],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":640.0,"n_steps_budget":1000.0,"object_pos_end":[0.50307,0.06743,0.0338],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14761,"object_z_max":0.0338,"peak_contact_force":0.54573,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":640.0,"raw_peak_contact_force":0.55159,"subtask_id":"descend_to_contact","tcp_end":[0.49901,0.09755,0.03662],"tcp_start":[0.50002,0.10866,0.13599],"tcp_to_object_dist_end":0.03053,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50664,0.04637,0.03582],"object_pos_start":[0.50307,0.06743,0.0338],"object_to_goal_dist_end":0.12661,"object_to_goal_dist_start":0.14759,"object_z_max":0.03583,"peak_contact_force":1.46573,"phase_name":"align_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1947.0,"raw_peak_contact_force":9.28528,"subtask_id":"align_at_channel","tcp_end":[0.49688,0.07499,0.03074],"tcp_start":[0.49901,0.09755,0.03662],"tcp_to_object_dist_end":0.03067,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.50202,-0.08575,0.03709],"object_pos_start":[0.50664,0.04637,0.03582],"object_to_goal_dist_end":0.00675,"object_to_goal_dist_start":0.12661,"object_z_max":0.03717,"peak_contact_force":0.78288,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":671.0,"raw_peak_contact_force":76.93944,"subtask_id":"push_through_channel","tcp_end":[0.49992,-0.05835,0.02928],"tcp_start":[0.49997,-0.05822,0.02934],"tcp_to_object_dist_end":0.02856,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":120.0,"n_steps_budget":600.0,"object_pos_end":[0.503,-0.08034,0.0516],"object_pos_start":[0.50195,-0.08611,0.03724],"object_to_goal_dist_end":0.01199,"object_to_goal_dist_start":0.00698,"object_z_max":0.05147,"peak_contact_force":33.01588,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":257.0,"raw_peak_contact_force":45.26086,"tcp_end":[0.49554,-0.05393,0.06047],"tcp_start":[0.49992,-0.05835,0.02928],"tcp_to_object_dist_end":0.02884,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.92282,"average_solve_count":298.0,"average_success_count":298.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_channel.align_force_threshold":11.8195,"align_at_channel.align_speed":0.02342,"approach_high.approach_speed":0.10356,"descend_to_peg.contact_force_threshold":17.18534,"descend_to_peg.descend_speed":0.02426,"push_through.push_retry_offset_x":-0.00198,"push_through.push_retry_offset_y":0.01117,"push_through.push_speed":0.02068,"retract_after_push.retract_speed":0.03229},"optimized_scores":{"best_composite_score":0.58036,"best_fitness_score":0.92036,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":363.0,"contact_point_centroid":[0.50347,0.02935,0.04599],"force_p95":24.47292,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.01827,"mean_force":6.10913,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49813,0.04083,0.0291]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":309.0,"contact_point_centroid":[0.52527,0.01369,0.0345],"force_p95":23.52219,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.50703,"mean_force":5.25029,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49796,0.0424,0.02899]},{"body_a":"peg","body_b":"channel_base_body","contact_count":169.0,"contact_point_centroid":[0.50636,-0.0113,0.00983],"force_p95":19.05656,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.55874,"mean_force":6.04426,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49856,0.03279,0.02931]},{"body_a":"peg","body_b":"channel_base_body","contact_count":378.0,"contact_point_centroid":[0.50359,0.08411,0.00996],"force_p95":4.34633,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.42787,"mean_force":2.4243,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.4974,0.12979,0.03242]},{"body_a":"attachment","body_b":"peg","contact_count":381.0,"contact_point_centroid":[0.5015,0.11752,0.04023],"force_p95":4.0374,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.06438,"mean_force":2.08276,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49732,0.12913,0.03224]},{"body_a":"peg","body_b":"channel_base_body","contact_count":573.0,"contact_point_centroid":[0.50341,0.11049,0.00943],"force_p95":0.60981,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.57228,"mean_force":0.57829,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50183,0.14445,0.08605]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.50311,0.12965,0.05787],"force_p95":4.80557,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.16674,"mean_force":1.76483,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50024,0.14157,0.04203]},{"body_a":"peg","body_b":"channel_base_body","contact_count":312.0,"contact_point_centroid":[0.50355,0.11168,0.00935],"force_p95":0.66057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56953,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50185,0.17531,0.21608]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.52501,0.09421,0.02222],"force_p95":1.20309,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79045,"mean_force":0.75321,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49745,0.12226,0.03149]},{"body_a":"peg","body_b":"channel_base_body","contact_count":30.0,"contact_point_centroid":[0.50619,-0.10034,0.02297],"force_p95":0.83129,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.97869,"mean_force":0.36358,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50052,-0.0496,0.03805]},{"body_a":"peg","body_b":"channel_base_body","contact_count":97.0,"contact_point_centroid":[0.50373,-0.07792,0.00957],"force_p95":0.71094,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.8856,"mean_force":0.51181,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49991,-0.04926,0.04564]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49971,0.19974,0.29832]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50536,-0.06135,0.0551],"force_p95":0.21384,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26503,"mean_force":0.08114,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50218,-0.04967,0.0306]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":13.0,"contact_point_centroid":[0.52528,-0.08159,0.05896],"force_p95":0.15121,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20372,"mean_force":0.03198,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49987,-0.04928,0.04252]}],"total_contact_groups":14},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50646,-0.08127,0.03406],"final_tcp_position":[0.4993,-0.04888,0.06101],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":3919.93736,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11175,0.03384],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.54065,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":328.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach_high","tcp_end":[0.50621,0.14841,0.1381],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11055,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":1000.0,"object_pos_end":[0.50348,0.11137,0.03458],"object_pos_start":[0.50372,0.11175,0.03384],"object_to_goal_dist_end":0.19148,"object_to_goal_dist_start":0.19188,"object_z_max":0.03459,"peak_contact_force":0.42582,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":587.0,"raw_peak_contact_force":5.57228,"subtask_id":"descend_to_contact","tcp_end":[0.5001,0.14128,0.03722],"tcp_start":[0.50621,0.14841,0.1381],"tcp_to_object_dist_end":0.03022,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":417.0,"n_steps_budget":1000.0,"object_pos_end":[0.50699,0.0925,0.03581],"object_pos_start":[0.50348,0.11137,0.03458],"object_to_goal_dist_end":0.17269,"object_to_goal_dist_start":0.19148,"object_z_max":0.03585,"peak_contact_force":3919.93736,"phase_name":"align_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":796.0,"raw_peak_contact_force":6.42787,"subtask_id":"align_at_channel","tcp_end":[0.49751,0.12117,0.03143],"tcp_start":[0.5001,0.14128,0.03722],"tcp_to_object_dist_end":0.03051,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.50432,-0.07847,0.03579],"object_pos_start":[0.50699,0.0925,0.03581],"object_to_goal_dist_end":0.00622,"object_to_goal_dist_start":0.17269,"object_z_max":0.03731,"peak_contact_force":0.34954,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":841.0,"raw_peak_contact_force":35.01827,"subtask_id":"push_through_channel","tcp_end":[0.50243,-0.04904,0.03066],"tcp_start":[0.49751,0.12117,0.03143],"tcp_to_object_dist_end":0.02994,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":110.0,"n_steps_budget":960.0,"object_pos_end":[0.50646,-0.08127,0.03406],"object_pos_start":[0.50432,-0.07847,0.03579],"object_to_goal_dist_end":0.00887,"object_to_goal_dist_start":0.00622,"object_z_max":0.03638,"peak_contact_force":0.50931,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":149.0,"raw_peak_contact_force":0.97869,"tcp_end":[0.4993,-0.04888,0.06101],"tcp_start":[0.50243,-0.04904,0.03066],"tcp_to_object_dist_end":0.04273,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94346,"average_solve_count":283.0,"average_success_count":283.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_channel.align_force_threshold":15.19204,"align_at_channel.align_speed":0.0169,"approach_high.approach_speed":0.12661,"descend_to_peg.contact_force_threshold":15.36807,"descend_to_peg.descend_speed":0.03043,"push_through.push_retry_offset_x":0.00258,"push_through.push_retry_offset_y":-0.0082,"push_through.push_speed":0.01718,"retract_after_push.retract_speed":0.08491},"optimized_scores":{"best_composite_score":0.25261,"best_fitness_score":0.79261,"best_task_score":0.65251},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":475.0,"contact_point_centroid":[0.49984,0.02986,0.04872],"force_p95":52.8082,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.18817,"mean_force":30.84023,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.4908,0.04009,0.02794]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":475.0,"contact_point_centroid":[0.52545,0.00914,0.04728],"force_p95":48.71709,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.9692,"mean_force":27.12709,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49093,0.03522,0.0279]},{"body_a":"peg","body_b":"channel_base_body","contact_count":280.0,"contact_point_centroid":[0.5074,0.0019,0.00986],"force_p95":32.43139,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.56872,"mean_force":18.79383,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49089,0.04242,0.02807]},{"body_a":"peg","body_b":"link7","contact_count":171.0,"contact_point_centroid":[0.52119,0.04611,0.06282],"force_p95":23.39591,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.2452,"mean_force":13.60117,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48951,0.06063,0.0275]},{"body_a":"attachment","body_b":"peg","contact_count":81.0,"contact_point_centroid":[0.49951,-0.06421,0.05041],"force_p95":22.88225,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.77384,"mean_force":9.0564,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.4955,-0.05275,0.04475]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50731,-0.1001,0.05992],"force_p95":23.35319,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.78541,"mean_force":19.92225,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49786,-0.05238,0.03077]},{"body_a":"peg","body_b":"channel_base_body","contact_count":87.0,"contact_point_centroid":[0.5045,-0.10015,0.06063],"force_p95":20.42085,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.41629,"mean_force":8.72783,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49547,-0.05272,0.04461]},{"body_a":"peg","body_b":"channel_base_body","contact_count":943.0,"contact_point_centroid":[0.49742,0.08521,0.00996],"force_p95":3.76831,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.93994,"mean_force":1.96396,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.48947,0.1305,0.03097]},{"body_a":"attachment","body_b":"peg","contact_count":965.0,"contact_point_centroid":[0.49421,0.11883,0.03921],"force_p95":3.38846,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.69271,"mean_force":1.59706,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.48945,0.13029,0.03092]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.52514,-0.08248,0.05999],"force_p95":6.83327,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.08191,"mean_force":4.13497,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49621,-0.05304,0.03523]},{"body_a":"peg","body_b":"channel_base_body","contact_count":32.0,"contact_point_centroid":[0.51018,-0.09329,0.00953],"force_p95":4.55274,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.67653,"mean_force":2.11884,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49484,-0.05242,0.04882]},{"body_a":"peg","body_b":"channel_base_body","contact_count":651.0,"contact_point_centroid":[0.49592,0.1177,0.00945],"force_p95":0.63283,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.1226,"mean_force":0.57913,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48731,0.15118,0.08505]},{"body_a":"attachment","body_b":"peg","contact_count":27.0,"contact_point_centroid":[0.49441,0.13695,0.05831],"force_p95":3.4175,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.72963,"mean_force":1.16596,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49092,0.14883,0.04291]},{"body_a":"peg","body_b":"channel_base_body","contact_count":292.0,"contact_point_centroid":[0.49656,0.11904,0.00936],"force_p95":0.63934,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56996,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49157,0.17761,0.21476]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49918,0.19954,0.2963]}],"total_contact_groups":15},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4997,-0.07726,0.03964],"final_tcp_position":[0.49461,-0.05223,0.06129],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":58.18817,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":317.0,"n_steps_budget":930.0,"object_pos_end":[0.49602,0.11914,0.03382],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19928,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.49994,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":316.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_high","tcp_end":[0.48568,0.15479,0.13883],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":651.0,"n_steps_budget":1000.0,"object_pos_end":[0.49608,0.11865,0.03445],"object_pos_start":[0.49602,0.11914,0.03382],"object_to_goal_dist_end":0.19877,"object_to_goal_dist_start":0.19928,"object_z_max":0.03446,"peak_contact_force":0.47782,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":678.0,"raw_peak_contact_force":4.1226,"subtask_id":"descend_to_contact","tcp_end":[0.49156,0.14846,0.03589],"tcp_start":[0.48568,0.15479,0.13883],"tcp_to_object_dist_end":0.03018,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50281,0.08863,0.03605],"object_pos_start":[0.49608,0.11865,0.03445],"object_to_goal_dist_end":0.1687,"object_to_goal_dist_start":0.19877,"object_z_max":0.03612,"peak_contact_force":1.53476,"phase_name":"align_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1908.0,"raw_peak_contact_force":8.93994,"subtask_id":"align_at_channel","tcp_end":[0.49054,0.11645,0.03036],"tcp_start":[0.49156,0.14846,0.03589],"tcp_to_object_dist_end":0.03093,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":554.0,"n_steps_budget":1000.0,"object_pos_end":[0.50721,-0.08126,0.03608],"object_pos_start":[0.50281,0.08863,0.03605],"object_to_goal_dist_end":0.00831,"object_to_goal_dist_start":0.1687,"object_z_max":0.03762,"peak_contact_force":24.98343,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1404.0,"raw_peak_contact_force":58.18817,"subtask_id":"push_through_channel","tcp_end":[0.49789,-0.05303,0.03077],"tcp_start":[0.49054,0.11645,0.03036],"tcp_to_object_dist_end":0.0302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":108.0,"n_steps_budget":600.0,"object_pos_end":[0.4997,-0.07726,0.03964],"object_pos_start":[0.50721,-0.08126,0.03608],"object_to_goal_dist_end":0.00278,"object_to_goal_dist_start":0.00831,"object_z_max":0.03947,"peak_contact_force":2.72521,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":237.0,"raw_peak_contact_force":24.77384,"tcp_end":[0.49461,-0.05223,0.06129],"tcp_start":[0.49789,-0.05303,0.03077],"tcp_to_object_dist_end":0.03348,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```