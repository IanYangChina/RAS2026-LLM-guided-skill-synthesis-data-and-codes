## Search State

- **Seed**: 1
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.4476 | 0.40 | ❌ rejected |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | -0.0080 | 0.27 | ❌ rejected |
| 9 | approach → descend → align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 15 | -0.4213 | 0.29 | ❌ rejected |
| 8 | approach → descend → align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.4345 | 0.47 | ✅ accepted |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.3902 | 0.39 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`
- Frozen object start: [0.5009457299760205, 0.11603709570607482, 0.04]
- Frozen task target: [0.5009457299760205, -0.04396290429392519, 0.04]
- Goal object position: (0.5009457299760205, -0.04396290429392519, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5009457299760205, 0.11603709570607482, 0.04)
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
  frozen_object_start: [0.5009, 0.116, 0.04]
  frozen_task_target: [0.5009, -0.044, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5009457299760205, 0.11603709570607482, 0.04]}
  frozen_targets: {'channel_exit': [0.5009457299760205, -0.04396290429392519, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a

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
| `object` | offset from object initial position (0.5009457299760205, 0.11603709570607482, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5009457299760205, -0.04396290429392519, 0.04) | final destination targets |
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

## Current Skill (Q=-0.448) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.05
  weight: 0.3
- id: push_channel
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.1
    - 0.15
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
    approach_y:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: reach_pre_contact
- id: descend_safe
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.1
    - 0.09
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    descend_y:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: reach_pre_contact
- id: align_to_peg
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_pre_contact
- id: descend_final
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_final_speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    descend_height:
      type: scalar
      range:
      - -0.01
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_pre_contact
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.18
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    force_guard_threshold:
      type: scalar
      range:
      - 30.0
      - 39.0
      default: 38.0
      binds_to:
      - path: guards.force_guard.threshold
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.25
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_max_time:
      type: scalar
      range:
      - 3.0
      - 10.0
      default: 6.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 38.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: push_channel
- id: retract_1
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
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_channel

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.1, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_y: status=consumed; consumers=target.offset.y (replace)
- **descend_safe** (`descend`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.1, 0.09], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_y: status=consumed; consumers=target.offset.y (replace)
- **align_to_peg** (`align`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **descend_final** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_final_speed: status=consumed; consumers=generator.speed (replace)
    - descend_height: status=consumed; consumers=target.offset.z (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.18, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_guard_threshold: status=consumed; consumers=guards.force_guard.threshold (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_max_time: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=38.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.448
- **task_score** (E): 0.402
- **fitness_score**: 0.372  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.820

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1555 |
| descend_safe | 1.00 | 1.00 | 0.0791 |
| align_to_peg | 1.00 | 1.00 | 0.0338 |
| descend_final | 1.00 | 1.00 | 0.0379 |
| push_1 | 0.67 | 1.00 | 0.0735 |
| retract_1 | 1.00 | 1.00 | 0.1830 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.149, 0.158) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.539 | 2.857 |
| descend_safe | descend | 1.00 / step_budget | (0.497, 0.149, 0.158)→(0.496, 0.149, 0.095) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.561 | 0.583 |
| align_to_peg | align | 1.00 / step_budget | (0.496, 0.149, 0.095)→(0.493, 0.118, 0.084) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.558 | 0.568 |
| descend_final | descend | 1.00 / step_budget | (0.493, 0.118, 0.084)→(0.492, 0.111, 0.047) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.559 | 0.576 |
| push_1 | push | 0.67 / time_limit | (0.497, 0.084, 0.046)→(0.510, 0.011, 0.043) | (0.497, 0.080, 0.034)→(0.507, -0.020, 0.038) | 0.160→0.061 | 1.00 / 2.667 | 18.591 | 38.959 |
| retract_1 | retract | 1.00 / step_budget | (0.510, 0.011, 0.043)→(0.507, 0.011, 0.226) | (0.507, -0.020, 0.038)→(0.498, -0.036, 0.026) | 0.061→0.050 | 1.00 / 1.667 | 0.572 | 22.769 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.831
- alignment_error: None
- force_efficiency: 0.481
- terminal_score: 0.461
- phase_score: 0.435
- phase_breakdown.push_channel_score: 0.451
- phase_breakdown.reach_pre_contact_score: 0.398

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.446
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.511
- **Median Q (composite search score)**: -0.448
- **K-run variance**: 0.0036
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.251


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a904e23429ae963dd2788b3e8d0575d9ce341e1daddfe013fbb1224c3e0c850e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6bee39a4c127c6d39ee1365e3969a50bb09484f7e2580b1a3dc4d8c4ae20213b`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55882,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_peg.align_speed":0.14475,"approach_1.approach_speed":0.24716,"approach_1.approach_y":0.08389,"descend_final.descend_final_speed":0.10018,"descend_final.descend_height":0.00837,"descend_safe.descend_speed":0.0913,"descend_safe.descend_y":0.16377,"push_1.force_guard_threshold":39.51714,"push_1.push_distance":0.1955,"push_1.push_lateral_x":0.04187,"push_1.push_max_time":7.49018,"push_1.push_speed":0.06501,"retract_1.retract_height":0.20996,"retract_1.retract_speed":0.21298},"optimized_scores":{"best_composite_score":-0.52084,"best_fitness_score":0.29916,"best_task_score":0.51114},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52501,0.06513,0.06],"force_p95":60.96462,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.4007,"mean_force":38.18385,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51058,0.06514,0.04687]},{"body_a":"attachment","body_b":"peg","contact_count":767.0,"contact_point_centroid":[0.5041,0.09371,0.04656],"force_p95":28.63438,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.32546,"mean_force":14.28648,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50176,0.1052,0.04669]},{"body_a":"peg","body_b":"channel_base_body","contact_count":791.0,"contact_point_centroid":[0.50628,0.0768,0.00982],"force_p95":24.98337,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.3447,"mean_force":12.47533,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50152,0.10669,0.04678]},{"body_a":"peg","body_b":"channel_base_body","contact_count":581.0,"contact_point_centroid":[0.49681,0.03526,0.00814],"force_p95":0.74611,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.30881,"mean_force":0.72579,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50775,0.06436,0.13793]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50964,0.05271,0.04698],"force_p95":15.37693,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.85966,"mean_force":3.74724,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51018,0.06466,0.04671]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":403.0,"contact_point_centroid":[0.52513,0.0593,0.04678],"force_p95":11.6297,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.63574,"mean_force":7.96263,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50409,0.09442,0.04672]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":16.0,"contact_point_centroid":[0.47492,0.00981,0.02451],"force_p95":9.60225,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.6608,"mean_force":3.12362,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50726,0.06432,0.08265]},{"body_a":"peg","body_b":"channel_base_body","contact_count":490.0,"contact_point_centroid":[0.50086,0.116,0.00936],"force_p95":0.6223,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56074,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49782,0.14428,0.22447]},{"body_a":"peg","body_b":"channel_base_body","contact_count":354.0,"contact_point_centroid":[0.50093,0.11603,0.00943],"force_p95":0.59708,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64271,"mean_force":0.54193,"phase_index":1.0,"phase_name":"descend_safe","phase_type":"descend","tcp_position_centroid":[0.4957,0.1224,0.12268]},{"body_a":"peg","body_b":"channel_base_body","contact_count":134.0,"contact_point_centroid":[0.50083,0.11602,0.0094],"force_p95":0.61377,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62556,"mean_force":0.54479,"phase_index":3.0,"phase_name":"descend_final","phase_type":"descend","tcp_position_centroid":[0.49537,0.14993,0.06997]},{"body_a":"peg","body_b":"channel_base_body","contact_count":25.0,"contact_point_centroid":[0.50259,0.11534,0.00942],"force_p95":0.59498,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59918,"mean_force":0.54522,"phase_index":2.0,"phase_name":"align_to_peg","phase_type":"align","tcp_position_centroid":[0.49583,0.15446,0.09073]}],"total_contact_groups":11},"final_pose_error":0.0183,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49887,0.03425,0.02409],"final_tcp_position":[0.50837,0.06443,0.23847],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":69.4007,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":506.0,"n_steps_budget":600.0,"object_pos_end":[0.50095,0.11603,0.03394],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19613,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.52071,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":490.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_pre_contact","tcp_end":[0.49713,0.09143,0.1557],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12428,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":354.0,"n_steps_budget":690.0,"object_pos_end":[0.50097,0.11601,0.03391],"object_pos_start":[0.50095,0.11603,0.03394],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19613,"object_z_max":0.03398,"peak_contact_force":0.58377,"phase_name":"descend_safe","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":354.0,"raw_peak_contact_force":0.64271,"subtask_id":"reach_pre_contact","tcp_end":[0.49632,0.15478,0.09231],"tcp_start":[0.49713,0.09143,0.1557],"tcp_to_object_dist_end":0.07025,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":25.0,"n_steps_budget":600.0,"object_pos_end":[0.50091,0.11601,0.03383],"object_pos_start":[0.50097,0.11601,0.03391],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19611,"object_z_max":0.03391,"peak_contact_force":0.57953,"phase_name":"align_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":25.0,"raw_peak_contact_force":0.59918,"subtask_id":"reach_pre_contact","tcp_end":[0.4959,0.15307,0.08855],"tcp_start":[0.49632,0.15478,0.09231],"tcp_to_object_dist_end":0.06628,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":134.0,"n_steps_budget":600.0,"object_pos_end":[0.5009,0.11608,0.03386],"object_pos_start":[0.50091,0.11601,0.03383],"object_to_goal_dist_end":0.19618,"object_to_goal_dist_start":0.19611,"object_z_max":0.03386,"peak_contact_force":0.59074,"phase_name":"descend_final","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":134.0,"raw_peak_contact_force":0.62556,"subtask_id":"reach_pre_contact","tcp_end":[0.49611,0.14701,0.05075],"tcp_start":[0.4959,0.15307,0.08855],"tcp_to_object_dist_end":0.03557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":799.0,"n_steps_budget":1000.0,"object_pos_end":[0.50682,0.03875,0.03212],"object_pos_start":[0.5009,0.11608,0.03386],"object_to_goal_dist_end":0.1192,"object_to_goal_dist_start":0.19618,"object_z_max":0.04054,"peak_contact_force":19.6457,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1968.0,"raw_peak_contact_force":69.4007,"subtask_id":"push_channel","tcp_end":[0.51046,0.06476,0.04669],"tcp_start":[0.51049,0.06479,0.04674],"tcp_to_object_dist_end":0.03004,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":581.0,"n_steps_budget":630.0,"object_pos_end":[0.49887,0.03425,0.02409],"object_pos_start":[0.50675,0.03861,0.03192],"object_to_goal_dist_end":0.11536,"object_to_goal_dist_start":0.11908,"object_z_max":0.03192,"peak_contact_force":0.72551,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":604.0,"raw_peak_contact_force":20.30881,"subtask_id":"push_channel","tcp_end":[0.50837,0.06443,0.23847],"tcp_start":[0.51046,0.06476,0.04669],"tcp_to_object_dist_end":0.2167,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8416ac3bebb4dbec2abbf751596843a33db171fd8d70765023f3b940d846bd0c`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72993,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_peg.align_speed":0.10013,"approach_1.approach_speed":0.22106,"approach_1.approach_y":0.18345,"descend_final.descend_final_speed":0.08776,"descend_final.descend_height":0.00233,"descend_safe.descend_speed":0.1566,"descend_safe.descend_y":0.11775,"push_1.force_guard_threshold":38.83538,"push_1.push_distance":0.17645,"push_1.push_lateral_x":0.03514,"push_1.push_max_time":9.95704,"push_1.push_speed":0.06904,"retract_1.retract_height":0.16837,"retract_1.retract_speed":0.1767},"optimized_scores":{"best_composite_score":-0.37431,"best_fitness_score":0.44569,"best_task_score":0.46124},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.5087,-0.0236,0.04126],"force_p95":18.22134,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.94558,"mean_force":4.07751,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50875,-0.01182,0.04109]},{"body_a":"peg","body_b":"channel_base_body","contact_count":565.0,"contact_point_centroid":[0.50067,-0.06528,0.00842],"force_p95":0.77105,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.88983,"mean_force":0.66797,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50612,-0.01164,0.11504]},{"body_a":"attachment","body_b":"peg","contact_count":923.0,"contact_point_centroid":[0.5022,0.02771,0.04172],"force_p95":20.95687,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.59146,"mean_force":11.30871,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4985,0.03886,0.04071]},{"body_a":"peg","body_b":"channel_base_body","contact_count":893.0,"contact_point_centroid":[0.50622,0.00247,0.00991],"force_p95":16.84606,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.08869,"mean_force":9.48467,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49839,0.0399,0.04082]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":762.0,"contact_point_centroid":[0.52523,0.00154,0.03486],"force_p95":12.0711,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.48907,"mean_force":6.93399,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50029,0.02973,0.04064]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52502,-0.04536,0.02381],"force_p95":5.60652,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.91177,"mean_force":1.98485,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50639,-0.01162,0.07508]},{"body_a":"peg","body_b":"channel_base_body","contact_count":362.0,"contact_point_centroid":[0.49569,0.06401,0.00936],"force_p95":0.6243,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56893,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49793,0.19129,0.22532]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49965,0.19928,0.29655]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":23.0,"contact_point_centroid":[0.47461,-0.06688,0.05247],"force_p95":0.85333,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.98958,"mean_force":0.29084,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50658,-0.01177,0.04953]},{"body_a":"peg","body_b":"channel_base_body","contact_count":137.0,"contact_point_centroid":[0.49527,0.06366,0.0094],"force_p95":0.55014,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55213,"mean_force":0.54533,"phase_index":3.0,"phase_name":"descend_final","phase_type":"descend","tcp_position_centroid":[0.4909,0.09955,0.06444]},{"body_a":"peg","body_b":"channel_base_body","contact_count":290.0,"contact_point_centroid":[0.49488,0.06392,0.0094],"force_p95":0.5502,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5516,"mean_force":0.54573,"phase_index":1.0,"phase_name":"descend_safe","phase_type":"descend","tcp_position_centroid":[0.49582,0.15538,0.12599]},{"body_a":"peg","body_b":"channel_base_body","contact_count":108.0,"contact_point_centroid":[0.49568,0.06383,0.0094],"force_p95":0.5506,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55124,"mean_force":0.5454,"phase_index":2.0,"phase_name":"align_to_peg","phase_type":"align","tcp_position_centroid":[0.49375,0.11489,0.0881]}],"total_contact_groups":12},"final_pose_error":0.01562,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49771,-0.06915,0.02414],"final_tcp_position":[0.50647,-0.01162,0.19384],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":25.94558,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":389.0,"n_steps_budget":600.0,"object_pos_end":[0.49494,0.06397,0.03392],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14419,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54583,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":390.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_pre_contact","tcp_end":[0.49727,0.18399,0.15943],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":290.0,"n_steps_budget":600.0,"object_pos_end":[0.4949,0.06375,0.03396],"object_pos_start":[0.49494,0.06397,0.03392],"object_to_goal_dist_end":0.14397,"object_to_goal_dist_start":0.14419,"object_z_max":0.03396,"peak_contact_force":0.54936,"phase_name":"descend_safe","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":290.0,"raw_peak_contact_force":0.5516,"subtask_id":"reach_pre_contact","tcp_end":[0.49628,0.12568,0.09433],"tcp_start":[0.49727,0.18399,0.15943],"tcp_to_object_dist_end":0.08649,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":108.0,"n_steps_budget":600.0,"object_pos_end":[0.49487,0.06399,0.03398],"object_pos_start":[0.4949,0.06375,0.03396],"object_to_goal_dist_end":0.14421,"object_to_goal_dist_start":0.14397,"object_z_max":0.03398,"peak_contact_force":0.54585,"phase_name":"align_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":108.0,"raw_peak_contact_force":0.55124,"subtask_id":"reach_pre_contact","tcp_end":[0.49222,0.10325,0.08302],"tcp_start":[0.49628,0.12568,0.09433],"tcp_to_object_dist_end":0.06287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":137.0,"n_steps_budget":600.0,"object_pos_end":[0.49497,0.06411,0.034],"object_pos_start":[0.49487,0.06399,0.03398],"object_to_goal_dist_end":0.14432,"object_to_goal_dist_start":0.14421,"object_z_max":0.034,"peak_contact_force":0.54141,"phase_name":"descend_final","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":137.0,"raw_peak_contact_force":0.55213,"subtask_id":"reach_pre_contact","tcp_end":[0.49072,0.0959,0.04504],"tcp_start":[0.49222,0.10325,0.08302],"tcp_to_object_dist_end":0.03392,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50705,-0.04545,0.04036],"object_pos_start":[0.49497,0.06411,0.034],"object_to_goal_dist_end":0.03526,"object_to_goal_dist_start":0.14432,"object_z_max":0.04063,"peak_contact_force":18.84174,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2578.0,"raw_peak_contact_force":24.59146,"subtask_id":"push_channel","tcp_end":[0.50908,-0.01163,0.04087],"tcp_start":[0.49072,0.0959,0.04504],"tcp_to_object_dist_end":0.03388,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":572.0,"n_steps_budget":630.0,"object_pos_end":[0.49771,-0.06915,0.02414],"object_pos_start":[0.50705,-0.04545,0.04036],"object_to_goal_dist_end":0.01935,"object_to_goal_dist_start":0.03526,"object_z_max":0.04054,"peak_contact_force":0.59389,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":606.0,"raw_peak_contact_force":25.94558,"subtask_id":"push_channel","tcp_end":[0.50647,-0.01162,0.19384],"tcp_start":[0.50908,-0.01163,0.04087],"tcp_to_object_dist_end":0.17939,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0188121de1b8142d5ff7a7406b62c43adf6da5520b986a997e46ef53b7d11bf9`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91176,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_peg.align_speed":0.12184,"approach_1.approach_speed":0.36273,"approach_1.approach_y":0.16897,"descend_final.descend_final_speed":0.06337,"descend_final.descend_height":0.00258,"descend_safe.descend_speed":0.11504,"descend_safe.descend_y":0.16768,"push_1.force_guard_threshold":39.17207,"push_1.push_distance":0.15233,"push_1.push_lateral_x":0.03125,"push_1.push_max_time":12.01059,"push_1.push_speed":0.06937,"retract_1.retract_height":0.22412,"retract_1.retract_speed":0.30768},"optimized_scores":{"best_composite_score":-0.44771,"best_fitness_score":0.37229,"best_task_score":0.23314},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":914.0,"contact_point_centroid":[0.50184,0.02116,0.04201],"force_p95":18.41408,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.88586,"mean_force":9.85247,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49815,0.03234,0.04072]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.50864,-0.03077,0.04117],"force_p95":14.09382,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.05381,"mean_force":2.74537,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50869,-0.01895,0.04103]},{"body_a":"peg","body_b":"channel_base_body","contact_count":538.0,"contact_point_centroid":[0.50167,-0.05002,0.00997],"force_p95":0.54862,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.96628,"mean_force":0.45481,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50642,-0.01873,0.13717]},{"body_a":"peg","body_b":"channel_base_body","contact_count":869.0,"contact_point_centroid":[0.5059,-0.00464,0.00993],"force_p95":14.81602,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.45599,"mean_force":8.52847,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49799,0.03358,0.04083]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":742.0,"contact_point_centroid":[0.5252,-0.0057,0.03529],"force_p95":10.28698,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.91665,"mean_force":6.02882,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50018,0.02222,0.04063]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52507,-0.03721,0.02055],"force_p95":4.2994,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.61182,"mean_force":2.33243,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50902,-0.01881,0.04077]},{"body_a":"peg","body_b":"channel_base_body","contact_count":366.0,"contact_point_centroid":[0.49446,0.05907,0.00934],"force_p95":0.60447,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.58619,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49791,0.18447,0.22488]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49955,0.19877,0.29526]},{"body_a":"peg","body_b":"channel_base_body","contact_count":406.0,"contact_point_centroid":[0.50708,-0.10004,0.02479],"force_p95":0.59137,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.54305,"mean_force":0.27955,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50636,-0.0187,0.15728]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":373.0,"contact_point_centroid":[0.47497,-0.09164,0.03474],"force_p95":0.36286,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.94377,"mean_force":0.16143,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50635,-0.01871,0.1534]},{"body_a":"peg","body_b":"channel_base_body","contact_count":304.0,"contact_point_centroid":[0.49405,0.05927,0.00939],"force_p95":0.55017,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54605,"phase_index":2.0,"phase_name":"align_to_peg","phase_type":"align","tcp_position_centroid":[0.49243,0.13248,0.08825]},{"body_a":"peg","body_b":"channel_base_body","contact_count":192.0,"contact_point_centroid":[0.4942,0.05851,0.00939],"force_p95":0.55084,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55326,"mean_force":0.54621,"phase_index":1.0,"phase_name":"descend_safe","phase_type":"descend","tcp_position_centroid":[0.49601,0.1689,0.12915]},{"body_a":"peg","body_b":"channel_base_body","contact_count":131.0,"contact_point_centroid":[0.49459,0.05889,0.00939],"force_p95":0.54984,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55091,"mean_force":0.54575,"phase_index":3.0,"phase_name":"descend_final","phase_type":"descend","tcp_position_centroid":[0.48988,0.09435,0.06353]}],"total_contact_groups":13},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49701,-0.07229,0.02841],"final_tcp_position":[0.50711,-0.01873,0.24512],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":22.88586,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":395.0,"n_steps_budget":600.0,"object_pos_end":[0.49404,0.0589,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13916,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.5506,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":401.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_pre_contact","tcp_end":[0.49725,0.17092,0.15915],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1681,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":192.0,"n_steps_budget":600.0,"object_pos_end":[0.49425,0.05899,0.03387],"object_pos_start":[0.49404,0.0589,0.03385],"object_to_goal_dist_end":0.13924,"object_to_goal_dist_start":0.13916,"object_z_max":0.03388,"peak_contact_force":0.55125,"phase_name":"descend_safe","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":192.0,"raw_peak_contact_force":0.55326,"subtask_id":"reach_pre_contact","tcp_end":[0.49623,0.16727,0.09896],"tcp_start":[0.49725,0.17092,0.15915],"tcp_to_object_dist_end":0.12636,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":304.0,"n_steps_budget":600.0,"object_pos_end":[0.49398,0.05886,0.03391],"object_pos_start":[0.49425,0.05899,0.03387],"object_to_goal_dist_end":0.13913,"object_to_goal_dist_start":0.13924,"object_z_max":0.03391,"peak_contact_force":0.5493,"phase_name":"align_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":304.0,"raw_peak_contact_force":0.55382,"subtask_id":"reach_pre_contact","tcp_end":[0.49105,0.09789,0.08105],"tcp_start":[0.49623,0.16727,0.09896],"tcp_to_object_dist_end":0.06127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":131.0,"n_steps_budget":600.0,"object_pos_end":[0.49397,0.05907,0.03393],"object_pos_start":[0.49398,0.05886,0.03391],"object_to_goal_dist_end":0.13933,"object_to_goal_dist_start":0.13913,"object_z_max":0.03393,"peak_contact_force":0.54501,"phase_name":"descend_final","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":131.0,"raw_peak_contact_force":0.55091,"subtask_id":"reach_pre_contact","tcp_end":[0.48976,0.09083,0.04509],"tcp_start":[0.49105,0.09789,0.08105],"tcp_to_object_dist_end":0.03392,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50717,-0.05197,0.04057],"object_pos_start":[0.49397,0.05907,0.03393],"object_to_goal_dist_end":0.02894,"object_to_goal_dist_start":0.13933,"object_z_max":0.04066,"peak_contact_force":17.28488,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2525.0,"raw_peak_contact_force":22.88586,"subtask_id":"push_channel","tcp_end":[0.50906,-0.01872,0.04078],"tcp_start":[0.48976,0.09083,0.04509],"tcp_to_object_dist_end":0.0333,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":561.0,"n_steps_budget":600.0,"object_pos_end":[0.49701,-0.07229,0.02841],"object_pos_start":[0.50717,-0.05197,0.04057],"object_to_goal_dist_end":0.01423,"object_to_goal_dist_start":0.02894,"object_z_max":0.04081,"peak_contact_force":0.39705,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1330.0,"raw_peak_contact_force":22.05381,"subtask_id":"push_channel","tcp_end":[0.50711,-0.01873,0.24512],"tcp_start":[0.50906,-0.01872,0.04078],"tcp_to_object_dist_end":0.22346,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```