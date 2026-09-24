## Search State

- **Seed**: 6
- **Iteration**: 13 / 15

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

## Current Skill (Q=0.465) — your mutation base

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

- **Composite score**: 0.465
- **task_score** (E): 0.831
- **fitness_score**: 0.855  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.590

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.1753 |
| descend_to_peg | 0.00 | 1.00 | 0.1016 |
| align_at_channel | 1.00 | 1.00 | 0.0268 |
| push_through | 0.67 | 1.00 | 0.1069 |
| retract_after_push | 1.00 | 1.00 | 0.0409 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.137, 0.138) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.528 | 2.127 |
| descend_to_peg | descend | 0.00 / step_budget | (0.497, 0.137, 0.138)→(0.497, 0.129, 0.037) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.179 | 1.00 / 1.333 | 0.805 | 3.917 |
| align_at_channel | contact | 1.00 / force_exceeded | (0.497, 0.129, 0.037)→(0.495, 0.103, 0.031) | (0.501, 0.099, 0.034)→(0.507, 0.075, 0.036) | 0.179→0.156 | 1.00 / 2.333 | 2635.757 | 8.082 |
| push_through | push | 0.67 / step_budget | (0.497, 0.058, 0.030)→(0.502, -0.049, 0.031) | (0.507, 0.075, 0.036)→(0.506, -0.079, 0.036) | 0.156→0.008 | 1.00 / 1.667 | 2.217 | 39.078 |
| retract_after_push | retract | 1.00 / step_budget | (0.502, -0.049, 0.031)→(0.498, -0.048, 0.071) | (0.506, -0.079, 0.036)→(0.504, -0.077, 0.040) | 0.008→0.011 | 1.00 / 1.333 | 1.262 | 11.851 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.866
- phase_breakdown.descend_to_contact_score: 0.813
- phase_breakdown.align_at_channel_score: 0.725
- phase_breakdown.approach_high_score: 0.672
- phase_breakdown.push_through_channel_score: 0.955

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.920
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.500
- **K-run variance**: 0.0051
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.302


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.79211,"average_solve_count":279.0,"average_success_count":279.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_channel.align_force_threshold":13.05227,"align_at_channel.align_speed":0.01483,"approach_high.approach_speed":0.09953,"descend_to_peg.contact_force_threshold":13.73051,"descend_to_peg.descend_speed":0.02483,"push_through.push_distance":0.1483,"push_through.push_force_guard_threshold":48.00815,"push_through.push_retry_offset_x":0.00263,"push_through.push_speed":0.0252,"retract_after_push.retract_speed":0.0538},"optimized_scores":{"best_composite_score":0.49961,"best_fitness_score":0.88961,"best_task_score":0.91537},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":294.0,"contact_point_centroid":[0.50264,0.00156,0.04285],"force_p95":22.42309,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.31061,"mean_force":6.1051,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49715,0.013,0.02896]},{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.50654,-0.10052,0.05992],"force_p95":49.29284,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.58368,"mean_force":26.93111,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.5007,-0.05322,0.0301]},{"body_a":"peg","body_b":"channel_base_body","contact_count":456.0,"contact_point_centroid":[0.50686,-0.10026,0.0639],"force_p95":16.2194,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.41169,"mean_force":8.50892,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49708,-0.05305,0.05023]},{"body_a":"attachment","body_b":"peg","contact_count":456.0,"contact_point_centroid":[0.50034,-0.06445,0.05192],"force_p95":15.87819,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.77779,"mean_force":8.62705,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49708,-0.05305,0.05023]},{"body_a":"peg","body_b":"channel_base_body","contact_count":134.0,"contact_point_centroid":[0.50602,-0.02679,0.00992],"force_p95":18.96544,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.1009,"mean_force":8.54117,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49702,0.01825,0.02905]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":282.0,"contact_point_centroid":[0.52515,-0.01177,0.03155],"force_p95":18.16983,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.64821,"mean_force":2.96744,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49695,0.01659,0.02889]},{"body_a":"peg","body_b":"channel_base_body","contact_count":13.0,"contact_point_centroid":[0.50281,-0.08501,0.00995],"force_p95":10.33113,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.89258,"mean_force":4.27606,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49943,-0.05389,0.03166]},{"body_a":"peg","body_b":"channel_base_body","contact_count":456.0,"contact_point_centroid":[0.50362,0.04274,0.00994],"force_p95":3.77024,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.04904,"mean_force":1.8649,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49626,0.08772,0.03195]},{"body_a":"attachment","body_b":"peg","contact_count":447.0,"contact_point_centroid":[0.5007,0.07566,0.03918],"force_p95":3.43262,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.79179,"mean_force":1.56184,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49616,0.08716,0.03176]},{"body_a":"peg","body_b":"channel_base_body","contact_count":369.0,"contact_point_centroid":[0.50298,0.06746,0.00932],"force_p95":0.61909,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56996,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49861,0.15716,0.21794]},{"body_a":"peg","body_b":"channel_base_body","contact_count":610.0,"contact_point_centroid":[0.50309,0.06741,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55159,"mean_force":0.54664,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49823,0.10282,0.08456]}],"total_contact_groups":11},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50308,-0.07664,0.05373],"final_tcp_position":[0.49704,-0.05333,0.0709],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":67.73339,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":385.0,"n_steps_budget":1000.0,"object_pos_end":[0.50307,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.55198,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":369.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_high","tcp_end":[0.50018,0.10864,0.13595],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11017,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":610.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06748,0.0338],"object_pos_start":[0.50307,0.0675,0.0338],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":0.54544,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":610.0,"raw_peak_contact_force":0.55159,"subtask_id":"descend_to_contact","tcp_end":[0.49901,0.0976,0.03667],"tcp_start":[0.50018,0.10864,0.13595],"tcp_to_object_dist_end":0.03052,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":480.0,"n_steps_budget":1000.0,"object_pos_end":[0.5068,0.05286,0.03595],"object_pos_start":[0.50301,0.06748,0.0338],"object_to_goal_dist_end":0.1331,"object_to_goal_dist_start":0.14764,"object_z_max":0.03598,"peak_contact_force":67.73339,"phase_name":"align_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":903.0,"raw_peak_contact_force":8.04904,"subtask_id":"align_at_channel","tcp_end":[0.49637,0.08129,0.03113],"tcp_start":[0.49901,0.0976,0.03667],"tcp_to_object_dist_end":0.03066,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.50665,-0.08339,0.03497],"object_pos_start":[0.5068,0.05286,0.03595],"object_to_goal_dist_end":0.00901,"object_to_goal_dist_start":0.1331,"object_z_max":0.03671,"peak_contact_force":5.33051,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":719.0,"raw_peak_contact_force":54.31061,"subtask_id":"push_through_channel","tcp_end":[0.50078,-0.05444,0.03007],"tcp_start":[0.5008,-0.05433,0.0301],"tcp_to_object_dist_end":0.02994,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":456.0,"n_steps_budget":600.0,"object_pos_end":[0.50308,-0.07664,0.05373],"object_pos_start":[0.50656,-0.08361,0.03492],"object_to_goal_dist_end":0.01447,"object_to_goal_dist_start":0.00905,"object_z_max":0.05369,"peak_contact_force":2.66956,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":925.0,"raw_peak_contact_force":25.41169,"tcp_end":[0.49704,-0.05333,0.0709],"tcp_start":[0.50078,-0.05444,0.03007],"tcp_to_object_dist_end":0.02957,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.68129,"average_solve_count":342.0,"average_success_count":342.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_channel.align_force_threshold":19.66031,"align_at_channel.align_speed":0.01253,"approach_high.approach_speed":0.05965,"descend_to_peg.contact_force_threshold":15.39281,"descend_to_peg.descend_speed":0.02216,"push_through.push_distance":0.15618,"push_through.push_force_guard_threshold":42.43465,"push_through.push_retry_offset_x":-0.00321,"push_through.push_speed":0.01467,"retract_after_push.retract_speed":0.06276},"optimized_scores":{"best_composite_score":0.52985,"best_fitness_score":0.91985,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_left_wall","contact_count":289.0,"contact_point_centroid":[0.52528,0.01562,0.03604],"force_p95":27.54154,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.11246,"mean_force":5.62133,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49802,0.04434,0.02879]},{"body_a":"attachment","body_b":"peg","contact_count":336.0,"contact_point_centroid":[0.50338,0.02774,0.04371],"force_p95":26.98878,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.06309,"mean_force":6.25161,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49829,0.03919,0.02892]},{"body_a":"peg","body_b":"channel_base_body","contact_count":160.0,"contact_point_centroid":[0.50452,-0.01044,0.00979],"force_p95":18.47972,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.1965,"mean_force":4.88214,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.4987,0.0321,0.02915]},{"body_a":"peg","body_b":"channel_base_body","contact_count":869.0,"contact_point_centroid":[0.5034,0.08114,0.00997],"force_p95":4.01809,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.74888,"mean_force":1.74789,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49738,0.12722,0.03191]},{"body_a":"attachment","body_b":"peg","contact_count":892.0,"contact_point_centroid":[0.5011,0.1154,0.03803],"force_p95":3.60056,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.44568,"mean_force":1.39693,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49736,0.12706,0.03186]},{"body_a":"peg","body_b":"channel_base_body","contact_count":161.0,"contact_point_centroid":[0.50669,-0.10032,0.03697],"force_p95":7.37304,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.95158,"mean_force":1.13514,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49943,-0.04904,0.04306]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":26.0,"contact_point_centroid":[0.5251,-0.08381,0.04058],"force_p95":8.28481,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.37087,"mean_force":5.79778,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50115,-0.04965,0.03167]},{"body_a":"peg","body_b":"channel_base_body","contact_count":583.0,"contact_point_centroid":[0.50373,0.11076,0.00942],"force_p95":0.6007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.01253,"mean_force":0.57754,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50177,0.14449,0.08616]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50305,0.12957,0.05617],"force_p95":5.47395,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.73237,"mean_force":1.98289,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50016,0.14151,0.04067]},{"body_a":"peg","body_b":"channel_base_body","contact_count":329.0,"contact_point_centroid":[0.50347,0.11167,0.00935],"force_p95":0.63578,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56814,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50183,0.17517,0.2165]},{"body_a":"peg","body_b":"channel_base_body","contact_count":396.0,"contact_point_centroid":[0.50634,-0.08017,0.00947],"force_p95":0.61687,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.88448,"mean_force":0.53578,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49885,-0.04879,0.05131]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49967,0.19971,0.29876]}],"total_contact_groups":12},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50668,-0.08196,0.03378],"final_tcp_position":[0.49863,-0.04864,0.07121],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":3919.55185,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":351.0,"n_steps_budget":1000.0,"object_pos_end":[0.50369,0.11178,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.5294,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":345.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach_high","tcp_end":[0.50612,0.14846,0.1383],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11075,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":583.0,"n_steps_budget":1000.0,"object_pos_end":[0.50381,0.11149,0.03433],"object_pos_start":[0.50369,0.11178,0.03382],"object_to_goal_dist_end":0.19161,"object_to_goal_dist_start":0.19191,"object_z_max":0.03431,"peak_contact_force":0.45832,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":595.0,"raw_peak_contact_force":6.01253,"subtask_id":"descend_to_contact","tcp_end":[0.50006,0.14131,0.03722],"tcp_start":[0.50612,0.14846,0.1383],"tcp_to_object_dist_end":0.0302,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.5069,0.08875,0.0358],"object_pos_start":[0.50381,0.11149,0.03433],"object_to_goal_dist_end":0.16895,"object_to_goal_dist_start":0.19161,"object_z_max":0.03579,"peak_contact_force":3919.55185,"phase_name":"align_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1761.0,"raw_peak_contact_force":9.74888,"subtask_id":"align_at_channel","tcp_end":[0.49788,0.11756,0.03111],"tcp_start":[0.50006,0.14131,0.03722],"tcp_to_object_dist_end":0.03055,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":455.0,"n_steps_budget":1000.0,"object_pos_end":[0.50706,-0.07962,0.03717],"object_pos_start":[0.5069,0.08875,0.0358],"object_to_goal_dist_end":0.00761,"object_to_goal_dist_start":0.16895,"object_z_max":0.03738,"peak_contact_force":0.19885,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":785.0,"raw_peak_contact_force":35.11246,"subtask_id":"push_through_channel","tcp_end":[0.50225,-0.04897,0.03052],"tcp_start":[0.49788,0.11756,0.03111],"tcp_to_object_dist_end":0.03173,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":406.0,"n_steps_budget":600.0,"object_pos_end":[0.50668,-0.08196,0.03378],"object_pos_start":[0.50706,-0.07962,0.03717],"object_to_goal_dist_end":0.00933,"object_to_goal_dist_start":0.00761,"object_z_max":0.03717,"peak_contact_force":0.57664,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":583.0,"raw_peak_contact_force":8.95158,"tcp_end":[0.49863,-0.04864,0.07121],"tcp_start":[0.50225,-0.04897,0.03052],"tcp_to_object_dist_end":0.05075,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.76101,"average_solve_count":318.0,"average_success_count":318.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_channel.align_force_threshold":21.11169,"align_at_channel.align_speed":0.02492,"approach_high.approach_speed":0.06767,"descend_to_peg.contact_force_threshold":6.74172,"descend_to_peg.descend_speed":0.02476,"push_through.push_distance":0.14611,"push_through.push_force_guard_threshold":48.45559,"push_through.push_retry_offset_x":0.00499,"push_through.push_speed":0.01123,"retract_after_push.retract_speed":0.05488},"optimized_scores":{"best_composite_score":0.36616,"best_fitness_score":0.75616,"best_task_score":0.57778},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_left_wall","contact_count":293.0,"contact_point_centroid":[0.52515,0.01065,0.03291],"force_p95":20.98405,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.8099,"mean_force":3.50517,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49441,0.03782,0.02886]},{"body_a":"attachment","body_b":"peg","contact_count":325.0,"contact_point_centroid":[0.50085,0.02495,0.04072],"force_p95":23.13593,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.76458,"mean_force":4.99292,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49464,0.03593,0.02898]},{"body_a":"peg","body_b":"channel_base_body","contact_count":148.0,"contact_point_centroid":[0.50685,-0.00703,0.00989],"force_p95":19.12925,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.47244,"mean_force":6.70995,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49471,0.03657,0.02911]},{"body_a":"peg","body_b":"channel_base_body","contact_count":756.0,"contact_point_centroid":[0.5022,0.08484,0.00995],"force_p95":3.30654,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.44952,"mean_force":2.16666,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.48972,0.12796,0.03103]},{"body_a":"attachment","body_b":"peg","contact_count":774.0,"contact_point_centroid":[0.49622,0.1162,0.04064],"force_p95":3.42691,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.2999,"mean_force":1.88857,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.48974,0.12708,0.03094]},{"body_a":"peg","body_b":"channel_base_body","contact_count":683.0,"contact_point_centroid":[0.49601,0.11775,0.00943],"force_p95":0.61839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.18674,"mean_force":0.58356,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48723,0.15118,0.08509]},{"body_a":"attachment","body_b":"peg","contact_count":25.0,"contact_point_centroid":[0.49454,0.1369,0.0586],"force_p95":3.98113,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.83418,"mean_force":1.39495,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49098,0.1488,0.04227]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":175.0,"contact_point_centroid":[0.52506,0.08916,0.03086],"force_p95":2.297,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.58114,"mean_force":1.34076,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49068,0.11439,0.03039]},{"body_a":"peg","body_b":"channel_base_body","contact_count":307.0,"contact_point_centroid":[0.49651,0.11908,0.00937],"force_p95":0.6327,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56841,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49154,0.17747,0.2152]},{"body_a":"attachment","body_b":"peg","contact_count":57.0,"contact_point_centroid":[0.5015,-0.0552,0.05377],"force_p95":0.59443,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.18908,"mean_force":0.19329,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49859,-0.04328,0.04044]},{"body_a":"peg","body_b":"channel_base_body","contact_count":404.0,"contact_point_centroid":[0.50161,-0.07576,0.00947],"force_p95":0.6499,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.08656,"mean_force":0.53919,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49835,-0.04314,0.05159]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49925,0.19955,0.29691]}],"total_contact_groups":12},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50213,-0.07318,0.0338],"final_tcp_position":[0.49805,-0.04298,0.07201],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":3919.98674,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":332.0,"n_steps_budget":1000.0,"object_pos_end":[0.49604,0.11915,0.0339],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19928,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50113,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":331.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_high","tcp_end":[0.48552,0.1548,0.13897],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11145,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":683.0,"n_steps_budget":1000.0,"object_pos_end":[0.49607,0.11871,0.03455],"object_pos_start":[0.49604,0.11915,0.0339],"object_to_goal_dist_end":0.19883,"object_to_goal_dist_start":0.19928,"object_z_max":0.03455,"peak_contact_force":1.41231,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":708.0,"raw_peak_contact_force":5.18674,"subtask_id":"descend_to_contact","tcp_end":[0.49156,0.14848,0.03599],"tcp_start":[0.48552,0.1548,0.13897],"tcp_to_object_dist_end":0.03014,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":847.0,"n_steps_budget":1000.0,"object_pos_end":[0.50695,0.08437,0.03665],"object_pos_start":[0.49607,0.11871,0.03455],"object_to_goal_dist_end":0.16455,"object_to_goal_dist_start":0.19883,"object_z_max":0.03672,"peak_contact_force":3919.98674,"phase_name":"align_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1705.0,"raw_peak_contact_force":6.44952,"subtask_id":"align_at_channel","tcp_end":[0.49104,0.11043,0.03027],"tcp_start":[0.49156,0.14848,0.03599],"tcp_to_object_dist_end":0.03119,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":430.0,"n_steps_budget":1000.0,"object_pos_end":[0.504,-0.07366,0.03589],"object_pos_start":[0.50695,0.08437,0.03665],"object_to_goal_dist_end":0.00855,"object_to_goal_dist_start":0.16455,"object_z_max":0.03701,"peak_contact_force":1.12058,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":766.0,"raw_peak_contact_force":27.8099,"subtask_id":"push_through_channel","tcp_end":[0.50165,-0.04328,0.03131],"tcp_start":[0.49104,0.11043,0.03027],"tcp_to_object_dist_end":0.03082,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":404.0,"n_steps_budget":600.0,"object_pos_end":[0.50213,-0.07318,0.0338],"object_pos_start":[0.504,-0.07366,0.03589],"object_to_goal_dist_end":0.00946,"object_to_goal_dist_start":0.00855,"object_z_max":0.03624,"peak_contact_force":0.54034,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":461.0,"raw_peak_contact_force":1.18908,"tcp_end":[0.49805,-0.04298,0.07201],"tcp_start":[0.50165,-0.04328,0.03131],"tcp_to_object_dist_end":0.04888,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```