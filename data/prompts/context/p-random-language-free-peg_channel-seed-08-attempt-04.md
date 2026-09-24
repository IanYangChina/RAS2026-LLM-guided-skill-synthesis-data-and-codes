## Search State

- **Seed**: 8
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → align → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | 0.1997 | 0.38 | ✅ accepted |
| 3 | approach → align → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | 0.0248 | 0.13 | ❌ rejected |
| 2 | approach → align → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | 0.0015 | 0.18 | ✅ accepted |
| 1 | approach → align → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.1407 | 0.16 | ✅ accepted |
| 0 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | 0.2633 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.38 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.200) — your mutation base

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

- **Composite score**: 0.200
- **task_score** (E): 0.382
- **fitness_score**: 0.623  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.217
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.640

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1473 |
| align_behind | 1.00 | 1.00 | 0.1141 |
| descend_contact | 1.00 | 1.00 | 0.0270 |
| push_peg | 0.33 | 1.00 | 0.0494 |
| retract_lift | 1.00 | 1.00 | 0.0860 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.514, 0.136, 0.173) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.537 | 3.526 |
| align_behind | align | 1.00 / step_budget | (0.514, 0.136, 0.173)→(0.501, 0.112, 0.063) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.537 | 0.602 |
| descend_contact | descend | 1.00 / force_exceeded | (0.501, 0.112, 0.063)→(0.499, 0.094, 0.043) | (0.503, 0.080, 0.034)→(0.507, 0.066, 0.036) | 0.160→0.146 | 1.00 / 2.667 | 1351.607 | 11.173 |
| push_peg | push | 0.33 / guard_failure | (0.496, 0.010, 0.036)→(0.495, -0.039, 0.031) | (0.507, 0.066, 0.036)→(0.503, -0.035, 0.032) | 0.146→0.049 | 1.00 / 2.667 | 21.996 | 43.024 |
| retract_lift | retract | 1.00 / step_budget | (0.495, -0.039, 0.031)→(0.492, -0.036, 0.117) | (0.503, -0.035, 0.032)→(0.503, -0.035, 0.031) | 0.049→0.049 | 1.00 / 1.000 | 0.580 | 96.925 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.522
- phase_score: 0.763
- phase_breakdown.push_goal_score: 0.841
- phase_breakdown.approach_peg_score: 0.743
- phase_breakdown.contact_peg_score: 0.590

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.667
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.522
- **Median Q (composite search score)**: 0.190
- **K-run variance**: 0.0035
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.255


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80357,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_speed":0.15859,"approach_peg.approach_speed":0.23255,"descend_contact.contact_force_threshold":20.96909,"descend_contact.descend_speed":0.06084,"push_peg.push_distance":0.16407,"push_peg.push_max_time":13.00264,"push_peg.push_speed":0.0987,"push_peg.push_z_offset":-0.00336,"push_peg.retry_x_offset":0.00245,"push_peg.retry_y_offset":0.00158,"retract_lift.retract_speed":0.26867},"optimized_scores":{"best_composite_score":0.27687,"best_fitness_score":0.66687,"best_task_score":0.52227},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":77.0,"contact_point_centroid":[0.47499,-0.00068,0.04521],"force_p95":222.67075,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":279.4056,"mean_force":118.81805,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.48679,-0.00068,0.04315]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.525,-0.00126,0.05999],"force_p95":57.21239,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":58.4248,"mean_force":47.33884,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.48817,-0.00635,0.0252]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.525,-0.00095,0.06],"force_p95":49.87664,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.98597,"mean_force":48.89266,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.48818,-0.00607,0.02522]},{"body_a":"peg","body_b":"channel_base_body","contact_count":804.0,"contact_point_centroid":[0.50964,0.01812,0.00987],"force_p95":27.06603,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.74137,"mean_force":18.40289,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.488,0.05706,0.02646]},{"body_a":"attachment","body_b":"peg","contact_count":807.0,"contact_point_centroid":[0.498,0.04734,0.04951],"force_p95":32.64514,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.28606,"mean_force":21.88112,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.488,0.05724,0.02646]},{"body_a":"peg","body_b":"link7","contact_count":749.0,"contact_point_centroid":[0.52058,0.03856,0.06179],"force_p95":20.04358,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.30725,"mean_force":13.92567,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.48786,0.05269,0.02624]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":793.0,"contact_point_centroid":[0.5251,0.0309,0.05657],"force_p95":19.62616,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.62207,"mean_force":13.67379,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.48801,0.0566,0.02646]},{"body_a":"peg","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.5205,-0.02069,0.06107],"force_p95":12.26303,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.42086,"mean_force":3.83062,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.48795,-0.00633,0.02553]},{"body_a":"attachment","body_b":"peg","contact_count":298.0,"contact_point_centroid":[0.49577,0.12121,0.05044],"force_p95":8.66161,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.73131,"mean_force":5.19633,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.49038,0.13247,0.04189]},{"body_a":"peg","body_b":"channel_base_body","contact_count":349.0,"contact_point_centroid":[0.50271,-0.03247,0.00945],"force_p95":0.65169,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.47816,"mean_force":0.59848,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.48593,0.00043,0.06867]},{"body_a":"peg","body_b":"channel_base_body","contact_count":404.0,"contact_point_centroid":[0.50412,0.09319,0.00985],"force_p95":8.296,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.57584,"mean_force":4.01506,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.49033,0.13473,0.04419]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":49.0,"contact_point_centroid":[0.52504,0.09472,0.06],"force_p95":4.16992,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.5006,"mean_force":2.91026,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.49152,0.12252,0.03283]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.49756,-0.01614,0.0599],"force_p95":7.26707,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.74052,"mean_force":1.34915,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.48742,-0.00533,0.028]},{"body_a":"peg","body_b":"channel_base_body","contact_count":260.0,"contact_point_centroid":[0.49662,0.11906,0.00936],"force_p95":0.64827,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.57316,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49177,0.19474,0.23018]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49951,0.19998,0.29653]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52514,-0.03226,0.06],"force_p95":0.71663,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.84309,"mean_force":0.21077,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.48815,-0.00636,0.02523]}],"total_contact_groups":17},"final_pose_error":0.01488,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50293,-0.03078,0.03407],"final_tcp_position":[0.48507,-0.00321,0.11098],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":6289.73959,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":285.0,"n_steps_budget":600.0,"object_pos_end":[0.49601,0.11914,0.03382],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19928,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50305,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":284.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_peg","tcp_end":[0.48548,0.17734,0.17229],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15057,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":349.0,"n_steps_budget":600.0,"object_pos_end":[0.49598,0.119,0.0339],"object_pos_start":[0.49601,0.11914,0.03382],"object_to_goal_dist_end":0.19913,"object_to_goal_dist_start":0.19928,"object_z_max":0.03405,"peak_contact_force":0.51126,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":349.0,"raw_peak_contact_force":0.64449,"subtask_id":"contact_peg","tcp_end":[0.49136,0.15129,0.06239],"tcp_start":[0.48548,0.17734,0.17229],"tcp_to_object_dist_end":0.04331,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":443.0,"n_steps_budget":600.0,"object_pos_end":[0.50704,0.09505,0.03601],"object_pos_start":[0.49598,0.119,0.0339],"object_to_goal_dist_end":0.17524,"object_to_goal_dist_start":0.19913,"object_z_max":0.03728,"peak_contact_force":6.11936,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":751.0,"raw_peak_contact_force":12.73131,"subtask_id":"contact_peg","tcp_end":[0.49165,0.12126,0.03159],"tcp_start":[0.49136,0.15129,0.06239],"tcp_to_object_dist_end":0.03072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":828.0,"n_steps_budget":1000.0,"object_pos_end":[0.50644,-0.03003,0.03595],"object_pos_start":[0.50704,0.09505,0.03601],"object_to_goal_dist_end":0.05055,"object_to_goal_dist_start":0.17524,"object_z_max":0.03704,"peak_contact_force":49.98597,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3155.0,"raw_peak_contact_force":49.98597,"subtask_id":"push_goal","tcp_end":[0.48819,-0.00629,0.0252],"tcp_start":[0.48819,-0.0062,0.02521],"tcp_to_object_dist_end":0.03182,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":356.0,"n_steps_budget":600.0,"object_pos_end":[0.50293,-0.03078,0.03407],"object_pos_start":[0.50644,-0.03031,0.03593],"object_to_goal_dist_end":0.04967,"object_to_goal_dist_start":0.05027,"object_z_max":0.03646,"peak_contact_force":0.55167,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":462.0,"raw_peak_contact_force":279.4056,"tcp_end":[0.48507,-0.00321,0.11098],"tcp_start":[0.48819,-0.00629,0.0252],"tcp_to_object_dist_end":0.08363,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.98058,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_speed":0.1703,"approach_peg.approach_speed":0.33406,"descend_contact.contact_force_threshold":14.72362,"descend_contact.descend_speed":0.05222,"push_peg.push_distance":0.18346,"push_peg.push_max_time":15.38425,"push_peg.push_speed":0.09098,"push_peg.push_z_offset":-0.01252,"push_peg.retry_x_offset":0.00129,"push_peg.retry_y_offset":-0.00108,"retract_lift.retract_speed":0.1938},"optimized_scores":{"best_composite_score":0.19007,"best_fitness_score":0.63007,"best_task_score":0.3745},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":396.0,"contact_point_centroid":[0.50415,0.04742,0.04891],"force_p95":34.21949,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.71474,"mean_force":17.65578,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.4994,0.058,0.04951]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50088,0.01954,0.00882],"force_p95":30.06275,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.64454,"mean_force":7.19117,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49889,0.01707,0.04612]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":185.0,"contact_point_centroid":[0.52502,0.0328,0.03991],"force_p95":11.56698,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.51919,"mean_force":7.85129,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49932,0.05741,0.04942]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47498,-0.01785,0.02434],"force_p95":9.11543,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.30876,"mean_force":2.29929,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49839,-0.00673,0.04393]},{"body_a":"peg","body_b":"channel_base_body","contact_count":57.0,"contact_point_centroid":[0.50732,0.05338,0.00948],"force_p95":5.79343,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.11159,"mean_force":0.95241,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50315,0.09266,0.05892]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50413,0.08024,0.05795],"force_p95":5.79236,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.84332,"mean_force":3.84857,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50284,0.09213,0.05808]},{"body_a":"peg","body_b":"channel_base_body","contact_count":321.0,"contact_point_centroid":[0.50565,0.06294,0.00934],"force_p95":0.60722,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.58869,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51486,0.15017,0.23763]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50074,0.19608,0.29625]},{"body_a":"peg","body_b":"channel_base_body","contact_count":373.0,"contact_point_centroid":[0.49709,0.00677,0.00807],"force_p95":0.64358,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6436,"mean_force":0.60602,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49535,-0.05047,0.0828]},{"body_a":"peg","body_b":"channel_base_body","contact_count":326.0,"contact_point_centroid":[0.50586,0.0631,0.00938],"force_p95":0.55188,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54659,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.51441,0.1065,0.11819]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52506,0.05987,0.06],"force_p95":0.10732,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12307,"mean_force":0.06696,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50231,0.09019,0.05563]}],"total_contact_groups":11},"final_pose_error":0.01481,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49811,0.00682,0.02415],"final_tcp_position":[0.49524,-0.05409,0.12627],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":127.89181,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":349.0,"n_steps_budget":600.0,"object_pos_end":[0.50595,0.06295,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54461,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":355.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach_peg","tcp_end":[0.52529,0.11756,0.17343],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15117,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":326.0,"n_steps_budget":600.0,"object_pos_end":[0.50604,0.063,0.0338],"object_pos_start":[0.50595,0.06295,0.0338],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14321,"object_z_max":0.03381,"peak_contact_force":0.54828,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":326.0,"raw_peak_contact_force":0.55501,"subtask_id":"contact_peg","tcp_end":[0.50476,0.09522,0.06323],"tcp_start":[0.52529,0.11756,0.17343],"tcp_to_object_dist_end":0.04365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":57.0,"n_steps_budget":600.0,"object_pos_end":[0.50655,0.06138,0.03573],"object_pos_start":[0.50604,0.063,0.0338],"object_to_goal_dist_end":0.1416,"object_to_goal_dist_start":0.14326,"object_z_max":0.03573,"peak_contact_force":127.89181,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":71.0,"raw_peak_contact_force":6.11159,"subtask_id":"contact_peg","tcp_end":[0.50223,0.08977,0.05515],"tcp_start":[0.50476,0.09522,0.06323],"tcp_to_object_dist_end":0.03466,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49593,0.00682,0.02415],"object_pos_start":[0.50655,0.06138,0.03573],"object_to_goal_dist_end":0.08835,"object_to_goal_dist_start":0.1416,"object_z_max":0.04027,"peak_contact_force":0.56826,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1590.0,"raw_peak_contact_force":38.71474,"subtask_id":"push_goal","tcp_end":[0.49837,-0.05735,0.04038],"tcp_start":[0.50223,0.08977,0.05515],"tcp_to_object_dist_end":0.06624,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":373.0,"n_steps_budget":600.0,"object_pos_end":[0.49811,0.00682,0.02415],"object_pos_start":[0.49593,0.00682,0.02415],"object_to_goal_dist_end":0.08827,"object_to_goal_dist_start":0.08835,"object_z_max":0.02415,"peak_contact_force":0.64358,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":373.0,"raw_peak_contact_force":0.6436,"tcp_end":[0.49524,-0.05409,0.12627],"tcp_start":[0.49837,-0.05735,0.04038],"tcp_to_object_dist_end":0.11894,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69748,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.align_speed":0.17151,"approach_peg.approach_speed":0.23011,"descend_contact.contact_force_threshold":24.04425,"descend_contact.descend_speed":0.02604,"push_peg.push_distance":0.16375,"push_peg.push_max_time":19.13215,"push_peg.push_speed":0.0831,"push_peg.push_z_offset":-0.01141,"push_peg.retry_x_offset":0.00037,"push_peg.retry_y_offset":-0.00057,"retract_lift.retract_speed":0.29999},"optimized_scores":{"best_composite_score":0.13216,"best_fitness_score":0.57216,"best_task_score":0.24955},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":805.0,"contact_point_centroid":[0.50291,-0.00323,0.04269],"force_p95":10.15149,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.3715,"mean_force":4.23248,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49863,0.00844,0.03369]},{"body_a":"peg","body_b":"channel_base_body","contact_count":23.0,"contact_point_centroid":[0.5068,-0.10037,0.05992],"force_p95":38.10358,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.36241,"mean_force":19.34537,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49836,-0.05304,0.02899]},{"body_a":"attachment","body_b":"peg","contact_count":182.0,"contact_point_centroid":[0.50426,0.06419,0.04679],"force_p95":9.70643,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.67726,"mean_force":6.22996,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50235,0.07591,0.04713]},{"body_a":"peg","body_b":"channel_base_body","contact_count":575.0,"contact_point_centroid":[0.50648,-0.03713,0.00994],"force_p95":9.52614,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.78116,"mean_force":5.35847,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49864,0.00843,0.0337]},{"body_a":"peg","body_b":"channel_base_body","contact_count":273.0,"contact_point_centroid":[0.50708,0.03705,0.00985],"force_p95":8.31807,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.68299,"mean_force":4.36447,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50272,0.07879,0.05029]},{"body_a":"peg","body_b":"channel_base_body","contact_count":30.0,"contact_point_centroid":[0.50628,-0.10028,0.06014],"force_p95":8.4762,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.72544,"mean_force":2.99512,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49691,-0.05276,0.03071]},{"body_a":"attachment","body_b":"peg","contact_count":31.0,"contact_point_centroid":[0.50269,-0.06396,0.05136],"force_p95":7.84839,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.71209,"mean_force":2.89854,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49677,-0.05239,0.03164]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":480.0,"contact_point_centroid":[0.52503,-0.02305,0.02222],"force_p95":3.58377,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.78747,"mean_force":1.26352,"phase_index":3.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49849,0.00519,0.0333]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":63.0,"contact_point_centroid":[0.52509,0.04746,0.0487],"force_p95":3.3224,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.97756,"mean_force":1.58447,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50242,0.07728,0.04857]},{"body_a":"peg","body_b":"channel_base_body","contact_count":333.0,"contact_point_centroid":[0.50571,0.05662,0.00934],"force_p95":0.60211,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.59432,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51849,0.14716,0.2378]},{"body_a":"peg","body_b":"channel_base_body","contact_count":343.0,"contact_point_centroid":[0.50664,-0.07967,0.0094],"force_p95":0.62025,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.21312,"mean_force":0.56469,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49499,-0.04642,0.07448]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50109,0.19558,0.29595]},{"body_a":"peg","body_b":"channel_base_body","contact_count":323.0,"contact_point_centroid":[0.50612,0.05668,0.00938],"force_p95":0.56646,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60599,"mean_force":0.54651,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.51818,0.10054,0.11808]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":27.0,"contact_point_centroid":[0.52505,-0.07994,0.05907],"force_p95":0.25747,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56746,"mean_force":0.09282,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49546,-0.04884,0.04146]}],"total_contact_groups":14},"final_pose_error":0.01487,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50694,-0.07957,0.03379],"final_tcp_position":[0.49505,-0.05062,0.11458],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":3920.81012,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":362.0,"n_steps_budget":600.0,"object_pos_end":[0.50613,0.0566,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.56351,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":370.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach_peg","tcp_end":[0.53164,0.11177,0.17294],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":323.0,"n_steps_budget":600.0,"object_pos_end":[0.50616,0.05659,0.03378],"object_pos_start":[0.50613,0.0566,0.03378],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.13688,"object_z_max":0.03379,"peak_contact_force":0.55137,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":323.0,"raw_peak_contact_force":0.60599,"subtask_id":"contact_peg","tcp_end":[0.50573,0.08902,0.06335],"tcp_start":[0.53164,0.11177,0.17294],"tcp_to_object_dist_end":0.04388,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":273.0,"n_steps_budget":1000.0,"object_pos_end":[0.50699,0.04201,0.03727],"object_pos_start":[0.50616,0.05659,0.03378],"object_to_goal_dist_end":0.12224,"object_to_goal_dist_start":0.13687,"object_z_max":0.03735,"peak_contact_force":3920.81012,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":518.0,"raw_peak_contact_force":14.67726,"subtask_id":"contact_peg","tcp_end":[0.50226,0.07094,0.04236],"tcp_start":[0.50573,0.08902,0.06335],"tcp_to_object_dist_end":0.02975,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":939.0,"n_steps_budget":1000.0,"object_pos_end":[0.50686,-0.08236,0.03545],"object_pos_start":[0.50699,0.04201,0.03727],"object_to_goal_dist_end":0.00856,"object_to_goal_dist_start":0.12224,"object_z_max":0.03727,"peak_contact_force":15.43374,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1883.0,"raw_peak_contact_force":40.3715,"subtask_id":"push_goal","tcp_end":[0.49826,-0.05388,0.02873],"tcp_start":[0.4983,-0.05387,0.02878],"tcp_to_object_dist_end":0.0305,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":373.0,"n_steps_budget":600.0,"object_pos_end":[0.50694,-0.07957,0.03379],"object_pos_start":[0.50684,-0.08248,0.0354],"object_to_goal_dist_end":0.00932,"object_to_goal_dist_start":0.00861,"object_z_max":0.03672,"peak_contact_force":0.54447,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":431.0,"raw_peak_contact_force":10.72544,"tcp_end":[0.49505,-0.05062,0.11458],"tcp_start":[0.49826,-0.05388,0.02873],"tcp_to_object_dist_end":0.08664,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```