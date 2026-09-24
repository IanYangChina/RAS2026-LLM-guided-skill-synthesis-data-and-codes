## Search State

- **Seed**: 8
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → align → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | 0.2119 | 0.37 | ❌ rejected |
| 8 | approach → align → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.2465 | 0.14 | ❌ rejected |
| 7 | approach → align → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0535 | 0.34 | ❌ rejected |
| 6 | approach → align → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2383 | 0.26 | ❌ rejected |
| 5 | approach → align → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.2766 | 0.01 | ❌ rejected |

**Proposal policy**: task_score is 0.37 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.212) — your mutation base

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

- **Composite score**: 0.212
- **task_score** (E): 0.372
- **fitness_score**: 0.602  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.640

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1473 |
| align_behind | 1.00 | 1.00 | 0.1141 |
| descend_contact | 1.00 | 1.00 | 0.0278 |
| push_peg | 0.67 | 1.00 | 0.0836 |
| retract_lift | 1.00 | 1.00 | 0.0859 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.514, 0.136, 0.173) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.537 | 3.526 |
| align_behind | align | 1.00 / step_budget | (0.514, 0.136, 0.173)→(0.501, 0.112, 0.063) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.537 | 0.602 |
| descend_contact | descend | 1.00 / force_exceeded | (0.501, 0.112, 0.063)→(0.499, 0.093, 0.042) | (0.503, 0.080, 0.034)→(0.507, 0.065, 0.036) | 0.160→0.146 | 1.00 / 2.667 | 1397.425 | 10.855 |
| push_peg | push | 0.67 / time_limit | (0.498, 0.071, 0.040)→(0.495, -0.013, 0.036) | (0.507, 0.065, 0.036)→(0.506, -0.015, 0.032) | 0.146→0.069 | 1.00 / 3.333 | 34.783 | 41.535 |
| retract_lift | retract | 1.00 / step_budget | (0.495, -0.013, 0.036)→(0.492, -0.010, 0.122) | (0.506, -0.015, 0.032)→(0.506, -0.014, 0.031) | 0.069→0.070 | 1.00 / 1.000 | 0.571 | 102.022 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.887
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.365
- phase_score: 0.804
- phase_breakdown.push_goal_score: 0.937
- phase_breakdown.approach_peg_score: 0.743
- phase_breakdown.contact_peg_score: 0.521

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.628
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.504
- **Median Q (composite search score)**: 0.216
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.317


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_speed":0.13186,"approach_peg.approach_speed":0.45713,"descend_contact.contact_force_threshold":16.54373,"descend_contact.descend_speed":0.04588,"push_peg.push_distance":0.16067,"push_peg.push_max_time":14.15211,"push_peg.push_speed":0.07998,"push_peg.push_z_offset":-0.00643,"push_peg.retry_x_offset":-0.00055,"push_peg.retry_y_offset":0.00531,"retract_lift.retract_speed":0.26654},"optimized_scores":{"best_composite_score":0.21641,"best_fitness_score":0.60641,"best_task_score":0.50358},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":81.0,"contact_point_centroid":[0.47499,0.05803,0.04492],"force_p95":259.81402,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":270.88637,"mean_force":119.71036,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.4868,0.05803,0.04287]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.525,0.05796,0.05998],"force_p95":66.46304,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.22761,"mean_force":48.05264,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.48805,0.05316,0.02515]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.525,0.0582,0.05999],"force_p95":69.0321,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.0568,"mean_force":64.1215,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.48806,0.05336,0.02517]},{"body_a":"peg","body_b":"channel_base_body","contact_count":539.0,"contact_point_centroid":[0.50965,0.04772,0.00987],"force_p95":23.03707,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.48317,"mean_force":15.24766,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.48817,0.08705,0.02652]},{"body_a":"peg","body_b":"link7","contact_count":473.0,"contact_point_centroid":[0.52048,0.0686,0.0617],"force_p95":17.57104,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.24054,"mean_force":12.11059,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.48794,0.08286,0.02613]},{"body_a":"attachment","body_b":"peg","contact_count":541.0,"contact_point_centroid":[0.49808,0.07706,0.04954],"force_p95":27.37616,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.06759,"mean_force":16.66594,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.48815,0.08709,0.0265]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":530.0,"contact_point_centroid":[0.52507,0.06114,0.05461],"force_p95":15.35722,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.91063,"mean_force":9.93793,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.48819,0.08697,0.02654]},{"body_a":"attachment","body_b":"peg","contact_count":298.0,"contact_point_centroid":[0.49577,0.12121,0.05044],"force_p95":8.66161,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.73131,"mean_force":5.19633,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.49038,0.13247,0.04189]},{"body_a":"attachment","body_b":"peg","contact_count":26.0,"contact_point_centroid":[0.49733,0.04388,0.06025],"force_p95":6.68805,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.37178,"mean_force":1.28337,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.48721,0.05468,0.02983]},{"body_a":"peg","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.52033,0.03885,0.06101],"force_p95":11.53541,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.85701,"mean_force":3.85944,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.48783,0.05318,0.02546]},{"body_a":"peg","body_b":"channel_base_body","contact_count":354.0,"contact_point_centroid":[0.50392,0.02723,0.00946],"force_p95":0.62795,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.50552,"mean_force":0.6005,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.48588,0.05931,0.06805]},{"body_a":"peg","body_b":"channel_base_body","contact_count":404.0,"contact_point_centroid":[0.50412,0.09319,0.00985],"force_p95":8.296,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.57584,"mean_force":4.01506,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.49033,0.13473,0.04419]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":49.0,"contact_point_centroid":[0.52504,0.09472,0.06],"force_p95":4.16992,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.5006,"mean_force":2.91026,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.49152,0.12252,0.03283]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52513,0.02706,0.06],"force_p95":4.68923,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.51674,"mean_force":1.37918,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.48803,0.05315,0.02517]},{"body_a":"peg","body_b":"channel_base_body","contact_count":260.0,"contact_point_centroid":[0.49662,0.11906,0.00936],"force_p95":0.64827,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.57316,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49177,0.19474,0.23018]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49951,0.19998,0.29653]}],"total_contact_groups":17},"final_pose_error":0.01489,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50319,0.02853,0.03409],"final_tcp_position":[0.48496,0.05592,0.11084],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":6289.37292,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":285.0,"n_steps_budget":600.0,"object_pos_end":[0.49601,0.11914,0.03382],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19928,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50305,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":284.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_peg","tcp_end":[0.48548,0.17734,0.17229],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15057,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":349.0,"n_steps_budget":600.0,"object_pos_end":[0.49598,0.119,0.0339],"object_pos_start":[0.49601,0.11914,0.03382],"object_to_goal_dist_end":0.19913,"object_to_goal_dist_start":0.19928,"object_z_max":0.03405,"peak_contact_force":0.51126,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":349.0,"raw_peak_contact_force":0.64449,"subtask_id":"contact_peg","tcp_end":[0.49136,0.15129,0.06239],"tcp_start":[0.48548,0.17734,0.17229],"tcp_to_object_dist_end":0.04331,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":443.0,"n_steps_budget":600.0,"object_pos_end":[0.50704,0.09505,0.03601],"object_pos_start":[0.49598,0.119,0.0339],"object_to_goal_dist_end":0.17524,"object_to_goal_dist_start":0.19913,"object_z_max":0.03728,"peak_contact_force":6.11936,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":751.0,"raw_peak_contact_force":12.73131,"subtask_id":"contact_peg","tcp_end":[0.49165,0.12126,0.03159],"tcp_start":[0.49136,0.15129,0.06239],"tcp_to_object_dist_end":0.03072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":555.0,"n_steps_budget":1000.0,"object_pos_end":[0.50637,0.02921,0.03591],"object_pos_start":[0.50704,0.09505,0.03601],"object_to_goal_dist_end":0.10948,"object_to_goal_dist_start":0.17524,"object_z_max":0.03695,"peak_contact_force":69.0568,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2086.0,"raw_peak_contact_force":69.0568,"subtask_id":"push_goal","tcp_end":[0.48806,0.0532,0.02515],"tcp_start":[0.48806,0.05325,0.02516],"tcp_to_object_dist_end":0.03204,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":359.0,"n_steps_budget":600.0,"object_pos_end":[0.50319,0.02853,0.03409],"object_pos_start":[0.50637,0.0289,0.03589],"object_to_goal_dist_end":0.10874,"object_to_goal_dist_start":0.10917,"object_z_max":0.03633,"peak_contact_force":0.54103,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":477.0,"raw_peak_contact_force":270.88637,"tcp_end":[0.48496,0.05592,0.11084],"tcp_start":[0.48806,0.0532,0.02515],"tcp_to_object_dist_end":0.0835,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97087,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_speed":0.17306,"approach_peg.approach_speed":0.38478,"descend_contact.contact_force_threshold":17.58066,"descend_contact.descend_speed":0.04999,"push_peg.push_distance":0.17407,"push_peg.push_max_time":10.19535,"push_peg.push_speed":0.07857,"push_peg.push_z_offset":0.00166,"push_peg.retry_x_offset":0.00044,"push_peg.retry_y_offset":-0.00065,"retract_lift.retract_speed":0.21981},"optimized_scores":{"best_composite_score":0.23807,"best_fitness_score":0.62807,"best_task_score":0.36474},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":378.0,"contact_point_centroid":[0.50328,0.05263,0.05085],"force_p95":15.75373,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.53941,"mean_force":8.87188,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49903,0.06363,0.0515]},{"body_a":"peg","body_b":"channel_base_body","contact_count":997.0,"contact_point_centroid":[0.50676,0.02133,0.00886],"force_p95":13.28177,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.4712,"mean_force":3.87503,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49873,0.02671,0.05148]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":184.0,"contact_point_centroid":[0.52501,0.03075,0.03842],"force_p95":8.44083,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.56068,"mean_force":4.90913,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49886,0.04558,0.05148]},{"body_a":"peg","body_b":"channel_base_body","contact_count":57.0,"contact_point_centroid":[0.50732,0.05338,0.00948],"force_p95":5.79343,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.11159,"mean_force":0.95241,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50315,0.09266,0.05892]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50413,0.08024,0.05795],"force_p95":5.79236,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.84332,"mean_force":3.84857,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50284,0.09213,0.05808]},{"body_a":"peg","body_b":"channel_base_body","contact_count":321.0,"contact_point_centroid":[0.50565,0.06294,0.00934],"force_p95":0.60722,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.58869,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51486,0.15017,0.23763]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50074,0.19608,0.29625]},{"body_a":"peg","body_b":"channel_base_body","contact_count":372.0,"contact_point_centroid":[0.50666,0.00905,0.00805],"force_p95":0.68506,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.94985,"mean_force":0.60674,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49547,-0.03073,0.09403]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.525,-0.00418,0.02416],"force_p95":0.65861,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68846,"mean_force":0.48428,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.4952,-0.03066,0.11123]},{"body_a":"peg","body_b":"channel_base_body","contact_count":326.0,"contact_point_centroid":[0.50586,0.0631,0.00938],"force_p95":0.55188,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54659,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.51441,0.1065,0.11819]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52506,0.05987,0.06],"force_p95":0.10732,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12307,"mean_force":0.06696,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50231,0.09019,0.05563]}],"total_contact_groups":11},"final_pose_error":0.01483,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50657,0.00917,0.02419],"final_tcp_position":[0.49538,-0.03436,0.13754],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":269.48152,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":349.0,"n_steps_budget":600.0,"object_pos_end":[0.50595,0.06295,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54461,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":355.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach_peg","tcp_end":[0.52529,0.11756,0.17343],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15117,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":326.0,"n_steps_budget":600.0,"object_pos_end":[0.50604,0.063,0.0338],"object_pos_start":[0.50595,0.06295,0.0338],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14321,"object_z_max":0.03381,"peak_contact_force":0.54828,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":326.0,"raw_peak_contact_force":0.55501,"subtask_id":"contact_peg","tcp_end":[0.50476,0.09522,0.06323],"tcp_start":[0.52529,0.11756,0.17343],"tcp_to_object_dist_end":0.04365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":57.0,"n_steps_budget":600.0,"object_pos_end":[0.50655,0.06138,0.03573],"object_pos_start":[0.50604,0.063,0.0338],"object_to_goal_dist_end":0.1416,"object_to_goal_dist_start":0.14326,"object_z_max":0.03573,"peak_contact_force":269.48152,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":71.0,"raw_peak_contact_force":6.11159,"subtask_id":"contact_peg","tcp_end":[0.50223,0.08977,0.05515],"tcp_start":[0.50476,0.09522,0.06323],"tcp_to_object_dist_end":0.03466,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50639,0.00905,0.02413],"object_pos_start":[0.50655,0.06138,0.03573],"object_to_goal_dist_end":0.09068,"object_to_goal_dist_start":0.1416,"object_z_max":0.04038,"peak_contact_force":0.6833,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1559.0,"raw_peak_contact_force":19.53941,"subtask_id":"push_goal","tcp_end":[0.49843,-0.03751,0.0517],"tcp_start":[0.50223,0.08977,0.05515],"tcp_to_object_dist_end":0.0547,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":372.0,"n_steps_budget":600.0,"object_pos_end":[0.50657,0.00917,0.02419],"object_pos_start":[0.50639,0.00905,0.02413],"object_to_goal_dist_end":0.0908,"object_to_goal_dist_start":0.09068,"object_z_max":0.02421,"peak_contact_force":0.62855,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":375.0,"raw_peak_contact_force":0.94985,"tcp_end":[0.49538,-0.03436,0.13754],"tcp_start":[0.49843,-0.03751,0.0517],"tcp_to_object_dist_end":0.12193,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86842,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_speed":0.15943,"approach_peg.approach_speed":0.28149,"descend_contact.contact_force_threshold":21.3548,"descend_contact.descend_speed":0.03528,"push_peg.push_distance":0.17738,"push_peg.push_max_time":18.64794,"push_peg.push_speed":0.0768,"push_peg.push_z_offset":-0.00647,"push_peg.retry_x_offset":-0.01171,"push_peg.retry_y_offset":0.00033,"retract_lift.retract_speed":0.21049},"optimized_scores":{"best_composite_score":0.18113,"best_fitness_score":0.57113,"best_task_score":0.24718},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":843.0,"contact_point_centroid":[0.50278,-0.00485,0.04206],"force_p95":7.95163,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.01014,"mean_force":3.70053,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49856,0.0068,0.03409]},{"body_a":"attachment","body_b":"peg","contact_count":32.0,"contact_point_centroid":[0.50239,-0.06372,0.05135],"force_p95":17.84728,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.23117,"mean_force":4.62635,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49683,-0.0522,0.03487]},{"body_a":"peg","body_b":"channel_base_body","contact_count":21.0,"contact_point_centroid":[0.50696,-0.10027,0.06012],"force_p95":31.62315,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.88299,"mean_force":17.78566,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49833,-0.05294,0.03157]},{"body_a":"peg","body_b":"channel_base_body","contact_count":29.0,"contact_point_centroid":[0.50644,-0.10028,0.06035],"force_p95":21.07792,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.37306,"mean_force":4.8465,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49706,-0.05278,0.03343]},{"body_a":"attachment","body_b":"peg","contact_count":206.0,"contact_point_centroid":[0.50431,0.06329,0.04594],"force_p95":11.33021,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.72321,"mean_force":6.50594,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50238,0.07502,0.04628]},{"body_a":"peg","body_b":"channel_base_body","contact_count":343.0,"contact_point_centroid":[0.50554,-0.07924,0.00946],"force_p95":0.57103,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.57128,"mean_force":0.59354,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49505,-0.04636,0.07728]},{"body_a":"peg","body_b":"channel_base_body","contact_count":281.0,"contact_point_centroid":[0.50691,0.036,0.00984],"force_p95":9.01899,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.49607,"mean_force":4.82148,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50272,0.07791,0.04943]},{"body_a":"peg","body_b":"channel_base_body","contact_count":606.0,"contact_point_centroid":[0.5065,-0.0367,0.00996],"force_p95":7.66643,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.92571,"mean_force":4.59799,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49856,0.00884,0.03417]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":107.0,"contact_point_centroid":[0.52506,0.04746,0.03761],"force_p95":3.6051,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.16501,"mean_force":2.00697,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50239,0.07577,0.04701]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":595.0,"contact_point_centroid":[0.52504,-0.0238,0.02453],"force_p95":2.86739,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.31962,"mean_force":1.15922,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.4985,0.00448,0.03394]},{"body_a":"peg","body_b":"channel_base_body","contact_count":333.0,"contact_point_centroid":[0.50571,0.05662,0.00934],"force_p95":0.60211,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.59432,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51849,0.14716,0.2378]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50109,0.19558,0.29595]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":42.0,"contact_point_centroid":[0.52515,-0.07909,0.01979],"force_p95":0.71744,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.80927,"mean_force":0.34464,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49584,-0.0498,0.04074]},{"body_a":"peg","body_b":"channel_base_body","contact_count":323.0,"contact_point_centroid":[0.50612,0.05668,0.00938],"force_p95":0.56646,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60599,"mean_force":0.54651,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.51818,0.10054,0.11808]}],"total_contact_groups":14},"final_pose_error":0.01481,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50688,-0.07869,0.03379],"final_tcp_position":[0.4951,-0.05057,0.11734],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":3916.67484,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":362.0,"n_steps_budget":600.0,"object_pos_end":[0.50613,0.0566,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.56351,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":370.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach_peg","tcp_end":[0.53164,0.11177,0.17294],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":323.0,"n_steps_budget":600.0,"object_pos_end":[0.50616,0.05659,0.03378],"object_pos_start":[0.50613,0.0566,0.03378],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.13688,"object_z_max":0.03379,"peak_contact_force":0.55137,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":323.0,"raw_peak_contact_force":0.60599,"subtask_id":"contact_peg","tcp_end":[0.50573,0.08902,0.06335],"tcp_start":[0.53164,0.11177,0.17294],"tcp_to_object_dist_end":0.04388,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":288.0,"n_steps_budget":780.0,"object_pos_end":[0.50695,0.03993,0.03706],"object_pos_start":[0.50616,0.05659,0.03378],"object_to_goal_dist_end":0.12017,"object_to_goal_dist_start":0.13687,"object_z_max":0.0374,"peak_contact_force":3916.67484,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":594.0,"raw_peak_contact_force":13.72321,"subtask_id":"contact_peg","tcp_end":[0.50224,0.06917,0.04073],"tcp_start":[0.50573,0.08902,0.06335],"tcp_to_object_dist_end":0.02984,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50637,-0.08235,0.03557],"object_pos_start":[0.50695,0.03993,0.03706],"object_to_goal_dist_end":0.00811,"object_to_goal_dist_start":0.12017,"object_z_max":0.03706,"peak_contact_force":34.60779,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2065.0,"raw_peak_contact_force":36.01014,"subtask_id":"push_goal","tcp_end":[0.49829,-0.05381,0.03144],"tcp_start":[0.50224,0.06917,0.04073],"tcp_to_object_dist_end":0.02995,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":373.0,"n_steps_budget":600.0,"object_pos_end":[0.50688,-0.07869,0.03379],"object_pos_start":[0.50637,-0.08235,0.03557],"object_to_goal_dist_end":0.00936,"object_to_goal_dist_start":0.00811,"object_z_max":0.0371,"peak_contact_force":0.54386,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":446.0,"raw_peak_contact_force":34.23117,"tcp_end":[0.4951,-0.05057,0.11734],"tcp_start":[0.49829,-0.05381,0.03144],"tcp_to_object_dist_end":0.08894,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```