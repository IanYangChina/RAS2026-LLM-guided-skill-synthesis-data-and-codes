## Search State

- **Seed**: 8
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → align → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | 0.0248 | 0.13 | ❌ rejected |
| 2 | approach → align → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | 0.0015 | 0.18 | ✅ accepted |
| 1 | approach → align → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.1407 | 0.16 | ✅ accepted |
| 0 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | 0.2633 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.13 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.48615778212844485, 0.11898214746703403, 0.04]
- Frozen task target: [0.48615778212844485, -0.04101785253296597, 0.04]
- Goal object position: (0.48615778212844485, -0.04101785253296597, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48615778212844485, 0.11898214746703403, 0.04)
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
  frozen_object_start: [0.4862, 0.119, 0.04]
  frozen_task_target: [0.4862, -0.041, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48615778212844485, 0.11898214746703403, 0.04]}
  frozen_targets: {'channel_exit': [0.48615778212844485, -0.04101785253296597, 0.04]}
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
| `object` | offset from object initial position (0.48615778212844485, 0.11898214746703403, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48615778212844485, -0.04101785253296597, 0.04) | final destination targets |
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

## Current Skill (Q=0.025) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.12
  weight: 0.2
- id: contact_peg
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.0
  weight: 0.2
- id: push_goal
  metric: goal_progress
  weight: 0.6
phases:
- id: approach_peg
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_peg
- id: align_behind
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.07
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact_peg
- id: descend_contact
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
    - 0.02
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 1.0
      - 8.0
      default: 4.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_check
    when: after_phase
    predicate: contact_detected
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: contact_peg
- id: push_peg
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - -0.02
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
      - 0.18
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_max_time:
      type: scalar
      range:
      - 5.0
      - 15.0
      default: 10.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
    push_z_offset:
      type: scalar
      range:
      - -0.04
      - 0.02
      default: -0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    retry_x_offset:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.005
      binds_to:
      - path: retry.offset.x
        mode: replace
  guards:
  - id: force_limit
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
  subtask_id: push_goal
