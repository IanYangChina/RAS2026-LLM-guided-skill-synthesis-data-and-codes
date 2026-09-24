## Search State

- **Seed**: 6
- **Iteration**: 10 / 15

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

## Current Skill (Q=0.321) — your mutation base

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

- **Composite score**: 0.321
- **task_score** (E): 0.811
- **fitness_score**: 0.844  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.067
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.590

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.1753 |
| descend_to_peg | 0.00 | 1.00 | 0.1017 |
| align_at_channel | 0.33 | 1.00 | 0.0300 |
| push_through | 0.67 | 0.33 | 0.1012 |
| retract_after_push | 1.00 | 1.00 | 0.0410 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.137, 0.138) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.523 | 2.127 |
| descend_to_peg | descend | 0.00 / step_budget | (0.497, 0.137, 0.138)→(0.497, 0.129, 0.037) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.179 | 1.00 / 1.333 | 0.812 | 3.044 |
| align_at_channel | contact | 0.33 / step_budget | (0.497, 0.129, 0.037)→(0.495, 0.100, 0.031) | (0.501, 0.099, 0.034)→(0.507, 0.072, 0.036) | 0.179→0.152 | 1.00 / 2.333 | 1307.161 | 8.390 |
| push_through | push | 0.67 / step_budget | (0.496, 0.057, 0.030)→(0.501, -0.044, 0.030) | (0.507, 0.072, 0.036)→(0.505, -0.074, 0.036) | 0.152→0.011 | 0.33 / 0.667 | 0.475 | 33.877 |
| retract_after_push | retract | 1.00 / step_budget | (0.501, -0.044, 0.030)→(0.498, -0.044, 0.071) | (0.504, -0.074, 0.036)→(0.504, -0.074, 0.041) | 0.011→0.013 | 1.00 / 1.333 | 3.024 | 9.418 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.523
- phase_score: 0.855
- phase_breakdown.descend_to_contact_score: 0.874
- phase_breakdown.align_at_channel_score: 0.779
- phase_breakdown.approach_high_score: 0.673
- phase_breakdown.push_through_channel_score: 0.907

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.916
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.326
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.273


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.62985,"average_solve_count":335.0,"average_success_count":335.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_channel.align_force_threshold":12.67076,"align_at_channel.align_speed":0.0113,"approach_high.approach_speed":0.07135,"descend_to_peg.contact_force_threshold":8.6681,"descend_to_peg.descend_speed":0.02,"push_through.push_distance":0.14291,"push_through.push_force_guard_threshold":44.15807,"push_through.push_retry_offset_x":0.00515,"push_through.push_speed":0.01843,"retract_after_push.retract_speed":0.09514},"optimized_scores":{"best_composite_score":0.30429,"best_fitness_score":0.89429,"best_task_score":0.91007},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":264.0,"contact_point_centroid":[0.50274,-0.00042,0.04609],"force_p95":23.09196,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.88868,"mean_force":5.48065,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49702,0.01105,0.02862]},{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.50333,-0.10077,0.04302],"force_p95":42.43766,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.6608,"mean_force":21.13316,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49987,-0.0537,0.0297]},{"body_a":"attachment","body_b":"peg","contact_count":463.0,"contact_point_centroid":[0.49826,-0.06472,0.05271],"force_p95":21.22909,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.24964,"mean_force":14.33669,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49601,-0.0532,0.04971]},{"body_a":"peg","body_b":"channel_base_body","contact_count":463.0,"contact_point_centroid":[0.50183,-0.10038,0.06347],"force_p95":20.9192,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.07637,"mean_force":14.19705,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49601,-0.0532,0.04971]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":225.0,"contact_point_centroid":[0.52522,-0.01009,0.03007],"force_p95":15.83358,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.38598,"mean_force":2.61042,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49659,0.01812,0.02836]},{"body_a":"peg","body_b":"channel_base_body","contact_count":132.0,"contact_point_centroid":[0.50667,-0.03348,0.00984],"force_p95":19.03136,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.20772,"mean_force":7.06249,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49707,0.01132,0.02869]},{"body_a":"peg","body_b":"channel_base_body","contact_count":966.0,"contact_point_centroid":[0.50296,0.03775,0.00996],"force_p95":3.04407,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.10756,"mean_force":1.52647,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.4963,0.08372,0.03143]},{"body_a":"attachment","body_b":"peg","contact_count":974.0,"contact_point_centroid":[0.50006,0.07176,0.03797],"force_p95":2.68702,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.87561,"mean_force":1.20228,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49626,0.08342,0.03134]},{"body_a":"peg","body_b":"channel_base_body","contact_count":376.0,"contact_point_centroid":[0.50304,0.06739,0.00932],"force_p95":0.61787,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56953,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.4985,0.15721,0.21816]},{"body_a":"peg","body_b":"channel_base_body","contact_count":638.0,"contact_point_centroid":[0.50309,0.06746,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55159,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.4981,0.10281,0.08442]}],"total_contact_groups":10},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50117,-0.07815,0.05528],"final_tcp_position":[0.4961,-0.05334,0.07053],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":44.88868,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":392.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54599,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":376.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_high","tcp_end":[0.5,0.10866,0.136],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":638.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06745,0.0338],"object_pos_start":[0.50302,0.06748,0.0338],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14764,"object_z_max":0.0338,"peak_contact_force":0.547,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":638.0,"raw_peak_contact_force":0.55159,"subtask_id":"descend_to_contact","tcp_end":[0.49893,0.09758,0.0366],"tcp_start":[0.5,0.10866,0.136],"tcp_to_object_dist_end":0.03053,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50578,0.04532,0.03569],"object_pos_start":[0.50301,0.06745,0.0338],"object_to_goal_dist_end":0.12552,"object_to_goal_dist_start":0.14761,"object_z_max":0.03575,"peak_contact_force":1.38611,"phase_name":"align_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1940.0,"raw_peak_contact_force":8.10756,"subtask_id":"align_at_channel","tcp_end":[0.49688,0.07421,0.03069],"tcp_start":[0.49893,0.09758,0.0366],"tcp_to_object_dist_end":0.03064,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.50209,-0.08397,0.0364],"object_pos_start":[0.50578,0.04532,0.03569],"object_to_goal_dist_end":0.00575,"object_to_goal_dist_start":0.12552,"object_z_max":0.03687,"peak_contact_force":1.42527,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":632.0,"raw_peak_contact_force":44.88868,"subtask_id":"push_through_channel","tcp_end":[0.49983,-0.05531,0.02958],"tcp_start":[0.4999,-0.05518,0.02964],"tcp_to_object_dist_end":0.02954,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":463.0,"n_steps_budget":600.0,"object_pos_end":[0.50117,-0.07815,0.05528],"object_pos_start":[0.50189,-0.08423,0.03653],"object_to_goal_dist_end":0.01544,"object_to_goal_dist_start":0.00579,"object_z_max":0.05524,"peak_contact_force":7.97309,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":926.0,"raw_peak_contact_force":25.24964,"tcp_end":[0.4961,-0.05334,0.07053],"tcp_start":[0.49983,-0.05531,0.02958],"tcp_to_object_dist_end":0.02956,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.63497,"average_solve_count":326.0,"average_success_count":326.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_channel.align_force_threshold":22.19394,"align_at_channel.align_speed":0.01473,"approach_high.approach_speed":0.09092,"descend_to_peg.contact_force_threshold":13.70925,"descend_to_peg.descend_speed":0.02119,"push_through.push_distance":0.14407,"push_through.push_force_guard_threshold":47.53338,"push_through.push_retry_offset_x":0.00785,"push_through.push_speed":0.01796,"retract_after_push.retract_speed":0.09},"optimized_scores":{"best_composite_score":0.32552,"best_fitness_score":0.91552,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":323.0,"contact_point_centroid":[0.50345,0.02979,0.04261],"force_p95":15.9669,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.08374,"mean_force":2.78818,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49879,0.04134,0.02881]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":267.0,"contact_point_centroid":[0.5252,0.0117,0.02626],"force_p95":6.94311,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.03216,"mean_force":1.61871,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49876,0.04055,0.02874]},{"body_a":"peg","body_b":"channel_base_body","contact_count":146.0,"contact_point_centroid":[0.50443,-0.01229,0.00989],"force_p95":15.87263,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.92048,"mean_force":4.91852,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49919,0.03201,0.02899]},{"body_a":"peg","body_b":"channel_base_body","contact_count":949.0,"contact_point_centroid":[0.50353,0.07858,0.00997],"force_p95":2.83138,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.68485,"mean_force":1.66404,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49767,0.12464,0.03171]},{"body_a":"attachment","body_b":"peg","contact_count":963.0,"contact_point_centroid":[0.50122,0.11244,0.03821],"force_p95":2.46169,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.25711,"mean_force":1.33988,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49764,0.12414,0.0316]},{"body_a":"peg","body_b":"channel_base_body","contact_count":587.0,"contact_point_centroid":[0.50373,0.11079,0.00941],"force_p95":0.59781,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.80444,"mean_force":0.56758,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50186,0.14449,0.08613]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.50303,0.12958,0.05611],"force_p95":2.65967,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.50875,"mean_force":1.3241,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50025,0.14152,0.04107]},{"body_a":"peg","body_b":"channel_base_body","contact_count":315.0,"contact_point_centroid":[0.50347,0.11161,0.00935],"force_p95":0.65414,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56892,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.5019,0.17531,0.21633]},{"body_a":"peg","body_b":"channel_base_body","contact_count":403.0,"contact_point_centroid":[0.50617,-0.07504,0.00941],"force_p95":0.58754,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.49315,"mean_force":0.55687,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49915,-0.04195,0.05091]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":74.0,"contact_point_centroid":[0.52502,0.08473,0.02594],"force_p95":0.82036,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86459,"mean_force":0.56873,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49837,0.11329,0.03086]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49972,0.19973,0.29848]}],"total_contact_groups":11},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50614,-0.0747,0.03378],"final_tcp_position":[0.49889,-0.04178,0.07116],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":20.08374,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":337.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.11176,0.03384],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.53927,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":331.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach_high","tcp_end":[0.50625,0.14849,0.13831],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11077,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":587.0,"n_steps_budget":1000.0,"object_pos_end":[0.50408,0.11139,0.03435],"object_pos_start":[0.50376,0.11176,0.03384],"object_to_goal_dist_end":0.19152,"object_to_goal_dist_start":0.1919,"object_z_max":0.03433,"peak_contact_force":0.47123,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":600.0,"raw_peak_contact_force":3.80444,"subtask_id":"descend_to_contact","tcp_end":[0.50013,0.14128,0.03717],"tcp_start":[0.50625,0.14849,0.13831],"tcp_to_object_dist_end":0.03028,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50706,0.08345,0.03568],"object_pos_start":[0.50408,0.11139,0.03435],"object_to_goal_dist_end":0.16366,"object_to_goal_dist_start":0.19152,"object_z_max":0.03575,"peak_contact_force":1.92896,"phase_name":"align_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1986.0,"raw_peak_contact_force":9.68485,"subtask_id":"align_at_channel","tcp_end":[0.49843,0.1124,0.03081],"tcp_start":[0.50013,0.14128,0.03717],"tcp_to_object_dist_end":0.0306,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":422.0,"n_steps_budget":1000.0,"object_pos_end":[0.50619,-0.07251,0.03622],"object_pos_start":[0.50706,0.08345,0.03568],"object_to_goal_dist_end":0.01042,"object_to_goal_dist_start":0.16366,"object_z_max":0.03694,"peak_contact_force":0.0,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":736.0,"raw_peak_contact_force":20.08374,"subtask_id":"push_through_channel","tcp_end":[0.5025,-0.04207,0.03046],"tcp_start":[0.49843,0.1124,0.03081],"tcp_to_object_dist_end":0.0312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":406.0,"n_steps_budget":600.0,"object_pos_end":[0.50614,-0.0747,0.03378],"object_pos_start":[0.50619,-0.07251,0.03622],"object_to_goal_dist_end":0.01022,"object_to_goal_dist_start":0.01042,"object_z_max":0.03622,"peak_contact_force":0.55727,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":403.0,"raw_peak_contact_force":1.49315,"tcp_end":[0.49889,-0.04178,0.07116],"tcp_start":[0.5025,-0.04207,0.03046],"tcp_to_object_dist_end":0.05033,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.56897,"average_solve_count":348.0,"average_success_count":348.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_channel.align_force_threshold":13.79764,"align_at_channel.align_speed":0.02301,"approach_high.approach_speed":0.05886,"descend_to_peg.contact_force_threshold":14.90803,"descend_to_peg.descend_speed":0.02041,"push_through.push_distance":0.14116,"push_through.push_force_guard_threshold":43.82138,"push_through.push_retry_offset_x":0.00763,"push_through.push_speed":0.01842,"retract_after_push.retract_speed":0.04658},"optimized_scores":{"best_composite_score":0.33202,"best_fitness_score":0.72202,"best_task_score":0.52284},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":313.0,"contact_point_centroid":[0.50068,0.0298,0.04023],"force_p95":27.35698,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.65907,"mean_force":5.24639,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.4945,0.04067,0.02905]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":261.0,"contact_point_centroid":[0.52522,0.0269,0.0318],"force_p95":21.90201,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.74926,"mean_force":4.08722,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49326,0.05356,0.02861]},{"body_a":"peg","body_b":"channel_base_body","contact_count":152.0,"contact_point_centroid":[0.50639,-0.00039,0.00986],"force_p95":19.67462,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.93457,"mean_force":6.34755,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49441,0.04224,0.02905]},{"body_a":"peg","body_b":"channel_base_body","contact_count":778.0,"contact_point_centroid":[0.50109,0.08515,0.00996],"force_p95":3.37611,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.3782,"mean_force":2.12577,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.4896,0.1287,0.031]},{"body_a":"attachment","body_b":"peg","contact_count":783.0,"contact_point_centroid":[0.49578,0.11716,0.04072],"force_p95":3.06431,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.22898,"mean_force":1.8052,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.48959,0.12818,0.03091]},{"body_a":"peg","body_b":"channel_base_body","contact_count":706.0,"contact_point_centroid":[0.49625,0.11771,0.00946],"force_p95":0.62106,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.77708,"mean_force":0.57325,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48718,0.15114,0.08506]},{"body_a":"attachment","body_b":"peg","contact_count":28.0,"contact_point_centroid":[0.49457,0.13685,0.05873],"force_p95":2.71729,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.24343,"mean_force":1.08317,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49098,0.14874,0.04214]},{"body_a":"peg","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.52099,0.07377,0.06332],"force_p95":2.2633,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.69299,"mean_force":0.84788,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.4902,0.08987,0.02782]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":68.0,"contact_point_centroid":[0.52509,0.08872,0.03024],"force_p95":2.14439,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.38747,"mean_force":1.34561,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49067,0.11387,0.03031]},{"body_a":"peg","body_b":"channel_base_body","contact_count":312.0,"contact_point_centroid":[0.49631,0.11909,0.00937],"force_p95":0.63203,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56782,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.4915,0.17742,0.21536]},{"body_a":"peg","body_b":"channel_base_body","contact_count":402.0,"contact_point_centroid":[0.50499,-0.06964,0.00947],"force_p95":0.59346,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.51105,"mean_force":0.55107,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49822,-0.03585,0.05193]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49923,0.19954,0.29707]}],"total_contact_groups":12},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50413,-0.06967,0.03446],"final_tcp_position":[0.49797,-0.03569,0.07207],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":3918.16715,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":337.0,"n_steps_budget":1000.0,"object_pos_end":[0.49604,0.11909,0.03392],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19923,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.48473,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":336.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_high","tcp_end":[0.48545,0.15478,0.13893],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":706.0,"n_steps_budget":1000.0,"object_pos_end":[0.49596,0.11866,0.03445],"object_pos_start":[0.49604,0.11909,0.03392],"object_to_goal_dist_end":0.19878,"object_to_goal_dist_start":0.19923,"object_z_max":0.03459,"peak_contact_force":1.41737,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":734.0,"raw_peak_contact_force":4.77708,"subtask_id":"descend_to_contact","tcp_end":[0.49155,0.14841,0.03596],"tcp_start":[0.48545,0.15478,0.13893],"tcp_to_object_dist_end":0.03012,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":853.0,"n_steps_budget":1000.0,"object_pos_end":[0.50699,0.08673,0.0367],"object_pos_start":[0.49596,0.11866,0.03445],"object_to_goal_dist_end":0.16691,"object_to_goal_dist_start":0.19878,"object_z_max":0.0367,"peak_contact_force":3918.16715,"phase_name":"align_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1629.0,"raw_peak_contact_force":7.3782,"subtask_id":"align_at_channel","tcp_end":[0.49076,0.11261,0.03026],"tcp_start":[0.49155,0.14841,0.03596],"tcp_to_object_dist_end":0.03122,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":416.0,"n_steps_budget":1000.0,"object_pos_end":[0.50524,-0.06588,0.03653],"object_pos_start":[0.50699,0.08673,0.0367],"object_to_goal_dist_end":0.01545,"object_to_goal_dist_start":0.16691,"object_z_max":0.03736,"peak_contact_force":0.0,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":732.0,"raw_peak_contact_force":36.65907,"subtask_id":"push_through_channel","tcp_end":[0.50158,-0.03594,0.03131],"tcp_start":[0.49076,0.11261,0.03026],"tcp_to_object_dist_end":0.03061,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":408.0,"n_steps_budget":690.0,"object_pos_end":[0.50413,-0.06967,0.03446],"object_pos_start":[0.50524,-0.06588,0.03653],"object_to_goal_dist_end":0.01243,"object_to_goal_dist_start":0.01545,"object_z_max":0.03653,"peak_contact_force":0.54302,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":402.0,"raw_peak_contact_force":1.51105,"tcp_end":[0.49797,-0.03569,0.07207],"tcp_start":[0.50158,-0.03594,0.03131],"tcp_to_object_dist_end":0.05106,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```