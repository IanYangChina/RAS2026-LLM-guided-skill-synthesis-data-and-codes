## Search State

- **Seed**: 8
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → align → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.2465 | 0.14 | ❌ rejected |
| 7 | approach → align → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0535 | 0.34 | ❌ rejected |
| 6 | approach → align → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2383 | 0.26 | ❌ rejected |
| 5 | approach → align → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.2766 | 0.01 | ❌ rejected |
| 4 | approach → align → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | 0.1997 | 0.38 | ✅ accepted |

**Proposal policy**: task_score is 0.14 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.247) — your mutation base

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

- **Composite score**: -0.247
- **task_score** (E): 0.145
- **fitness_score**: 0.263  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1473 |
| align_behind | 1.00 | 1.00 | 0.1140 |
| push_peg | 0.00 | 1.00 | 0.0001 |
| retract_lift | 1.00 | 1.00 | 0.0855 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.514, 0.136, 0.173) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.537 | 3.526 |
| align_behind | align | 1.00 / step_budget | (0.514, 0.136, 0.173)→(0.501, 0.111, 0.063) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.531 | 0.602 |
| push_peg | push | 0.00 / guard_failure | (0.499, 0.080, 0.057)→(0.499, 0.080, 0.057) | (0.503, 0.080, 0.034)→(0.504, 0.059, 0.036) | 0.160→0.140 | 1.00 / 2.667 | 51.981 | 55.897 |
| retract_lift | retract | 1.00 / step_budget | (0.499, 0.080, 0.057)→(0.496, 0.082, 0.143) | (0.504, 0.059, 0.036)→(0.502, 0.053, 0.031) | 0.139→0.134 | 1.00 / 1.000 | 0.576 | 103.683 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.489
- alignment_error: None
- force_efficiency: 0.128
- terminal_score: 0.433
- phase_score: 0.510
- phase_breakdown.push_goal_score: 0.297
- phase_breakdown.approach_peg_score: 0.743
- phase_breakdown.contact_peg_score: 0.880

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.479
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.433
- **Median Q (composite search score)**: -0.347
- **K-run variance**: 0.0233
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.251


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95402,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_speed":0.22382,"approach_peg.approach_speed":0.37157,"push_peg.push_distance":0.15478,"push_peg.push_max_time":14.63486,"push_peg.push_speed":0.06541,"push_peg.push_z_offset":-0.01063,"push_peg.retry_x_offset":0.00424,"push_peg.retry_y_offset":0.00211,"retract_lift.retract_speed":0.19307},"optimized_scores":{"best_composite_score":-0.03099,"best_fitness_score":0.47901,"best_task_score":0.43326},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":648.0,"contact_point_centroid":[0.49711,0.09054,0.00978],"force_p95":22.01031,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.60474,"mean_force":9.36193,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.48921,0.11425,0.05622]},{"body_a":"attachment","body_b":"peg","contact_count":542.0,"contact_point_centroid":[0.49407,0.10864,0.045],"force_p95":21.78632,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.21089,"mean_force":10.68175,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.48907,0.10853,0.05566]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.475,0.11998,0.0282],"force_p95":30.51356,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":30.77154,"mean_force":28.27156,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.48911,0.07994,0.05468]},{"body_a":"peg","body_b":"channel_base_body","contact_count":348.0,"contact_point_centroid":[0.49618,0.04398,0.0083],"force_p95":0.89435,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.11586,"mean_force":0.66308,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.48725,0.08585,0.09647]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.49391,0.08015,0.04381],"force_p95":7.29895,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.5758,"mean_force":1.52001,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.48922,0.08001,0.05457]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47499,0.01625,0.02426],"force_p95":7.83208,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.65477,"mean_force":3.15281,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.48721,0.08414,0.13373]},{"body_a":"peg","body_b":"channel_base_body","contact_count":260.0,"contact_point_centroid":[0.49662,0.11906,0.00936],"force_p95":0.64827,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.57316,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49177,0.19474,0.23018]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49951,0.19998,0.29653]},{"body_a":"peg","body_b":"channel_base_body","contact_count":346.0,"contact_point_centroid":[0.49588,0.11903,0.00944],"force_p95":0.60642,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64449,"mean_force":0.54079,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.48448,0.16987,0.10349]}],"total_contact_groups":9},"final_pose_error":0.01496,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49359,0.0407,0.02436],"final_tcp_position":[0.48727,0.08242,0.13978],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":43.60474,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":285.0,"n_steps_budget":600.0,"object_pos_end":[0.49601,0.11914,0.03382],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19928,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50305,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":284.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_peg","tcp_end":[0.48548,0.17734,0.17229],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15057,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":346.0,"n_steps_budget":600.0,"object_pos_end":[0.49603,0.11908,0.03384],"object_pos_start":[0.49601,0.11914,0.03382],"object_to_goal_dist_end":0.19921,"object_to_goal_dist_start":0.19928,"object_z_max":0.03405,"peak_contact_force":0.50685,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":346.0,"raw_peak_contact_force":0.64449,"subtask_id":"contact_peg","tcp_end":[0.49178,0.1506,0.06254],"tcp_start":[0.48548,0.17734,0.17229],"tcp_to_object_dist_end":0.04285,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":648.0,"n_steps_budget":1000.0,"object_pos_end":[0.49942,0.06008,0.03931],"object_pos_start":[0.49603,0.11908,0.03384],"object_to_goal_dist_end":0.14009,"object_to_goal_dist_start":0.19921,"object_z_max":0.04043,"peak_contact_force":38.9266,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1190.0,"raw_peak_contact_force":43.60474,"subtask_id":"push_goal","tcp_end":[0.48943,0.08013,0.0544],"tcp_start":[0.48941,0.08019,0.05443],"tcp_to_object_dist_end":0.02701,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":355.0,"n_steps_budget":600.0,"object_pos_end":[0.49359,0.0407,0.02436],"object_pos_start":[0.49952,0.05993,0.03929],"object_to_goal_dist_end":0.12188,"object_to_goal_dist_start":0.13994,"object_z_max":0.03929,"peak_contact_force":0.63896,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":362.0,"raw_peak_contact_force":30.77154,"tcp_end":[0.48727,0.08242,0.13978],"tcp_start":[0.48943,0.08013,0.0544],"tcp_to_object_dist_end":0.12289,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87356,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_speed":0.06345,"approach_peg.approach_speed":0.29277,"push_peg.push_distance":0.18196,"push_peg.push_max_time":18.88008,"push_peg.push_speed":0.10685,"push_peg.push_z_offset":-0.00261,"push_peg.retry_x_offset":-0.00349,"push_peg.retry_y_offset":-0.00068,"retract_lift.retract_speed":0.1583},"optimized_scores":{"best_composite_score":-0.3472,"best_fitness_score":0.1628,"best_task_score":0.00032},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.475,0.11984,0.04713],"force_p95":139.63478,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":140.78242,"mean_force":81.73955,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.50269,0.07956,0.05928]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.475,0.11984,0.04725],"force_p95":53.68318,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":57.71557,"mean_force":21.86599,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.50272,0.07957,0.05932]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.525,0.11984,0.03859],"force_p95":51.26098,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":53.53346,"mean_force":19.1409,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.50269,0.07956,0.05928]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.525,0.11985,0.03857],"force_p95":38.19488,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":38.3955,"mean_force":21.8672,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.50272,0.07961,0.05932]},{"body_a":"peg","body_b":"channel_base_body","contact_count":95.0,"contact_point_centroid":[0.50572,0.06024,0.00939],"force_p95":3.96823,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.69879,"mean_force":1.03514,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.5035,0.08671,0.06056]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50592,0.08047,0.04783],"force_p95":12.80112,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.35733,"mean_force":8.09137,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.50276,0.08042,0.05938]},{"body_a":"peg","body_b":"channel_base_body","contact_count":321.0,"contact_point_centroid":[0.50565,0.06294,0.00934],"force_p95":0.60722,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.58869,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51486,0.15017,0.23763]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50074,0.19608,0.29625]},{"body_a":"peg","body_b":"channel_base_body","contact_count":359.0,"contact_point_centroid":[0.50581,0.06236,0.00943],"force_p95":0.61244,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.9512,"mean_force":0.5415,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.50055,0.08534,0.10093]},{"body_a":"peg","body_b":"channel_base_body","contact_count":429.0,"contact_point_centroid":[0.50599,0.06303,0.00938],"force_p95":0.55156,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54658,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.51188,0.10967,0.11186]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50645,0.08185,0.05904],"force_p95":0.09663,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12822,"mean_force":0.02077,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.50156,0.08177,0.06428]}],"total_contact_groups":11},"final_pose_error":0.01487,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50624,0.06282,0.03398],"final_tcp_position":[0.50053,0.08171,0.14473],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":140.78242,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":349.0,"n_steps_budget":600.0,"object_pos_end":[0.50595,0.06295,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54461,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":355.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach_peg","tcp_end":[0.52529,0.11756,0.17343],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15117,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":429.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.06294,0.0338],"object_pos_start":[0.50595,0.06295,0.0338],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14321,"object_z_max":0.03381,"peak_contact_force":0.54563,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":429.0,"raw_peak_contact_force":0.55501,"subtask_id":"contact_peg","tcp_end":[0.50535,0.09446,0.06352],"tcp_start":[0.52529,0.11756,0.17343],"tcp_to_object_dist_end":0.04333,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":95.0,"n_steps_budget":1000.0,"object_pos_end":[0.50576,0.06139,0.03508],"object_pos_start":[0.50598,0.06294,0.0338],"object_to_goal_dist_end":0.14159,"object_to_goal_dist_start":0.1432,"object_z_max":0.03517,"peak_contact_force":57.71557,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":116.0,"raw_peak_contact_force":57.71557,"subtask_id":"push_goal","tcp_end":[0.5027,0.07943,0.05927],"tcp_start":[0.50269,0.07941,0.05931],"tcp_to_object_dist_end":0.03033,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":359.0,"n_steps_budget":600.0,"object_pos_end":[0.50624,0.06282,0.03398],"object_pos_start":[0.50571,0.06125,0.03525],"object_to_goal_dist_end":0.14308,"object_to_goal_dist_start":0.14144,"object_z_max":0.03558,"peak_contact_force":0.54644,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":377.0,"raw_peak_contact_force":140.78242,"tcp_end":[0.50053,0.08171,0.14473],"tcp_start":[0.5027,0.07943,0.05927],"tcp_to_object_dist_end":0.11249,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.04348,"average_solve_count":69.0,"average_success_count":69.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_speed":0.17533,"approach_peg.approach_speed":0.26873,"push_peg.push_distance":0.14756,"push_peg.push_max_time":12.96324,"push_peg.push_speed":0.04853,"push_peg.push_z_offset":-0.01978,"push_peg.retry_x_offset":-0.00718,"push_peg.retry_y_offset":-0.00489,"retract_lift.retract_speed":0.19907},"optimized_scores":{"best_composite_score":-0.36141,"best_fitness_score":0.14859,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.475,0.11988,0.04807],"force_p95":138.15762,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":139.49645,"mean_force":86.15003,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.50359,0.07964,0.05856]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.475,0.11989,0.04822],"force_p95":63.89658,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":66.37102,"mean_force":29.52881,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.50363,0.07964,0.05862]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.525,0.11987,0.03705],"force_p95":31.12678,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":37.61922,"mean_force":9.46414,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.50364,0.07966,0.05863]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.525,0.11987,0.03703],"force_p95":25.8332,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":30.392,"mean_force":7.598,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.50359,0.07964,0.05856]},{"body_a":"peg","body_b":"channel_base_body","contact_count":333.0,"contact_point_centroid":[0.50571,0.05662,0.00934],"force_p95":0.60211,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.59432,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51849,0.14716,0.2378]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50109,0.19558,0.29595]},{"body_a":"peg","body_b":"channel_base_body","contact_count":336.0,"contact_point_centroid":[0.50605,0.05656,0.00938],"force_p95":0.56581,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60599,"mean_force":0.54649,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.51431,0.10354,0.10597]},{"body_a":"peg","body_b":"channel_base_body","contact_count":80.0,"contact_point_centroid":[0.50637,0.05649,0.00938],"force_p95":0.55587,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56297,"mean_force":0.54668,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.50441,0.08353,0.06024]},{"body_a":"peg","body_b":"channel_base_body","contact_count":359.0,"contact_point_centroid":[0.50609,0.05674,0.00938],"force_p95":0.55329,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56148,"mean_force":0.54664,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.50145,0.08544,0.10022]}],"total_contact_groups":9},"final_pose_error":0.01488,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50616,0.05663,0.0338],"final_tcp_position":[0.50144,0.08186,0.14402],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":139.49645,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":362.0,"n_steps_budget":600.0,"object_pos_end":[0.50613,0.0566,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.56351,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":370.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach_peg","tcp_end":[0.53164,0.11177,0.17294],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":336.0,"n_steps_budget":600.0,"object_pos_end":[0.50613,0.05664,0.03379],"object_pos_start":[0.50613,0.0566,0.03378],"object_to_goal_dist_end":0.13692,"object_to_goal_dist_start":0.13688,"object_z_max":0.03379,"peak_contact_force":0.5405,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":336.0,"raw_peak_contact_force":0.60599,"subtask_id":"contact_peg","tcp_end":[0.50615,0.08827,0.06338],"tcp_start":[0.53164,0.11177,0.17294],"tcp_to_object_dist_end":0.04331,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":80.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.05658,0.03379],"object_pos_start":[0.50613,0.05664,0.03379],"object_to_goal_dist_end":0.13685,"object_to_goal_dist_start":0.13692,"object_z_max":0.03379,"peak_contact_force":59.30121,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":97.0,"raw_peak_contact_force":66.37102,"subtask_id":"push_goal","tcp_end":[0.50362,0.07957,0.05856],"tcp_start":[0.50361,0.07954,0.0586],"tcp_to_object_dist_end":0.03389,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":359.0,"n_steps_budget":600.0,"object_pos_end":[0.50616,0.05663,0.0338],"object_pos_start":[0.5061,0.05662,0.03379],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.1369,"object_z_max":0.0338,"peak_contact_force":0.54234,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":367.0,"raw_peak_contact_force":139.49645,"tcp_end":[0.50144,0.08186,0.14402],"tcp_start":[0.50362,0.07957,0.05856],"tcp_to_object_dist_end":0.11317,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```