## Search State

- **Seed**: 6
- **Iteration**: 5 / 15

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

## Current Skill (Q=0.419) — your mutation base

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

- **Composite score**: 0.419
- **task_score** (E): 0.872
- **fitness_score**: 0.876  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.590

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.1753 |
| descend_to_peg | 0.00 | 1.00 | 0.1017 |
| align_at_channel | 0.67 | 1.00 | 0.0347 |
| push_through | 0.67 | 0.67 | 0.1054 |
| retract_after_push | 1.00 | 1.00 | 0.0410 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.137, 0.138) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.548 | 2.127 |
| descend_to_peg | descend | 0.00 / step_budget | (0.497, 0.137, 0.138)→(0.497, 0.129, 0.037) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.179 | 1.00 / 1.333 | 0.847 | 2.661 |
| align_at_channel | contact | 0.67 / force_exceeded | (0.497, 0.129, 0.037)→(0.496, 0.095, 0.030) | (0.501, 0.099, 0.034)→(0.507, 0.067, 0.036) | 0.179→0.147 | 1.00 / 2.000 | 2612.928 | 5.989 |
| push_through | push | 0.67 / step_budget | (0.497, 0.053, 0.030)→(0.502, -0.052, 0.030) | (0.507, 0.067, 0.036)→(0.503, -0.082, 0.035) | 0.147→0.007 | 0.67 / 1.333 | 1.561 | 38.457 |
| retract_after_push | retract | 1.00 / step_budget | (0.502, -0.052, 0.030)→(0.498, -0.051, 0.071) | (0.503, -0.082, 0.035)→(0.501, -0.080, 0.041) | 0.007→0.010 | 1.00 / 1.333 | 4.856 | 14.558 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.916
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.916
- phase_score: 0.882
- phase_breakdown.descend_to_contact_score: 0.899
- phase_breakdown.align_at_channel_score: 0.799
- phase_breakdown.approach_high_score: 0.674
- phase_breakdown.push_through_channel_score: 0.941

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.921
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.420
- **K-run variance**: 0.0051
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.239


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.57492,"average_solve_count":327.0,"average_success_count":327.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_channel.align_force_threshold":21.22373,"align_at_channel.align_speed":0.01694,"approach_high.approach_speed":0.07966,"descend_to_peg.contact_force_threshold":9.99839,"descend_to_peg.descend_speed":0.01886,"push_through.push_distance":0.14241,"push_through.push_force_guard_threshold":46.79458,"push_through.push_retry_offset_x":-0.00076,"push_through.push_speed":0.01701,"retract_after_push.retract_speed":0.05549},"optimized_scores":{"best_composite_score":0.50547,"best_fitness_score":0.89547,"best_task_score":0.91574},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":279.0,"contact_point_centroid":[0.50273,-0.00261,0.04254],"force_p95":25.12492,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.06659,"mean_force":6.80667,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49753,0.00886,0.02829]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.50281,-0.10092,0.05301],"force_p95":50.39888,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.91605,"mean_force":28.51159,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50053,-0.05372,0.02943]},{"body_a":"attachment","body_b":"peg","contact_count":469.0,"contact_point_centroid":[0.49869,-0.06506,0.05324],"force_p95":26.68539,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.53189,"mean_force":20.28019,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49657,-0.05356,0.04922]},{"body_a":"peg","body_b":"channel_base_body","contact_count":469.0,"contact_point_centroid":[0.5012,-0.1005,0.0637],"force_p95":26.44542,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.29884,"mean_force":20.14655,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49657,-0.05356,0.04922]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":235.0,"contact_point_centroid":[0.52518,-0.01399,0.02878],"force_p95":22.82029,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.51223,"mean_force":3.43805,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49721,0.01429,0.02813]},{"body_a":"peg","body_b":"channel_base_body","contact_count":116.0,"contact_point_centroid":[0.50686,-0.03773,0.00989],"force_p95":17.95641,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.2155,"mean_force":6.93986,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49779,0.00647,0.02851]},{"body_a":"peg","body_b":"channel_base_body","contact_count":869.0,"contact_point_centroid":[0.50277,0.03514,0.00995],"force_p95":3.46772,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.22139,"mean_force":1.92458,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49658,0.08107,0.03132]},{"body_a":"attachment","body_b":"peg","contact_count":887.0,"contact_point_centroid":[0.5005,0.06901,0.03904],"force_p95":3.10035,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.84347,"mean_force":1.5742,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49655,0.08068,0.03123]},{"body_a":"peg","body_b":"channel_base_body","contact_count":373.0,"contact_point_centroid":[0.50312,0.06748,0.00932],"force_p95":0.61839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.5697,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49851,0.15716,0.2181]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":45.0,"contact_point_centroid":[0.52501,0.04079,0.02411],"force_p95":0.90029,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.94918,"mean_force":0.6209,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49735,0.06893,0.03041]},{"body_a":"peg","body_b":"channel_base_body","contact_count":643.0,"contact_point_centroid":[0.50299,0.06741,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55159,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.4981,0.10278,0.0845]}],"total_contact_groups":11},"final_pose_error":0.01006,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49974,-0.07906,0.0555],"final_tcp_position":[0.49677,-0.05368,0.07031],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":3919.07954,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":389.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54682,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":373.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_high","tcp_end":[0.49997,0.10864,0.13596],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11021,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":643.0,"n_steps_budget":1000.0,"object_pos_end":[0.50304,0.0675,0.0338],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":0.5455,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":643.0,"raw_peak_contact_force":0.55159,"subtask_id":"descend_to_contact","tcp_end":[0.49896,0.09752,0.03659],"tcp_start":[0.49997,0.10864,0.13596],"tcp_to_object_dist_end":0.03043,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":925.0,"n_steps_budget":1000.0,"object_pos_end":[0.50699,0.03936,0.03582],"object_pos_start":[0.50304,0.0675,0.0338],"object_to_goal_dist_end":0.11964,"object_to_goal_dist_start":0.14766,"object_z_max":0.03585,"peak_contact_force":3919.07954,"phase_name":"align_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1801.0,"raw_peak_contact_force":7.22139,"subtask_id":"align_at_channel","tcp_end":[0.49741,0.06804,0.03035],"tcp_start":[0.49896,0.09752,0.03659],"tcp_to_object_dist_end":0.03072,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":354.0,"n_steps_budget":1000.0,"object_pos_end":[0.50225,-0.08496,0.03557],"object_pos_start":[0.50699,0.03936,0.03582],"object_to_goal_dist_end":0.00702,"object_to_goal_dist_start":0.11964,"object_z_max":0.03645,"peak_contact_force":2.42722,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":650.0,"raw_peak_contact_force":51.06659,"subtask_id":"push_through_channel","tcp_end":[0.50049,-0.05647,0.02923],"tcp_start":[0.50055,-0.05637,0.02929],"tcp_to_object_dist_end":0.02924,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":469.0,"n_steps_budget":600.0,"object_pos_end":[0.49974,-0.07906,0.0555],"object_pos_start":[0.5022,-0.08524,0.0356],"object_to_goal_dist_end":0.01553,"object_to_goal_dist_start":0.00719,"object_z_max":0.05546,"peak_contact_force":13.48296,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":938.0,"raw_peak_contact_force":31.53189,"tcp_end":[0.49677,-0.05368,0.07031],"tcp_start":[0.50049,-0.05647,0.02923],"tcp_to_object_dist_end":0.02953,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.73422,"average_solve_count":301.0,"average_success_count":301.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_channel.align_force_threshold":17.53234,"align_at_channel.align_speed":0.018,"approach_high.approach_speed":0.09209,"descend_to_peg.contact_force_threshold":14.39795,"descend_to_peg.descend_speed":0.02792,"push_through.push_distance":0.14555,"push_through.push_force_guard_threshold":48.0919,"push_through.push_retry_offset_x":0.00338,"push_through.push_speed":0.02191,"retract_after_push.retract_speed":0.08151},"optimized_scores":{"best_composite_score":0.33072,"best_fitness_score":0.92072,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":335.0,"contact_point_centroid":[0.50358,0.02093,0.04496],"force_p95":17.16537,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.8088,"mean_force":2.9322,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49895,0.03248,0.02864]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":176.0,"contact_point_centroid":[0.52516,0.02094,0.02989],"force_p95":16.03293,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.43871,"mean_force":2.66659,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49834,0.04981,0.02845]},{"body_a":"peg","body_b":"channel_base_body","contact_count":167.0,"contact_point_centroid":[0.50561,-0.01515,0.00982],"force_p95":15.68779,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.0806,"mean_force":4.27849,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49917,0.02772,0.02876]},{"body_a":"peg","body_b":"channel_base_body","contact_count":923.0,"contact_point_centroid":[0.50436,0.07659,0.00996],"force_p95":2.84373,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.49442,"mean_force":1.87432,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.4977,0.12254,0.03156]},{"body_a":"attachment","body_b":"peg","contact_count":944.0,"contact_point_centroid":[0.50162,0.11019,0.03921],"force_p95":2.55573,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.1301,"mean_force":1.57216,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49767,0.12185,0.03143]},{"body_a":"peg","body_b":"channel_base_body","contact_count":575.0,"contact_point_centroid":[0.50388,0.11084,0.00941],"force_p95":0.59803,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.41312,"mean_force":0.56515,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50187,0.14449,0.0861]},{"body_a":"attachment","body_b":"peg","contact_count":15.0,"contact_point_centroid":[0.50309,0.12957,0.05599],"force_p95":1.668,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.12838,"mean_force":1.06405,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50024,0.1415,0.04068]},{"body_a":"peg","body_b":"channel_base_body","contact_count":315.0,"contact_point_centroid":[0.50347,0.11161,0.00935],"force_p95":0.65414,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56892,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.5019,0.17531,0.21633]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":276.0,"contact_point_centroid":[0.52503,0.08352,0.02724],"force_p95":0.99424,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.99081,"mean_force":0.67268,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49824,0.1121,0.03073]},{"body_a":"peg","body_b":"channel_base_body","contact_count":405.0,"contact_point_centroid":[0.50579,-0.08121,0.00942],"force_p95":0.61519,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.54004,"mean_force":0.55512,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49915,-0.04825,0.05082]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49972,0.19973,0.29848]},{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.50518,-0.10015,0.05922],"force_p95":0.08031,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.10647,"mean_force":0.0193,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50141,-0.04929,0.03121]}],"total_contact_groups":12},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50585,-0.08072,0.03385],"final_tcp_position":[0.49887,-0.04808,0.07113],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":24.8088,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":337.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.11176,0.03384],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.53927,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":331.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach_high","tcp_end":[0.50625,0.14849,0.13831],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11077,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":575.0,"n_steps_budget":1000.0,"object_pos_end":[0.50369,0.11137,0.03421],"object_pos_start":[0.50376,0.11176,0.03384],"object_to_goal_dist_end":0.1915,"object_to_goal_dist_start":0.1919,"object_z_max":0.0342,"peak_contact_force":0.57221,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":590.0,"raw_peak_contact_force":2.41312,"subtask_id":"descend_to_contact","tcp_end":[0.50013,0.14128,0.03718],"tcp_start":[0.50625,0.14849,0.13831],"tcp_to_object_dist_end":0.03026,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50702,0.07849,0.0357],"object_pos_start":[0.50369,0.11137,0.03421],"object_to_goal_dist_end":0.15871,"object_to_goal_dist_start":0.1915,"object_z_max":0.03578,"peak_contact_force":1.42316,"phase_name":"align_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2143.0,"raw_peak_contact_force":5.49442,"subtask_id":"align_at_channel","tcp_end":[0.49857,0.10741,0.03046],"tcp_start":[0.50013,0.14128,0.03718],"tcp_to_object_dist_end":0.03058,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":428.0,"n_steps_budget":1000.0,"object_pos_end":[0.50561,-0.07864,0.03563],"object_pos_start":[0.50702,0.07849,0.0357],"object_to_goal_dist_end":0.00725,"object_to_goal_dist_start":0.15871,"object_z_max":0.03748,"peak_contact_force":0.0,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":678.0,"raw_peak_contact_force":24.8088,"subtask_id":"push_through_channel","tcp_end":[0.50249,-0.04841,0.03043],"tcp_start":[0.49857,0.10741,0.03046],"tcp_to_object_dist_end":0.03083,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":407.0,"n_steps_budget":600.0,"object_pos_end":[0.50585,-0.08072,0.03385],"object_pos_start":[0.50561,-0.07864,0.03563],"object_to_goal_dist_end":0.00852,"object_to_goal_dist_start":0.00725,"object_z_max":0.03563,"peak_contact_force":0.54373,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":416.0,"raw_peak_contact_force":1.54004,"tcp_end":[0.49887,-0.04808,0.07113],"tcp_start":[0.50249,-0.04841,0.03043],"tcp_to_object_dist_end":0.05004,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95455,"average_solve_count":330.0,"average_success_count":330.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_channel.align_force_threshold":14.90999,"align_at_channel.align_speed":0.02965,"approach_high.approach_speed":0.04133,"descend_to_peg.contact_force_threshold":6.78523,"descend_to_peg.descend_speed":0.03188,"push_through.push_distance":0.15219,"push_through.push_force_guard_threshold":41.17785,"push_through.push_retry_offset_x":-0.00712,"push_through.push_speed":0.0175,"retract_after_push.retract_speed":0.06069},"optimized_scores":{"best_composite_score":0.42038,"best_fitness_score":0.81038,"best_task_score":0.70124},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":316.0,"contact_point_centroid":[0.50098,0.02509,0.04426],"force_p95":32.47153,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.49454,"mean_force":8.13045,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49427,0.03597,0.0289]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":287.0,"contact_point_centroid":[0.52535,0.01721,0.03462],"force_p95":30.14801,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.89455,"mean_force":6.62074,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49347,0.04413,0.02858]},{"body_a":"peg","body_b":"channel_base_body","contact_count":178.0,"contact_point_centroid":[0.50742,-0.01172,0.00985],"force_p95":20.31396,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.26086,"mean_force":7.30572,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49474,0.03087,0.02908]},{"body_a":"peg","body_b":"channel_base_body","contact_count":22.0,"contact_point_centroid":[0.49773,-0.10029,0.05869],"force_p95":9.2248,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.60218,"mean_force":4.91452,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50093,-0.05132,0.0319]},{"body_a":"attachment","body_b":"peg","contact_count":70.0,"contact_point_centroid":[0.499,-0.0628,0.03783],"force_p95":6.44661,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.09607,"mean_force":1.63146,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49934,-0.05083,0.03704]},{"body_a":"peg","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.52125,0.0547,0.0633],"force_p95":9.25692,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.79868,"mean_force":2.67329,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49104,0.07224,0.0277]},{"body_a":"peg","body_b":"channel_base_body","contact_count":632.0,"contact_point_centroid":[0.50368,0.08476,0.00995],"force_p95":3.49176,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.25108,"mean_force":2.25179,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.48979,0.12752,0.03108]},{"body_a":"attachment","body_b":"peg","contact_count":653.0,"contact_point_centroid":[0.49656,0.11564,0.041],"force_p95":3.79325,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.02482,"mean_force":2.03751,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.48984,0.12639,0.03099]},{"body_a":"peg","body_b":"channel_base_body","contact_count":654.0,"contact_point_centroid":[0.49635,0.11734,0.00945],"force_p95":0.6373,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.0173,"mean_force":0.59648,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48727,0.15113,0.08514]},{"body_a":"attachment","body_b":"peg","contact_count":31.0,"contact_point_centroid":[0.4944,0.13686,0.05868],"force_p95":3.85154,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.53801,"mean_force":1.45388,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49091,0.14873,0.04338]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":247.0,"contact_point_centroid":[0.52506,0.09042,0.02949],"force_p95":2.3632,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.81866,"mean_force":1.35483,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.4906,0.11546,0.03053]},{"body_a":"peg","body_b":"channel_base_body","contact_count":406.0,"contact_point_centroid":[0.49745,-0.08398,0.0095],"force_p95":0.63015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.5493,"mean_force":0.55716,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.4984,-0.05046,0.05153]},{"body_a":"peg","body_b":"channel_base_body","contact_count":314.0,"contact_point_centroid":[0.49641,0.11911,0.00937],"force_p95":0.62917,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56827,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49159,0.17749,0.21571]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49927,0.19954,0.29745]}],"total_contact_groups":14},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49826,-0.08042,0.0338],"final_tcp_position":[0.49811,-0.05032,0.072],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":3918.28242,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":339.0,"n_steps_budget":1000.0,"object_pos_end":[0.49607,0.11898,0.03382],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19911,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.55747,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":338.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_high","tcp_end":[0.48553,0.15483,0.13909],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1117,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":654.0,"n_steps_budget":1000.0,"object_pos_end":[0.49608,0.11869,0.03477],"object_pos_start":[0.49607,0.11898,0.03382],"object_to_goal_dist_end":0.1988,"object_to_goal_dist_start":0.19911,"object_z_max":0.0349,"peak_contact_force":1.42472,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":685.0,"raw_peak_contact_force":5.0173,"subtask_id":"descend_to_contact","tcp_end":[0.4916,0.14833,0.03591],"tcp_start":[0.48553,0.15483,0.13909],"tcp_to_object_dist_end":0.02999,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":740.0,"n_steps_budget":1000.0,"object_pos_end":[0.50693,0.08313,0.03664],"object_pos_start":[0.49608,0.11869,0.03477],"object_to_goal_dist_end":0.16331,"object_to_goal_dist_start":0.1988,"object_z_max":0.03677,"peak_contact_force":3918.28242,"phase_name":"align_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1532.0,"raw_peak_contact_force":5.25108,"subtask_id":"align_at_channel","tcp_end":[0.49116,0.10926,0.0304],"tcp_start":[0.4916,0.14833,0.03591],"tcp_to_object_dist_end":0.03115,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":446.0,"n_steps_budget":1000.0,"object_pos_end":[0.49982,-0.08095,0.03447],"object_pos_start":[0.50693,0.08313,0.03664],"object_to_goal_dist_end":0.00562,"object_to_goal_dist_start":0.16331,"object_z_max":0.038,"peak_contact_force":2.2556,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":809.0,"raw_peak_contact_force":39.49454,"subtask_id":"push_through_channel","tcp_end":[0.50172,-0.05067,0.03131],"tcp_start":[0.49116,0.10926,0.0304],"tcp_to_object_dist_end":0.0305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":406.0,"n_steps_budget":600.0,"object_pos_end":[0.49826,-0.08042,0.0338],"object_pos_start":[0.49982,-0.08095,0.03447],"object_to_goal_dist_end":0.00645,"object_to_goal_dist_start":0.00562,"object_z_max":0.03548,"peak_contact_force":0.54275,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":498.0,"raw_peak_contact_force":10.60218,"tcp_end":[0.49811,-0.05032,0.072],"tcp_start":[0.50172,-0.05067,0.03131],"tcp_to_object_dist_end":0.04863,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```