- id: retract_lift
  type: retract
  generator: arc_cartesian
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
    retract_speed:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **align_behind** (`align`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.07], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **descend_contact** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_check, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **push_peg** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, -0.02], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_max_time: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_z_offset: status=consumed; consumers=target.offset.z (replace)
    - retry_x_offset: status=consumed; consumers=retry.offset.x (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **retract_lift** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.025
- **task_score** (E): 0.128
- **fitness_score**: 0.365  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.590

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1523 |
| align_behind | 1.00 | 1.00 | 0.0718 |
| descend_contact | 1.00 | 1.00 | 0.0460 |
| push_peg | 1.00 | 1.00 | 0.1242 |
| retract_lift | 1.00 | 1.00 | 0.0886 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.514, 0.134, 0.168) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.533 | 3.526 |
| align_behind | align | 1.00 / step_budget | (0.514, 0.134, 0.168)→(0.501, 0.103, 0.106) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.570 | 0.592 |
| descend_contact | descend | 1.00 / force_exceeded | (0.501, 0.103, 0.106)→(0.498, 0.100, 0.060) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 18.981 | 18.981 |
| push_peg | push | 1.00 / time_limit | (0.498, 0.100, 0.060)→(0.495, -0.024, 0.067) | (0.503, 0.080, 0.034)→(0.497, 0.015, 0.029) | 0.160→0.097 | 1.00 / 1.333 | 5.256 | 39.725 |
| retract_lift | retract | 1.00 / step_budget | (0.495, -0.024, 0.067)→(0.492, -0.021, 0.156) | (0.497, 0.015, 0.029)→(0.495, 0.018, 0.027) | 0.097→0.100 | 1.00 / 1.000 | 0.536 | 15.102 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.466
- alignment_error: None
- force_efficiency: 0.203
- terminal_score: 0.106
- phase_score: 0.568
- phase_breakdown.push_goal_score: 0.506
- phase_breakdown.approach_peg_score: 0.819
- phase_breakdown.contact_peg_score: 0.503

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.383
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.201
- **Median Q (composite search score)**: 0.033
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.310


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
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63393,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_speed":0.21021,"approach_peg.approach_speed":0.33704,"descend_contact.contact_force_threshold":7.03474,"descend_contact.descend_speed":0.06804,"push_peg.push_distance":0.15708,"push_peg.push_max_time":11.79514,"push_peg.push_speed":0.05234,"push_peg.push_z_offset":0.00708,"push_peg.retry_x_offset":0.00624,"retract_lift.retract_speed":0.28672},"optimized_scores":{"best_composite_score":-0.00174,"best_fitness_score":0.33826,"best_task_score":0.20104},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.498,0.08551,0.0095],"force_p95":37.25023,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.671,"mean_force":27.41056,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.48875,0.09628,0.06034]},{"body_a":"attachment","body_b":"peg","contact_count":1000.0,"contact_point_centroid":[0.49936,0.09904,0.05911],"force_p95":36.79221,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.30064,"mean_force":26.94176,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.48875,0.09628,0.06034]},{"body_a":"peg","body_b":"channel_base_body","contact_count":523.0,"contact_point_centroid":[0.49403,0.08168,0.00946],"force_p95":0.76488,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.23963,"mean_force":0.65795,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.48519,0.05885,0.1046]},{"body_a":"attachment","body_b":"peg","contact_count":15.0,"contact_point_centroid":[0.49307,0.06306,0.06119],"force_p95":19.33364,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.86208,"mean_force":4.24703,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.48769,0.05244,0.06188]},{"body_a":"peg","body_b":"channel_base_body","contact_count":242.0,"contact_point_centroid":[0.49614,0.1191,0.00942],"force_p95":0.61729,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.13576,"mean_force":0.59354,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.49009,0.14018,0.08206]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50192,0.13603,0.05911],"force_p95":12.69321,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.69321,"mean_force":12.69321,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.49051,0.13926,0.06085]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":59.0,"contact_point_centroid":[0.47487,0.08018,0.05959],"force_p95":1.56643,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.85296,"mean_force":0.39607,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.48557,0.0571,0.07564]},{"body_a":"peg","body_b":"channel_base_body","contact_count":354.0,"contact_point_centroid":[0.49635,0.11906,0.00942],"force_p95":0.62581,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56103,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49135,0.19431,0.22846]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49949,0.19988,0.29729]},{"body_a":"peg","body_b":"channel_base_body","contact_count":413.0,"contact_point_centroid":[0.49594,0.1192,0.00944],"force_p95":0.61011,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65775,"mean_force":0.54107,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.48712,0.15804,0.13433]}],"total_contact_groups":10},"final_pose_error":0.01183,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49333,0.08313,0.03388],"final_tcp_position":[0.4852,0.05444,0.15026],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":39.671,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":379.0,"n_steps_budget":600.0,"object_pos_end":[0.49603,0.11945,0.03396],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19958,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50578,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":378.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_peg","tcp_end":[0.48475,0.17515,0.16755],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14517,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":413.0,"n_steps_budget":600.0,"object_pos_end":[0.49609,0.11909,0.03381],"object_pos_start":[0.49603,0.11945,0.03396],"object_to_goal_dist_end":0.19923,"object_to_goal_dist_start":0.19958,"object_z_max":0.03414,"peak_contact_force":0.61704,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":413.0,"raw_peak_contact_force":0.65775,"subtask_id":"contact_peg","tcp_end":[0.49168,0.14165,0.10473],"tcp_start":[0.48475,0.17515,0.16755],"tcp_to_object_dist_end":0.07455,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":242.0,"n_steps_budget":660.0,"object_pos_end":[0.49602,0.11902,0.03419],"object_pos_start":[0.49609,0.11909,0.03381],"object_to_goal_dist_end":0.19914,"object_to_goal_dist_start":0.19923,"object_z_max":0.03419,"peak_contact_force":13.13576,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":243.0,"raw_peak_contact_force":13.13576,"subtask_id":"contact_peg","tcp_end":[0.49052,0.13925,0.0607],"tcp_start":[0.49168,0.14165,0.10473],"tcp_to_object_dist_end":0.0338,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49348,0.07436,0.03873],"object_pos_start":[0.49602,0.11902,0.03419],"object_to_goal_dist_end":0.1545,"object_to_goal_dist_start":0.19914,"object_z_max":0.03871,"peak_contact_force":14.49487,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2000.0,"raw_peak_contact_force":39.671,"subtask_id":"push_goal","tcp_end":[0.48817,0.05248,0.06154],"tcp_start":[0.49052,0.13925,0.0607],"tcp_to_object_dist_end":0.03205,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":524.0,"n_steps_budget":600.0,"object_pos_end":[0.49333,0.08313,0.03388],"object_pos_start":[0.49348,0.07436,0.03873],"object_to_goal_dist_end":0.16339,"object_to_goal_dist_start":0.1545,"object_z_max":0.03891,"peak_contact_force":0.55193,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":597.0,"raw_peak_contact_force":36.23963,"tcp_end":[0.4852,0.05444,0.15026],"tcp_start":[0.48817,0.05248,0.06154],"tcp_to_object_dist_end":0.12014,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82456,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_speed":0.24147,"approach_peg.approach_speed":0.3483,"descend_contact.contact_force_threshold":4.10585,"descend_contact.descend_speed":0.04486,"push_peg.push_distance":0.14964,"push_peg.push_max_time":11.31923,"push_peg.push_speed":0.10612,"push_peg.push_z_offset":0.01521,"push_peg.retry_x_offset":-0.00017,"retract_lift.retract_speed":0.2518},"optimized_scores":{"best_composite_score":0.0432,"best_fitness_score":0.3832,"best_task_score":0.10569},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":839.0,"contact_point_centroid":[0.50497,0.01819,0.00936],"force_p95":34.52683,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.85405,"mean_force":14.64241,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.4994,0.01494,0.06409]},{"body_a":"attachment","body_b":"peg","contact_count":523.0,"contact_point_centroid":[0.50918,0.04714,0.06097],"force_p95":35.99792,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.44733,"mean_force":22.69293,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.50004,0.04267,0.06206]},{"body_a":"peg","body_b":"channel_base_body","contact_count":262.0,"contact_point_centroid":[0.50609,0.06306,0.00938],"force_p95":0.55153,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.24774,"mean_force":0.64467,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50243,0.08506,0.08311]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51298,0.07964,0.05874],"force_p95":25.69544,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.69544,"mean_force":25.69544,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50192,0.08393,0.06049]},{"body_a":"peg","body_b":"channel_base_body","contact_count":524.0,"contact_point_centroid":[0.49645,-0.0108,0.00809],"force_p95":0.71581,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.36823,"mean_force":0.64593,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49526,-0.05155,0.1129]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.475,-0.03494,0.02422],"force_p95":7.99013,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.01875,"mean_force":3.57489,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49517,-0.05137,0.14218]},{"body_a":"peg","body_b":"channel_base_body","contact_count":442.0,"contact_point_centroid":[0.50572,0.06293,0.00935],"force_p95":0.58023,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57717,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5148,0.14953,0.23653]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50049,0.19661,0.29674]},{"body_a":"peg","body_b":"channel_base_body","contact_count":314.0,"contact_point_centroid":[0.50584,0.06309,0.00938],"force_p95":0.5514,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54658,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.51471,0.10163,0.13725]}],"total_contact_groups":9},"final_pose_error":0.01217,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49495,-0.0116,0.02404],"final_tcp_position":[0.4953,-0.05594,0.15862],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":39.85405,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":470.0,"n_steps_budget":600.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54685,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":476.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach_peg","tcp_end":[0.52558,0.11588,0.16864],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14617,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":314.0,"n_steps_budget":600.0,"object_pos_end":[0.50601,0.06303,0.0338],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14323,"object_z_max":0.03381,"peak_contact_force":0.55058,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":314.0,"raw_peak_contact_force":0.55501,"subtask_id":"contact_peg","tcp_end":[0.50509,0.08656,0.10711],"tcp_start":[0.52558,0.11588,0.16864],"tcp_to_object_dist_end":0.07699,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.50605,0.06299,0.03381],"object_pos_start":[0.50601,0.06303,0.0338],"object_to_goal_dist_end":0.14325,"object_to_goal_dist_start":0.14329,"object_z_max":0.03381,"peak_contact_force":26.24774,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":263.0,"raw_peak_contact_force":26.24774,"subtask_id":"contact_peg","tcp_end":[0.50193,0.08392,0.06033],"tcp_start":[0.50509,0.08656,0.10711],"tcp_to_object_dist_end":0.03404,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":847.0,"n_steps_budget":900.0,"object_pos_end":[0.49873,-0.0111,0.02413],"object_pos_start":[0.50605,0.06299,0.03381],"object_to_goal_dist_end":0.07072,"object_to_goal_dist_start":0.14325,"object_z_max":0.04078,"peak_contact_force":0.7316,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1362.0,"raw_peak_contact_force":39.85405,"subtask_id":"push_goal","tcp_end":[0.49828,-0.05851,0.07014],"tcp_start":[0.50193,0.08392,0.06033],"tcp_to_object_dist_end":0.06607,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":524.0,"n_steps_budget":600.0,"object_pos_end":[0.49495,-0.0116,0.02404],"object_pos_start":[0.49873,-0.0111,0.02413],"object_to_goal_dist_end":0.07042,"object_to_goal_dist_start":0.07072,"object_z_max":0.02484,"peak_contact_force":0.46703,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":531.0,"raw_peak_contact_force":8.36823,"tcp_end":[0.4953,-0.05594,0.15862],"tcp_start":[0.49828,-0.05851,0.07014],"tcp_to_object_dist_end":0.1417,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.07558,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_speed":0.1015,"approach_peg.approach_speed":0.32543,"descend_contact.contact_force_threshold":4.0341,"descend_contact.descend_speed":0.01035,"push_peg.push_distance":0.14993,"push_peg.push_max_time":13.97694,"push_peg.push_speed":0.10568,"push_peg.push_z_offset":0.01527,"push_peg.retry_x_offset":0.00146,"retract_lift.retract_speed":0.29882},"optimized_scores":{"best_composite_score":0.03295,"best_fitness_score":0.37295,"best_task_score":0.0771},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":838.0,"contact_point_centroid":[0.50529,0.01198,0.00935],"force_p95":33.36776,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.64855,"mean_force":14.38435,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49983,0.00841,0.06418]},{"body_a":"attachment","body_b":"peg","contact_count":521.0,"contact_point_centroid":[0.50955,0.04084,0.06105],"force_p95":34.99492,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.23559,"mean_force":22.33579,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.50047,0.03628,0.06213]},{"body_a":"peg","body_b":"channel_base_body","contact_count":283.0,"contact_point_centroid":[0.50597,0.05663,0.00938],"force_p95":0.55244,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.55836,"mean_force":0.60683,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50309,0.07877,0.08326]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51335,0.07313,0.05877],"force_p95":17.04987,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.04987,"mean_force":17.04987,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50236,0.0776,0.06055]},{"body_a":"peg","body_b":"channel_base_body","contact_count":460.0,"contact_point_centroid":[0.50586,0.05661,0.00935],"force_p95":0.60397,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.58114,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51847,0.1465,0.23675]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50078,0.19617,0.29647]},{"body_a":"peg","body_b":"channel_base_body","contact_count":524.0,"contact_point_centroid":[0.49749,-0.01693,0.00805],"force_p95":0.69709,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69714,"mean_force":0.60599,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49569,-0.05807,0.11299]},{"body_a":"peg","body_b":"channel_base_body","contact_count":313.0,"contact_point_centroid":[0.50613,0.05657,0.00938],"force_p95":0.55456,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56198,"mean_force":0.54668,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.51858,0.09555,0.13697]}],"total_contact_groups":8},"final_pose_error":0.0122,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49577,-0.01692,0.02414],"final_tcp_position":[0.49574,-0.06247,0.1587],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":39.64855,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":489.0,"n_steps_budget":600.0,"object_pos_end":[0.50612,0.05659,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54749,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":497.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach_peg","tcp_end":[0.53207,0.10995,0.1682],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14693,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":313.0,"n_steps_budget":600.0,"object_pos_end":[0.5061,0.05659,0.03379],"object_pos_start":[0.50612,0.05659,0.03378],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.13687,"object_z_max":0.03379,"peak_contact_force":0.54207,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":313.0,"raw_peak_contact_force":0.56198,"subtask_id":"contact_peg","tcp_end":[0.50606,0.08027,0.10701],"tcp_start":[0.53207,0.10995,0.1682],"tcp_to_object_dist_end":0.07695,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":283.0,"n_steps_budget":1000.0,"object_pos_end":[0.50612,0.05665,0.03379],"object_pos_start":[0.5061,0.05659,0.03379],"object_to_goal_dist_end":0.13693,"object_to_goal_dist_start":0.13687,"object_z_max":0.03379,"peak_contact_force":17.55836,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":284.0,"raw_peak_contact_force":17.55836,"subtask_id":"contact_peg","tcp_end":[0.50237,0.07759,0.06041],"tcp_start":[0.50606,0.08027,0.10701],"tcp_to_object_dist_end":0.03407,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":846.0,"n_steps_budget":900.0,"object_pos_end":[0.4994,-0.01711,0.02414],"object_pos_start":[0.50612,0.05665,0.03379],"object_to_goal_dist_end":0.06486,"object_to_goal_dist_start":0.13693,"object_z_max":0.04078,"peak_contact_force":0.54242,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1359.0,"raw_peak_contact_force":39.64855,"subtask_id":"push_goal","tcp_end":[0.49871,-0.06508,0.07025],"tcp_start":[0.50237,0.07759,0.06041],"tcp_to_object_dist_end":0.06654,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":524.0,"n_steps_budget":600.0,"object_pos_end":[0.49577,-0.01692,0.02414],"object_pos_start":[0.4994,-0.01711,0.02414],"object_to_goal_dist_end":0.06518,"object_to_goal_dist_start":0.06486,"object_z_max":0.02414,"peak_contact_force":0.58799,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":524.0,"raw_peak_contact_force":0.69714,"tcp_end":[0.49574,-0.06247,0.1587],"tcp_start":[0.49871,-0.06508,0.07025],"tcp_to_object_dist_end":0.14206,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```