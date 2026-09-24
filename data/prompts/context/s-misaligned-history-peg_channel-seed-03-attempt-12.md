## Search State

- **Seed**: 3
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 14  | -0.5473 | 0.09 | ❌ rejected |
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 14  | -0.3452 | 0.08 | ❌ rejected |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 14  | -0.5566 | 0.31 | ✅ accepted |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 14  | 0.0091 | 0.28 | ✅ accepted |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8  | -0.6319 | 0.09 | ❌ rejected |

**Proposal policy**: task_score is 0.09 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.632) — your mutation base

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

- **Composite score**: -0.632
- **task_score** (E): 0.093
- **fitness_score**: 0.128  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.760

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0667 |
| descend_1 | 1.00 | 1.00 | 0.2140 |
| push_1 | 0.00 | 1.00 | 0.0015 |
| retract_1 | 1.00 | 1.00 | 0.2873 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.504, 0.140, 0.281) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.544 | 3.954 |
| descend_1 | descend | 1.00 / step_budget | (0.504, 0.140, 0.281)→(0.499, 0.114, 0.070) | (0.502, 0.081, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 1.000 | 0.545 | 0.563 |
| push_1 | push | 0.00 / guard_failure | (0.514, 0.102, 0.054)→(0.515, 0.102, 0.053) | (0.502, 0.081, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.161 | 1.00 / 2.333 | 467.777 | 1112.344 |
| retract_1 | retract | 1.00 / step_budget | (0.515, 0.102, 0.053)→(0.514, 0.108, 0.340) | (0.502, 0.080, 0.034)→(0.502, 0.038, 0.031) | 0.160→0.121 | 1.00 / 1.000 | 0.568 | 351.500 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.818
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.279
- phase_score: 0.131
- phase_breakdown.push_through_channel_score: 0.014
- phase_breakdown.reach_peg_score: 0.404

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.190
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.279
- **Median Q (composite search score)**: -0.655
- **K-run variance**: 0.0020
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.373


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53012,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.30922,"approach_1.approach_y_offset":0.02443,"approach_1.approach_z_offset":0.12258,"descend_1.descend_speed":0.04027,"descend_1.descend_y_offset":0.01184,"descend_1.descend_z_offset":0.00545,"push_1.force_threshold":12.75348,"push_1.lateral_force_guard_threshold":22.14821,"push_1.push_distance":0.16592,"push_1.push_speed":0.05413,"push_1.retry_x_offset":0.00265,"push_1.retry_y_offset":0.00378,"retract_1.retract_height":0.17783,"retract_1.retract_speed":0.56612},"optimized_scores":{"best_composite_score":-0.56978,"best_fitness_score":0.19022,"best_task_score":0.27857},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.5032,0.05675,0.00921],"force_p95":153.76941,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":164.68587,"mean_force":34.37545,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49238,0.08916,0.05008]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49427,0.07545,0.04879],"force_p95":161.98777,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":164.43785,"mean_force":104.66411,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49437,0.0871,0.04848]},{"body_a":"peg","body_b":"channel_base_body","contact_count":491.0,"contact_point_centroid":[0.49966,-0.06871,0.00836],"force_p95":1.55245,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.04746,"mean_force":0.85504,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49747,0.1049,0.20344]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":29.0,"contact_point_centroid":[0.47499,-0.04573,0.02583],"force_p95":8.36995,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.59464,"mean_force":3.88207,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49883,0.09655,0.31269]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":22.0,"contact_point_centroid":[0.52519,-0.07439,0.03113],"force_p95":7.69165,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.30138,"mean_force":1.093,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49575,0.09988,0.09769]},{"body_a":"peg","body_b":"channel_base_body","contact_count":153.0,"contact_point_centroid":[0.49493,0.05916,0.00927],"force_p95":0.91111,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.64161,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48372,0.15592,0.28827]},{"body_a":"peg","body_b":"channel_base_body","contact_count":93.0,"contact_point_centroid":[0.49651,-0.1007,0.02612],"force_p95":1.30498,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.75434,"mean_force":0.45605,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49608,0.09911,0.12119]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49733,0.19416,0.29795]},{"body_a":"peg","body_b":"channel_base_body","contact_count":606.0,"contact_point_centroid":[0.49409,0.05884,0.00939],"force_p95":0.5504,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54621,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47967,0.10746,0.16773]}],"total_contact_groups":9},"final_pose_error":0.02606,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49341,-0.07202,0.02469],"final_tcp_position":[0.49897,0.08925,0.348],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":164.68587,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":182.0,"n_steps_budget":600.0,"object_pos_end":[0.49408,0.05891,0.03381],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13918,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54795,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":188.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_peg","tcp_end":[0.47207,0.12235,0.28166],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.25678,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":606.0,"n_steps_budget":1000.0,"object_pos_end":[0.49425,0.05888,0.0339],"object_pos_start":[0.49408,0.05891,0.03381],"object_to_goal_dist_end":0.13913,"object_to_goal_dist_start":0.13918,"object_z_max":0.0339,"peak_contact_force":0.54208,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":606.0,"raw_peak_contact_force":0.55382,"subtask_id":"reach_peg","tcp_end":[0.48908,0.0925,0.05296],"tcp_start":[0.47207,0.12235,0.28166],"tcp_to_object_dist_end":0.03899,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":9.0,"n_steps_budget":1000.0,"object_pos_end":[0.49365,0.05687,0.03404],"object_pos_start":[0.49425,0.05888,0.0339],"object_to_goal_dist_end":0.13714,"object_to_goal_dist_start":0.13913,"object_z_max":0.03461,"peak_contact_force":1.88713,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":164.68587,"subtask_id":"push_through_channel","tcp_end":[0.49962,0.08249,0.04533],"tcp_start":[0.49787,0.08399,0.04646],"tcp_to_object_dist_end":0.02863,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.49341,-0.07202,0.02469],"object_pos_start":[0.49359,0.05295,0.03528],"object_to_goal_dist_end":0.01848,"object_to_goal_dist_start":0.13319,"object_z_max":0.04402,"peak_contact_force":0.62379,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":635.0,"raw_peak_contact_force":9.04746,"tcp_end":[0.49897,0.08925,0.348],"tcp_start":[0.49962,0.08249,0.04533],"tcp_to_object_dist_end":0.36134,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.44444,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.31294,"approach_1.approach_y_offset":0.02173,"approach_1.approach_z_offset":0.11672,"descend_1.descend_speed":0.08268,"descend_1.descend_y_offset":0.01124,"descend_1.descend_z_offset":0.02998,"push_1.force_threshold":16.25074,"push_1.lateral_force_guard_threshold":25.81476,"push_1.push_distance":0.13948,"push_1.push_speed":0.08938,"push_1.retry_x_offset":0.01347,"push_1.retry_y_offset":0.00214,"retract_1.retract_height":0.17287,"retract_1.retract_speed":0.44662},"optimized_scores":{"best_composite_score":-0.67127,"best_fitness_score":0.08873,"best_task_score":2e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.53042,0.10712,0.05827],"force_p95":1590.30154,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1602.00784,"mean_force":1491.71664,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52105,0.1,0.05888]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.53055,0.10837,0.05793],"force_p95":409.45006,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":525.51693,"mean_force":138.94809,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52263,0.09985,0.05879]},{"body_a":"peg","body_b":"channel_base_body","contact_count":132.0,"contact_point_centroid":[0.50473,0.08098,0.00929],"force_p95":1.04839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.66235,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51419,0.16534,0.28552]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50164,0.19488,0.29754]},{"body_a":"peg","body_b":"channel_base_body","contact_count":542.0,"contact_point_centroid":[0.50592,0.08087,0.00938],"force_p95":0.55017,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59006,"mean_force":0.54681,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52045,0.1203,0.201]},{"body_a":"peg","body_b":"channel_base_body","contact_count":465.0,"contact_point_centroid":[0.50605,0.08083,0.00938],"force_p95":0.55009,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55176,"mean_force":0.54677,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51476,0.12688,0.17793]},{"body_a":"peg","body_b":"channel_base_body","contact_count":18.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55007,"mean_force":0.54677,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51315,0.10641,0.06981]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.51862,0.09354,0.05843],"force_p95":0.03326,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.04752,"mean_force":0.00679,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52296,0.09888,0.05642]}],"total_contact_groups":8},"final_pose_error":0.02618,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50597,0.0809,0.03378],"final_tcp_position":[0.52147,0.10602,0.3545],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":1602.00784,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":161.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.08088,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54638,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":168.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.52562,0.13979,0.27676],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.25079,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.50599,0.08088,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54819,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":465.0,"raw_peak_contact_force":0.55176,"subtask_id":"reach_peg","tcp_end":[0.50464,0.11395,0.0785],"tcp_start":[0.52562,0.13979,0.27676],"tcp_to_object_dist_end":0.05565,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":18.0,"n_steps_budget":990.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":46.49271,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":21.0,"raw_peak_contact_force":1602.00784,"subtask_id":"push_through_channel","tcp_end":[0.52213,0.09934,0.05693],"tcp_start":[0.52165,0.09963,0.05765],"tcp_to_object_dist_end":0.03373,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":0.54526,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":569.0,"raw_peak_contact_force":525.51693,"tcp_end":[0.52147,0.10602,0.3545],"tcp_start":[0.52213,0.09934,0.05693],"tcp_to_object_dist_end":0.32207,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.2551,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.49991,"approach_1.approach_y_offset":0.01566,"approach_1.approach_z_offset":0.12658,"descend_1.descend_speed":0.08854,"descend_1.descend_y_offset":0.0102,"descend_1.descend_z_offset":0.02898,"push_1.force_threshold":16.42325,"push_1.lateral_force_guard_threshold":23.37547,"push_1.push_distance":0.16298,"push_1.push_speed":0.05806,"push_1.retry_x_offset":0.00716,"push_1.retry_y_offset":-0.00651,"retract_1.retract_height":0.13488,"retract_1.retract_speed":0.5214},"optimized_scores":{"best_composite_score":-0.65479,"best_fitness_score":0.10521,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.53327,0.1197,0.05829],"force_p95":1557.50852,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1570.33813,"mean_force":1455.77668,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52203,0.12341,0.0578]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.53419,0.11951,0.05804],"force_p95":415.93641,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":519.9348,"mean_force":150.28918,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52357,0.1244,0.05679]},{"body_a":"peg","body_b":"channel_base_body","contact_count":87.0,"contact_point_centroid":[0.5042,0.10432,0.00929],"force_p95":1.39153,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.67663,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5087,0.17498,0.29076]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50103,0.19577,0.29824]},{"body_a":"peg","body_b":"channel_base_body","contact_count":542.0,"contact_point_centroid":[0.50585,0.10483,0.00939],"force_p95":0.57078,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.47931,"mean_force":0.54892,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52124,0.14141,0.18205]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.51804,0.11783,0.05808],"force_p95":0.66331,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.88702,"mean_force":0.20911,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52407,0.12312,0.05537]},{"body_a":"peg","body_b":"channel_base_body","contact_count":486.0,"contact_point_centroid":[0.50598,0.10472,0.00939],"force_p95":0.57504,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58307,"mean_force":0.54627,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50898,0.14696,0.18201]},{"body_a":"peg","body_b":"channel_base_body","contact_count":18.0,"contact_point_centroid":[0.50268,0.10234,0.00939],"force_p95":0.55632,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57624,"mean_force":0.54681,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51299,0.12911,0.06876]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51948,0.11619,0.05842],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52272,0.12311,0.05653]}],"total_contact_groups":9},"final_pose_error":0.02403,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5059,0.10465,0.03379],"final_tcp_position":[0.52215,0.12869,0.31732],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":1570.33813,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":114.0,"n_steps_budget":600.0,"object_pos_end":[0.50586,0.10465,0.03381],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18485,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.53845,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":119.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_peg","tcp_end":[0.51534,0.15803,0.28584],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.25779,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":486.0,"n_steps_budget":1000.0,"object_pos_end":[0.50591,0.10456,0.03384],"object_pos_start":[0.50586,0.10465,0.03381],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18485,"object_z_max":0.03384,"peak_contact_force":0.54541,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":486.0,"raw_peak_contact_force":0.58307,"subtask_id":"reach_peg","tcp_end":[0.50356,0.13604,0.0775],"tcp_start":[0.51534,0.15803,0.28584],"tcp_to_object_dist_end":0.05387,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":18.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.10463,0.03384],"object_pos_start":[0.50591,0.10456,0.03384],"object_to_goal_dist_end":0.18482,"object_to_goal_dist_start":0.18476,"object_z_max":0.03384,"peak_contact_force":1354.94988,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":22.0,"raw_peak_contact_force":1570.33813,"subtask_id":"push_through_channel","tcp_end":[0.52327,0.1229,0.05573],"tcp_start":[0.52272,0.12311,0.05653],"tcp_to_object_dist_end":0.03343,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.5059,0.10465,0.03379],"object_pos_start":[0.50585,0.1047,0.03384],"object_to_goal_dist_end":0.18485,"object_to_goal_dist_start":0.1849,"object_z_max":0.03404,"peak_contact_force":0.53427,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":570.0,"raw_peak_contact_force":519.9348,"tcp_end":[0.52215,0.12869,0.31732],"tcp_start":[0.52327,0.1229,0.05573],"tcp_to_object_dist_end":0.28501,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```