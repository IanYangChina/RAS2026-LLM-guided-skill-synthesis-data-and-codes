## Search State

- **Seed**: 6
- **Iteration**: 9 / 15

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

## Current Skill (Q=-0.162) — your mutation base

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

- **Composite score**: -0.162
- **task_score** (E): 0.413
- **fitness_score**: 0.398  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.560

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.1754 |
| descend_to_peg | 1.00 | 1.00 | 0.0850 |
| push_through | 1.00 | 1.00 | 0.0554 |
| retract_after_push | 1.00 | 1.00 | 0.0305 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.137, 0.138) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.550 | 2.127 |
| descend_to_peg | descend | 1.00 / step_budget | (0.497, 0.137, 0.138)→(0.497, 0.130, 0.053) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.577 | 0.601 |
| push_through | push | 1.00 / time_limit | (0.497, 0.130, 0.053)→(0.495, 0.076, 0.043) | (0.501, 0.099, 0.034)→(0.506, 0.045, 0.040) | 0.180→0.125 | 1.00 / 2.667 | 12.616 | 12.790 |
| retract_after_push | retract | 1.00 / step_budget | (0.495, 0.076, 0.043)→(0.492, 0.075, 0.074) | (0.506, 0.045, 0.040)→(0.501, 0.022, 0.025) | 0.125→0.103 | 1.00 / 1.000 | 1.076 | 84.019 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.487
- alignment_error: None
- force_efficiency: 0.493
- terminal_score: 0.487
- phase_score: 0.434
- phase_breakdown.descend_to_contact_score: 0.759
- phase_breakdown.approach_high_score: 0.674
- phase_breakdown.push_through_channel_score: 0.363

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.455
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.487
- **Median Q (composite search score)**: -0.166
- **K-run variance**: 0.0021
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.267


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.93458,"average_solve_count":214.0,"average_success_count":214.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_speed":0.07843,"descend_to_peg.descend_speed":0.02704,"descend_to_peg.descend_tolerance":0.02172,"push_through.push_distance":0.15887,"push_through.push_force_guard_threshold":44.63589,"push_through.push_max_time":475.6941,"push_through.push_retry_offset_x":0.01143,"push_through.push_speed":0.01908,"retract_after_push.retract_speed":0.02332,"retract_after_push.retract_tolerance":0.03378},"optimized_scores":{"best_composite_score":-0.10514,"best_fitness_score":0.45486,"best_task_score":0.48676},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":17.0,"contact_point_centroid":[0.50158,0.0339,0.04266],"force_p95":17.84901,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.33036,"mean_force":3.38655,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49624,0.04437,0.0434]},{"body_a":"peg","body_b":"channel_base_body","contact_count":108.0,"contact_point_centroid":[0.50285,0.01497,0.00992],"force_p95":2.35802,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.83179,"mean_force":1.08237,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49455,0.04425,0.05586]},{"body_a":"attachment","body_b":"peg","contact_count":958.0,"contact_point_centroid":[0.50033,0.05826,0.0452],"force_p95":11.77147,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.38165,"mean_force":5.1139,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49623,0.06937,0.04572]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50526,0.03508,0.0099],"force_p95":10.26413,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.70788,"mean_force":5.09892,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49627,0.07053,0.04591]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":135.0,"contact_point_centroid":[0.52502,0.01911,0.04006],"force_p95":5.12357,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.74203,"mean_force":3.40814,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49666,0.04849,0.04369]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52504,0.02837,0.02314],"force_p95":3.22949,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.37739,"mean_force":2.19123,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49672,0.04443,0.04329]},{"body_a":"peg","body_b":"channel_base_body","contact_count":373.0,"contact_point_centroid":[0.50312,0.06748,0.00932],"force_p95":0.61839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.5697,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49851,0.15716,0.2181]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":12.0,"contact_point_centroid":[0.47482,-0.01165,0.0496],"force_p95":0.89888,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.98766,"mean_force":0.4513,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49409,0.04422,0.05843]},{"body_a":"peg","body_b":"channel_base_body","contact_count":180.0,"contact_point_centroid":[0.50305,0.06746,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55159,"mean_force":0.54666,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49888,0.10408,0.0964]}],"total_contact_groups":9},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50016,-0.01042,0.02634],"final_tcp_position":[0.49372,0.04421,0.07369],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":25.33036,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":389.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54682,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":373.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_high","tcp_end":[0.49997,0.10864,0.13596],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11021,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":180.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":0.54792,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":180.0,"raw_peak_contact_force":0.55159,"subtask_id":"descend_to_contact","tcp_end":[0.49924,0.09942,0.05309],"tcp_start":[0.49997,0.10864,0.13596],"tcp_to_object_dist_end":0.03757,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50711,0.01376,0.04025],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.09403,"object_to_goal_dist_start":0.14758,"object_z_max":0.0406,"peak_contact_force":15.10292,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2093.0,"raw_peak_contact_force":15.38165,"subtask_id":"push_through_channel","tcp_end":[0.49677,0.04449,0.04335],"tcp_start":[0.49924,0.09942,0.05309],"tcp_to_object_dist_end":0.03257,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":115.0,"n_steps_budget":1000.0,"object_pos_end":[0.50016,-0.01042,0.02634],"object_pos_start":[0.50711,0.01376,0.04025],"object_to_goal_dist_end":0.07091,"object_to_goal_dist_start":0.09403,"object_z_max":0.0404,"peak_contact_force":1.80629,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":142.0,"raw_peak_contact_force":25.33036,"tcp_end":[0.49372,0.04421,0.07369],"tcp_start":[0.49677,0.04449,0.04335],"tcp_to_object_dist_end":0.07258,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04167,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_speed":0.11488,"descend_to_peg.descend_speed":0.02879,"descend_to_peg.descend_tolerance":0.01964,"push_through.push_distance":0.1571,"push_through.push_force_guard_threshold":45.05967,"push_through.push_max_time":635.88933,"push_through.push_retry_offset_x":-0.00134,"push_through.push_speed":0.02307,"retract_after_push.retract_speed":0.05247,"retract_after_push.retract_tolerance":0.0294},"optimized_scores":{"best_composite_score":-0.16586,"best_fitness_score":0.39414,"best_task_score":0.42979},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.50281,0.07709,0.0429],"force_p95":19.9166,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.20898,"mean_force":4.34435,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49807,0.08787,0.04353]},{"body_a":"peg","body_b":"channel_base_body","contact_count":99.0,"contact_point_centroid":[0.50237,0.05358,0.00976],"force_p95":1.76286,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.69317,"mean_force":0.98323,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49629,0.08758,0.05698]},{"body_a":"attachment","body_b":"peg","contact_count":973.0,"contact_point_centroid":[0.50151,0.10167,0.04538],"force_p95":10.0605,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.81468,"mean_force":5.10479,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.498,0.11299,0.04585]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50537,0.07824,0.00991],"force_p95":9.08302,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.68484,"mean_force":5.25956,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49804,0.11373,0.04598]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52502,0.0731,0.02164],"force_p95":5.29203,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.49727,"mean_force":3.82389,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49836,0.08796,0.04343]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":95.0,"contact_point_centroid":[0.52501,0.05985,0.04089],"force_p95":4.05326,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.77546,"mean_force":2.78997,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49832,0.09097,0.0437]},{"body_a":"peg","body_b":"channel_base_body","contact_count":310.0,"contact_point_centroid":[0.50346,0.11166,0.00935],"force_p95":0.66485,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56951,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50184,0.17534,0.21611]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":12.0,"contact_point_centroid":[0.47477,0.02867,0.04741],"force_p95":0.98881,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.08474,"mean_force":0.55914,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49599,0.08754,0.05735]},{"body_a":"peg","body_b":"channel_base_body","contact_count":179.0,"contact_point_centroid":[0.50375,0.11166,0.00942],"force_p95":0.5897,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63653,"mean_force":0.54307,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50312,0.14533,0.09753]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49969,0.19973,0.29836]}],"total_contact_groups":10},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50234,0.03321,0.02477],"final_tcp_position":[0.49545,0.08748,0.07376],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":27.20898,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":332.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11175,0.03387],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.54697,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":326.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach_high","tcp_end":[0.50618,0.14847,0.13829],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":179.0,"n_steps_budget":1000.0,"object_pos_end":[0.50369,0.11176,0.03381],"object_pos_start":[0.50371,0.11175,0.03387],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19188,"object_z_max":0.03391,"peak_contact_force":0.58372,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":179.0,"raw_peak_contact_force":0.63653,"subtask_id":"descend_to_contact","tcp_end":[0.50119,0.14242,0.0533],"tcp_start":[0.50618,0.14847,0.13829],"tcp_to_object_dist_end":0.03641,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50705,0.05643,0.04021],"object_pos_start":[0.50369,0.11176,0.03381],"object_to_goal_dist_end":0.13661,"object_to_goal_dist_start":0.1919,"object_z_max":0.04057,"peak_contact_force":13.80319,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2068.0,"raw_peak_contact_force":13.81468,"subtask_id":"push_through_channel","tcp_end":[0.49837,0.088,0.04345],"tcp_start":[0.50119,0.14242,0.0533],"tcp_to_object_dist_end":0.0329,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":105.0,"n_steps_budget":630.0,"object_pos_end":[0.50234,0.03321,0.02477],"object_pos_start":[0.50705,0.05643,0.04021],"object_to_goal_dist_end":0.11425,"object_to_goal_dist_start":0.13661,"object_z_max":0.04023,"peak_contact_force":0.46451,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":124.0,"raw_peak_contact_force":27.20898,"tcp_end":[0.49545,0.08748,0.07376],"tcp_start":[0.49837,0.088,0.04345],"tcp_to_object_dist_end":0.07344,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.67391,"average_solve_count":230.0,"average_success_count":230.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_speed":0.07888,"descend_to_peg.descend_speed":0.01186,"descend_to_peg.descend_tolerance":0.02316,"push_through.push_distance":0.15487,"push_through.push_force_guard_threshold":50.35398,"push_through.push_max_time":579.5274,"push_through.push_retry_offset_x":0.00527,"push_through.push_speed":0.0135,"retract_after_push.retract_speed":0.04592,"retract_after_push.retract_tolerance":0.03146},"optimized_scores":{"best_composite_score":-0.21633,"best_fitness_score":0.34367,"best_task_score":0.32133},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.475,0.09471,0.05606],"force_p95":191.26373,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":199.51629,"mean_force":123.7713,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.48682,0.09471,0.05403]},{"body_a":"peg","body_b":"channel_base_body","contact_count":99.0,"contact_point_centroid":[0.49959,0.06079,0.0095],"force_p95":1.72914,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.28426,"mean_force":0.87011,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.48686,0.09473,0.05695]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.49557,0.08581,0.04213],"force_p95":15.06649,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.80646,"mean_force":3.28184,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.48844,0.0952,0.04319]},{"body_a":"peg","body_b":"channel_base_body","contact_count":998.0,"contact_point_centroid":[0.50007,0.08632,0.00991],"force_p95":7.91315,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.1732,"mean_force":4.70355,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48792,0.121,0.04573]},{"body_a":"attachment","body_b":"peg","contact_count":967.0,"contact_point_centroid":[0.49308,0.10954,0.0449],"force_p95":7.52008,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.77115,"mean_force":4.43657,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.4879,0.12017,0.04559]},{"body_a":"peg","body_b":"channel_base_body","contact_count":302.0,"contact_point_centroid":[0.49643,0.11907,0.00936],"force_p95":0.63317,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56926,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49159,0.17751,0.215]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47498,0.02905,0.04104],"force_p95":1.37309,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.39652,"mean_force":1.21985,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.48668,0.09446,0.06041]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49922,0.19954,0.29673]},{"body_a":"peg","body_b":"channel_base_body","contact_count":196.0,"contact_point_centroid":[0.49591,0.11898,0.0094],"force_p95":0.59883,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61523,"mean_force":0.54399,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.487,0.15206,0.09849]}],"total_contact_groups":9},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49902,0.04279,0.02368],"final_tcp_position":[0.48604,0.09464,0.07366],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":199.51629,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":327.0,"n_steps_budget":1000.0,"object_pos_end":[0.49599,0.11912,0.03383],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19926,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.55647,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":326.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_high","tcp_end":[0.48564,0.15475,0.13871],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":196.0,"n_steps_budget":1000.0,"object_pos_end":[0.49607,0.11914,0.0338],"object_pos_start":[0.49599,0.11912,0.03383],"object_to_goal_dist_end":0.19927,"object_to_goal_dist_start":0.19926,"object_z_max":0.03391,"peak_contact_force":0.5999,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":196.0,"raw_peak_contact_force":0.61523,"subtask_id":"descend_to_contact","tcp_end":[0.49061,0.14951,0.0529],"tcp_start":[0.48564,0.15475,0.13871],"tcp_to_object_dist_end":0.03629,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5034,0.06571,0.0403],"object_pos_start":[0.49607,0.11914,0.0338],"object_to_goal_dist_end":0.14575,"object_to_goal_dist_start":0.19927,"object_z_max":0.04058,"peak_contact_force":8.94251,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1965.0,"raw_peak_contact_force":9.1732,"subtask_id":"push_through_channel","tcp_end":[0.48869,0.09534,0.04318],"tcp_start":[0.49061,0.14951,0.0529],"tcp_to_object_dist_end":0.0332,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":105.0,"n_steps_budget":690.0,"object_pos_end":[0.49902,0.04279,0.02368],"object_pos_start":[0.5034,0.06571,0.0403],"object_to_goal_dist_end":0.12388,"object_to_goal_dist_start":0.14575,"object_z_max":0.0403,"peak_contact_force":0.95638,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":122.0,"raw_peak_contact_force":199.51629,"tcp_end":[0.48604,0.09464,0.07366],"tcp_start":[0.48869,0.09534,0.04318],"tcp_to_object_dist_end":0.07318,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```