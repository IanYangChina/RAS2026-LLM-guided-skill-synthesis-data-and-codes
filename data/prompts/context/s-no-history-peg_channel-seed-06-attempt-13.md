## Search State

- **Seed**: 6
- **Iteration**: 14 / 15

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

## Current Skill (Q=0.456) — your mutation base

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

- **Composite score**: 0.456
- **task_score** (E): 0.840
- **fitness_score**: 0.862  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.1754 |
| descend_to_peg | 1.00 | 1.00 | 0.0954 |
| align_at_channel | 0.67 | 1.00 | 0.0352 |
| push_through | 0.33 | 1.00 | 0.0532 |
| retract_after_push | 1.00 | 1.00 | 0.0410 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.137, 0.138) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.543 | 2.127 |
| descend_to_peg | descend | 1.00 / step_budget | (0.497, 0.137, 0.138)→(0.497, 0.130, 0.043) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.390 | 2.769 |
| align_at_channel | contact | 0.67 / force_exceeded | (0.497, 0.130, 0.043)→(0.496, 0.096, 0.032) | (0.501, 0.099, 0.034)→(0.506, 0.068, 0.036) | 0.180→0.148 | 1.00 / 2.000 | 2613.967 | 7.011 |
| push_through | push | 0.33 / guard_failure | (0.500, 0.001, 0.031)→(0.501, -0.052, 0.031) | (0.506, 0.068, 0.036)→(0.503, -0.081, 0.037) | 0.148→0.006 | 1.00 / 2.000 | 4.975 | 39.827 |
| retract_after_push | retract | 1.00 / step_budget | (0.501, -0.052, 0.031)→(0.497, -0.051, 0.071) | (0.503, -0.082, 0.037)→(0.502, -0.078, 0.048) | 0.006→0.013 | 1.00 / 1.667 | 3.746 | 20.778 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.886
- phase_breakdown.descend_to_contact_score: 0.818
- phase_breakdown.align_at_channel_score: 0.763
- phase_breakdown.approach_high_score: 0.672
- phase_breakdown.push_through_channel_score: 0.975

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.932
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.557
- **K-run variance**: 0.0285
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.251


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.69595,"average_solve_count":296.0,"average_success_count":296.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_channel.align_force_threshold":14.80318,"align_at_channel.align_speed":0.01844,"approach_high.approach_speed":0.08867,"descend_to_peg.descend_speed":0.02401,"push_through.push_distance":0.13619,"push_through.push_force_guard_threshold":39.76468,"push_through.push_retry_offset_x":0.00643,"push_through.push_speed":0.01887,"retract_after_push.retract_speed":0.0557},"optimized_scores":{"best_composite_score":0.55736,"best_fitness_score":0.89736,"best_task_score":0.90675},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":271.0,"contact_point_centroid":[0.50242,-0.00035,0.04315],"force_p95":22.02038,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.58375,"mean_force":4.6538,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49764,0.01112,0.03071]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.50281,-0.10057,0.02982],"force_p95":39.17097,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.50978,"mean_force":23.79213,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50117,-0.0538,0.03077]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":191.0,"contact_point_centroid":[0.52525,0.00595,0.02895],"force_p95":21.74243,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.8814,"mean_force":3.23429,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.4964,0.03379,0.03068]},{"body_a":"attachment","body_b":"peg","contact_count":462.0,"contact_point_centroid":[0.49882,-0.06448,0.0527],"force_p95":18.07801,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.47455,"mean_force":13.0626,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49743,-0.05283,0.05074]},{"body_a":"peg","body_b":"channel_base_body","contact_count":462.0,"contact_point_centroid":[0.50063,-0.10036,0.06377],"force_p95":17.81264,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.25724,"mean_force":12.92729,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49743,-0.05283,0.05074]},{"body_a":"peg","body_b":"channel_base_body","contact_count":135.0,"contact_point_centroid":[0.50676,-0.03292,0.00989],"force_p95":16.7473,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.54736,"mean_force":5.04466,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49777,0.01031,0.03082]},{"body_a":"peg","body_b":"channel_base_body","contact_count":634.0,"contact_point_centroid":[0.50467,0.04009,0.00995],"force_p95":3.18329,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.43474,"mean_force":2.0098,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49646,0.08465,0.03608]},{"body_a":"attachment","body_b":"peg","contact_count":632.0,"contact_point_centroid":[0.50069,0.07229,0.03994],"force_p95":2.88383,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.14038,"mean_force":1.74431,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.4964,0.08371,0.03576]},{"body_a":"peg","body_b":"channel_base_body","contact_count":372.0,"contact_point_centroid":[0.50309,0.06752,0.00932],"force_p95":0.61857,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56976,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49866,0.15712,0.21799]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":180.0,"contact_point_centroid":[0.52502,0.04956,0.02894],"force_p95":1.24862,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.86385,"mean_force":0.7726,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49674,0.07743,0.0345]},{"body_a":"peg","body_b":"channel_base_body","contact_count":336.0,"contact_point_centroid":[0.50305,0.06732,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55159,"mean_force":0.54666,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49849,0.10326,0.08924]}],"total_contact_groups":11},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49946,-0.07762,0.05558],"final_tcp_position":[0.49751,-0.05299,0.07159],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":3920.08431,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":388.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54395,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":372.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_high","tcp_end":[0.50021,0.10856,0.13583],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11005,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":336.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06745,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54659,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":336.0,"raw_peak_contact_force":0.55159,"subtask_id":"descend_to_contact","tcp_end":[0.49903,0.09822,0.0427],"tcp_start":[0.50021,0.10856,0.13583],"tcp_to_object_dist_end":0.03228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":679.0,"n_steps_budget":1000.0,"object_pos_end":[0.50699,0.04574,0.03591],"object_pos_start":[0.50301,0.06745,0.0338],"object_to_goal_dist_end":0.126,"object_to_goal_dist_start":0.14761,"object_z_max":0.03599,"peak_contact_force":3920.08431,"phase_name":"align_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1446.0,"raw_peak_contact_force":4.43474,"subtask_id":"align_at_channel","tcp_end":[0.49698,0.07413,0.03391],"tcp_start":[0.49903,0.09822,0.0427],"tcp_to_object_dist_end":0.03017,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.50265,-0.08352,0.03608],"object_pos_start":[0.50699,0.04574,0.03591],"object_to_goal_dist_end":0.0059,"object_to_goal_dist_start":0.126,"object_z_max":0.03683,"peak_contact_force":6.98581,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":605.0,"raw_peak_contact_force":40.58375,"subtask_id":"push_through_channel","tcp_end":[0.50115,-0.0548,0.03066],"tcp_start":[0.50118,-0.05469,0.03071],"tcp_to_object_dist_end":0.02927,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":462.0,"n_steps_budget":600.0,"object_pos_end":[0.49946,-0.07762,0.05558],"object_pos_start":[0.50247,-0.08414,0.03605],"object_to_goal_dist_end":0.01577,"object_to_goal_dist_start":0.00623,"object_z_max":0.05554,"peak_contact_force":6.55109,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":924.0,"raw_peak_contact_force":20.47455,"tcp_end":[0.49751,-0.05299,0.07159],"tcp_start":[0.50115,-0.0548,0.03066],"tcp_to_object_dist_end":0.02944,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.78361,"average_solve_count":305.0,"average_success_count":305.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_channel.align_force_threshold":14.43564,"align_at_channel.align_speed":0.01617,"approach_high.approach_speed":0.09233,"descend_to_peg.descend_speed":0.02605,"push_through.push_distance":0.1489,"push_through.push_force_guard_threshold":43.13116,"push_through.push_retry_offset_x":-0.00177,"push_through.push_speed":0.01764,"retract_after_push.retract_speed":0.06546},"optimized_scores":{"best_composite_score":0.59184,"best_fitness_score":0.93184,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":278.0,"contact_point_centroid":[0.50299,0.03124,0.04416],"force_p95":16.7897,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.94978,"mean_force":3.48268,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49869,0.04272,0.0302]},{"body_a":"peg","body_b":"channel_base_body","contact_count":180.0,"contact_point_centroid":[0.50381,-0.01355,0.00962],"force_p95":16.25623,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.66095,"mean_force":4.77623,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49922,0.02954,0.03024]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":182.0,"contact_point_centroid":[0.52521,0.02538,0.02804],"force_p95":8.61234,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.84325,"mean_force":2.08968,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49812,0.0539,0.03]},{"body_a":"peg","body_b":"channel_base_body","contact_count":877.0,"contact_point_centroid":[0.50319,0.07886,0.00996],"force_p95":3.61829,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.14333,"mean_force":2.02739,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49783,0.12497,0.03558]},{"body_a":"attachment","body_b":"peg","contact_count":893.0,"contact_point_centroid":[0.50106,0.1129,0.03967],"force_p95":3.26604,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.88936,"mean_force":1.67428,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.4978,0.12459,0.03545]},{"body_a":"peg","body_b":"channel_base_body","contact_count":315.0,"contact_point_centroid":[0.50347,0.11161,0.00935],"force_p95":0.65414,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56892,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.5019,0.17531,0.21633]},{"body_a":"peg","body_b":"channel_base_body","contact_count":15.0,"contact_point_centroid":[0.50354,-0.1005,0.01636],"force_p95":1.44098,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.59066,"mean_force":0.73117,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50142,-0.04754,0.03155]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":26.0,"contact_point_centroid":[0.52501,0.08468,0.02685],"force_p95":0.90796,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.51992,"mean_force":0.64566,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.4984,0.11318,0.03317]},{"body_a":"peg","body_b":"channel_base_body","contact_count":378.0,"contact_point_centroid":[0.50616,-0.0783,0.00935],"force_p95":0.70114,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.40234,"mean_force":0.56447,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49899,-0.04644,0.05254]},{"body_a":"peg","body_b":"channel_base_body","contact_count":330.0,"contact_point_centroid":[0.50362,0.11166,0.0094],"force_p95":0.59046,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.80779,"mean_force":0.54549,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50231,0.14482,0.09066]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50316,0.12976,0.0588],"force_p95":0.60548,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.60548,"mean_force":0.60548,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50048,0.14172,0.0437]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49972,0.19973,0.29848]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52544,-0.0785,0.05776],"force_p95":0.3681,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42493,"mean_force":0.09333,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49998,-0.04693,0.0354]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50548,-0.05838,0.06305],"force_p95":0.14249,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17384,"mean_force":0.06135,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50221,-0.04729,0.03077]}],"total_contact_groups":14},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50628,-0.0784,0.03379],"final_tcp_position":[0.49888,-0.04634,0.07146],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":3920.39529,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":337.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.11176,0.03384],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.53927,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":331.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach_high","tcp_end":[0.50625,0.14849,0.13831],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11077,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":330.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.11173,0.03378],"object_pos_start":[0.50376,0.11176,0.03384],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.1919,"object_z_max":0.0339,"peak_contact_force":0.59787,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":331.0,"raw_peak_contact_force":0.80779,"subtask_id":"descend_to_contact","tcp_end":[0.50045,0.14168,0.04313],"tcp_start":[0.50625,0.14849,0.13831],"tcp_to_object_dist_end":0.03155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":921.0,"n_steps_budget":1000.0,"object_pos_end":[0.50699,0.08377,0.03573],"object_pos_start":[0.50374,0.11173,0.03378],"object_to_goal_dist_end":0.16397,"object_to_goal_dist_start":0.19187,"object_z_max":0.03575,"peak_contact_force":3920.39529,"phase_name":"align_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1796.0,"raw_peak_contact_force":9.14333,"subtask_id":"align_at_channel","tcp_end":[0.49843,0.11261,0.03306],"tcp_start":[0.50045,0.14168,0.04313],"tcp_to_object_dist_end":0.0302,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":432.0,"n_steps_budget":1000.0,"object_pos_end":[0.50121,-0.07604,0.04027],"object_pos_start":[0.50699,0.08377,0.03573],"object_to_goal_dist_end":0.00415,"object_to_goal_dist_start":0.16397,"object_z_max":0.04018,"peak_contact_force":0.17205,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":640.0,"raw_peak_contact_force":25.94978,"subtask_id":"push_through_channel","tcp_end":[0.5025,-0.04666,0.03076],"tcp_start":[0.49843,0.11261,0.03306],"tcp_to_object_dist_end":0.03091,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":407.0,"n_steps_budget":600.0,"object_pos_end":[0.50628,-0.0784,0.03379],"object_pos_start":[0.50121,-0.07604,0.04027],"object_to_goal_dist_end":0.00898,"object_to_goal_dist_start":0.00415,"object_z_max":0.04034,"peak_contact_force":0.54618,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":416.0,"raw_peak_contact_force":1.59066,"tcp_end":[0.49888,-0.04634,0.07146],"tcp_start":[0.5025,-0.04666,0.03076],"tcp_to_object_dist_end":0.05002,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.64365,"average_solve_count":362.0,"average_success_count":362.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_channel.align_force_threshold":17.92849,"align_at_channel.align_speed":0.02691,"approach_high.approach_speed":0.0609,"descend_to_peg.descend_speed":0.01491,"push_through.push_distance":0.15254,"push_through.push_force_guard_threshold":48.42536,"push_through.push_retry_offset_x":0.00236,"push_through.push_speed":0.01465,"retract_after_push.retract_speed":0.07612},"optimized_scores":{"best_composite_score":0.21782,"best_fitness_score":0.75782,"best_task_score":0.61415},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":312.0,"contact_point_centroid":[0.5004,0.01161,0.03911],"force_p95":34.30726,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.94752,"mean_force":7.471,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49407,0.02248,0.02848]},{"body_a":"peg","body_b":"channel_base_body","contact_count":13.0,"contact_point_centroid":[0.50565,-0.10091,0.05205],"force_p95":48.69213,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.84953,"mean_force":12.12557,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49902,-0.05368,0.03045]},{"body_a":"peg","body_b":"channel_base_body","contact_count":459.0,"contact_point_centroid":[0.50523,-0.10033,0.06407],"force_p95":22.65869,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.26802,"mean_force":12.47832,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49533,-0.05359,0.0506]},{"body_a":"attachment","body_b":"peg","contact_count":459.0,"contact_point_centroid":[0.49887,-0.06487,0.0535],"force_p95":22.63609,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.93234,"mean_force":12.51561,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49533,-0.05359,0.0506]},{"body_a":"peg","body_b":"channel_base_body","contact_count":194.0,"contact_point_centroid":[0.5065,-0.00771,0.00984],"force_p95":23.80019,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.52252,"mean_force":8.75424,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49337,0.03507,0.02827]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":293.0,"contact_point_centroid":[0.52519,-0.00722,0.03294],"force_p95":20.60984,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.0983,"mean_force":4.22285,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.4941,0.02019,0.0284]},{"body_a":"peg","body_b":"link7","contact_count":54.0,"contact_point_centroid":[0.52115,0.04645,0.06304],"force_p95":19.88694,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.66941,"mean_force":7.00523,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49134,0.06473,0.02738]},{"body_a":"peg","body_b":"channel_base_body","contact_count":13.0,"contact_point_centroid":[0.49694,-0.09672,0.00978],"force_p95":10.62979,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.84993,"mean_force":7.41594,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49865,-0.05541,0.03048]},{"body_a":"peg","body_b":"channel_base_body","contact_count":907.0,"contact_point_centroid":[0.49664,0.07759,0.00995],"force_p95":3.38709,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.45443,"mean_force":2.49256,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.48991,0.12319,0.03374]},{"body_a":"attachment","body_b":"peg","contact_count":921.0,"contact_point_centroid":[0.49399,0.11076,0.04144],"force_p95":2.9869,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.11246,"mean_force":2.11081,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.48992,0.12238,0.03353]},{"body_a":"peg","body_b":"channel_base_body","contact_count":368.0,"contact_point_centroid":[0.49624,0.11881,0.00945],"force_p95":0.60563,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.94694,"mean_force":0.56022,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48696,0.15147,0.09064]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49416,0.13699,0.05874],"force_p95":5.94641,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.53479,"mean_force":2.60477,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49082,0.14888,0.04531]},{"body_a":"peg","body_b":"channel_base_body","contact_count":309.0,"contact_point_centroid":[0.49642,0.11901,0.00937],"force_p95":0.63084,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56771,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49149,0.17745,0.21534]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49926,0.19955,0.29701]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":26.0,"contact_point_centroid":[0.47493,0.11346,0.01992],"force_p95":0.81818,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.85101,"mean_force":0.36712,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.48875,0.14332,0.03814]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47499,-0.07257,0.03747],"force_p95":0.25506,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26107,"mean_force":0.20304,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49531,-0.054,0.07049]}],"total_contact_groups":16},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50091,-0.07755,0.0541],"final_tcp_position":[0.49536,-0.0541,0.07132],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":52.94752,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11902,0.03401],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19915,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.54481,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":333.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_high","tcp_end":[0.48543,0.15477,0.13892],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":368.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.1189,0.03382],"object_pos_start":[0.49602,0.11902,0.03401],"object_to_goal_dist_end":0.19904,"object_to_goal_dist_start":0.19915,"object_z_max":0.0341,"peak_contact_force":0.02545,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":371.0,"raw_peak_contact_force":6.94694,"subtask_id":"descend_to_contact","tcp_end":[0.49108,0.14872,0.04246],"tcp_start":[0.48543,0.15477,0.13892],"tcp_to_object_dist_end":0.03144,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50438,0.07352,0.036],"object_pos_start":[0.49602,0.1189,0.03382],"object_to_goal_dist_end":0.15363,"object_to_goal_dist_start":0.19904,"object_z_max":0.03607,"peak_contact_force":1.4202,"phase_name":"align_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1854.0,"raw_peak_contact_force":7.45443,"subtask_id":"align_at_channel","tcp_end":[0.49187,0.10132,0.02977],"tcp_start":[0.49108,0.14872,0.04246],"tcp_to_object_dist_end":0.03112,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":437.0,"n_steps_budget":1000.0,"object_pos_end":[0.50527,-0.08434,0.03453],"object_pos_start":[0.50438,0.07352,0.036],"object_to_goal_dist_end":0.00875,"object_to_goal_dist_start":0.15363,"object_z_max":0.03718,"peak_contact_force":7.76859,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":866.0,"raw_peak_contact_force":52.94752,"subtask_id":"push_through_channel","tcp_end":[0.49911,-0.05552,0.03041],"tcp_start":[0.49915,-0.05543,0.03046],"tcp_to_object_dist_end":0.02975,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":459.0,"n_steps_budget":600.0,"object_pos_end":[0.50091,-0.07755,0.0541],"object_pos_start":[0.50503,-0.08451,0.03447],"object_to_goal_dist_end":0.01434,"object_to_goal_dist_start":0.00874,"object_z_max":0.05406,"peak_contact_force":4.13967,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":934.0,"raw_peak_contact_force":40.26802,"tcp_end":[0.49536,-0.0541,0.07132],"tcp_start":[0.49911,-0.05552,0.03041],"tcp_to_object_dist_end":0.02962,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```