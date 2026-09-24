## Search State

- **Seed**: 6
- **Iteration**: 4 / 15

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.848, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.438) — your mutation base

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
      tolerance: 0.1
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
      tolerance: 0.1
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
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - -0.01
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
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
      tolerance: 0.1
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
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
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
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=approach_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=60.0
  - retries: max_attempts=1, strategy=reduce_speed
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.0]
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=descend_force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
- **align_at_channel** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, -0.01, 0.0]
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - align_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - align_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=align_force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
- **push_through** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=push_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **retract_after_push** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.438
- **task_score** (E): 0.848
- **fitness_score**: 0.861  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.067
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.1753 |
| descend_to_peg | 0.00 | 1.00 | 0.1017 |
| align_at_channel | 0.67 | 1.00 | 0.0286 |
| push_through | 0.67 | 1.00 | 0.0983 |
| retract_after_push | 1.00 | 1.00 | 0.0409 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.137, 0.138) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.543 | 2.127 |
| descend_to_peg | descend | 0.00 / step_budget | (0.497, 0.137, 0.138)→(0.497, 0.129, 0.037) | (0.501, 0.099, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.179 | 1.00 / 1.000 | 0.356 | 2.342 |
| align_at_channel | contact | 0.67 / step_budget | (0.497, 0.129, 0.037)→(0.496, 0.101, 0.030) | (0.501, 0.099, 0.034)→(0.506, 0.073, 0.036) | 0.179→0.153 | 1.00 / 2.000 | 1307.713 | 6.494 |
| push_through | push | 0.67 / step_budget | (0.498, 0.047, 0.030)→(0.501, -0.052, 0.030) | (0.506, 0.073, 0.036)→(0.506, -0.081, 0.036) | 0.153→0.007 | 1.00 / 1.667 | 0.564 | 34.917 |
| retract_after_push | retract | 1.00 / step_budget | (0.501, -0.052, 0.030)→(0.497, -0.051, 0.071) | (0.506, -0.081, 0.036)→(0.505, -0.079, 0.035) | 0.007→0.008 | 1.00 / 1.000 | 0.888 | 12.505 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.933
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.933
- phase_score: 0.865
- phase_breakdown.descend_to_contact_score: 0.899
- phase_breakdown.align_at_channel_score: 0.693
- phase_breakdown.approach_high_score: 0.674
- phase_breakdown.push_through_channel_score: 0.948

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.922
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.432
- **K-run variance**: 0.0175
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.290


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.5625,"average_solve_count":336.0,"average_success_count":336.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_channel.align_force_threshold":20.40118,"align_at_channel.align_speed":0.02016,"approach_high.approach_speed":0.0746,"descend_to_peg.contact_force_threshold":9.69046,"descend_to_peg.descend_speed":0.01328,"push_through.push_distance":0.1214,"push_through.push_speed":0.00661,"retract_after_push.retract_speed":0.06889},"optimized_scores":{"best_composite_score":0.6021,"best_fitness_score":0.8921,"best_task_score":0.93349},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":262.0,"contact_point_centroid":[0.50252,0.00771,0.03924],"force_p95":25.23615,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.08629,"mean_force":5.39834,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49772,0.01912,0.02903]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":227.0,"contact_point_centroid":[0.52539,-0.0014,0.03723],"force_p95":24.72816,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.94472,"mean_force":4.43498,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49718,0.02717,0.02883]},{"body_a":"peg","body_b":"channel_base_body","contact_count":149.0,"contact_point_centroid":[0.50668,-0.0248,0.00985],"force_p95":17.91457,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.78729,"mean_force":4.79658,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.4978,0.01924,0.02913]},{"body_a":"peg","body_b":"channel_base_body","contact_count":343.0,"contact_point_centroid":[0.50408,0.04355,0.00994],"force_p95":3.93352,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.6159,"mean_force":2.16865,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49643,0.08859,0.03198]},{"body_a":"attachment","body_b":"peg","contact_count":332.0,"contact_point_centroid":[0.50094,0.07643,0.04049],"force_p95":3.59732,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.3612,"mean_force":1.88975,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49632,0.08796,0.03174]},{"body_a":"peg","body_b":"channel_base_body","contact_count":37.0,"contact_point_centroid":[0.50533,-0.10008,0.05985],"force_p95":3.9569,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.03676,"mean_force":0.82881,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49948,-0.04966,0.0362]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":75.0,"contact_point_centroid":[0.52523,-0.08175,0.03996],"force_p95":3.65627,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.96215,"mean_force":0.54472,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49944,-0.04963,0.03673]},{"body_a":"peg","body_b":"channel_base_body","contact_count":374.0,"contact_point_centroid":[0.50312,0.06744,0.00932],"force_p95":0.61822,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56964,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.4985,0.15715,0.21814]},{"body_a":"peg","body_b":"channel_base_body","contact_count":399.0,"contact_point_centroid":[0.50536,-0.08142,0.00946],"force_p95":0.66938,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.01518,"mean_force":0.55057,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49849,-0.04921,0.05112]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.525,0.05477,0.02437],"force_p95":0.88766,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.90029,"mean_force":0.65037,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49652,0.0826,0.03098]},{"body_a":"peg","body_b":"channel_base_body","contact_count":640.0,"contact_point_centroid":[0.50304,0.06743,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55159,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49809,0.10279,0.08449]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50352,-0.06145,0.0316],"force_p95":0.12695,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14935,"mean_force":0.03734,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50186,-0.04972,0.03039]}],"total_contact_groups":12},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50691,-0.0819,0.03379],"final_tcp_position":[0.49825,-0.04906,0.07113],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":3919.67866,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":390.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54714,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":374.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_high","tcp_end":[0.49998,0.10864,0.13597],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11021,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":640.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06745,0.0338],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.547,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":640.0,"raw_peak_contact_force":0.55159,"subtask_id":"descend_to_contact","tcp_end":[0.49894,0.09753,0.0366],"tcp_start":[0.49998,0.10864,0.13597],"tcp_to_object_dist_end":0.03048,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":367.0,"n_steps_budget":1000.0,"object_pos_end":[0.50698,0.05359,0.03589],"object_pos_start":[0.50301,0.06745,0.0338],"object_to_goal_dist_end":0.13384,"object_to_goal_dist_start":0.14761,"object_z_max":0.03595,"peak_contact_force":3919.67866,"phase_name":"align_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":686.0,"raw_peak_contact_force":6.6159,"subtask_id":"align_at_channel","tcp_end":[0.49657,0.08204,0.03093],"tcp_start":[0.49894,0.09753,0.0366],"tcp_to_object_dist_end":0.0307,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.50553,-0.07886,0.03588],"object_pos_start":[0.50698,0.05359,0.03589],"object_to_goal_dist_end":0.00699,"object_to_goal_dist_start":0.13384,"object_z_max":0.03745,"peak_contact_force":0.29354,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":638.0,"raw_peak_contact_force":31.08629,"subtask_id":"push_through_channel","tcp_end":[0.50187,-0.04939,0.0304],"tcp_start":[0.49657,0.08204,0.03093],"tcp_to_object_dist_end":0.03019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":407.0,"n_steps_budget":600.0,"object_pos_end":[0.50691,-0.0819,0.03379],"object_pos_start":[0.50553,-0.07886,0.03588],"object_to_goal_dist_end":0.00948,"object_to_goal_dist_start":0.00699,"object_z_max":0.03647,"peak_contact_force":0.54309,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":515.0,"raw_peak_contact_force":4.03676,"tcp_end":[0.49825,-0.04906,0.07113],"tcp_start":[0.50187,-0.04939,0.0304],"tcp_to_object_dist_end":0.05048,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.8179,"average_solve_count":324.0,"average_success_count":324.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_channel.align_force_threshold":20.01183,"align_at_channel.align_speed":0.01525,"approach_high.approach_speed":0.06566,"descend_to_peg.contact_force_threshold":14.32215,"descend_to_peg.descend_speed":0.02579,"push_through.push_distance":0.15281,"push_through.push_speed":0.01827,"retract_after_push.retract_speed":0.06386},"optimized_scores":{"best_composite_score":0.43225,"best_fitness_score":0.92225,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_left_wall","contact_count":231.0,"contact_point_centroid":[0.52517,0.01576,0.02592],"force_p95":16.01684,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.83604,"mean_force":2.40256,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49859,0.04453,0.02824]},{"body_a":"attachment","body_b":"peg","contact_count":342.0,"contact_point_centroid":[0.50396,0.01815,0.04472],"force_p95":16.82198,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.76534,"mean_force":3.44533,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49919,0.02976,0.02857]},{"body_a":"peg","body_b":"channel_base_body","contact_count":139.0,"contact_point_centroid":[0.50687,-0.01131,0.00987],"force_p95":16.12204,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.77116,"mean_force":5.91806,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49909,0.03441,0.02856]},{"body_a":"peg","body_b":"channel_base_body","contact_count":949.0,"contact_point_centroid":[0.50275,0.07769,0.00997],"force_p95":3.70046,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.25384,"mean_force":1.83096,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.4979,0.1243,0.03144]},{"body_a":"attachment","body_b":"peg","contact_count":981.0,"contact_point_centroid":[0.50115,0.11231,0.0385],"force_p95":3.32505,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.91911,"mean_force":1.46376,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49788,0.1241,0.03138]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50578,-0.06374,0.0504],"force_p95":6.98372,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.75588,"mean_force":2.59674,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50242,-0.05191,0.03034]},{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.50552,-0.10011,0.04344],"force_p95":0.37365,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.24492,"mean_force":0.16632,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.4994,-0.05161,0.04691]},{"body_a":"peg","body_b":"channel_base_body","contact_count":406.0,"contact_point_centroid":[0.50531,-0.08049,0.00946],"force_p95":0.6171,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.0423,"mean_force":0.55431,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49909,-0.05147,0.05079]},{"body_a":"peg","body_b":"channel_base_body","contact_count":576.0,"contact_point_centroid":[0.50373,0.11077,0.0094],"force_p95":0.60024,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.14015,"mean_force":0.57316,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50177,0.14449,0.08612]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.50308,0.1296,0.05646],"force_p95":3.81422,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.89771,"mean_force":1.44874,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50024,0.14153,0.04102]},{"body_a":"peg","body_b":"channel_base_body","contact_count":323.0,"contact_point_centroid":[0.50342,0.11161,0.00935],"force_p95":0.6399,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56833,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.5018,0.17521,0.21652]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49968,0.19971,0.29869]}],"total_contact_groups":12},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50556,-0.08199,0.0338],"final_tcp_position":[0.49883,-0.0513,0.07112],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":26.83604,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":345.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.11178,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.59042,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":339.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach_high","tcp_end":[0.50606,0.14848,0.13839],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11084,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":576.0,"n_steps_budget":1000.0,"object_pos_end":[0.50379,0.11139,0.03428],"object_pos_start":[0.50377,0.11178,0.03382],"object_to_goal_dist_end":0.19151,"object_to_goal_dist_start":0.19191,"object_z_max":0.03426,"peak_contact_force":0.49406,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":590.0,"raw_peak_contact_force":4.14015,"subtask_id":"descend_to_contact","tcp_end":[0.50012,0.1413,0.03718],"tcp_start":[0.50606,0.14848,0.13839],"tcp_to_object_dist_end":0.03027,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50686,0.08241,0.03559],"object_pos_start":[0.50379,0.11139,0.03428],"object_to_goal_dist_end":0.16261,"object_to_goal_dist_start":0.19151,"object_z_max":0.03567,"peak_contact_force":1.45884,"phase_name":"align_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1930.0,"raw_peak_contact_force":8.25384,"subtask_id":"align_at_channel","tcp_end":[0.49887,0.11156,0.03031],"tcp_start":[0.50012,0.1413,0.03718],"tcp_to_object_dist_end":0.03069,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":441.0,"n_steps_budget":1000.0,"object_pos_end":[0.50564,-0.08116,0.03552],"object_pos_start":[0.50686,0.08241,0.03559],"object_to_goal_dist_end":0.00729,"object_to_goal_dist_start":0.16261,"object_z_max":0.03682,"peak_contact_force":0.10095,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":712.0,"raw_peak_contact_force":26.83604,"subtask_id":"push_through_channel","tcp_end":[0.50244,-0.05165,0.03036],"tcp_start":[0.49887,0.11156,0.03031],"tcp_to_object_dist_end":0.03013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":408.0,"n_steps_budget":600.0,"object_pos_end":[0.50556,-0.08199,0.0338],"object_pos_start":[0.50564,-0.08116,0.03552],"object_to_goal_dist_end":0.00856,"object_to_goal_dist_start":0.00729,"object_z_max":0.03552,"peak_contact_force":0.52224,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":609.0,"raw_peak_contact_force":7.75588,"tcp_end":[0.49883,-0.0513,0.07112],"tcp_start":[0.50244,-0.05165,0.03036],"tcp_to_object_dist_end":0.04879,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.66144,"average_solve_count":319.0,"average_success_count":319.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_channel.align_force_threshold":10.5822,"align_at_channel.align_speed":0.02724,"approach_high.approach_speed":0.11007,"descend_to_peg.contact_force_threshold":15.66279,"descend_to_peg.descend_speed":0.01382,"push_through.push_distance":0.17284,"push_through.push_speed":0.01659,"retract_after_push.retract_speed":0.06614},"optimized_scores":{"best_composite_score":0.27826,"best_fitness_score":0.76826,"best_task_score":0.60931},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":304.0,"contact_point_centroid":[0.4999,0.01612,0.03951],"force_p95":18.06203,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.82816,"mean_force":4.48771,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49332,0.02693,0.02839]},{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.50614,-0.10038,0.05958],"force_p95":37.7985,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.54758,"mean_force":15.08356,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.4974,-0.05284,0.03015]},{"body_a":"peg","body_b":"channel_base_body","contact_count":191.0,"contact_point_centroid":[0.50608,-0.00707,0.00986],"force_p95":21.7865,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.81191,"mean_force":6.12678,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49289,0.03625,0.02824]},{"body_a":"peg","body_b":"channel_base_body","contact_count":416.0,"contact_point_centroid":[0.50743,-0.10017,0.06372],"force_p95":12.31591,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.72204,"mean_force":5.36068,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49383,-0.05321,0.04913]},{"body_a":"attachment","body_b":"peg","contact_count":410.0,"contact_point_centroid":[0.49814,-0.06437,0.05038],"force_p95":12.46948,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.16874,"mean_force":5.96221,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49383,-0.0532,0.04894]},{"body_a":"peg","body_b":"link7","contact_count":45.0,"contact_point_centroid":[0.5212,0.05195,0.06283],"force_p95":19.94833,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.30939,"mean_force":5.53396,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49099,0.06945,0.02724]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":266.0,"contact_point_centroid":[0.52517,-0.00693,0.0311],"force_p95":11.99463,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.51096,"mean_force":2.40452,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49353,0.0201,0.02837]},{"body_a":"peg","body_b":"channel_base_body","contact_count":35.0,"contact_point_centroid":[0.51363,-0.08534,0.00989],"force_p95":6.48317,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.0825,"mean_force":1.65385,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49475,-0.05341,0.03905]},{"body_a":"peg","body_b":"channel_base_body","contact_count":702.0,"contact_point_centroid":[0.49638,0.08213,0.00994],"force_p95":3.16182,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.61158,"mean_force":2.24771,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49018,0.12777,0.03077]},{"body_a":"attachment","body_b":"peg","contact_count":711.0,"contact_point_centroid":[0.49429,0.11521,0.04018],"force_p95":2.82906,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.38799,"mean_force":1.87224,"phase_index":2.0,"phase_name":"align_at_channel","phase_type":"contact","tcp_position_centroid":[0.49018,0.12688,0.03061]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":184.0,"contact_point_centroid":[0.52502,-0.08231,0.05999],"force_p95":2.31712,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.50205,"mean_force":1.78851,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49338,-0.05312,0.05037]},{"body_a":"peg","body_b":"channel_base_body","contact_count":719.0,"contact_point_centroid":[0.49612,0.11795,0.00944],"force_p95":0.61891,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.33471,"mean_force":0.56413,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48723,0.15114,0.08492]},{"body_a":"peg","body_b":"channel_base_body","contact_count":296.0,"contact_point_centroid":[0.4963,0.11906,0.00936],"force_p95":0.63675,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56961,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49147,0.17754,0.2148]},{"body_a":"attachment","body_b":"peg","contact_count":24.0,"contact_point_centroid":[0.49478,0.13673,0.05743],"force_p95":1.7496,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.9407,"mean_force":0.93024,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.4912,0.14864,0.03987]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":14.0,"contact_point_centroid":[0.47496,-0.07702,0.02714],"force_p95":1.03153,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.77465,"mean_force":0.59369,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49336,-0.05302,0.05766]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49917,0.19953,0.29646]}],"total_contact_groups":16},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50107,-0.0741,0.03727],"final_tcp_position":[0.49378,-0.05355,0.0709],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":46.82816,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":321.0,"n_steps_budget":1000.0,"object_pos_end":[0.49605,0.11912,0.03383],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19926,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.49272,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":320.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_high","tcp_end":[0.48554,0.15477,0.13883],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11139,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":719.0,"n_steps_budget":1000.0,"object_pos_end":[0.49598,0.11865,0.0344],"object_pos_start":[0.49605,0.11912,0.03383],"object_to_goal_dist_end":0.19877,"object_to_goal_dist_start":0.19926,"object_z_max":0.03439,"peak_contact_force":0.02548,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":743.0,"raw_peak_contact_force":2.33471,"subtask_id":"descend_to_contact","tcp_end":[0.49157,0.14843,0.03584],"tcp_start":[0.48554,0.15477,0.13883],"tcp_to_object_dist_end":0.03013,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":783.0,"n_steps_budget":930.0,"object_pos_end":[0.50309,0.08211,0.03591],"object_pos_start":[0.49598,0.11865,0.0344],"object_to_goal_dist_end":0.16219,"object_to_goal_dist_start":0.19877,"object_z_max":0.03596,"peak_contact_force":2.00215,"phase_name":"align_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1413.0,"raw_peak_contact_force":4.61158,"subtask_id":"align_at_channel","tcp_end":[0.49188,0.11032,0.02989],"tcp_start":[0.49157,0.14843,0.03584],"tcp_to_object_dist_end":0.03095,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":446.0,"n_steps_budget":1000.0,"object_pos_end":[0.50632,-0.08209,0.03533],"object_pos_start":[0.50309,0.08211,0.03591],"object_to_goal_dist_end":0.00813,"object_to_goal_dist_start":0.16219,"object_z_max":0.03725,"peak_contact_force":1.29733,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":815.0,"raw_peak_contact_force":46.82816,"subtask_id":"push_through_channel","tcp_end":[0.49745,-0.05419,0.03012],"tcp_start":[0.49748,-0.05405,0.03016],"tcp_to_object_dist_end":0.02973,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":444.0,"n_steps_budget":600.0,"object_pos_end":[0.50107,-0.0741,0.03727],"object_pos_start":[0.50625,-0.08226,0.03533],"object_to_goal_dist_end":0.00659,"object_to_goal_dist_start":0.00813,"object_z_max":0.04946,"peak_contact_force":1.59797,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1059.0,"raw_peak_contact_force":25.72204,"tcp_end":[0.49378,-0.05355,0.0709],"tcp_start":[0.49745,-0.05419,0.03012],"tcp_to_object_dist_end":0.04008,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```