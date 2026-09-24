## Search State

- **Seed**: 1
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.5530 | 0.21 | ❌ rejected |
| 12 | approach → descend → align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.4342 | 0.28 | ❌ rejected |
| 11 | approach → descend → align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.4476 | 0.40 | ❌ rejected |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | -0.0080 | 0.27 | ❌ rejected |
| 9 | approach → descend → align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 15 | -0.4213 | 0.29 | ❌ rejected |

**Proposal policy**: task_score is 0.21 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.553) — your mutation base

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

- **Composite score**: -0.553
- **task_score** (E): 0.205
- **fitness_score**: 0.187  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.740

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1235 |
| descend_1 | 1.00 | 1.00 | 0.1030 |
| align_lateral | 1.00 | 1.00 | 0.0315 |
| push_1 | 1.00 | 1.00 | 0.0355 |
| retract_1 | 1.00 | 1.00 | 0.1624 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.484, 0.195, 0.179) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.552 | 2.857 |
| descend_1 | descend | 1.00 / step_budget | (0.484, 0.195, 0.179)→(0.492, 0.144, 0.095) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.557 | 0.588 |
| align_lateral | align | 1.00 / step_budget | (0.492, 0.144, 0.095)→(0.492, 0.119, 0.076) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.556 | 0.588 |
| push_1 | push | 1.00 / time_limit | (0.492, 0.119, 0.076)→(0.498, 0.086, 0.068) | (0.497, 0.080, 0.034)→(0.499, 0.028, 0.024) | 0.160→0.109 | 1.00 / 2.000 | 213.326 | 1055.534 |
| retract_1 | retract | 1.00 / step_budget | (0.498, 0.086, 0.068)→(0.497, 0.086, 0.230) | (0.499, 0.028, 0.024)→(0.499, 0.028, 0.024) | 0.109→0.109 | 1.00 / 1.000 | 0.673 | 198.391 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.403
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.403
- phase_score: 0.190
- phase_breakdown.push_channel_score: 0.000
- phase_breakdown.reach_pre_contact_score: 0.632

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.275
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.403
- **Median Q (composite search score)**: -0.583
- **K-run variance**: 0.0040
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.297


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.09483,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.align_speed":0.13032,"align_lateral.align_tol":0.01326,"align_lateral.align_y":0.02593,"approach_1.approach_speed":0.33404,"approach_1.approach_y_offset":0.09568,"descend_1.descend_height":0.04327,"descend_1.descend_speed":0.11173,"descend_1.descend_y":0.07935,"push_1.push_distance":0.19861,"push_1.push_max_time":4.38534,"push_1.push_speed":0.09915,"retract_1.retract_height":0.18173,"retract_1.retract_speed":0.32661},"optimized_scores":{"best_composite_score":-0.46502,"best_fitness_score":0.27498,"best_task_score":0.40273},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":952.0,"contact_point_centroid":[0.49455,0.06803,0.00881],"force_p95":5.22342,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":436.00783,"mean_force":2.03035,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49746,0.09484,0.06348]},{"body_a":"attachment","body_b":"peg","contact_count":198.0,"contact_point_centroid":[0.49474,0.10634,0.05225],"force_p95":10.86262,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":435.99453,"mean_force":7.23834,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49431,0.10728,0.05951]},{"body_a":"attachment","body_b":"world","contact_count":12.0,"contact_point_centroid":[0.50081,0.15098,-0.00042],"force_p95":307.13541,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":312.30568,"mean_force":261.47018,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49825,0.14237,0.00709]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":557.0,"contact_point_centroid":[0.46634,0.11991,0.05954],"force_p95":216.38786,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":241.09327,"mean_force":189.38031,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49856,0.08208,0.06812]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.46522,0.11996,0.06],"force_p95":201.1195,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":210.01225,"mean_force":125.402,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50148,0.08542,0.06676]},{"body_a":"world","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.48286,0.20687,-0.00014],"force_p95":132.78671,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":133.51805,"mean_force":113.04155,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4903,0.13147,0.02202]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":67.0,"contact_point_centroid":[0.47443,0.09984,0.04625],"force_p95":3.73827,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.46998,"mean_force":0.7544,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49854,0.12742,0.04029]},{"body_a":"peg","body_b":"channel_base_body","contact_count":205.0,"contact_point_centroid":[0.50083,0.11592,0.0093],"force_p95":0.84996,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.58438,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49905,0.20408,0.2367]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52516,0.11152,0.0573],"force_p95":1.71346,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.72325,"mean_force":1.39411,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49063,0.12856,0.03401]},{"body_a":"peg","body_b":"channel_base_body","contact_count":210.0,"contact_point_centroid":[0.50077,0.11607,0.00941],"force_p95":0.60723,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66197,"mean_force":0.54347,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.49614,0.17433,0.0831]},{"body_a":"peg","body_b":"channel_base_body","contact_count":156.0,"contact_point_centroid":[0.50125,0.11618,0.00942],"force_p95":0.60735,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65796,"mean_force":0.54279,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49774,0.20313,0.13846]},{"body_a":"peg","body_b":"channel_base_body","contact_count":391.0,"contact_point_centroid":[0.4972,0.05154,0.00808],"force_p95":0.60842,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60911,"mean_force":0.60621,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50013,0.08525,0.14649]}],"total_contact_groups":12},"final_pose_error":0.01966,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49907,0.0516,0.02417],"final_tcp_position":[0.50024,0.08558,0.22887],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":436.00783,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":221.0,"n_steps_budget":600.0,"object_pos_end":[0.50099,0.11604,0.03384],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19614,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.55758,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":205.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_pre_contact","tcp_end":[0.49873,0.20859,0.17941],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17251,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":156.0,"n_steps_budget":600.0,"object_pos_end":[0.50088,0.116,0.0339],"object_pos_start":[0.50099,0.11604,0.03384],"object_to_goal_dist_end":0.1961,"object_to_goal_dist_start":0.19614,"object_z_max":0.03398,"peak_contact_force":0.57846,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":156.0,"raw_peak_contact_force":0.65796,"subtask_id":"reach_pre_contact","tcp_end":[0.49779,0.19745,0.09646],"tcp_start":[0.49873,0.20859,0.17941],"tcp_to_object_dist_end":0.10275,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":210.0,"n_steps_budget":600.0,"object_pos_end":[0.50097,0.11596,0.03383],"object_pos_start":[0.50088,0.116,0.0339],"object_to_goal_dist_end":0.19606,"object_to_goal_dist_start":0.1961,"object_z_max":0.03392,"peak_contact_force":0.57914,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":210.0,"raw_peak_contact_force":0.66197,"subtask_id":"reach_pre_contact","tcp_end":[0.49683,0.15094,0.07301],"tcp_start":[0.49779,0.19745,0.09646],"tcp_to_object_dist_end":0.05269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49519,0.0516,0.02434],"object_pos_start":[0.50097,0.11596,0.03383],"object_to_goal_dist_end":0.13261,"object_to_goal_dist_start":0.19606,"object_z_max":0.04193,"peak_contact_force":209.49847,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1804.0,"raw_peak_contact_force":436.00783,"subtask_id":"push_channel","tcp_end":[0.50151,0.08537,0.06676],"tcp_start":[0.49683,0.15094,0.07301],"tcp_to_object_dist_end":0.05459,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":391.0,"n_steps_budget":600.0,"object_pos_end":[0.49907,0.0516,0.02417],"object_pos_start":[0.49519,0.0516,0.02434],"object_to_goal_dist_end":0.13255,"object_to_goal_dist_start":0.13261,"object_z_max":0.02434,"peak_contact_force":0.60595,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":394.0,"raw_peak_contact_force":210.01225,"subtask_id":"push_channel","tcp_end":[0.50024,0.08558,0.22887],"tcp_start":[0.50151,0.08537,0.06676],"tcp_to_object_dist_end":0.20751,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02542,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.align_speed":0.09807,"align_lateral.align_tol":0.00963,"align_lateral.align_y":0.034,"approach_1.approach_speed":0.3497,"approach_1.approach_y_offset":0.1407,"descend_1.descend_height":0.0487,"descend_1.descend_speed":0.13379,"descend_1.descend_y":0.04135,"push_1.push_distance":0.17642,"push_1.push_max_time":6.13721,"push_1.push_speed":0.07084,"retract_1.retract_height":0.18517,"retract_1.retract_speed":0.40951},"optimized_scores":{"best_composite_score":-0.58308,"best_fitness_score":0.15692,"best_task_score":0.12757},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.53542,0.11955,0.05863],"force_p95":1141.91685,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1335.6667,"mean_force":490.01764,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50013,0.09106,0.0353]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50402,0.07878,0.05555],"force_p95":342.68184,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":389.60766,"mean_force":119.37537,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50807,0.08924,0.05297]},{"body_a":"peg","body_b":"channel_base_body","contact_count":983.0,"contact_point_centroid":[0.49967,0.02004,0.00812],"force_p95":0.72625,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":388.43511,"mean_force":1.10072,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4919,0.08302,0.06728]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":782.0,"contact_point_centroid":[0.46162,0.11993,0.05999],"force_p95":216.19984,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":236.66915,"mean_force":184.8126,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49202,0.08191,0.07049]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.46031,0.11995,0.05999],"force_p95":189.65988,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":199.33977,"mean_force":120.63182,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49566,0.08518,0.0686]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":49.0,"contact_point_centroid":[0.47492,0.08808,0.05194],"force_p95":191.30142,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":194.76662,"mean_force":121.53165,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48677,0.08704,0.05161]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52502,-0.00349,0.02394],"force_p95":6.9261,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.29798,"mean_force":2.01395,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48695,0.08685,0.05218]},{"body_a":"peg","body_b":"channel_base_body","contact_count":192.0,"contact_point_centroid":[0.49628,0.0639,0.00933],"force_p95":0.75823,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.58937,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4902,0.20116,0.23396]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47491,0.04696,0.04731],"force_p95":1.38228,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.46143,"mean_force":0.83321,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50078,0.08726,0.04775]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49925,0.19977,0.29502]},{"body_a":"peg","body_b":"channel_base_body","contact_count":393.0,"contact_point_centroid":[0.50314,0.01844,0.00806],"force_p95":0.7171,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.88184,"mean_force":0.60527,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4944,0.08509,0.14981]},{"body_a":"peg","body_b":"channel_base_body","contact_count":235.0,"contact_point_centroid":[0.49467,0.064,0.00939],"force_p95":0.55029,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55295,"mean_force":0.54588,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48534,0.16275,0.13636]},{"body_a":"peg","body_b":"channel_base_body","contact_count":88.0,"contact_point_centroid":[0.4959,0.06295,0.0094],"force_p95":0.54973,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55052,"mean_force":0.54565,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.48964,0.11339,0.0854]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,-0.00381,0.02421],"force_p95":0.38297,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38297,"mean_force":0.38297,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49451,0.08504,0.08698]}],"total_contact_groups":14},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50199,0.01832,0.02412],"final_tcp_position":[0.49445,0.08542,0.23382],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":1335.6667,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":219.0,"n_steps_budget":600.0,"object_pos_end":[0.49508,0.06402,0.03389],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14424,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54927,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":220.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_pre_contact","tcp_end":[0.48234,0.20275,0.17979],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.20172,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":235.0,"n_steps_budget":660.0,"object_pos_end":[0.49503,0.06369,0.03394],"object_pos_start":[0.49508,0.06402,0.03389],"object_to_goal_dist_end":0.1439,"object_to_goal_dist_start":0.14424,"object_z_max":0.03393,"peak_contact_force":0.54675,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":235.0,"raw_peak_contact_force":0.55295,"subtask_id":"reach_pre_contact","tcp_end":[0.49014,0.12073,0.09396],"tcp_start":[0.48234,0.20275,0.17979],"tcp_to_object_dist_end":0.08295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":88.0,"n_steps_budget":600.0,"object_pos_end":[0.49527,0.06398,0.03394],"object_pos_start":[0.49503,0.06369,0.03394],"object_to_goal_dist_end":0.14418,"object_to_goal_dist_start":0.1439,"object_z_max":0.03394,"peak_contact_force":0.54288,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":88.0,"raw_peak_contact_force":0.55052,"subtask_id":"reach_pre_contact","tcp_end":[0.49026,0.10554,0.07736],"tcp_start":[0.49014,0.12073,0.09396],"tcp_to_object_dist_end":0.06031,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50313,0.01841,0.02414],"object_pos_start":[0.49527,0.06398,0.03394],"object_to_goal_dist_end":0.09973,"object_to_goal_dist_start":0.14418,"object_z_max":0.04073,"peak_contact_force":211.30245,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1859.0,"raw_peak_contact_force":1335.6667,"subtask_id":"push_channel","tcp_end":[0.49568,0.08515,0.06858],"tcp_start":[0.49026,0.10554,0.07736],"tcp_to_object_dist_end":0.08052,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":393.0,"n_steps_budget":600.0,"object_pos_end":[0.50199,0.01832,0.02412],"object_pos_start":[0.50313,0.01841,0.02414],"object_to_goal_dist_end":0.09962,"object_to_goal_dist_start":0.09973,"object_z_max":0.02431,"peak_contact_force":0.71702,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":397.0,"raw_peak_contact_force":199.33977,"subtask_id":"push_channel","tcp_end":[0.49445,0.08542,0.23382],"tcp_start":[0.49568,0.08515,0.06858],"tcp_to_object_dist_end":0.2203,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.06034,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.align_speed":0.1258,"align_lateral.align_tol":0.01225,"align_lateral.align_y":0.03387,"approach_1.approach_speed":0.30866,"approach_1.approach_y_offset":0.10967,"descend_1.descend_height":0.04613,"descend_1.descend_speed":0.1379,"descend_1.descend_y":0.04083,"push_1.push_distance":0.18094,"push_1.push_max_time":5.86284,"push_1.push_speed":0.08781,"retract_1.retract_height":0.17965,"retract_1.retract_speed":0.24067},"optimized_scores":{"best_composite_score":-0.6108,"best_fitness_score":0.1292,"best_task_score":0.08526},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":40.0,"contact_point_centroid":[0.52824,0.11961,0.05863],"force_p95":1136.34024,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1394.9289,"mean_force":469.16899,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49705,0.08345,0.04216]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50246,0.07335,0.0556],"force_p95":255.05044,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":286.6389,"mean_force":93.04788,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50552,0.08359,0.05312]},{"body_a":"peg","body_b":"channel_base_body","contact_count":983.0,"contact_point_centroid":[0.50176,0.0156,0.00812],"force_p95":0.69717,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":285.25726,"mean_force":0.9814,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49359,0.08285,0.06787]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":858.0,"contact_point_centroid":[0.46263,0.11991,0.05999],"force_p95":227.59854,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":247.46703,"mean_force":202.20559,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49362,0.08277,0.06992]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.45923,0.11995,0.05999],"force_p95":176.17253,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":185.81987,"mean_force":117.93719,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49675,0.08757,0.06853]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":31.0,"contact_point_centroid":[0.4749,0.08061,0.05842],"force_p95":147.61982,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":150.39522,"mean_force":120.18941,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48673,0.07954,0.05837]},{"body_a":"peg","body_b":"channel_base_body","contact_count":197.0,"contact_point_centroid":[0.49501,0.05899,0.00929],"force_p95":0.77094,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.6204,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48373,0.18516,0.23299]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49828,0.19827,0.29321]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47492,0.05142,0.05806],"force_p95":1.40608,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.43499,"mean_force":1.16653,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50468,0.08369,0.04316]},{"body_a":"peg","body_b":"channel_base_body","contact_count":378.0,"contact_point_centroid":[0.49761,0.01336,0.00805],"force_p95":0.69712,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69712,"mean_force":0.60592,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4956,0.08758,0.14705]},{"body_a":"peg","body_b":"channel_base_body","contact_count":211.0,"contact_point_centroid":[0.49407,0.05911,0.00939],"force_p95":0.55025,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55206,"mean_force":0.54629,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47789,0.14356,0.13603]},{"body_a":"peg","body_b":"channel_base_body","contact_count":80.0,"contact_point_centroid":[0.49341,0.05889,0.00939],"force_p95":0.55035,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55186,"mean_force":0.54629,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.48715,0.10638,0.08524]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,-0.00858,0.02421],"force_p95":0.40241,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40241,"mean_force":0.40241,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49182,0.08047,0.07178]}],"total_contact_groups":13},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49604,0.01322,0.02414],"final_tcp_position":[0.49563,0.08789,0.22839],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":1394.9289,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":226.0,"n_steps_budget":600.0,"object_pos_end":[0.4941,0.05904,0.03383],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.1393,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54884,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":232.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_pre_contact","tcp_end":[0.47058,0.1731,0.17902],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.18614,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":211.0,"n_steps_budget":600.0,"object_pos_end":[0.49402,0.059,0.03386],"object_pos_start":[0.4941,0.05904,0.03383],"object_to_goal_dist_end":0.13926,"object_to_goal_dist_start":0.1393,"object_z_max":0.03386,"peak_contact_force":0.54634,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":211.0,"raw_peak_contact_force":0.55206,"subtask_id":"reach_pre_contact","tcp_end":[0.48709,0.11239,0.09325],"tcp_start":[0.47058,0.1731,0.17902],"tcp_to_object_dist_end":0.08017,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":80.0,"n_steps_budget":600.0,"object_pos_end":[0.49406,0.05885,0.03387],"object_pos_start":[0.49402,0.059,0.03386],"object_to_goal_dist_end":0.13912,"object_to_goal_dist_start":0.13926,"object_z_max":0.03387,"peak_contact_force":0.54625,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":80.0,"raw_peak_contact_force":0.55186,"subtask_id":"reach_pre_contact","tcp_end":[0.4884,0.09998,0.0777],"tcp_start":[0.48709,0.11239,0.09325],"tcp_to_object_dist_end":0.06037,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49929,0.01358,0.02414],"object_pos_start":[0.49406,0.05885,0.03387],"object_to_goal_dist_end":0.09491,"object_to_goal_dist_start":0.13912,"object_z_max":0.04045,"peak_contact_force":219.17679,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1920.0,"raw_peak_contact_force":1394.9289,"subtask_id":"push_channel","tcp_end":[0.49677,0.08753,0.0685],"tcp_start":[0.4884,0.09998,0.0777],"tcp_to_object_dist_end":0.08628,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":378.0,"n_steps_budget":600.0,"object_pos_end":[0.49604,0.01322,0.02414],"object_pos_start":[0.49929,0.01358,0.02414],"object_to_goal_dist_end":0.09464,"object_to_goal_dist_start":0.09491,"object_z_max":0.02414,"peak_contact_force":0.69711,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":381.0,"raw_peak_contact_force":185.81987,"subtask_id":"push_channel","tcp_end":[0.49563,0.08789,0.22839],"tcp_start":[0.49677,0.08753,0.0685],"tcp_to_object_dist_end":0.21747,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```