## Search State

- **Seed**: 3
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3360 | 0.32 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | time_limit | time_limit | force_exceeded | pose_tolerance | 9 | 0.1497 | 0.06 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1753 | 0.33 | ✅ accepted |
| 7 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.2081 | 0.10 | ❌ rejected |
| 6 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.1448 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.336) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.05
  weight: 0.3
- id: push_progress
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
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_peg
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_peg
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  subtask_id: reach_peg
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: channel_exit
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.18
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_safe
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  retries:
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_progress
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_peg, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=channel_exit, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_safe, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.336
- **task_score** (E): 0.323
- **fitness_score**: 0.646  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_align | 1.00 | 1.00 | 0.1767 |
| descend_align | 1.00 | 1.00 | 0.0958 |
| push_through | 0.00 | 1.00 | 0.3293 |
| retract_after | 1.00 | 1.00 | 0.0804 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_align | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.506, 0.270, 0.141) | (0.509, 0.081, 0.040)→(0.502, 0.082, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.558 | 3.954 |
| descend_align | descend | 1.00 / step_budget | (0.506, 0.270, 0.141)→(0.500, 0.278, 0.047) | (0.502, 0.082, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 1.000 | 0.549 | 0.560 |
| push_through | push | 0.00 / guard_failure | (0.500, 0.278, 0.047)→(0.496, -0.051, 0.036) | (0.502, 0.082, 0.034)→(0.501, -0.081, 0.037) | 0.162→0.006 | 1.00 / 2.667 | 41.100 | 41.100 |
| retract_after | retract | 1.00 / step_budget | (0.496, -0.051, 0.036)→(0.493, -0.051, 0.116) | (0.501, -0.081, 0.037)→(0.501, -0.066, 0.037) | 0.006→0.017 | 1.00 / 1.000 | 0.487 | 38.060 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.172
- terminal_score: 0.520
- phase_score: 0.866
- phase_breakdown.reach_peg_score: 0.654
- phase_breakdown.push_progress_score: 0.957

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.728
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.520
- **Median Q (composite search score)**: 0.309
- **K-run variance**: 0.0035
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.341


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.89137,"average_solve_count":313.0,"average_success_count":313.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_align.approach_height":0.10952,"approach_align.speed":0.06074,"descend_align.speed":0.0253,"push_through.speed":0.02778,"retract_after.speed":0.06679},"optimized_scores":{"best_composite_score":0.30877,"best_fitness_score":0.61877,"best_task_score":0.23135},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":202.0,"contact_point_centroid":[0.4953,0.00373,0.04366],"force_p95":31.73209,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.93599,"mean_force":6.24236,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49305,0.01526,0.03748]},{"body_a":"peg","body_b":"channel_base_body","contact_count":10.0,"contact_point_centroid":[0.49965,-0.10035,0.06069],"force_p95":38.7199,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.66213,"mean_force":31.99583,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49539,-0.05147,0.03592]},{"body_a":"attachment","body_b":"peg","contact_count":134.0,"contact_point_centroid":[0.49529,-0.06265,0.0552],"force_p95":30.56525,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.08255,"mean_force":18.9344,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.49246,-0.0513,0.0537]},{"body_a":"peg","body_b":"channel_base_body","contact_count":146.0,"contact_point_centroid":[0.49898,-0.10035,0.06424],"force_p95":30.25978,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.94641,"mean_force":17.50076,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.49241,-0.0513,0.0556]},{"body_a":"peg","body_b":"channel_base_body","contact_count":597.0,"contact_point_centroid":[0.49561,0.03425,0.00942],"force_p95":16.98162,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.76468,"mean_force":2.16493,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48904,0.12448,0.03957]},{"body_a":"peg","body_b":"channel_base_body","contact_count":98.0,"contact_point_centroid":[0.49863,-0.05468,0.00949],"force_p95":3.84649,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.06334,"mean_force":1.1021,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.49223,-0.05257,0.09758]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":58.0,"contact_point_centroid":[0.47455,-0.02356,0.04817],"force_p95":6.58608,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.26739,"mean_force":1.32569,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49323,0.0092,0.03731]},{"body_a":"peg","body_b":"channel_base_body","contact_count":266.0,"contact_point_centroid":[0.49467,0.05912,0.00932],"force_p95":0.66141,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.60116,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.4833,0.22543,0.2276]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.49872,0.20123,0.29469]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":52.0,"contact_point_centroid":[0.47481,-0.05737,0.03372],"force_p95":0.77987,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.81298,"mean_force":0.3691,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.49212,-0.05216,0.0904]},{"body_a":"peg","body_b":"channel_base_body","contact_count":329.0,"contact_point_centroid":[0.49425,0.05884,0.00939],"force_p95":0.55039,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55326,"mean_force":0.54626,"phase_index":1.0,"phase_name":"descend_align","phase_type":"descend","tcp_position_centroid":[0.47704,0.2519,0.1072]}],"total_contact_groups":11},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49414,-0.05387,0.03751],"final_tcp_position":[0.49222,-0.05277,0.11597],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":40.93599,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.49403,0.05895,0.03384],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13921,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54676,"phase_name":"approach_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":301.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_peg","tcp_end":[0.46947,0.24898,0.16642],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.23301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":329.0,"n_steps_budget":1000.0,"object_pos_end":[0.4941,0.05909,0.03388],"object_pos_start":[0.49403,0.05895,0.03384],"object_to_goal_dist_end":0.13935,"object_to_goal_dist_start":0.13921,"object_z_max":0.03388,"peak_contact_force":0.54966,"phase_name":"descend_align","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":329.0,"raw_peak_contact_force":0.55326,"subtask_id":"reach_peg","tcp_end":[0.48735,0.2559,0.04666],"tcp_start":[0.46947,0.24898,0.16642],"tcp_to_object_dist_end":0.19734,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":777.0,"n_steps_budget":1000.0,"object_pos_end":[0.50133,-0.08186,0.03749],"object_pos_start":[0.4941,0.05909,0.03388],"object_to_goal_dist_end":0.00339,"object_to_goal_dist_start":0.13935,"object_z_max":0.0402,"peak_contact_force":40.93599,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":867.0,"raw_peak_contact_force":40.93599,"subtask_id":"push_progress","tcp_end":[0.49534,-0.05316,0.03572],"tcp_start":[0.48735,0.2559,0.04666],"tcp_to_object_dist_end":0.02937,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":264.0,"n_steps_budget":930.0,"object_pos_end":[0.49414,-0.05387,0.03751],"object_pos_start":[0.50133,-0.08186,0.03749],"object_to_goal_dist_end":0.0269,"object_to_goal_dist_start":0.00339,"object_z_max":0.05731,"peak_contact_force":0.43131,"phase_name":"retract_after","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":430.0,"raw_peak_contact_force":40.08255,"tcp_end":[0.49222,-0.05277,0.11597],"tcp_start":[0.49534,-0.05316,0.03572],"tcp_to_object_dist_end":0.07849,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0981,"average_solve_count":316.0,"average_success_count":316.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_align.approach_height":0.06849,"approach_align.speed":0.03728,"descend_align.speed":0.03673,"push_through.speed":0.04136,"retract_after.speed":0.06873},"optimized_scores":{"best_composite_score":0.28115,"best_fitness_score":0.59115,"best_task_score":0.21767},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":134.0,"contact_point_centroid":[0.49554,-0.06235,0.05601],"force_p95":31.42006,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.0361,"mean_force":20.14837,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.49456,-0.05077,0.05458]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":23.0,"contact_point_centroid":[0.47482,-0.07654,0.03415],"force_p95":41.59562,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.37891,"mean_force":10.87822,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.49569,-0.05229,0.04552]},{"body_a":"attachment","body_b":"peg","contact_count":206.0,"contact_point_centroid":[0.50016,0.0131,0.04642],"force_p95":15.53167,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.96627,"mean_force":3.56145,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49877,0.02468,0.03762]},{"body_a":"peg","body_b":"channel_base_body","contact_count":144.0,"contact_point_centroid":[0.49613,-0.10043,0.06009],"force_p95":30.20304,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.03009,"mean_force":17.10858,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.49451,-0.05077,0.05615]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":73.0,"contact_point_centroid":[0.47439,-0.03874,0.02847],"force_p95":4.59296,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.4697,"mean_force":1.61642,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49803,-0.00885,0.03692]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.4978,-0.1009,0.01426],"force_p95":23.35413,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.93416,"mean_force":8.84389,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49713,-0.05101,0.03603]},{"body_a":"peg","body_b":"channel_base_body","contact_count":586.0,"contact_point_centroid":[0.5043,0.05141,0.00944],"force_p95":9.40346,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.97253,"mean_force":1.55187,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50145,0.14035,0.03993]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":55.0,"contact_point_centroid":[0.52541,0.02292,0.03315],"force_p95":15.06035,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.66327,"mean_force":1.50669,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49938,0.05287,0.03817]},{"body_a":"peg","body_b":"channel_base_body","contact_count":91.0,"contact_point_centroid":[0.50016,-0.06797,0.00943],"force_p95":2.3888,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.21091,"mean_force":0.8184,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.49401,-0.05203,0.10046]},{"body_a":"peg","body_b":"channel_base_body","contact_count":378.0,"contact_point_centroid":[0.50555,0.08091,0.00935],"force_p95":0.56235,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.58714,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.51433,0.23598,0.20686]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.50041,0.20117,0.29528]},{"body_a":"peg","body_b":"channel_base_body","contact_count":185.0,"contact_point_centroid":[0.50597,0.08078,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5501,"mean_force":0.54675,"phase_index":1.0,"phase_name":"descend_align","phase_type":"descend","tcp_position_centroid":[0.51803,0.27291,0.0863]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":12.0,"contact_point_centroid":[0.52508,-0.07435,0.05877],"force_p95":0.22567,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25173,"mean_force":0.10097,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.49401,-0.05222,0.11229]}],"total_contact_groups":13},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50195,-0.06388,0.04058],"final_tcp_position":[0.49404,-0.05226,0.11629],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":56.0361,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.55009,"phase_name":"approach_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":414.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.52882,0.27039,0.12376],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.21102,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":185.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54526,"phase_name":"descend_align","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":185.0,"raw_peak_contact_force":0.5501,"subtask_id":"reach_peg","tcp_end":[0.50768,0.27672,0.04767],"tcp_start":[0.52882,0.27039,0.12376],"tcp_to_object_dist_end":0.19632,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":808.0,"n_steps_budget":1000.0,"object_pos_end":[0.49485,-0.08247,0.0373],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.00632,"object_to_goal_dist_start":0.16113,"object_z_max":0.04007,"peak_contact_force":40.96627,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":928.0,"raw_peak_contact_force":40.96627,"subtask_id":"push_progress","tcp_end":[0.49715,-0.05266,0.03603],"tcp_start":[0.50768,0.27672,0.04767],"tcp_to_object_dist_end":0.02993,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":262.0,"n_steps_budget":930.0,"object_pos_end":[0.50195,-0.06388,0.04058],"object_pos_start":[0.49485,-0.08247,0.0373],"object_to_goal_dist_end":0.01624,"object_to_goal_dist_start":0.00632,"object_z_max":0.05788,"peak_contact_force":0.48499,"phase_name":"retract_after","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":404.0,"raw_peak_contact_force":56.0361,"tcp_end":[0.49404,-0.05226,0.11629],"tcp_start":[0.49715,-0.05266,0.03603],"tcp_to_object_dist_end":0.07701,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.82105,"average_solve_count":380.0,"average_success_count":380.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_align.approach_height":0.07908,"approach_align.speed":0.06355,"descend_align.speed":0.02055,"push_through.speed":0.02273,"retract_after.speed":0.02133},"optimized_scores":{"best_composite_score":0.41796,"best_fitness_score":0.72796,"best_task_score":0.52028},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":293.0,"contact_point_centroid":[0.50217,0.03345,0.04473],"force_p95":27.40831,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.39642,"mean_force":6.54989,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49812,0.04482,0.03787]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":263.0,"contact_point_centroid":[0.52529,0.02778,0.03411],"force_p95":27.45607,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.39061,"mean_force":4.84227,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49828,0.05624,0.03809]},{"body_a":"peg","body_b":"channel_base_body","contact_count":559.0,"contact_point_centroid":[0.50625,0.07164,0.00951],"force_p95":10.70273,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.85494,"mean_force":2.08108,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.5001,0.16321,0.04017]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50337,-0.06011,0.06045],"force_p95":13.54626,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.06167,"mean_force":3.01028,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.49622,-0.04885,0.03552]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":12.0,"contact_point_centroid":[0.52528,-0.07841,0.05956],"force_p95":8.21701,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.88474,"mean_force":1.61171,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.49539,-0.04886,0.03794]},{"body_a":"peg","body_b":"channel_base_body","contact_count":373.0,"contact_point_centroid":[0.50541,0.10467,0.00936],"force_p95":0.58313,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57669,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.50935,0.24693,0.21159]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.50031,0.20168,0.29561]},{"body_a":"peg","body_b":"channel_base_body","contact_count":284.0,"contact_point_centroid":[0.50582,-0.08134,0.00941],"force_p95":0.71202,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.18224,"mean_force":0.55415,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.49353,-0.04835,0.07378]},{"body_a":"peg","body_b":"channel_base_body","contact_count":216.0,"contact_point_centroid":[0.50612,0.10444,0.00939],"force_p95":0.57537,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57724,"mean_force":0.5463,"phase_index":1.0,"phase_name":"descend_align","phase_type":"descend","tcp_position_centroid":[0.51177,0.29484,0.09169]},{"body_a":"peg","body_b":"channel_base_body","contact_count":24.0,"contact_point_centroid":[0.5053,-0.10037,0.05881],"force_p95":0.40856,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55656,"mean_force":0.07968,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.49425,-0.04885,0.04071]}],"total_contact_groups":10},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50633,-0.08146,0.03383],"final_tcp_position":[0.49337,-0.04817,0.11615],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":41.39642,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":400.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.10471,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.57865,"phase_name":"approach_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":405.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_peg","tcp_end":[0.51916,0.29141,0.13313],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.21187,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":216.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.10463,0.03384],"object_pos_start":[0.50597,0.10471,0.03384],"object_to_goal_dist_end":0.18482,"object_to_goal_dist_start":0.18491,"object_z_max":0.03384,"peak_contact_force":0.55076,"phase_name":"descend_align","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":216.0,"raw_peak_contact_force":0.57724,"subtask_id":"reach_peg","tcp_end":[0.5053,0.29999,0.04792],"tcp_start":[0.51916,0.29141,0.13313],"tcp_to_object_dist_end":0.19586,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":849.0,"n_steps_budget":1000.0,"object_pos_end":[0.50675,-0.0778,0.03653],"object_pos_start":[0.50583,0.10463,0.03384],"object_to_goal_dist_end":0.0079,"object_to_goal_dist_start":0.18482,"object_z_max":0.03789,"peak_contact_force":41.39642,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1115.0,"raw_peak_contact_force":41.39642,"subtask_id":"push_progress","tcp_end":[0.49641,-0.04843,0.03568],"tcp_start":[0.5053,0.29999,0.04792],"tcp_to_object_dist_end":0.03114,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":286.0,"n_steps_budget":1000.0,"object_pos_end":[0.50633,-0.08146,0.03383],"object_pos_start":[0.50675,-0.0778,0.03653],"object_to_goal_dist_end":0.00896,"object_to_goal_dist_start":0.0079,"object_z_max":0.03653,"peak_contact_force":0.5452,"phase_name":"retract_after","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":326.0,"raw_peak_contact_force":18.06167,"tcp_end":[0.49337,-0.04817,0.11615],"tcp_start":[0.49641,-0.04843,0.03568],"tcp_to_object_dist_end":0.08974,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```