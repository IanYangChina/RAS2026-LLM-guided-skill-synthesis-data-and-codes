## Search State

- **Seed**: 8
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → rotate → align → push → push → retract | arc_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | 0.3097 | 0.40 | ✅ accepted |
| 13 | approach → align → push → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.0042 | 0.20 | ❌ rejected |
| 12 | approach → align → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | 0.0186 | 0.12 | ❌ rejected |
| 11 | approach → align → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | -0.2398 | 0.06 | ❌ rejected |
| 10 | approach → align → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.4041 | 0.02 | ❌ rejected |

**Proposal policy**: task_score is 0.40 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.310) — your mutation base

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
  - 0.025
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
- id: orient_tool
  type: rotate
  generator: joint_interpolation
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
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
    - 0.025
    - 0.0
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
- id: contact_engage
  type: push
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
    offset_along_axis:
      distance: 0.025
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    engage_force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    engage_speed:
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
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    force_limit_guard:
      type: scalar
      range:
      - 30.0
      - 50.0
      default: 40.0
      binds_to:
      - path: guards.force_limit.threshold
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
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
    offset:
    - 0.0
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
- **orient_tool** (`rotate`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings: none
- **align_behind** (`align`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.025, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **contact_engage** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.025, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - engage_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - engage_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_check, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **push_peg** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_limit_guard: status=consumed; consumers=guards.force_limit.threshold (replace)
    - push_max_time: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **retract_lift** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.310
- **task_score** (E): 0.397
- **fitness_score**: 0.641  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.189
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1473 |
| orient_tool | 1.00 | 1.00 | 0.0249 |
| align_behind | 1.00 | 1.00 | 0.1360 |
| contact_engage | 1.00 | 1.00 | 0.0199 |
| push_peg | 0.67 | 1.00 | 0.0891 |
| retract_lift | 1.00 | 1.00 | 0.0859 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.514, 0.136, 0.173) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.537 | 3.526 |
| orient_tool | rotate | 1.00 / step_budget | (0.514, 0.136, 0.173)→(0.505, 0.158, 0.168) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.545 | 0.606 |
| align_behind | align | 1.00 / step_budget | (0.505, 0.158, 0.168)→(0.499, 0.109, 0.042) | (0.503, 0.080, 0.034)→(0.503, 0.079, 0.034) | 0.160→0.159 | 1.00 / 1.333 | 0.677 | 4.898 |
| contact_engage | push | 1.00 / force_exceeded | (0.499, 0.109, 0.042)→(0.498, 0.091, 0.036) | (0.503, 0.079, 0.034)→(0.507, 0.062, 0.036) | 0.159→0.142 | 1.00 / 2.000 | 2610.744 | 10.077 |
| push_peg | push | 0.67 / time_limit | (0.499, 0.037, 0.037)→(0.496, -0.052, 0.035) | (0.507, 0.062, 0.036)→(0.507, -0.080, 0.036) | 0.142→0.008 | 1.00 / 2.000 | 5.188 | 21.258 |
| retract_lift | retract | 1.00 / step_budget | (0.496, -0.052, 0.035)→(0.493, -0.049, 0.120) | (0.507, -0.080, 0.036)→(0.505, -0.079, 0.034) | 0.008→0.008 | 1.00 / 1.333 | 0.563 | 4.647 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.580
- phase_score: 0.796
- phase_breakdown.contact_peg_score: 0.457
- phase_breakdown.approach_peg_score: 0.743
- phase_breakdown.push_goal_score: 0.950

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.710
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.580
- **Median Q (composite search score)**: 0.313
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.286


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64493,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_speed":0.06188,"approach_peg.approach_speed":0.2367,"contact_engage.engage_force_threshold":25.90906,"contact_engage.engage_speed":0.05869,"push_peg.force_limit_guard":35.94199,"push_peg.push_max_time":14.68276,"push_peg.push_speed":0.11758,"retract_lift.retract_speed":0.2632},"optimized_scores":{"best_composite_score":0.35617,"best_fitness_score":0.70951,"best_task_score":0.57992},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":13.0,"contact_point_centroid":[0.50675,-0.10024,0.06061],"force_p95":40.62583,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.55298,"mean_force":17.9831,"phase_index":4.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49489,-0.05382,0.0342]},{"body_a":"attachment","body_b":"peg","contact_count":662.0,"contact_point_centroid":[0.49832,0.01752,0.03792],"force_p95":16.3653,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.53465,"mean_force":5.01479,"phase_index":4.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49104,0.02771,0.03078]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":647.0,"contact_point_centroid":[0.52517,0.00645,0.03114],"force_p95":9.4926,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.47398,"mean_force":2.90089,"phase_index":4.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49085,0.03164,0.03062]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.507,-0.00799,0.00993],"force_p95":13.06691,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.46301,"mean_force":5.41054,"phase_index":4.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49084,0.03314,0.03061]},{"body_a":"peg","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.52032,0.07041,0.06337],"force_p95":12.30219,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.6456,"mean_force":6.91284,"phase_index":4.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.48814,0.08467,0.02819]},{"body_a":"attachment","body_b":"peg","contact_count":330.0,"contact_point_centroid":[0.49687,0.11392,0.04291],"force_p95":10.11259,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.50682,"mean_force":4.55805,"phase_index":3.0,"phase_name":"contact_engage","phase_type":"push","tcp_position_centroid":[0.48921,0.12401,0.03392]},{"body_a":"peg","body_b":"channel_base_body","contact_count":327.0,"contact_point_centroid":[0.50636,0.08717,0.00992],"force_p95":7.09781,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.90529,"mean_force":3.64749,"phase_index":3.0,"phase_name":"contact_engage","phase_type":"push","tcp_position_centroid":[0.48904,0.12754,0.03457]},{"body_a":"peg","body_b":"channel_base_body","contact_count":21.0,"contact_point_centroid":[0.50619,-0.10032,0.0606],"force_p95":1.55191,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.29216,"mean_force":0.87739,"phase_index":5.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49385,-0.0541,0.03521]},{"body_a":"attachment","body_b":"peg","contact_count":27.0,"contact_point_centroid":[0.50072,-0.06452,0.06101],"force_p95":1.30746,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.25227,"mean_force":0.78241,"phase_index":5.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49346,-0.05319,0.03738]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":243.0,"contact_point_centroid":[0.52516,0.0946,0.035],"force_p95":6.48447,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.21683,"mean_force":3.39269,"phase_index":3.0,"phase_name":"contact_engage","phase_type":"push","tcp_position_centroid":[0.48948,0.11891,0.033]},{"body_a":"peg","body_b":"channel_base_body","contact_count":482.0,"contact_point_centroid":[0.49609,0.1188,0.00944],"force_p95":0.59939,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.0013,"mean_force":0.5703,"phase_index":2.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.48112,0.17289,0.10394]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.49388,0.13716,0.05886],"force_p95":6.57513,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.63199,"mean_force":3.78618,"phase_index":2.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.49004,0.14894,0.04382]},{"body_a":"peg","body_b":"channel_base_body","contact_count":260.0,"contact_point_centroid":[0.49662,0.11906,0.00936],"force_p95":0.64827,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.57316,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49177,0.19474,0.23018]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49951,0.19998,0.29653]},{"body_a":"peg","body_b":"channel_base_body","contact_count":352.0,"contact_point_centroid":[0.50245,-0.08068,0.00943],"force_p95":0.60115,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.83191,"mean_force":0.54139,"phase_index":5.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49171,-0.04739,0.07851]},{"body_a":"peg","body_b":"channel_base_body","contact_count":280.0,"contact_point_centroid":[0.49584,0.11897,0.00944],"force_p95":0.61556,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65811,"mean_force":0.54021,"phase_index":1.0,"phase_name":"orient_tool","phase_type":"rotate","tcp_position_centroid":[0.47876,0.18757,0.16808]}],"total_contact_groups":16},"final_pose_error":0.01496,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50206,-0.07985,0.03381],"final_tcp_position":[0.49171,-0.05135,0.11989],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":3917.53386,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":285.0,"n_steps_budget":600.0,"object_pos_end":[0.49601,0.11914,0.03382],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19928,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50305,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":284.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_peg","tcp_end":[0.48548,0.17734,0.17229],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15057,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":280.0,"n_steps_budget":600.0,"object_pos_end":[0.49602,0.11914,0.03396],"object_pos_start":[0.49601,0.11914,0.03382],"object_to_goal_dist_end":0.19927,"object_to_goal_dist_start":0.19928,"object_z_max":0.03415,"peak_contact_force":0.54334,"phase_name":"orient_tool","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":280.0,"raw_peak_contact_force":0.65811,"tcp_end":[0.47435,0.19747,0.16741],"tcp_start":[0.48548,0.17734,0.17229],"tcp_to_object_dist_end":0.15625,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":482.0,"n_steps_budget":1000.0,"object_pos_end":[0.49623,0.11841,0.03446],"object_pos_start":[0.49602,0.11914,0.03396],"object_to_goal_dist_end":0.19853,"object_to_goal_dist_start":0.19927,"object_z_max":0.03435,"peak_contact_force":0.4488,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":486.0,"raw_peak_contact_force":7.0013,"subtask_id":"contact_peg","tcp_end":[0.49042,0.14788,0.04118],"tcp_start":[0.47435,0.19747,0.16741],"tcp_to_object_dist_end":0.03078,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":427.0,"n_steps_budget":600.0,"object_pos_end":[0.50691,0.08017,0.03659],"object_pos_start":[0.49623,0.11841,0.03446],"object_to_goal_dist_end":0.16036,"object_to_goal_dist_start":0.19853,"object_z_max":0.03704,"peak_contact_force":3917.53386,"phase_name":"contact_engage","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":900.0,"raw_peak_contact_force":11.50682,"subtask_id":"contact_peg","tcp_end":[0.49089,0.10609,0.03145],"tcp_start":[0.49042,0.14788,0.04118],"tcp_to_object_dist_end":0.0309,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":856.0,"n_steps_budget":990.0,"object_pos_end":[0.50661,-0.08214,0.03611],"object_pos_start":[0.50691,0.08017,0.03659],"object_to_goal_dist_end":0.00796,"object_to_goal_dist_start":0.16036,"object_z_max":0.03738,"peak_contact_force":12.157,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1795.0,"raw_peak_contact_force":41.55298,"subtask_id":"push_goal","tcp_end":[0.49487,-0.05465,0.03414],"tcp_start":[0.49491,-0.05459,0.03419],"tcp_to_object_dist_end":0.02995,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":370.0,"n_steps_budget":600.0,"object_pos_end":[0.50206,-0.07985,0.03381],"object_pos_start":[0.50647,-0.08231,0.03603],"object_to_goal_dist_end":0.00652,"object_to_goal_dist_start":0.00794,"object_z_max":0.03628,"peak_contact_force":0.54516,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":400.0,"raw_peak_contact_force":7.29216,"tcp_end":[0.49171,-0.05135,0.11989],"tcp_start":[0.49487,-0.05465,0.03414],"tcp_to_object_dist_end":0.09127,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.99038,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_speed":0.13825,"approach_peg.approach_speed":0.35694,"contact_engage.engage_force_threshold":19.81227,"contact_engage.engage_speed":0.06666,"push_peg.force_limit_guard":34.6515,"push_peg.push_max_time":11.85451,"push_peg.push_speed":0.08323,"retract_lift.retract_speed":0.16241},"optimized_scores":{"best_composite_score":0.31297,"best_fitness_score":0.63297,"best_task_score":0.36415},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":831.0,"contact_point_centroid":[0.50159,0.00442,0.04157],"force_p95":8.22672,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.40841,"mean_force":2.89637,"phase_index":4.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49651,0.01577,0.03361]},{"body_a":"peg","body_b":"channel_base_body","contact_count":72.0,"contact_point_centroid":[0.50571,0.0421,0.00981],"force_p95":8.47909,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.69577,"mean_force":3.13682,"phase_index":3.0,"phase_name":"contact_engage","phase_type":"push","tcp_position_centroid":[0.50128,0.08764,0.03864]},{"body_a":"peg","body_b":"channel_base_body","contact_count":570.0,"contact_point_centroid":[0.50642,-0.02694,0.00995],"force_p95":8.23231,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.55808,"mean_force":4.34306,"phase_index":4.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49657,0.01794,0.03363]},{"body_a":"attachment","body_b":"peg","contact_count":61.0,"contact_point_centroid":[0.50399,0.07513,0.0458],"force_p95":8.24262,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.26913,"mean_force":3.21312,"phase_index":3.0,"phase_name":"contact_engage","phase_type":"push","tcp_position_centroid":[0.50106,0.08687,0.03823]},{"body_a":"peg","body_b":"channel_base_body","contact_count":401.0,"contact_point_centroid":[0.50596,0.06276,0.00938],"force_p95":0.55231,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.78785,"mean_force":0.5649,"phase_index":2.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.50913,0.11691,0.10523]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50556,0.08091,0.0546],"force_p95":5.88282,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.44293,"mean_force":2.70299,"phase_index":2.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.50346,0.09283,0.04316]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":563.0,"contact_point_centroid":[0.52504,-0.01092,0.0221],"force_p95":3.44482,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.89679,"mean_force":1.08411,"phase_index":4.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49654,0.01659,0.03363]},{"body_a":"peg","body_b":"channel_base_body","contact_count":321.0,"contact_point_centroid":[0.50565,0.06294,0.00934],"force_p95":0.60722,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.58869,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51486,0.15017,0.23763]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50074,0.19608,0.29625]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":30.0,"contact_point_centroid":[0.5251,0.0558,0.03696],"force_p95":2.07697,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.25342,"mean_force":0.90474,"phase_index":3.0,"phase_name":"contact_engage","phase_type":"push","tcp_position_centroid":[0.50063,0.0851,0.03735]},{"body_a":"peg","body_b":"channel_base_body","contact_count":368.0,"contact_point_centroid":[0.50604,-0.07846,0.00945],"force_p95":0.58945,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.79938,"mean_force":0.53996,"phase_index":5.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49316,-0.04386,0.07744]},{"body_a":"peg","body_b":"channel_base_body","contact_count":296.0,"contact_point_centroid":[0.50583,0.0631,0.00938],"force_p95":0.55215,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.5466,"phase_index":1.0,"phase_name":"orient_tool","phase_type":"rotate","tcp_position_centroid":[0.51964,0.12944,0.16877]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":84.0,"contact_point_centroid":[0.52505,-0.07823,0.04344],"force_p95":0.32012,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3973,"mean_force":0.1072,"phase_index":5.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49383,-0.04607,0.05432]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50102,-0.06048,0.05527],"force_p95":0.21783,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24233,"mean_force":0.09936,"phase_index":5.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49473,-0.04903,0.03914]}],"total_contact_groups":14},"final_pose_error":0.01497,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50691,-0.07826,0.03381],"final_tcp_position":[0.49306,-0.04749,0.12054],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":3897.08313,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":349.0,"n_steps_budget":600.0,"object_pos_end":[0.50595,0.06295,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54461,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":355.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach_peg","tcp_end":[0.52529,0.11756,0.17343],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15117,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":296.0,"n_steps_budget":600.0,"object_pos_end":[0.50603,0.06301,0.03381],"object_pos_start":[0.50595,0.06295,0.0338],"object_to_goal_dist_end":0.14327,"object_to_goal_dist_start":0.14321,"object_z_max":0.03381,"peak_contact_force":0.54849,"phase_name":"orient_tool","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":296.0,"raw_peak_contact_force":0.55501,"tcp_end":[0.51645,0.14025,0.16809],"tcp_start":[0.52529,0.11756,0.17343],"tcp_to_object_dist_end":0.15526,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":401.0,"n_steps_budget":660.0,"object_pos_end":[0.50593,0.06257,0.03383],"object_pos_start":[0.50603,0.06301,0.03381],"object_to_goal_dist_end":0.14283,"object_to_goal_dist_start":0.14327,"object_z_max":0.03381,"peak_contact_force":0.67916,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":404.0,"raw_peak_contact_force":6.78785,"subtask_id":"contact_peg","tcp_end":[0.50333,0.0924,0.04207],"tcp_start":[0.51645,0.14025,0.16809],"tcp_to_object_dist_end":0.03106,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":93.0,"n_steps_budget":600.0,"object_pos_end":[0.50712,0.0535,0.03553],"object_pos_start":[0.50593,0.06257,0.03383],"object_to_goal_dist_end":0.13377,"object_to_goal_dist_start":0.14283,"object_z_max":0.03578,"peak_contact_force":3897.08313,"phase_name":"contact_engage","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":163.0,"raw_peak_contact_force":9.69577,"subtask_id":"contact_peg","tcp_end":[0.50036,0.08272,0.03656],"tcp_start":[0.50333,0.0924,0.04207],"tcp_to_object_dist_end":0.03001,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50708,-0.07881,0.03609],"object_pos_start":[0.50712,0.0535,0.03553],"object_to_goal_dist_end":0.00818,"object_to_goal_dist_start":0.13377,"object_z_max":0.0362,"peak_contact_force":1.06728,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1964.0,"raw_peak_contact_force":10.40841,"subtask_id":"push_goal","tcp_end":[0.49622,-0.05076,0.0348],"tcp_start":[0.50036,0.08272,0.03656],"tcp_to_object_dist_end":0.0301,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":371.0,"n_steps_budget":600.0,"object_pos_end":[0.50691,-0.07826,0.03381],"object_pos_start":[0.50708,-0.07881,0.03609],"object_to_goal_dist_end":0.00944,"object_to_goal_dist_start":0.00818,"object_z_max":0.03609,"peak_contact_force":0.54587,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":461.0,"raw_peak_contact_force":0.79938,"tcp_end":[0.49306,-0.04749,0.12054],"tcp_start":[0.49622,-0.05076,0.0348],"tcp_to_object_dist_end":0.09307,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_speed":0.14098,"approach_peg.approach_speed":0.21304,"contact_engage.engage_force_threshold":13.0691,"contact_engage.engage_speed":0.0471,"push_peg.force_limit_guard":34.79804,"push_peg.push_max_time":13.58854,"push_peg.push_speed":0.08269,"retract_lift.retract_speed":0.14782},"optimized_scores":{"best_composite_score":0.25982,"best_fitness_score":0.57982,"best_task_score":0.2483},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":809.0,"contact_point_centroid":[0.50196,0.0029,0.04118],"force_p95":8.37543,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.81165,"mean_force":3.30055,"phase_index":4.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49745,0.01431,0.03498]},{"body_a":"peg","body_b":"channel_base_body","contact_count":597.0,"contact_point_centroid":[0.50642,-0.02645,0.00994],"force_p95":8.59354,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.37172,"mean_force":4.53745,"phase_index":4.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.4976,0.01878,0.03506]},{"body_a":"peg","body_b":"channel_base_body","contact_count":34.0,"contact_point_centroid":[0.50336,0.04482,0.00972],"force_p95":8.32678,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.02785,"mean_force":2.54401,"phase_index":3.0,"phase_name":"contact_engage","phase_type":"push","tcp_position_centroid":[0.50287,0.08464,0.04032]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.50485,0.07274,0.04878],"force_p95":8.53517,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.56547,"mean_force":3.87304,"phase_index":3.0,"phase_name":"contact_engage","phase_type":"push","tcp_position_centroid":[0.50289,0.08461,0.04033]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":631.0,"contact_point_centroid":[0.52505,-0.01329,0.02489],"force_p95":3.2882,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.1593,"mean_force":1.17948,"phase_index":4.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49741,0.01458,0.03493]},{"body_a":"peg","body_b":"channel_base_body","contact_count":371.0,"contact_point_centroid":[0.50515,-0.07899,0.00949],"force_p95":0.62024,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.85003,"mean_force":0.5554,"phase_index":5.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49346,-0.04392,0.07748]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50107,-0.06213,0.0386],"force_p95":4.73679,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.95152,"mean_force":2.80424,"phase_index":5.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49648,-0.05083,0.03518]},{"body_a":"peg","body_b":"channel_base_body","contact_count":333.0,"contact_point_centroid":[0.50571,0.05662,0.00934],"force_p95":0.60211,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.59432,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51849,0.14716,0.2378]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50109,0.19558,0.29595]},{"body_a":"peg","body_b":"channel_base_body","contact_count":398.0,"contact_point_centroid":[0.50617,0.05664,0.00938],"force_p95":0.55403,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.90426,"mean_force":0.54788,"phase_index":2.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.51274,0.11172,0.10494]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50591,0.07459,0.05255],"force_p95":0.73473,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.74027,"mean_force":0.68493,"phase_index":2.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.50416,0.08649,0.04252]},{"body_a":"peg","body_b":"channel_base_body","contact_count":368.0,"contact_point_centroid":[0.50605,0.0566,0.00938],"force_p95":0.56531,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60599,"mean_force":0.54653,"phase_index":1.0,"phase_name":"orient_tool","phase_type":"rotate","tcp_position_centroid":[0.52569,0.12521,0.16805]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":108.0,"contact_point_centroid":[0.52505,-0.07827,0.05066],"force_p95":0.25316,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4498,"mean_force":0.09277,"phase_index":5.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.4937,-0.04499,0.06926]}],"total_contact_groups":13},"final_pose_error":0.01498,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50701,-0.07844,0.03377],"final_tcp_position":[0.49333,-0.0475,0.12093],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":17.61464,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":362.0,"n_steps_budget":600.0,"object_pos_end":[0.50613,0.0566,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.56351,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":370.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach_peg","tcp_end":[0.53164,0.11177,0.17294],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":368.0,"n_steps_budget":600.0,"object_pos_end":[0.50614,0.05665,0.03379],"object_pos_start":[0.50613,0.0566,0.03378],"object_to_goal_dist_end":0.13693,"object_to_goal_dist_start":0.13688,"object_z_max":0.03379,"peak_contact_force":0.5439,"phase_name":"orient_tool","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":368.0,"raw_peak_contact_force":0.60599,"tcp_end":[0.52274,0.13587,0.16749],"tcp_start":[0.53164,0.11177,0.17294],"tcp_to_object_dist_end":0.1563,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":398.0,"n_steps_budget":660.0,"object_pos_end":[0.50615,0.05654,0.03374],"object_pos_start":[0.50614,0.05665,0.03379],"object_to_goal_dist_end":0.13683,"object_to_goal_dist_start":0.13693,"object_z_max":0.0338,"peak_contact_force":0.90426,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":400.0,"raw_peak_contact_force":0.90426,"subtask_id":"contact_peg","tcp_end":[0.50409,0.08632,0.04212],"tcp_start":[0.52274,0.13587,0.16749],"tcp_to_object_dist_end":0.031,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":35.0,"n_steps_budget":750.0,"object_pos_end":[0.5059,0.05302,0.0352],"object_pos_start":[0.50615,0.05654,0.03374],"object_to_goal_dist_end":0.13324,"object_to_goal_dist_start":0.13683,"object_z_max":0.03516,"peak_contact_force":17.61464,"phase_name":"contact_engage","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":53.0,"raw_peak_contact_force":9.02785,"subtask_id":"contact_peg","tcp_end":[0.50202,0.0827,0.03893],"tcp_start":[0.50409,0.08632,0.04212],"tcp_to_object_dist_end":0.03017,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50689,-0.07893,0.03597],"object_pos_start":[0.5059,0.05302,0.0352],"object_to_goal_dist_end":0.00805,"object_to_goal_dist_start":0.13324,"object_z_max":0.03616,"peak_contact_force":2.33847,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2037.0,"raw_peak_contact_force":11.81165,"subtask_id":"push_goal","tcp_end":[0.49649,-0.05077,0.0352],"tcp_start":[0.50202,0.0827,0.03893],"tcp_to_object_dist_end":0.03003,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":371.0,"n_steps_budget":600.0,"object_pos_end":[0.50701,-0.07844,0.03377],"object_pos_start":[0.50689,-0.07893,0.03597],"object_to_goal_dist_end":0.0095,"object_to_goal_dist_start":0.00805,"object_z_max":0.03609,"peak_contact_force":0.59861,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":481.0,"raw_peak_contact_force":5.85003,"tcp_end":[0.49333,-0.0475,0.12093],"tcp_start":[0.49649,-0.05077,0.0352],"tcp_to_object_dist_end":0.09349,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```