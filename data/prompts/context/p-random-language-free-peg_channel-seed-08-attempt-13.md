## Search State

- **Seed**: 8
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → align → push → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.0042 | 0.20 | ❌ rejected |
| 12 | approach → align → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | 0.0186 | 0.12 | ❌ rejected |
| 11 | approach → align → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | -0.2398 | 0.06 | ❌ rejected |
| 10 | approach → align → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.4041 | 0.02 | ❌ rejected |
| 9 | approach → align → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | 0.2119 | 0.37 | ✅ accepted |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.004) — your mutation base

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
  weight: 0.15
- id: contact_peg
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.0
  weight: 0.25
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
    tolerance: 0.015
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
    - 0.03
    - 0.02
    tolerance: 0.01
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
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 10.0
      - 30.0
      default: 18.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
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
    - -0.01
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
      - 0.14
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_max_time:
      type: scalar
      range:
      - 8.0
      - 20.0
      default: 14.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    push_z_offset:
      type: scalar
      range:
      - -0.025
      - 0.01
      default: -0.015
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
    retry_y_offset:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: retry.offset.y
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
    tolerance: 0.015
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
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.12], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **align_behind** (`align`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **descend_contact** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_check, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **push_peg** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, -0.01], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_max_time: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_z_offset: status=consumed; consumers=target.offset.z (replace)
    - retry_x_offset: status=consumed; consumers=retry.offset.x (replace)
    - retry_y_offset: status=consumed; consumers=retry.offset.y (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **retract_lift** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.004
- **task_score** (E): 0.195
- **fitness_score**: 0.436  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.640

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1473 |
| align_behind | 1.00 | 1.00 | 0.1342 |
| contact_engage | 1.00 | 1.00 | 0.0151 |
| push_peg | 0.00 | 1.00 | 0.0001 |
| retract_lift | 1.00 | 1.00 | 0.0858 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.514, 0.136, 0.173) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.537 | 3.526 |
| align_behind | align | 1.00 / step_budget | (0.514, 0.136, 0.173)→(0.502, 0.104, 0.044) | (0.503, 0.080, 0.034)→(0.503, 0.064, 0.037) | 0.160→0.144 | 1.00 / 1.667 | 38.517 | 139.020 |
| contact_engage | push | 1.00 / force_exceeded | (0.502, 0.104, 0.044)→(0.500, 0.090, 0.040) | (0.503, 0.064, 0.037)→(0.495, 0.050, 0.026) | 0.144→0.131 | 1.00 / 2.333 | 40.399 | 40.399 |
| push_peg | push | 0.00 / guard_failure | (0.497, 0.023, 0.035)→(0.497, 0.023, 0.035) | (0.495, 0.050, 0.026)→(0.496, -0.010, 0.028) | 0.131→0.076 | 1.00 / 3.000 | 50.003 | 64.987 |
| retract_lift | retract | 1.00 / step_budget | (0.497, 0.023, 0.035)→(0.494, 0.026, 0.121) | (0.496, -0.010, 0.028)→(0.504, 0.001, 0.021) | 0.076→0.090 | 1.00 / 1.000 | 0.571 | 52.915 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.861
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.350
- phase_score: 0.747
- phase_breakdown.contact_peg_score: 0.480
- phase_breakdown.approach_peg_score: 0.743
- phase_breakdown.push_goal_score: 0.860

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.588
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.350
- **Median Q (composite search score)**: 0.099
- **K-run variance**: 0.0331
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 4.7
- **Final σ (mean)**: 0.318


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.23438,"average_solve_count":64.0,"average_success_count":64.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_speed":0.17321,"approach_peg.approach_speed":0.307,"contact_engage.engage_force_threshold":11.75153,"contact_engage.engage_speed":0.02098,"push_peg.push_distance":0.17741,"push_peg.push_max_time":11.43931,"push_peg.push_speed":0.06622,"push_peg.push_z_offset":-0.0014,"push_peg.retry_x_offset":0.00421,"push_peg.retry_y_offset":0.00028,"retract_lift.retract_speed":0.21423},"optimized_scores":{"best_composite_score":-0.25995,"best_fitness_score":0.18005,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":411.0,"contact_point_centroid":[0.49693,0.11911,0.00919],"force_p95":114.90851,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":160.28141,"mean_force":18.8333,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.48799,0.15936,0.10464]},{"body_a":"attachment","body_b":"peg","contact_count":72.0,"contact_point_centroid":[0.50001,0.13744,0.0526],"force_p95":153.57182,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":159.7133,"mean_force":104.72956,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.49305,0.1467,0.0521]},{"body_a":"attachment","body_b":"peg","contact_count":41.0,"contact_point_centroid":[0.49941,0.13882,0.05077],"force_p95":64.2319,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":113.45694,"mean_force":22.29394,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49543,0.14962,0.05]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50019,0.13702,0.04719],"force_p95":106.88713,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":108.79679,"mean_force":96.03433,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49603,0.14748,0.04548]},{"body_a":"peg","body_b":"channel_base_body","contact_count":118.0,"contact_point_centroid":[0.4951,0.11965,0.00914],"force_p95":39.91587,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":105.58196,"mean_force":8.06621,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49428,0.15201,0.05904]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.4814,0.11893,0.00669],"force_p95":102.8531,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":102.8531,"mean_force":102.8531,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"push","tcp_position_centroid":[0.49594,0.14741,0.04549]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50023,0.13699,0.04718],"force_p95":102.00141,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":102.00141,"mean_force":102.00141,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"push","tcp_position_centroid":[0.49594,0.14741,0.04549]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49256,0.11892,0.00672],"force_p95":96.00158,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":97.02973,"mean_force":89.91128,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49603,0.14748,0.04548]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.49755,0.12899,-3e-05],"force_p95":20.97597,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.97597,"mean_force":20.97597,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.49586,0.14739,0.04561]},{"body_a":"peg","body_b":"world","contact_count":3.0,"contact_point_centroid":[0.49763,0.12877,-6e-05],"force_p95":12.36113,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.17024,"mean_force":7.52064,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49603,0.14748,0.04548]},{"body_a":"peg","body_b":"world","contact_count":247.0,"contact_point_centroid":[0.49777,0.15027,-0.00188],"force_p95":0.98379,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.43853,"mean_force":0.71284,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.493,0.15438,0.10208]},{"body_a":"peg","body_b":"channel_base_body","contact_count":260.0,"contact_point_centroid":[0.49662,0.11906,0.00936],"force_p95":0.64827,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.57316,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49177,0.19474,0.23018]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49951,0.19998,0.29653]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.49761,0.12889,-7e-05],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"push","tcp_position_centroid":[0.49594,0.14741,0.04549]}],"total_contact_groups":14},"final_pose_error":0.01493,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4996,0.15104,0.01412],"final_tcp_position":[0.49311,0.14973,0.13107],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":160.28141,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":285.0,"n_steps_budget":600.0,"object_pos_end":[0.49601,0.11914,0.03382],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19928,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50305,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":284.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_peg","tcp_end":[0.48548,0.17734,0.17229],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15057,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":411.0,"n_steps_budget":600.0,"object_pos_end":[0.49781,0.11944,0.02917],"object_pos_start":[0.49601,0.11914,0.03382],"object_to_goal_dist_end":0.19974,"object_to_goal_dist_start":0.19928,"object_z_max":0.03415,"peak_contact_force":114.42841,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":484.0,"raw_peak_contact_force":160.28141,"subtask_id":"contact_peg","tcp_end":[0.49594,0.14741,0.04549],"tcp_start":[0.48548,0.17734,0.17229],"tcp_to_object_dist_end":0.03244,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49779,0.11945,0.02919],"object_pos_start":[0.49781,0.11944,0.02917],"object_to_goal_dist_end":0.19976,"object_to_goal_dist_start":0.19974,"object_z_max":0.02917,"peak_contact_force":102.8531,"phase_name":"contact_engage","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":102.8531,"subtask_id":"contact_peg","tcp_end":[0.49598,0.14744,0.04547],"tcp_start":[0.49594,0.14741,0.04549],"tcp_to_object_dist_end":0.03242,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49777,0.11948,0.02924],"object_pos_start":[0.49779,0.11945,0.02919],"object_to_goal_dist_end":0.19979,"object_to_goal_dist_start":0.19976,"object_z_max":0.0293,"peak_contact_force":108.79679,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":108.79679,"subtask_id":"push_goal","tcp_end":[0.4961,0.1476,0.04553],"tcp_start":[0.49608,0.14753,0.0455],"tcp_to_object_dist_end":0.03254,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":369.0,"n_steps_budget":600.0,"object_pos_end":[0.4996,0.15104,0.01412],"object_pos_start":[0.49772,0.11957,0.02936],"object_to_goal_dist_end":0.23248,"object_to_goal_dist_start":0.19987,"object_z_max":0.03489,"peak_contact_force":0.53279,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":406.0,"raw_peak_contact_force":113.45694,"tcp_end":[0.49311,0.14973,0.13107],"tcp_start":[0.4961,0.1476,0.04553],"tcp_to_object_dist_end":0.11713,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42177,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_speed":0.05249,"approach_peg.approach_speed":0.47567,"contact_engage.engage_force_threshold":6.77515,"contact_engage.engage_speed":0.02954,"push_peg.push_distance":0.16021,"push_peg.push_max_time":13.45607,"push_peg.push_speed":0.08476,"push_peg.push_z_offset":-0.0018,"push_peg.retry_x_offset":-0.00348,"push_peg.retry_y_offset":-0.00037,"retract_lift.retract_speed":0.19169},"optimized_scores":{"best_composite_score":0.14835,"best_fitness_score":0.58835,"best_task_score":0.34984},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":443.0,"contact_point_centroid":[0.50645,0.06214,0.00937],"force_p95":56.65671,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":118.17946,"mean_force":5.85263,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.51394,0.10169,0.10721]},{"body_a":"attachment","body_b":"peg","contact_count":31.0,"contact_point_centroid":[0.51208,0.07897,0.05679],"force_p95":114.69482,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":117.70611,"mean_force":76.10082,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.50713,0.08929,0.05669]},{"body_a":"attachment","body_b":"peg","contact_count":579.0,"contact_point_centroid":[0.49646,-0.00579,0.03209],"force_p95":5.74513,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.00564,"mean_force":2.03532,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49744,0.00611,0.03199]},{"body_a":"peg","body_b":"channel_base_body","contact_count":26.0,"contact_point_centroid":[0.51116,-0.10037,0.02787],"force_p95":35.8089,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.21128,"mean_force":22.37654,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49731,-0.03804,0.03132]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.49753,-0.05041,0.04038],"force_p95":17.69645,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.35316,"mean_force":4.05701,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.4965,-0.03866,0.03151]},{"body_a":"peg","body_b":"channel_base_body","contact_count":29.0,"contact_point_centroid":[0.49642,-0.10022,0.02965],"force_p95":12.36324,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.76404,"mean_force":1.93607,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49592,-0.03792,0.03312]},{"body_a":"peg","body_b":"channel_base_body","contact_count":352.0,"contact_point_centroid":[0.50095,-0.07427,0.00823],"force_p95":0.70355,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.71672,"mean_force":0.80321,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49402,-0.03177,0.07564]},{"body_a":"peg","body_b":"channel_base_body","contact_count":721.0,"contact_point_centroid":[0.49479,-0.03014,0.00967],"force_p95":2.00304,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.87031,"mean_force":0.98915,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49761,0.01068,0.03224]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52503,-0.09251,0.02423],"force_p95":9.39977,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.42936,"mean_force":2.80892,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49384,-0.03221,0.1037]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":77.0,"contact_point_centroid":[0.47499,-0.0462,0.02731],"force_p95":5.92658,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.15863,"mean_force":3.10981,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.4977,0.0144,0.0324]},{"body_a":"peg","body_b":"channel_base_body","contact_count":465.0,"contact_point_centroid":[0.49899,0.01915,0.00802],"force_p95":0.81731,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.82934,"mean_force":0.637,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"push","tcp_position_centroid":[0.50154,0.07137,0.03804]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,-0.00535,0.02385],"force_p95":8.46098,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.46098,"mean_force":8.46098,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"push","tcp_position_centroid":[0.50123,0.05994,0.03708]},{"body_a":"peg","body_b":"channel_base_body","contact_count":321.0,"contact_point_centroid":[0.50565,0.06294,0.00934],"force_p95":0.60722,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.58869,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51486,0.15017,0.23763]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":17.0,"contact_point_centroid":[0.47487,-0.05008,0.02761],"force_p95":3.25155,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.26749,"mean_force":1.62477,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49526,-0.03678,0.03571]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50074,0.19608,0.29625]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52501,0.04681,0.06],"force_p95":0.79736,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.80535,"mean_force":0.72547,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.50706,0.08809,0.05124]}],"total_contact_groups":16},"final_pose_error":0.01484,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5066,-0.07488,0.02418],"final_tcp_position":[0.49401,-0.03578,0.11701],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":118.17946,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":349.0,"n_steps_budget":600.0,"object_pos_end":[0.50595,0.06295,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54461,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":355.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach_peg","tcp_end":[0.52529,0.11756,0.17343],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15117,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":448.0,"n_steps_budget":1000.0,"object_pos_end":[0.50519,0.0406,0.0405],"object_pos_start":[0.50595,0.06295,0.0338],"object_to_goal_dist_end":0.12071,"object_to_goal_dist_start":0.14321,"object_z_max":0.0408,"peak_contact_force":0.42597,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":476.0,"raw_peak_contact_force":118.17946,"subtask_id":"contact_peg","tcp_end":[0.50516,0.08598,0.04319],"tcp_start":[0.52529,0.11756,0.17343],"tcp_to_object_dist_end":0.04546,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":476.0,"n_steps_budget":1000.0,"object_pos_end":[0.49472,0.01829,0.02401],"object_pos_start":[0.50519,0.0406,0.0405],"object_to_goal_dist_end":0.09973,"object_to_goal_dist_start":0.12071,"object_z_max":0.0405,"peak_contact_force":8.82934,"phase_name":"contact_engage","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":466.0,"raw_peak_contact_force":8.82934,"subtask_id":"contact_peg","tcp_end":[0.50123,0.05988,0.03708],"tcp_start":[0.50516,0.08598,0.04319],"tcp_to_object_dist_end":0.04408,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":727.0,"n_steps_budget":1000.0,"object_pos_end":[0.49502,-0.07484,0.028],"object_pos_start":[0.49472,0.01829,0.02401],"object_to_goal_dist_end":0.01398,"object_to_goal_dist_start":0.09973,"object_z_max":0.02806,"peak_contact_force":14.04262,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1403.0,"raw_peak_contact_force":42.00564,"subtask_id":"push_goal","tcp_end":[0.49719,-0.03896,0.03116],"tcp_start":[0.49723,-0.03894,0.03121],"tcp_to_object_dist_end":0.03608,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":371.0,"n_steps_budget":600.0,"object_pos_end":[0.5066,-0.07488,0.02418],"object_pos_start":[0.49496,-0.07493,0.02794],"object_to_goal_dist_end":0.01789,"object_to_goal_dist_start":0.01402,"object_z_max":0.02906,"peak_contact_force":0.54691,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":419.0,"raw_peak_contact_force":18.35316,"tcp_end":[0.49401,-0.03578,0.11701],"tcp_start":[0.49719,-0.03896,0.03116],"tcp_to_object_dist_end":0.10152,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56098,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_speed":0.1354,"approach_peg.approach_speed":0.49925,"contact_engage.engage_force_threshold":6.91763,"contact_engage.engage_speed":0.01479,"push_peg.push_distance":0.17587,"push_peg.push_max_time":14.96095,"push_peg.push_speed":0.07449,"push_peg.push_z_offset":-0.00616,"push_peg.retry_x_offset":0.00267,"push_peg.retry_y_offset":0.00035,"retract_lift.retract_speed":0.30357},"optimized_scores":{"best_composite_score":0.09914,"best_fitness_score":0.53914,"best_task_score":0.23554},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":390.0,"contact_point_centroid":[0.50656,0.05583,0.00934],"force_p95":47.67867,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":138.59993,"mean_force":5.48308,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.51782,0.09587,0.10763]},{"body_a":"attachment","body_b":"peg","contact_count":27.0,"contact_point_centroid":[0.51229,0.07239,0.05666],"force_p95":135.83929,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":138.24911,"mean_force":71.61348,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.50843,0.0831,0.05645]},{"body_a":"attachment","body_b":"peg","contact_count":646.0,"contact_point_centroid":[0.49733,-0.01017,0.03115],"force_p95":25.88661,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.15957,"mean_force":3.22556,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49829,0.00172,0.03057]},{"body_a":"peg","body_b":"channel_base_body","contact_count":51.0,"contact_point_centroid":[0.5112,-0.10042,0.02737],"force_p95":37.48718,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.50193,"mean_force":27.51109,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.4983,-0.03807,0.02908]},{"body_a":"attachment","body_b":"peg","contact_count":31.0,"contact_point_centroid":[0.49658,-0.04947,0.03333],"force_p95":12.98255,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.93551,"mean_force":2.48349,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49683,-0.03773,0.03222]},{"body_a":"peg","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.50689,-0.10038,0.03628],"force_p95":14.89697,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.77115,"mean_force":2.46397,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49705,-0.03828,0.03081]},{"body_a":"peg","body_b":"channel_base_body","contact_count":871.0,"contact_point_centroid":[0.49474,-0.03013,0.00945],"force_p95":4.52983,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.28005,"mean_force":1.15692,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.4985,0.01067,0.03112]},{"body_a":"peg","body_b":"channel_base_body","contact_count":350.0,"contact_point_centroid":[0.50039,-0.07375,0.0083],"force_p95":0.73751,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.45943,"mean_force":0.73872,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49506,-0.03213,0.07346]},{"body_a":"peg","body_b":"channel_base_body","contact_count":501.0,"contact_point_centroid":[0.49968,0.01184,0.00814],"force_p95":0.79775,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.51341,"mean_force":0.63738,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"push","tcp_position_centroid":[0.50238,0.06943,0.03803]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52503,-0.04773,0.02426],"force_p95":7.15031,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.38149,"mean_force":1.8659,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49495,-0.03299,0.10315]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,-0.01339,0.02407],"force_p95":9.10841,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.10841,"mean_force":9.10841,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"push","tcp_position_centroid":[0.50219,0.06293,0.03732]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":107.0,"contact_point_centroid":[0.47498,-0.04898,0.0271],"force_p95":5.43734,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.21721,"mean_force":3.22342,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49845,0.01191,0.03112]},{"body_a":"peg","body_b":"channel_base_body","contact_count":333.0,"contact_point_centroid":[0.50571,0.05662,0.00934],"force_p95":0.60211,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.59432,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51849,0.14716,0.2378]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47495,-0.09731,0.02667],"force_p95":4.00168,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.07378,"mean_force":1.48429,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49554,-0.0346,0.04053]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50109,0.19558,0.29595]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,0.01476,0.05726],"force_p95":0.91528,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.91528,"mean_force":0.91528,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.50605,0.07993,0.04364]}],"total_contact_groups":16},"final_pose_error":0.01498,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50684,-0.07259,0.02419],"final_tcp_position":[0.49504,-0.03614,0.11459],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":138.59993,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":362.0,"n_steps_budget":600.0,"object_pos_end":[0.50613,0.0566,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.56351,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":370.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach_peg","tcp_end":[0.53164,0.11177,0.17294],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":397.0,"n_steps_budget":690.0,"object_pos_end":[0.50673,0.03165,0.0399],"object_pos_start":[0.50613,0.0566,0.03378],"object_to_goal_dist_end":0.11185,"object_to_goal_dist_start":0.13688,"object_z_max":0.04082,"peak_contact_force":0.69626,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":418.0,"raw_peak_contact_force":138.59993,"subtask_id":"contact_peg","tcp_end":[0.50588,0.07977,0.04306],"tcp_start":[0.53164,0.11177,0.17294],"tcp_to_object_dist_end":0.04823,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":511.0,"n_steps_budget":1000.0,"object_pos_end":[0.49313,0.01149,0.02413],"object_pos_start":[0.50673,0.03165,0.0399],"object_to_goal_dist_end":0.09311,"object_to_goal_dist_start":0.11185,"object_z_max":0.0399,"peak_contact_force":9.51341,"phase_name":"contact_engage","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":502.0,"raw_peak_contact_force":9.51341,"subtask_id":"contact_peg","tcp_end":[0.5022,0.0629,0.03732],"tcp_start":[0.50588,0.07977,0.04306],"tcp_to_object_dist_end":0.05384,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":874.0,"n_steps_budget":1000.0,"object_pos_end":[0.49562,-0.07492,0.02786],"object_pos_start":[0.49313,0.01149,0.02413],"object_to_goal_dist_end":0.01387,"object_to_goal_dist_start":0.09311,"object_z_max":0.02805,"peak_contact_force":27.16986,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1675.0,"raw_peak_contact_force":44.15957,"subtask_id":"push_goal","tcp_end":[0.49824,-0.03936,0.02886],"tcp_start":[0.49827,-0.03936,0.0289],"tcp_to_object_dist_end":0.03568,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":370.0,"n_steps_budget":600.0,"object_pos_end":[0.50684,-0.07259,0.02419],"object_pos_start":[0.49558,-0.07497,0.02785],"object_to_goal_dist_end":0.01876,"object_to_goal_dist_start":0.01387,"object_z_max":0.02975,"peak_contact_force":0.63391,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":424.0,"raw_peak_contact_force":26.93551,"tcp_end":[0.49504,-0.03614,0.11459],"tcp_start":[0.49824,-0.03936,0.02886],"tcp_to_object_dist_end":0.09818,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```