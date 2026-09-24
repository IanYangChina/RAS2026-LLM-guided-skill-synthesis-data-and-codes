## Search State

- **Seed**: 1
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.4345 | 0.47 | ✅ accepted |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.3902 | 0.39 | ✅ accepted |
| 6 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | time_limit | pose_tolerance | 14 | -0.4785 | 0.11 | ❌ rejected |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.1871 | 0.34 | ✅ accepted |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.1244 | 0.23 | ❌ rejected |

**Proposal policy**: task_score is 0.47 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.435) — your mutation base

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

- **Composite score**: -0.435
- **task_score** (E): 0.470
- **fitness_score**: 0.335  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.770

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1599 |
| descend_safe | 1.00 | 1.00 | 0.0742 |
| align_to_peg | 1.00 | 1.00 | 0.0218 |
| descend_final | 1.00 | 1.00 | 0.0399 |
| push_1 | 0.67 | 1.00 | 0.0840 |
| retract_1 | 1.00 | 1.00 | 0.1717 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.128, 0.158) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.557 | 2.857 |
| descend_safe | descend | 1.00 / step_budget | (0.497, 0.128, 0.158)→(0.496, 0.120, 0.096) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.531 | 0.581 |
| align_to_peg | align | 1.00 / step_budget | (0.496, 0.120, 0.096)→(0.493, 0.112, 0.084) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.545 | 0.576 |
| descend_final | descend | 1.00 / step_budget | (0.493, 0.112, 0.084)→(0.494, 0.111, 0.045) | (0.497, 0.080, 0.034)→(0.497, 0.077, 0.034) | 0.160→0.157 | 1.00 / 1.333 | 0.833 | 52.506 |
| push_1 | push | 0.67 / time_limit | (0.493, 0.088, 0.044)→(0.490, 0.004, 0.041) | (0.497, 0.077, 0.034)→(0.508, -0.021, 0.039) | 0.157→0.060 | 1.00 / 2.667 | 23.344 | 33.422 |
| retract_1 | retract | 1.00 / step_budget | (0.490, 0.004, 0.041)→(0.488, 0.004, 0.212) | (0.508, -0.021, 0.039)→(0.501, -0.035, 0.027) | 0.060→0.047 | 1.00 / 1.000 | 0.552 | 124.285 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.564
- terminal_score: 0.974
- phase_score: 0.113
- phase_breakdown.push_channel_score: 0.000
- phase_breakdown.reach_pre_contact_score: 0.376

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.457
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.974
- **Median Q (composite search score)**: -0.494
- **K-run variance**: 0.0074
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.283


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79412,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_peg.align_speed":0.11259,"approach_1.approach_speed":0.25653,"approach_1.approach_y":0.11598,"descend_final.descend_final_speed":0.12726,"descend_final.descend_height":-0.00097,"descend_safe.descend_speed":0.12177,"descend_safe.descend_y":0.1761,"push_1.force_guard_threshold":35.98362,"push_1.push_distance":0.19182,"push_1.push_max_time":7.63221,"push_1.push_speed":0.1065,"retract_1.retract_height":0.19135,"retract_1.retract_speed":0.22335},"optimized_scores":{"best_composite_score":-0.3129,"best_fitness_score":0.4571,"best_task_score":0.97354},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":768.0,"contact_point_centroid":[0.49854,0.05005,0.03909],"force_p95":13.26683,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.82167,"mean_force":4.17069,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49244,0.06051,0.03688]},{"body_a":"peg","body_b":"channel_base_body","contact_count":569.0,"contact_point_centroid":[0.50615,0.02437,0.0099],"force_p95":11.15897,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.08458,"mean_force":4.85262,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49256,0.06585,0.03702]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":730.0,"contact_point_centroid":[0.52512,0.03123,0.02785],"force_p95":6.94655,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.48115,"mean_force":2.32865,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49237,0.05646,0.03681]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.52505,-0.05084,0.06],"force_p95":2.38372,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.13674,"mean_force":0.34188,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49045,-0.02336,0.04298]},{"body_a":"attachment","body_b":"peg","contact_count":32.0,"contact_point_centroid":[0.49827,-0.03368,0.05892],"force_p95":1.18218,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.58219,"mean_force":0.40037,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49018,-0.02323,0.04646]},{"body_a":"peg","body_b":"channel_base_body","contact_count":435.0,"contact_point_centroid":[0.50085,0.11606,0.00936],"force_p95":0.63079,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56272,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49787,0.16012,0.22575]},{"body_a":"peg","body_b":"channel_base_body","contact_count":542.0,"contact_point_centroid":[0.50693,-0.05033,0.00947],"force_p95":0.56878,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.07027,"mean_force":0.53881,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48959,-0.023,0.12088]},{"body_a":"peg","body_b":"channel_base_body","contact_count":290.0,"contact_point_centroid":[0.50102,0.11601,0.00943],"force_p95":0.60351,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63808,"mean_force":0.54149,"phase_index":1.0,"phase_name":"descend_safe","phase_type":"descend","tcp_position_centroid":[0.49581,0.14405,0.12475]},{"body_a":"peg","body_b":"channel_base_body","contact_count":75.0,"contact_point_centroid":[0.50079,0.11582,0.00939],"force_p95":0.61639,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62405,"mean_force":0.54611,"phase_index":2.0,"phase_name":"align_to_peg","phase_type":"align","tcp_position_centroid":[0.49565,0.1621,0.08889]},{"body_a":"peg","body_b":"channel_base_body","contact_count":151.0,"contact_point_centroid":[0.50102,0.11615,0.00942],"force_p95":0.59376,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61572,"mean_force":0.54208,"phase_index":3.0,"phase_name":"descend_final","phase_type":"descend","tcp_position_centroid":[0.49549,0.15085,0.06304]}],"total_contact_groups":10},"final_pose_error":0.0174,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50648,-0.0482,0.03388],"final_tcp_position":[0.49007,-0.02296,0.21093],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":21.82167,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":451.0,"n_steps_budget":600.0,"object_pos_end":[0.50092,0.11608,0.03386],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19618,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.57518,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":435.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_pre_contact","tcp_end":[0.49718,0.12209,0.15733],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":290.0,"n_steps_budget":600.0,"object_pos_end":[0.50096,0.11603,0.03382],"object_pos_start":[0.50092,0.11608,0.03386],"object_to_goal_dist_end":0.19613,"object_to_goal_dist_start":0.19618,"object_z_max":0.03398,"peak_contact_force":0.50368,"phase_name":"descend_safe","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":290.0,"raw_peak_contact_force":0.63808,"subtask_id":"reach_pre_contact","tcp_end":[0.4963,0.16779,0.09401],"tcp_start":[0.49718,0.12209,0.15733],"tcp_to_object_dist_end":0.07952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":75.0,"n_steps_budget":600.0,"object_pos_end":[0.50096,0.11605,0.0338],"object_pos_start":[0.50096,0.11603,0.03382],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19613,"object_z_max":0.03382,"peak_contact_force":0.5381,"phase_name":"align_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":75.0,"raw_peak_contact_force":0.62405,"subtask_id":"reach_pre_contact","tcp_end":[0.49613,0.15472,0.08419],"tcp_start":[0.4963,0.16779,0.09401],"tcp_to_object_dist_end":0.06371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":151.0,"n_steps_budget":600.0,"object_pos_end":[0.5009,0.11604,0.03396],"object_pos_start":[0.50096,0.11605,0.0338],"object_to_goal_dist_end":0.19613,"object_to_goal_dist_start":0.19615,"object_z_max":0.03397,"peak_contact_force":0.57604,"phase_name":"descend_final","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":151.0,"raw_peak_contact_force":0.61572,"subtask_id":"reach_pre_contact","tcp_end":[0.4962,0.14723,0.04134],"tcp_start":[0.49613,0.15472,0.08419],"tcp_to_object_dist_end":0.0324,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50681,-0.04912,0.03679],"object_pos_start":[0.5009,0.11604,0.03396],"object_to_goal_dist_end":0.03179,"object_to_goal_dist_start":0.19613,"object_z_max":0.0371,"peak_contact_force":0.19282,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2067.0,"raw_peak_contact_force":21.82167,"subtask_id":"push_channel","tcp_end":[0.49237,-0.02302,0.03683],"tcp_start":[0.4962,0.14723,0.04134],"tcp_to_object_dist_end":0.02983,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":545.0,"n_steps_budget":600.0,"object_pos_end":[0.50648,-0.0482,0.03388],"object_pos_start":[0.50681,-0.04912,0.03679],"object_to_goal_dist_end":0.03302,"object_to_goal_dist_start":0.03179,"object_z_max":0.03679,"peak_contact_force":0.54884,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":594.0,"raw_peak_contact_force":3.13674,"subtask_id":"push_channel","tcp_end":[0.49007,-0.02296,0.21093],"tcp_start":[0.49237,-0.02302,0.03683],"tcp_to_object_dist_end":0.17959,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57692,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_peg.align_speed":0.16763,"approach_1.approach_speed":0.34341,"approach_1.approach_y":0.14295,"descend_final.descend_final_speed":0.04928,"descend_final.descend_height":0.00655,"descend_safe.descend_speed":0.12515,"descend_safe.descend_y":0.12488,"push_1.force_guard_threshold":35.47386,"push_1.push_distance":0.17754,"push_1.push_max_time":7.6438,"push_1.push_speed":0.05904,"retract_1.retract_height":0.16566,"retract_1.retract_speed":0.32191},"optimized_scores":{"best_composite_score":-0.49379,"best_fitness_score":0.27621,"best_task_score":0.2978},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":50.0,"contact_point_centroid":[0.47496,0.02876,0.05277],"force_p95":309.43929,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":331.43397,"mean_force":195.42033,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48673,0.02876,0.05064]},{"body_a":"attachment","body_b":"peg","contact_count":597.0,"contact_point_centroid":[0.49498,0.04873,0.04532],"force_p95":30.49894,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.85547,"mean_force":11.87934,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48699,0.05727,0.04479]},{"body_a":"peg","body_b":"channel_base_body","contact_count":648.0,"contact_point_centroid":[0.50615,0.02945,0.00986],"force_p95":21.13084,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.48661,"mean_force":8.08936,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48716,0.0605,0.04496]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":57.0,"contact_point_centroid":[0.52554,0.0166,0.03272],"force_p95":35.05828,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.29256,"mean_force":7.00697,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48676,0.02879,0.0497]},{"body_a":"attachment","body_b":"peg","contact_count":17.0,"contact_point_centroid":[0.49656,0.02295,0.04406],"force_p95":38.31521,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.44496,"mean_force":21.74095,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48673,0.02899,0.04566]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":426.0,"contact_point_centroid":[0.5254,0.03024,0.03629],"force_p95":26.81305,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.55479,"mean_force":11.77094,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48684,0.04835,0.04472]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":48.0,"contact_point_centroid":[0.475,0.03571,0.04703],"force_p95":25.53683,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":31.00529,"mean_force":18.39493,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4868,0.03574,0.04489]},{"body_a":"peg","body_b":"channel_base_body","contact_count":527.0,"contact_point_centroid":[0.4995,-0.00416,0.00843],"force_p95":2.05158,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.85132,"mean_force":1.00101,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48439,0.02889,0.11884]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.47499,-0.03308,0.02425],"force_p95":8.04945,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.19142,"mean_force":3.2529,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48409,0.02897,0.17367]},{"body_a":"peg","body_b":"channel_base_body","contact_count":388.0,"contact_point_centroid":[0.49541,0.06393,0.00936],"force_p95":0.6113,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.5674,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49788,0.17227,0.2248]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49961,0.19854,0.29656]},{"body_a":"peg","body_b":"channel_base_body","contact_count":122.0,"contact_point_centroid":[0.49605,0.06372,0.0094],"force_p95":0.55084,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5516,"mean_force":0.5455,"phase_index":2.0,"phase_name":"align_to_peg","phase_type":"align","tcp_position_centroid":[0.49354,0.11632,0.09045]},{"body_a":"peg","body_b":"channel_base_body","contact_count":126.0,"contact_point_centroid":[0.49407,0.06367,0.0094],"force_p95":0.5501,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55124,"mean_force":0.54535,"phase_index":3.0,"phase_name":"descend_final","phase_type":"descend","tcp_position_centroid":[0.49097,0.09967,0.0669]},{"body_a":"peg","body_b":"channel_base_body","contact_count":202.0,"contact_point_centroid":[0.4951,0.06394,0.0094],"force_p95":0.55001,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55112,"mean_force":0.54573,"phase_index":1.0,"phase_name":"descend_safe","phase_type":"descend","tcp_position_centroid":[0.49596,0.13801,0.12852]}],"total_contact_groups":14},"final_pose_error":0.0156,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49468,-0.00993,0.02439],"final_tcp_position":[0.4843,0.02898,0.19522],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":331.43397,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":415.0,"n_steps_budget":600.0,"object_pos_end":[0.49507,0.06368,0.03393],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.1439,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.5465,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":416.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_pre_contact","tcp_end":[0.49723,0.14724,0.15856],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15007,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":202.0,"n_steps_budget":600.0,"object_pos_end":[0.49502,0.06367,0.03395],"object_pos_start":[0.49507,0.06368,0.03393],"object_to_goal_dist_end":0.14388,"object_to_goal_dist_start":0.1439,"object_z_max":0.03395,"peak_contact_force":0.54424,"phase_name":"descend_safe","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":202.0,"raw_peak_contact_force":0.55112,"subtask_id":"reach_pre_contact","tcp_end":[0.49619,0.12837,0.09845],"tcp_start":[0.49723,0.14724,0.15856],"tcp_to_object_dist_end":0.09136,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":122.0,"n_steps_budget":600.0,"object_pos_end":[0.49502,0.06411,0.03398],"object_pos_start":[0.49502,0.06367,0.03395],"object_to_goal_dist_end":0.14432,"object_to_goal_dist_start":0.14388,"object_z_max":0.03398,"peak_contact_force":0.54496,"phase_name":"align_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":122.0,"raw_peak_contact_force":0.5516,"subtask_id":"reach_pre_contact","tcp_end":[0.49215,0.10323,0.08383],"tcp_start":[0.49619,0.12837,0.09845],"tcp_to_object_dist_end":0.06344,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":126.0,"n_steps_budget":600.0,"object_pos_end":[0.49518,0.06363,0.034],"object_pos_start":[0.49502,0.06411,0.03398],"object_to_goal_dist_end":0.14384,"object_to_goal_dist_start":0.14432,"object_z_max":0.034,"peak_contact_force":0.5415,"phase_name":"descend_final","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":126.0,"raw_peak_contact_force":0.55124,"subtask_id":"reach_pre_contact","tcp_end":[0.49084,0.09614,0.04911],"tcp_start":[0.49215,0.10323,0.08383],"tcp_to_object_dist_end":0.03611,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":712.0,"n_steps_budget":1000.0,"object_pos_end":[0.50835,0.00866,0.0393],"object_pos_start":[0.49518,0.06363,0.034],"object_to_goal_dist_end":0.08905,"object_to_goal_dist_start":0.14384,"object_z_max":0.04046,"peak_contact_force":37.49387,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1719.0,"raw_peak_contact_force":45.85547,"subtask_id":"push_channel","tcp_end":[0.48678,0.02916,0.04496],"tcp_start":[0.48679,0.0292,0.04498],"tcp_to_object_dist_end":0.03029,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49468,-0.00993,0.02439],"object_pos_start":[0.50833,0.00842,0.03922],"object_to_goal_dist_end":0.07198,"object_to_goal_dist_start":0.08882,"object_z_max":0.03968,"peak_contact_force":0.50627,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":664.0,"raw_peak_contact_force":331.43397,"subtask_id":"push_channel","tcp_end":[0.4843,0.02898,0.19522],"tcp_start":[0.48678,0.02916,0.04496],"tcp_to_object_dist_end":0.17551,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58571,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_peg.align_speed":0.11454,"approach_1.approach_speed":0.32067,"approach_1.approach_y":0.10949,"descend_final.descend_final_speed":0.10984,"descend_final.descend_height":0.00045,"descend_safe.descend_speed":0.13767,"descend_safe.descend_y":0.05575,"push_1.force_guard_threshold":34.221,"push_1.push_distance":0.18779,"push_1.push_max_time":7.51581,"push_1.push_speed":0.04959,"retract_1.retract_height":0.20695,"retract_1.retract_speed":0.18947},"optimized_scores":{"best_composite_score":-0.49682,"best_fitness_score":0.27318,"best_task_score":0.13951},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.49911,0.06499,0.00893],"force_p95":154.92375,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":156.35102,"mean_force":57.28083,"phase_index":3.0,"phase_name":"descend_final","phase_type":"descend","tcp_position_centroid":[0.4929,0.08418,0.06131]},{"body_a":"attachment","body_b":"peg","contact_count":101.0,"contact_point_centroid":[0.50135,0.07751,0.05529],"force_p95":154.86278,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":155.85183,"mean_force":112.38296,"phase_index":3.0,"phase_name":"descend_final","phase_type":"descend","tcp_position_centroid":[0.49439,0.0862,0.05397]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.4986,-0.00154,0.03927],"force_p95":22.53638,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.28565,"mean_force":4.71595,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49087,0.00717,0.04046]},{"body_a":"attachment","body_b":"peg","contact_count":874.0,"contact_point_centroid":[0.49729,0.03281,0.04077],"force_p95":26.68831,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.58772,"mean_force":9.75909,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49156,0.04301,0.03986]},{"body_a":"peg","body_b":"channel_base_body","contact_count":621.0,"contact_point_centroid":[0.50426,-0.04116,0.00845],"force_p95":0.88474,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.87552,"mean_force":0.66993,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48868,0.00723,0.13348]},{"body_a":"peg","body_b":"channel_base_body","contact_count":915.0,"contact_point_centroid":[0.50438,0.00724,0.00988],"force_p95":19.56398,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.40883,"mean_force":7.38417,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49167,0.04529,0.03998]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":562.0,"contact_point_centroid":[0.52525,0.00785,0.02719],"force_p95":18.88558,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.88694,"mean_force":8.64153,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49148,0.02922,0.03986]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":39.0,"contact_point_centroid":[0.52517,-0.01038,0.02602],"force_p95":2.57498,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.27245,"mean_force":1.01143,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49001,0.00714,0.04352]},{"body_a":"peg","body_b":"channel_base_body","contact_count":432.0,"contact_point_centroid":[0.49444,0.05886,0.00934],"force_p95":0.59375,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.58008,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49782,0.15578,0.22347]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49949,0.19739,0.29545]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47497,0.04844,0.05812],"force_p95":1.29147,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.29147,"mean_force":1.29147,"phase_index":3.0,"phase_name":"descend_final","phase_type":"descend","tcp_position_centroid":[0.49546,0.08859,0.04447]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.4748,0.04715,0.05879],"force_p95":0.93776,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.02474,"mean_force":0.40207,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49477,0.08835,0.04351]},{"body_a":"peg","body_b":"channel_base_body","contact_count":96.0,"contact_point_centroid":[0.49352,0.0598,0.00939],"force_p95":0.55068,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54606,"phase_index":2.0,"phase_name":"align_to_peg","phase_type":"align","tcp_position_centroid":[0.4937,0.07052,0.08872]},{"body_a":"peg","body_b":"channel_base_body","contact_count":279.0,"contact_point_centroid":[0.49426,0.05899,0.00939],"force_p95":0.55035,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55326,"mean_force":0.54613,"phase_index":1.0,"phase_name":"descend_safe","phase_type":"descend","tcp_position_centroid":[0.49576,0.09024,0.12497]}],"total_contact_groups":14},"final_pose_error":0.01654,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50294,-0.04669,0.02413],"final_tcp_position":[0.4892,0.00725,0.2306],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":156.35102,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":461.0,"n_steps_budget":600.0,"object_pos_end":[0.49424,0.05898,0.03386],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13923,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54838,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":467.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_pre_contact","tcp_end":[0.49717,0.11594,0.15698],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13569,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":279.0,"n_steps_budget":600.0,"object_pos_end":[0.4942,0.05908,0.03389],"object_pos_start":[0.49424,0.05898,0.03386],"object_to_goal_dist_end":0.13933,"object_to_goal_dist_start":0.13923,"object_z_max":0.03389,"peak_contact_force":0.54624,"phase_name":"descend_safe","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":279.0,"raw_peak_contact_force":0.55326,"subtask_id":"reach_pre_contact","tcp_end":[0.49622,0.0636,0.09458],"tcp_start":[0.49717,0.11594,0.15698],"tcp_to_object_dist_end":0.06089,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":96.0,"n_steps_budget":600.0,"object_pos_end":[0.49399,0.05886,0.0339],"object_pos_start":[0.4942,0.05908,0.03389],"object_to_goal_dist_end":0.13913,"object_to_goal_dist_start":0.13933,"object_z_max":0.0339,"peak_contact_force":0.55067,"phase_name":"align_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":96.0,"raw_peak_contact_force":0.55382,"subtask_id":"reach_pre_contact","tcp_end":[0.49191,0.07936,0.08368],"tcp_start":[0.49622,0.0636,0.09458],"tcp_to_object_dist_end":0.05388,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":200.0,"n_steps_budget":600.0,"object_pos_end":[0.49372,0.05148,0.03423],"object_pos_start":[0.49399,0.05886,0.0339],"object_to_goal_dist_end":0.13176,"object_to_goal_dist_start":0.13913,"object_z_max":0.03427,"peak_contact_force":1.38007,"phase_name":"descend_final","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":302.0,"raw_peak_contact_force":156.35102,"subtask_id":"reach_pre_contact","tcp_end":[0.49535,0.08858,0.04418],"tcp_start":[0.49191,0.07936,0.08368],"tcp_to_object_dist_end":0.03844,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50787,-0.02159,0.04019],"object_pos_start":[0.49372,0.05148,0.03423],"object_to_goal_dist_end":0.05894,"object_to_goal_dist_start":0.13176,"object_z_max":0.04033,"peak_contact_force":32.34577,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2360.0,"raw_peak_contact_force":32.58772,"subtask_id":"push_channel","tcp_end":[0.49141,0.00732,0.04005],"tcp_start":[0.49535,0.08858,0.04418],"tcp_to_object_dist_end":0.03327,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":632.0,"n_steps_budget":690.0,"object_pos_end":[0.50294,-0.04669,0.02413],"object_pos_start":[0.50787,-0.02159,0.04019],"object_to_goal_dist_end":0.03702,"object_to_goal_dist_start":0.05894,"object_z_max":0.04079,"peak_contact_force":0.60162,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":670.0,"raw_peak_contact_force":38.28565,"subtask_id":"push_channel","tcp_end":[0.4892,0.00725,0.2306],"tcp_start":[0.49141,0.00732,0.04005],"tcp_to_object_dist_end":0.21384,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```