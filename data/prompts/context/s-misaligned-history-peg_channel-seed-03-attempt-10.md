## Search State

- **Seed**: 3
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 14  | -0.5566 | 0.31 | ✅ accepted |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 14  | 0.0091 | 0.28 | ✅ accepted |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8  | -0.0495 | 0.25 | ✅ accepted |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | -0.3779 | 0.00 | ❌ rejected |
| 6 | approach → push → retract | linear_cartesian | linear_cartesian | arc_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 7  | -0.3452 | 0.08 | ❌ rejected |

**Proposal policy**: task_score is 0.08 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`
- Frozen object start: [0.46685193337148995, 0.058944840527687975, 0.04]
- Frozen task target: [0.46685193337148995, -0.10105515947231203, 0.04]
- Goal object position: (0.46685193337148995, -0.10105515947231203, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.46685193337148995, 0.058944840527687975, 0.04)
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
  frozen_object_start: [0.4669, 0.0589, 0.04]
  frozen_task_target: [0.4669, -0.1011, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.46685193337148995, 0.058944840527687975, 0.04]}
  frozen_targets: {'channel_exit': [0.46685193337148995, -0.10105515947231203, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834

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
| `object` | offset from object initial position (0.46685193337148995, 0.058944840527687975, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.46685193337148995, -0.10105515947231203, 0.04) | final destination targets |
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

## Current Skill (Q=-0.345) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.05
  weight: 0.3
- id: push_through_channel
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
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - 0.12
    tolerance: 0.02
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
    approach_y_offset:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: target.offset.y
        mode: add
    approach_z_offset:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: add
  subtask_id: reach_peg
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.03
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
    descend_y_offset:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: target.offset.y
        mode: add
    descend_z_offset:
      type: scalar
      range:
      - -0.01
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: add
  subtask_id: reach_peg
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    force_threshold:
      type: scalar
      range:
      - 8.0
      - 20.0
      default: 12.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    lateral_force_guard_threshold:
      type: scalar
      range:
      - 15.0
      - 30.0
      default: 22.0
      binds_to:
      - path: guards.lateral_force_ok.threshold
        mode: replace
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
      - 0.03
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
    retry_x_offset:
      type: scalar
      range:
      - -0.015
      - 0.015
      default: 0.0
      binds_to:
      - path: retry.offset.x
        mode: replace
    retry_y_offset:
      type: scalar
      range:
      - -0.015
      - 0.015
      default: 0.0
      binds_to:
      - path: retry.offset.y
        mode: replace
  guards:
  - id: contact_maintained
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  - id: lateral_force_ok
    when: during_phase
    predicate: force_below
    threshold: 22.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_through_channel
- id: retract_1
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: add
    retract_speed:
      type: scalar
      range:
      - 0.2
      - 0.8
      default: 0.4
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.12], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_y_offset: status=consumed; consumers=target.offset.y (add)
    - approach_z_offset: status=consumed; consumers=target.offset.z (add)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_y_offset: status=consumed; consumers=target.offset.y (add)
    - descend_z_offset: status=consumed; consumers=target.offset.z (add)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - lateral_force_guard_threshold: status=consumed; consumers=guards.lateral_force_ok.threshold (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - retry_x_offset: status=consumed; consumers=retry.offset.x (replace)
    - retry_y_offset: status=consumed; consumers=retry.offset.y (replace)
  - guards:
    - id=contact_maintained, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
    - id=lateral_force_ok, when=during_phase, predicate=force_below, on_failure=retry, threshold=22.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (add)
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.345
- **task_score** (E): 0.078
- **fitness_score**: 0.165  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.760

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0607 |
| descend_1 | 1.00 | 1.00 | 0.2146 |
| push_1 | 1.00 | 1.00 | 0.0373 |
| retract_1 | 1.00 | 1.00 | 0.2603 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.503, 0.148, 0.280) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.537 | 3.954 |
| descend_1 | descend | 1.00 / step_budget | (0.503, 0.148, 0.280)→(0.499, 0.117, 0.068) | (0.502, 0.081, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 1.000 | 0.544 | 0.564 |
| push_1 | push | 1.00 / force_exceeded | (0.499, 0.117, 0.068)→(0.496, 0.080, 0.064) | (0.502, 0.081, 0.034)→(0.503, 0.061, 0.037) | 0.162→0.141 | 1.00 / 3.667 | 24.839 | 24.839 |
| retract_1 | retract | 1.00 / step_budget | (0.496, 0.080, 0.064)→(0.496, 0.086, 0.324) | (0.503, 0.061, 0.037)→(0.502, 0.055, 0.031) | 0.141→0.136 | 1.00 / 1.000 | 0.575 | 153.950 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.405
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.206
- phase_score: 0.291
- phase_breakdown.push_through_channel_score: 0.230
- phase_breakdown.approach_peg_score: 0.434

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.257
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.206
- **Median Q (composite search score)**: -0.378
- **K-run variance**: 0.0044
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.293


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `cc7283febf3c95cef1fde4c5a16cbcb134186cb6faf3a169717a9aa53375931d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `178d67757a065da6e29d31070e25f6065dc7e42bdbf58dfbff0deec513214033`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.15054,"average_solve_count":93.0,"average_success_count":93.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.37418,"approach_1.approach_y_offset":0.02221,"approach_1.approach_z_offset":0.12039,"descend_1.descend_speed":0.09085,"descend_1.descend_y_offset":0.01059,"descend_1.descend_z_offset":0.02995,"push_1.force_threshold":13.93872,"push_1.lateral_force_limit":33.07845,"push_1.push_distance":0.15197,"push_1.push_speed":0.07166,"push_1.retry_x_offset":0.00437,"push_1.retry_y_offset":0.01533,"retract_1.retract_height":0.12531,"retract_1.retract_speed":0.56203},"optimized_scores":{"best_composite_score":-0.40417,"best_fitness_score":0.10583,"best_task_score":0.0005},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.475,0.11993,0.05144],"force_p95":124.89621,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":131.35825,"mean_force":82.16677,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48733,0.07987,0.07875]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.475,0.11999,0.05139],"force_p95":21.04375,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":21.04375,"mean_force":21.04375,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48744,0.07999,0.07864]},{"body_a":"peg","body_b":"channel_base_body","contact_count":158.0,"contact_point_centroid":[0.49506,0.05879,0.00927],"force_p95":0.88007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.6386,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48371,0.15494,0.28727]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4974,0.19422,0.29787]},{"body_a":"peg","body_b":"channel_base_body","contact_count":705.0,"contact_point_centroid":[0.49406,0.05905,0.00939],"force_p95":0.55037,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54619,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47479,0.11018,0.18095]},{"body_a":"peg","body_b":"channel_base_body","contact_count":540.0,"contact_point_centroid":[0.4941,0.05893,0.0094],"force_p95":0.55052,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55347,"mean_force":0.54552,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48612,0.09741,0.20139]},{"body_a":"peg","body_b":"channel_base_body","contact_count":79.0,"contact_point_centroid":[0.49388,0.05839,0.00939],"force_p95":0.5501,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55091,"mean_force":0.54579,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48829,0.08506,0.07993]}],"total_contact_groups":7},"final_pose_error":0.02302,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49422,0.0587,0.03401],"final_tcp_position":[0.48703,0.08542,0.33159],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":131.35825,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":187.0,"n_steps_budget":600.0,"object_pos_end":[0.49418,0.05899,0.03381],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13925,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.55229,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":193.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach_peg","tcp_end":[0.47192,0.12018,0.27983],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.25449,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":705.0,"n_steps_budget":1000.0,"object_pos_end":[0.49402,0.05882,0.03391],"object_pos_start":[0.49418,0.05899,0.03381],"object_to_goal_dist_end":0.13909,"object_to_goal_dist_start":0.13925,"object_z_max":0.03391,"peak_contact_force":0.54494,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":705.0,"raw_peak_contact_force":0.55382,"subtask_id":"approach_peg","tcp_end":[0.48991,0.09018,0.08251],"tcp_start":[0.47192,0.12018,0.27983],"tcp_to_object_dist_end":0.05798,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":79.0,"n_steps_budget":1000.0,"object_pos_end":[0.49417,0.05878,0.03392],"object_pos_start":[0.49402,0.05882,0.03391],"object_to_goal_dist_end":0.13904,"object_to_goal_dist_start":0.13909,"object_z_max":0.03392,"peak_contact_force":21.04375,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":80.0,"raw_peak_contact_force":21.04375,"subtask_id":"push_through_channel","tcp_end":[0.48744,0.0799,0.07862],"tcp_start":[0.48991,0.09018,0.08251],"tcp_to_object_dist_end":0.04989,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":540.0,"n_steps_budget":600.0,"object_pos_end":[0.49422,0.0587,0.03401],"object_pos_start":[0.49417,0.05878,0.03392],"object_to_goal_dist_end":0.13895,"object_to_goal_dist_start":0.13904,"object_z_max":0.03401,"peak_contact_force":0.54187,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":545.0,"raw_peak_contact_force":131.35825,"tcp_end":[0.48703,0.08542,0.33159],"tcp_start":[0.48744,0.0799,0.07862],"tcp_to_object_dist_end":0.29886,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.18584,"average_solve_count":113.0,"average_success_count":113.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.41334,"approach_1.approach_y_offset":0.02887,"approach_1.approach_z_offset":0.12152,"descend_1.descend_speed":0.08024,"descend_1.descend_y_offset":0.01011,"descend_1.descend_z_offset":0.00607,"push_1.force_threshold":15.45457,"push_1.lateral_force_limit":35.0958,"push_1.push_distance":0.13785,"push_1.push_speed":0.06329,"push_1.retry_x_offset":-0.00677,"push_1.retry_y_offset":-0.00408,"retract_1.retract_height":0.13549,"retract_1.retract_speed":0.44164},"optimized_scores":{"best_composite_score":-0.37822,"best_fitness_score":0.13178,"best_task_score":0.02753},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.475,0.11991,0.03986],"force_p95":158.9416,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":164.61166,"mean_force":100.49335,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50098,0.07978,0.05506]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.525,0.1199,0.03566],"force_p95":29.61506,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.84124,"mean_force":8.71031,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50098,0.07978,0.05506]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.475,0.11997,0.03994],"force_p95":33.46431,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":33.68165,"mean_force":31.50819,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50107,0.07992,0.05501]},{"body_a":"peg","body_b":"channel_base_body","contact_count":276.0,"contact_point_centroid":[0.50608,0.06564,0.00971],"force_p95":7.12056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.95868,"mean_force":2.90503,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50146,0.0952,0.05551]},{"body_a":"attachment","body_b":"peg","contact_count":164.0,"contact_point_centroid":[0.50617,0.08857,0.04411],"force_p95":7.96558,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.7361,"mean_force":4.18789,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50106,0.08862,0.05495]},{"body_a":"peg","body_b":"channel_base_body","contact_count":118.0,"contact_point_centroid":[0.50473,0.08075,0.00927],"force_p95":1.21237,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.67608,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51406,0.16883,0.28782]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50179,0.19504,0.29776]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":26.0,"contact_point_centroid":[0.52506,0.07221,0.02948],"force_p95":2.51635,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.64177,"mean_force":1.14659,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50103,0.08988,0.05489]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.50646,0.08277,0.05208],"force_p95":0.85589,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.87765,"mean_force":0.43164,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49999,0.08272,0.06209]},{"body_a":"peg","body_b":"channel_base_body","contact_count":541.0,"contact_point_centroid":[0.50679,0.06553,0.00944],"force_p95":0.5695,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72721,"mean_force":0.53968,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49958,0.09808,0.18251]},{"body_a":"peg","body_b":"channel_base_body","contact_count":741.0,"contact_point_centroid":[0.50598,0.08092,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55543,"mean_force":0.54677,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51177,0.13284,0.17159]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52501,0.06674,0.05097],"force_p95":0.28656,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3369,"mean_force":0.10433,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49915,0.08722,0.07519]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.525,0.11995,0.03554],"force_p95":0.0,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50107,0.07987,0.05501]}],"total_contact_groups":13},"final_pose_error":0.02354,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50688,0.0666,0.03383],"final_tcp_position":[0.50054,0.0856,0.3177],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":164.61166,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":147.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54197,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":154.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach_peg","tcp_end":[0.52503,0.14654,0.28086],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.25636,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":741.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54458,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":741.0,"raw_peak_contact_force":0.55543,"subtask_id":"approach_peg","tcp_end":[0.50416,0.11166,0.05962],"tcp_start":[0.52503,0.14654,0.28086],"tcp_to_object_dist_end":0.04024,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":293.0,"n_steps_budget":1000.0,"object_pos_end":[0.50697,0.0627,0.03735],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.14289,"object_to_goal_dist_start":0.1611,"object_z_max":0.03733,"peak_contact_force":33.68165,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":469.0,"raw_peak_contact_force":33.68165,"subtask_id":"push_through_channel","tcp_end":[0.50107,0.07979,0.05501],"tcp_start":[0.50416,0.11166,0.05962],"tcp_to_object_dist_end":0.02528,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.50688,0.0666,0.03383],"object_pos_start":[0.50697,0.0627,0.03735],"object_to_goal_dist_end":0.14689,"object_to_goal_dist_start":0.14289,"object_z_max":0.03737,"peak_contact_force":0.54728,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":566.0,"raw_peak_contact_force":164.61166,"tcp_end":[0.50054,0.0856,0.3177],"tcp_start":[0.50107,0.07979,0.05501],"tcp_to_object_dist_end":0.28457,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63194,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.3163,"approach_1.approach_y_offset":0.03895,"approach_1.approach_z_offset":0.11082,"descend_1.descend_speed":0.06568,"descend_1.descend_y_offset":0.02311,"descend_1.descend_z_offset":0.00905,"push_1.force_threshold":19.61446,"push_1.lateral_force_limit":28.80864,"push_1.push_distance":0.14187,"push_1.push_speed":0.04465,"push_1.retry_x_offset":-0.00704,"push_1.retry_y_offset":-0.00022,"retract_1.retract_height":0.13768,"retract_1.retract_speed":0.62958},"optimized_scores":{"best_composite_score":-0.25306,"best_fitness_score":0.25694,"best_task_score":0.20603},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.475,0.11993,0.042],"force_p95":161.44864,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":165.87938,"mean_force":102.76495,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50045,0.07985,0.05812]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.525,0.11992,0.03938],"force_p95":28.17846,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":31.3094,"mean_force":10.43647,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50047,0.0798,0.0581]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.475,0.11995,0.042],"force_p95":19.57387,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":19.79181,"mean_force":17.2407,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50048,0.0799,0.05809]},{"body_a":"attachment","body_b":"peg","contact_count":592.0,"contact_point_centroid":[0.5044,0.10123,0.04649],"force_p95":9.65421,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.71318,"mean_force":5.11809,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50036,0.10126,0.05772]},{"body_a":"peg","body_b":"channel_base_body","contact_count":884.0,"contact_point_centroid":[0.50639,0.08557,0.00973],"force_p95":8.64674,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.57244,"mean_force":3.8241,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50047,0.11208,0.0578]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":50.0,"contact_point_centroid":[0.525,0.0637,0.04307],"force_p95":3.94557,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.15177,"mean_force":2.94794,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50045,0.08266,0.05801]},{"body_a":"peg","body_b":"channel_base_body","contact_count":53.0,"contact_point_centroid":[0.50365,0.10486,0.00924],"force_p95":2.08855,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.76114,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5079,0.18616,0.2861]},{"body_a":"peg","body_b":"channel_base_body","contact_count":534.0,"contact_point_centroid":[0.50559,0.04339,0.00829],"force_p95":0.72574,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.73329,"mean_force":0.60928,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49907,0.09835,0.188]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50141,0.19699,0.297]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50363,0.07995,0.04674],"force_p95":1.48581,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.76073,"mean_force":0.42937,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50043,0.07992,0.05816]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.525,0.06665,0.0354],"force_p95":1.00612,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.09277,"mean_force":0.601,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50043,0.07992,0.05816]},{"body_a":"peg","body_b":"channel_base_body","contact_count":746.0,"contact_point_centroid":[0.50583,0.10459,0.00939],"force_p95":0.57541,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58307,"mean_force":0.54624,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50551,0.16678,0.17203]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.525,0.11995,0.03935],"force_p95":0.0,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50048,0.07987,0.05809]}],"total_contact_groups":13},"final_pose_error":0.02348,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50587,0.03978,0.0241],"final_tcp_position":[0.5,0.08562,0.32304],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":165.87938,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":80.0,"n_steps_budget":600.0,"object_pos_end":[0.50593,0.10462,0.03374],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18482,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.51552,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":85.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach_peg","tcp_end":[0.51302,0.17797,0.27855],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.25566,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":746.0,"n_steps_budget":1000.0,"object_pos_end":[0.50585,0.1047,0.03384],"object_pos_start":[0.50593,0.10462,0.03374],"object_to_goal_dist_end":0.18489,"object_to_goal_dist_start":0.18482,"object_z_max":0.03384,"peak_contact_force":0.543,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":746.0,"raw_peak_contact_force":0.58307,"subtask_id":"approach_peg","tcp_end":[0.50342,0.14791,0.06242],"tcp_start":[0.51302,0.17797,0.27855],"tcp_to_object_dist_end":0.05186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":884.0,"n_steps_budget":1000.0,"object_pos_end":[0.50701,0.06227,0.04016],"object_pos_start":[0.50585,0.1047,0.03384],"object_to_goal_dist_end":0.14245,"object_to_goal_dist_start":0.18489,"object_z_max":0.04055,"peak_contact_force":19.79181,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1533.0,"raw_peak_contact_force":19.79181,"subtask_id":"push_through_channel","tcp_end":[0.50048,0.07979,0.05809],"tcp_start":[0.50342,0.14791,0.06242],"tcp_to_object_dist_end":0.02591,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.50587,0.03978,0.0241],"object_pos_start":[0.50701,0.06227,0.04016],"object_to_goal_dist_end":0.12098,"object_to_goal_dist_start":0.14245,"object_z_max":0.0403,"peak_contact_force":0.63682,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":551.0,"raw_peak_contact_force":165.87938,"tcp_end":[0.5,0.08562,0.32304],"tcp_start":[0.50048,0.07979,0.05809],"tcp_to_object_dist_end":0.30249,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```