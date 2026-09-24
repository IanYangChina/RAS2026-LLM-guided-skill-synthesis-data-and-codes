## Search State

- **Seed**: 6
- **Iteration**: 11 / 15

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

## Current Skill (Q=0.367) — your mutation base

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

- **Composite score**: 0.367
- **task_score** (E): 0.866
- **fitness_score**: 0.874  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.640

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.1754 |
| descend_to_peg | 1.00 | 1.00 | 0.0953 |
| align_at_channel | 0.67 | 1.00 | 0.0287 |
| push_through | 0.67 | 1.00 | 0.1102 |
| retract_after_push | 1.00 | 1.00 | 0.0409 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.137, 0.138) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.582 | 2.127 |
| descend_to_peg | descend | 1.00 / step_budget | (0.497, 0.137, 0.138)→(0.497, 0.130, 0.043) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.590 | 0.814 |
| align_at_channel | contact | 0.67 / force_exceeded | (0.497, 0.130, 0.043)→(0.495, 0.102, 0.034) | (0.501, 0.099, 0.034)→(0.507, 0.075, 0.036) | 0.180→0.155 | 1.00 / 2.000 | 1323.236 | 8.966 |
| push_through | push | 0.67 / step_budget | (0.496, 0.057, 0.033)→(0.501, -0.053, 0.031) | (0.507, 0.075, 0.036)→(0.507, -0.082, 0.036) | 0.155→0.008 | 1.00 / 3.000 | 8.901 | 38.919 |
| retract_after_push | retract | 1.00 / step_budget | (0.501, -0.053, 0.031)→(0.498, -0.052, 0.072) | (0.506, -0.082, 0.036)→(0.503, -0.075, 0.042) | 0.008→0.012 | 1.00 / 1.000 | 0.698 | 15.834 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.879
- phase_breakdown.descend_to_contact_score: 0.818
- phase_breakdown.align_at_channel_score: 0.764
- phase_breakdown.approach_high_score: 0.676
- phase_breakdown.push_through_channel_score: 0.960

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.927
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.457
- **K-run variance**: 0.0223
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.281


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95273,"average_solve_count":275.0,"average_success_count":275.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_channel.align_force_threshold":10.39303,"align_at_channel.align_push_distance":0.05813,"align_at_channel.align_speed":0.02092,"approach_high.approach_speed":0.08157,"descend_to_peg.descend_speed":0.02657,"push_through.push_distance":0.15553,"push_through.push_force_guard_threshold":37.44413,"push_through.push_retry_offset_x":0.00159,"push_through.push_retry_offset_y":-0.00164,"push_through.push_speed":0.01385,"retract_after_push.retract_speed":0.08995},"optimized_scores":{"best_composite_score":0.45741,"best_fitness_score":0.89741,"best_task_score":0.93403},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.50731,-0.1006,0.06006],"force_p95":43.16455,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.60384,"mean_force":20.76668,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50013,-0.0532,0.03142]},{"body_a":"attachment","body_b":"peg","contact_count":277.0,"contact_point_centroid":[0.50223,0.00384,0.04499],"force_p95":29.16691,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.55889,"mean_force":8.27983,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.4965,0.01514,0.03228]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":301.0,"contact_point_centroid":[0.52529,-0.01569,0.03445],"force_p95":25.31491,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.01934,"mean_force":4.56247,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49664,0.01234,0.03224]},{"body_a":"peg","body_b":"channel_base_body","contact_count":133.0,"contact_point_centroid":[0.50707,-0.02875,0.00988],"force_p95":22.52883,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.46994,"mean_force":9.29946,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.4966,0.01568,0.03245]},{"body_a":"peg","body_b":"channel_base_body","contact_count":454.0,"contact_point_centroid":[0.50741,-0.10027,0.06308],"force_p95":16.20208,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.14169,"mean_force":7.59073,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.4964,-0.05328,0.05132]},{"body_a":"attachment","body_b":"peg","contact_count":454.0,"contact_point_centroid":[0.50003,-0.06457,0.05267],"force_p95":15.22469,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.97541,"mean_force":7.67742,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.4964,-0.05328,0.05132]},{"body_a":"peg","body_b":"channel_base_body","contact_count":21.0,"contact_point_centroid":[0.50405,-0.08228,0.00994],"force_p95":6.17428,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.19776,"mean_force":2.55085,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49886,-0.05438,0.03241]},{"body_a":"peg","body_b":"channel_base_body","contact_count":392.0,"contact_point_centroid":[0.50353,0.04338,0.00992],"force_p95":4.20736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.40254,"mean_force":2.29116,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49599,0.08777,0.03773]},{"body_a":"attachment","body_b":"peg","contact_count":369.0,"contact_point_centroid":[0.49998,0.07549,0.04101],"force_p95":3.91015,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.03306,"mean_force":2.05719,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49584,0.08692,0.03743]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.52502,-0.08244,0.05998],"force_p95":2.3471,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.60286,"mean_force":1.61522,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49638,-0.05331,0.04204]},{"body_a":"peg","body_b":"channel_base_body","contact_count":374.0,"contact_point_centroid":[0.50312,0.06744,0.00932],"force_p95":0.61822,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56964,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49857,0.15725,0.21814]},{"body_a":"peg","body_b":"channel_base_body","contact_count":336.0,"contact_point_centroid":[0.50292,0.06743,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55159,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49833,0.10329,0.0893]}],"total_contact_groups":12},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5038,-0.07562,0.0532],"final_tcp_position":[0.49638,-0.05365,0.07205],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":49.88835,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":390.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54714,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":374.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_high","tcp_end":[0.49998,0.10862,0.13592],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":336.0,"n_steps_budget":1000.0,"object_pos_end":[0.50304,0.0675,0.0338],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54548,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":336.0,"raw_peak_contact_force":0.55159,"subtask_id":"descend_to_contact","tcp_end":[0.49895,0.09825,0.04287],"tcp_start":[0.49998,0.10862,0.13592],"tcp_to_object_dist_end":0.03232,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":416.0,"n_steps_budget":1000.0,"object_pos_end":[0.50675,0.05221,0.03607],"object_pos_start":[0.50304,0.0675,0.0338],"object_to_goal_dist_end":0.13244,"object_to_goal_dist_start":0.14766,"object_z_max":0.03612,"peak_contact_force":49.88835,"phase_name":"align_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":761.0,"raw_peak_contact_force":8.40254,"subtask_id":"align_at_channel","tcp_end":[0.49591,0.08013,0.03647],"tcp_start":[0.49895,0.09825,0.04287],"tcp_to_object_dist_end":0.02996,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":374.0,"n_steps_budget":1000.0,"object_pos_end":[0.50695,-0.08315,0.03537],"object_pos_start":[0.50675,0.05221,0.03607],"object_to_goal_dist_end":0.00892,"object_to_goal_dist_start":0.13244,"object_z_max":0.03687,"peak_contact_force":1.3998,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":720.0,"raw_peak_contact_force":43.60384,"subtask_id":"push_through_channel","tcp_end":[0.50008,-0.05455,0.03128],"tcp_start":[0.50013,-0.05441,0.03134],"tcp_to_object_dist_end":0.0297,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":454.0,"n_steps_budget":600.0,"object_pos_end":[0.5038,-0.07562,0.0532],"object_pos_start":[0.50679,-0.08354,0.03519],"object_to_goal_dist_end":0.01441,"object_to_goal_dist_start":0.00904,"object_z_max":0.05315,"peak_contact_force":1.11199,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":944.0,"raw_peak_contact_force":24.14169,"tcp_end":[0.49638,-0.05365,0.07205],"tcp_start":[0.50008,-0.05455,0.03128],"tcp_to_object_dist_end":0.02989,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.77287,"average_solve_count":317.0,"average_success_count":317.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_channel.align_force_threshold":9.20621,"align_at_channel.align_push_distance":0.05562,"align_at_channel.align_speed":0.01342,"approach_high.approach_speed":0.09991,"descend_to_peg.descend_speed":0.02195,"push_through.push_distance":0.15487,"push_through.push_force_guard_threshold":46.53542,"push_through.push_retry_offset_x":-0.00412,"push_through.push_retry_offset_y":0.00116,"push_through.push_speed":0.01423,"retract_after_push.retract_speed":0.06338},"optimized_scores":{"best_composite_score":0.48715,"best_fitness_score":0.92715,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":374.0,"contact_point_centroid":[0.50342,0.02228,0.0471],"force_p95":28.34587,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.28749,"mean_force":6.91089,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49825,0.03374,0.03138]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":283.0,"contact_point_centroid":[0.52532,0.01892,0.03466],"force_p95":27.96692,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.80196,"mean_force":6.99268,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49747,0.04721,0.03129]},{"body_a":"peg","body_b":"channel_base_body","contact_count":155.0,"contact_point_centroid":[0.50617,-0.01692,0.00986],"force_p95":19.35427,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.93749,"mean_force":6.59515,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49867,0.02611,0.03141]},{"body_a":"peg","body_b":"channel_base_body","contact_count":898.0,"contact_point_centroid":[0.50496,0.08057,0.00996],"force_p95":3.30025,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.21506,"mean_force":1.84034,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49734,0.12572,0.03684]},{"body_a":"attachment","body_b":"peg","contact_count":923.0,"contact_point_centroid":[0.50115,0.11379,0.03867],"force_p95":2.93892,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.91402,"mean_force":1.56548,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.4973,0.12524,0.03672]},{"body_a":"peg","body_b":"channel_base_body","contact_count":313.0,"contact_point_centroid":[0.5034,0.11168,0.00935],"force_p95":0.65842,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56906,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50187,0.17526,0.21606]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":378.0,"contact_point_centroid":[0.52504,0.09061,0.02775],"force_p95":1.0607,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.94488,"mean_force":0.68086,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49742,0.11861,0.03586]},{"body_a":"peg","body_b":"channel_base_body","contact_count":128.0,"contact_point_centroid":[0.50601,-0.10022,0.04078],"force_p95":0.59645,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.39163,"mean_force":0.18145,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49963,-0.05087,0.04574]},{"body_a":"peg","body_b":"channel_base_body","contact_count":392.0,"contact_point_centroid":[0.50572,-0.08095,0.00945],"force_p95":0.61516,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.88364,"mean_force":0.54287,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49899,-0.05058,0.05221]},{"body_a":"peg","body_b":"channel_base_body","contact_count":333.0,"contact_point_centroid":[0.50382,0.11161,0.0094],"force_p95":0.59487,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69702,"mean_force":0.54556,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50228,0.14475,0.09054]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49971,0.19974,0.29836]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50313,0.12977,0.05882],"force_p95":0.49982,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49982,"mean_force":0.49982,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50046,0.14172,0.04416]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50358,-0.06279,0.03089],"force_p95":0.12701,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13369,"mean_force":0.06685,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50242,-0.05093,0.03112]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52507,-0.08186,0.05945],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50042,-0.05108,0.03443]}],"total_contact_groups":14},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50613,-0.08196,0.03378],"final_tcp_position":[0.49881,-0.05044,0.07184],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":3919.81978,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":335.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11174,0.03383],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.60708,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":329.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach_high","tcp_end":[0.50622,0.14838,0.138],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11045,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":333.0,"n_steps_budget":1000.0,"object_pos_end":[0.50379,0.11171,0.03379],"object_pos_start":[0.50375,0.11174,0.03383],"object_to_goal_dist_end":0.19185,"object_to_goal_dist_start":0.19188,"object_z_max":0.03387,"peak_contact_force":0.57456,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":334.0,"raw_peak_contact_force":0.69702,"subtask_id":"descend_to_contact","tcp_end":[0.50042,0.14164,0.04305],"tcp_start":[0.50622,0.14838,0.138],"tcp_to_object_dist_end":0.03151,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":956.0,"n_steps_budget":1000.0,"object_pos_end":[0.50699,0.08543,0.0359],"object_pos_start":[0.50379,0.11171,0.03379],"object_to_goal_dist_end":0.16563,"object_to_goal_dist_start":0.19185,"object_z_max":0.03596,"peak_contact_force":3919.81978,"phase_name":"align_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2199.0,"raw_peak_contact_force":9.21506,"subtask_id":"align_at_channel","tcp_end":[0.49759,0.11392,0.03536],"tcp_start":[0.50042,0.14164,0.04305],"tcp_to_object_dist_end":0.03001,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":452.0,"n_steps_budget":1000.0,"object_pos_end":[0.50572,-0.0806,0.03688],"object_pos_start":[0.50699,0.08543,0.0359],"object_to_goal_dist_end":0.00655,"object_to_goal_dist_start":0.16563,"object_z_max":0.03688,"peak_contact_force":0.39824,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":812.0,"raw_peak_contact_force":33.28749,"subtask_id":"push_through_channel","tcp_end":[0.50243,-0.05079,0.03113],"tcp_start":[0.49759,0.11392,0.03536],"tcp_to_object_dist_end":0.03054,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":408.0,"n_steps_budget":600.0,"object_pos_end":[0.50613,-0.08196,0.03378],"object_pos_start":[0.50572,-0.0806,0.03688],"object_to_goal_dist_end":0.00895,"object_to_goal_dist_start":0.00655,"object_z_max":0.03688,"peak_contact_force":0.53142,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":529.0,"raw_peak_contact_force":1.39163,"tcp_end":[0.49881,-0.05044,0.07184],"tcp_start":[0.50243,-0.05079,0.03113],"tcp_to_object_dist_end":0.04995,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.6345,"average_solve_count":342.0,"average_success_count":342.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_channel.align_force_threshold":10.50594,"align_at_channel.align_push_distance":0.02001,"align_at_channel.align_speed":0.01967,"approach_high.approach_speed":0.09759,"descend_to_peg.descend_speed":0.01796,"push_through.push_distance":0.15736,"push_through.push_force_guard_threshold":40.38853,"push_through.push_retry_offset_x":0.00515,"push_through.push_retry_offset_y":0.00709,"push_through.push_speed":0.02219,"retract_after_push.retract_speed":0.04839},"optimized_scores":{"best_composite_score":0.1564,"best_fitness_score":0.7964,"best_task_score":0.66289},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":343.0,"contact_point_centroid":[0.50059,0.0212,0.04115],"force_p95":22.3851,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.865,"mean_force":4.33029,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49435,0.03202,0.02966]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":270.0,"contact_point_centroid":[0.52526,0.0096,0.03252],"force_p95":14.83087,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.09538,"mean_force":2.9621,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49394,0.03654,0.02952]},{"body_a":"peg","body_b":"channel_base_body","contact_count":169.0,"contact_point_centroid":[0.50744,-0.00983,0.00989],"force_p95":21.05621,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.34807,"mean_force":6.7136,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49434,0.03326,0.02975]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50649,-0.10013,0.06042],"force_p95":24.90476,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.90476,"mean_force":24.90476,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50116,-0.05227,0.03123]},{"body_a":"peg","body_b":"channel_base_body","contact_count":403.0,"contact_point_centroid":[0.50659,-0.10026,0.05778],"force_p95":7.0184,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.96829,"mean_force":4.60077,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49767,-0.05182,0.04995]},{"body_a":"attachment","body_b":"peg","contact_count":359.0,"contact_point_centroid":[0.5007,-0.06315,0.05279],"force_p95":7.27722,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.58237,"mean_force":5.491,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49744,-0.05167,0.05155]},{"body_a":"peg","body_b":"channel_base_body","contact_count":942.0,"contact_point_centroid":[0.50065,0.08481,0.00996],"force_p95":3.56424,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.27951,"mean_force":2.18271,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.4894,0.12876,0.03459]},{"body_a":"attachment","body_b":"peg","contact_count":946.0,"contact_point_centroid":[0.495,0.11727,0.04193],"force_p95":3.20442,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.99403,"mean_force":1.82209,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.48938,0.1284,0.03447]},{"body_a":"peg","body_b":"channel_base_body","contact_count":75.0,"contact_point_centroid":[0.50605,-0.07954,0.00977],"force_p95":2.84272,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.36882,"mean_force":0.86084,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49871,-0.05265,0.04347]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":123.0,"contact_point_centroid":[0.52503,-0.08228,0.05947],"force_p95":2.71847,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.89813,"mean_force":1.88686,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49723,-0.05156,0.04936]},{"body_a":"peg","body_b":"channel_base_body","contact_count":297.0,"contact_point_centroid":[0.49638,0.11906,0.00936],"force_p95":0.6361,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56971,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49151,0.17757,0.21498]},{"body_a":"peg","body_b":"channel_base_body","contact_count":368.0,"contact_point_centroid":[0.49608,0.11881,0.00942],"force_p95":0.61539,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.19288,"mean_force":0.54976,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48707,0.15154,0.09059]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.49429,0.13708,0.05873],"force_p95":0.90899,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.95088,"mean_force":0.70688,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49093,0.14896,0.04471]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.4992,0.19954,0.29654]}],"total_contact_groups":14},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49938,-0.06842,0.03753],"final_tcp_position":[0.49754,-0.05201,0.07201],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":39.865,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":322.0,"n_steps_budget":1000.0,"object_pos_end":[0.49607,0.11914,0.03383],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19928,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.59313,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":321.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_high","tcp_end":[0.48559,0.15481,0.13896],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11152,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":368.0,"n_steps_budget":1000.0,"object_pos_end":[0.49605,0.11887,0.0337],"object_pos_start":[0.49607,0.11914,0.03383],"object_to_goal_dist_end":0.19901,"object_to_goal_dist_start":0.19928,"object_z_max":0.034,"peak_contact_force":0.64948,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":373.0,"raw_peak_contact_force":1.19288,"subtask_id":"descend_to_contact","tcp_end":[0.49114,0.14883,0.04238],"tcp_start":[0.48559,0.15481,0.13896],"tcp_to_object_dist_end":0.03158,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50627,0.08638,0.03636],"object_pos_start":[0.49605,0.11887,0.0337],"object_to_goal_dist_end":0.16654,"object_to_goal_dist_start":0.19901,"object_z_max":0.03637,"peak_contact_force":0.0,"phase_name":"align_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1888.0,"raw_peak_contact_force":9.27951,"subtask_id":"align_at_channel","tcp_end":[0.49079,0.11261,0.0316],"tcp_start":[0.49114,0.14883,0.04238],"tcp_to_object_dist_end":0.03083,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":451.0,"n_steps_budget":1000.0,"object_pos_end":[0.50688,-0.08219,0.03573],"object_pos_start":[0.50627,0.08638,0.03636],"object_to_goal_dist_end":0.00839,"object_to_goal_dist_start":0.16654,"object_z_max":0.03758,"peak_contact_force":24.90476,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":783.0,"raw_peak_contact_force":39.865,"subtask_id":"push_through_channel","tcp_end":[0.50118,-0.05262,0.03123],"tcp_start":[0.49079,0.11261,0.0316],"tcp_to_object_dist_end":0.03045,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":438.0,"n_steps_budget":660.0,"object_pos_end":[0.49938,-0.06842,0.03753],"object_pos_start":[0.50688,-0.08219,0.03573],"object_to_goal_dist_end":0.01186,"object_to_goal_dist_start":0.00839,"object_z_max":0.04848,"peak_contact_force":0.44984,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":960.0,"raw_peak_contact_force":21.96829,"tcp_end":[0.49754,-0.05201,0.07201],"tcp_start":[0.50118,-0.05262,0.03123],"tcp_to_object_dist_end":0.03823,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```