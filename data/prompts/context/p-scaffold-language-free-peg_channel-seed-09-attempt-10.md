## Search State

- **Seed**: 9
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | 0.0845 | 0.12 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | 0.3782 | 0.23 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.2691 | 0.03 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | 0.3809 | 0.25 | ✅ accepted |
| 6 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.0974 | 0.11 | ❌ rejected |

**Proposal policy**: task_score is 0.12 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`
- Frozen object start: [0.5296199363176067, 0.06294537672700443, 0.04]
- Frozen task target: [0.5296199363176067, -0.09705462327299558, 0.04]
- Goal object position: (0.5296199363176067, -0.09705462327299558, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5296199363176067, 0.06294537672700443, 0.04)
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
  frozen_object_start: [0.5296, 0.0629, 0.04]
  frozen_task_target: [0.5296, -0.0971, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5296199363176067, 0.06294537672700443, 0.04]}
  frozen_targets: {'channel_exit': [0.5296199363176067, -0.09705462327299558, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9

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
| `object` | offset from object initial position (0.5296199363176067, 0.06294537672700443, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5296199363176067, -0.09705462327299558, 0.04) | final destination targets |
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

## Current Skill (Q=0.084) — your mutation base

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
- id: push_through_channel
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_peg
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
    - 0.06
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
    lateral_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_peg
- id: contact_peg
  type: contact
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
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: peg_contact
    when: after_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.005
    - 0.0
- id: push_along_channel
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
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
      - 0.12
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_through_channel
- id: retract_from_channel
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.06, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - lateral_offset: status=consumed; consumers=target.offset.x (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=peg_contact, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.005, 0.0]
- **push_along_channel** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_from_channel** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.084
- **task_score** (E): 0.118
- **fitness_score**: 0.389  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.306
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.610

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2287 |
| contact_peg | 1.00 | 1.00 | 0.0478 |
| push_along_channel | 0.67 | 1.00 | 0.0676 |
| retract_from_channel | 1.00 | 1.00 | 0.0892 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.501, 0.130, 0.084) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.546 | 4.034 |
| contact_peg | contact | 1.00 / force_exceeded | (0.501, 0.130, 0.084)→(0.497, 0.095, 0.053) | (0.502, 0.067, 0.034)→(0.502, 0.065, 0.035) | 0.147→0.145 | 1.00 / 2.000 | 30.987 | 30.987 |
| push_along_channel | push | 0.67 / time_limit | (0.497, 0.095, 0.052)→(0.494, 0.028, 0.045) | (0.502, 0.065, 0.035)→(0.499, -0.007, 0.038) | 0.145→0.073 | 1.00 / 2.333 | 25.769 | 40.198 |
| retract_from_channel | retract | 1.00 / step_budget | (0.494, 0.028, 0.045)→(0.491, 0.028, 0.134) | (0.499, -0.007, 0.038)→(0.496, -0.020, 0.027) | 0.073→0.066 | 1.00 / 1.000 | 0.600 | 37.996 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.854
- alignment_error: None
- force_efficiency: 0.576
- terminal_score: 0.204
- phase_score: 0.794
- phase_breakdown.push_through_channel_score: 0.839
- phase_breakdown.reach_peg_score: 0.690

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.558
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.204
- **Median Q (composite search score)**: 0.193
- **K-run variance**: 0.0479
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.303


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `bf8103833c1e96f48e87b3ce39b3b3bf17e268470bd7b5c037546fb78b5150b8`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `98954a34ee744fa939070f7dadee8a411de43cdcfeddcf3b4bfc5c3a4c536020`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36145,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.03304,"approach_peg.lateral_offset":-0.0036,"approach_peg.speed":0.06507,"contact_peg.contact_force":14.93226,"push_along_channel.force_threshold":30.3108,"push_along_channel.push_distance":0.17787,"push_along_channel.push_lateral":0.00176,"push_along_channel.push_speed":0.06629,"push_along_channel.retry_lateral":0.00391,"retract_from_channel.retract_height":0.09585,"retract_from_channel.speed":0.05045},"optimized_scores":{"best_composite_score":0.28151,"best_fitness_score":0.55818,"best_task_score":0.20407},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":843.0,"contact_point_centroid":[0.49954,-0.05785,0.00945],"force_p95":0.70812,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.19106,"mean_force":0.53074,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.50117,-0.02082,0.08129]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.50088,-0.03242,0.03855],"force_p95":16.97479,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.66321,"mean_force":4.00558,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.50422,-0.02108,0.03793]},{"body_a":"peg","body_b":"channel_base_body","contact_count":989.0,"contact_point_centroid":[0.49982,-0.00306,0.0099],"force_p95":16.05078,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.91582,"mean_force":11.38167,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50467,0.03265,0.04047]},{"body_a":"attachment","body_b":"peg","contact_count":999.0,"contact_point_centroid":[0.50321,0.02148,0.04082],"force_p95":15.68165,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.62886,"mean_force":10.88015,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50468,0.03316,0.04051]},{"body_a":"peg","body_b":"channel_base_body","contact_count":330.0,"contact_point_centroid":[0.50539,0.05987,0.00944],"force_p95":8.8972,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.2479,"mean_force":1.32699,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51303,0.10584,0.0616]},{"body_a":"attachment","body_b":"peg","contact_count":32.0,"contact_point_centroid":[0.50736,0.07732,0.04888],"force_p95":14.27583,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.04222,"mean_force":8.35166,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50857,0.08922,0.04876]},{"body_a":"peg","body_b":"channel_base_body","contact_count":739.0,"contact_point_centroid":[0.50583,0.06301,0.00936],"force_p95":0.55699,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56487,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50988,0.16184,0.18557]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49984,0.19864,0.29641]},{"body_a":"peg","body_b":"channel_base_body","contact_count":547.0,"contact_point_centroid":[0.49335,-0.10003,0.02412],"force_p95":0.49669,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.53059,"mean_force":0.28051,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.50098,-0.0208,0.0766]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":25.0,"contact_point_centroid":[0.47462,-0.07662,0.05674],"force_p95":0.74283,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.89794,"mean_force":0.21194,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.50295,-0.02106,0.03991]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":141.0,"contact_point_centroid":[0.52503,-0.09659,0.0291],"force_p95":0.32226,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68219,"mean_force":0.18818,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.50102,-0.02079,0.09062]}],"total_contact_groups":11},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.496,-0.07361,0.02422],"final_tcp_position":[0.50128,-0.0208,0.12436],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":21.19106,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":767.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,0.06294,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54773,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":773.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_peg","tcp_end":[0.52099,0.12645,0.08072],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":330.0,"n_steps_budget":600.0,"object_pos_end":[0.50509,0.05828,0.03671],"object_pos_start":[0.50601,0.06294,0.03381],"object_to_goal_dist_end":0.13841,"object_to_goal_dist_start":0.1432,"object_z_max":0.03671,"peak_contact_force":15.2479,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":362.0,"raw_peak_contact_force":15.2479,"tcp_end":[0.50808,0.08693,0.04708],"tcp_start":[0.52099,0.12645,0.08072],"tcp_to_object_dist_end":0.03061,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49673,-0.05792,0.03998],"object_pos_start":[0.50509,0.05828,0.03671],"object_to_goal_dist_end":0.02232,"object_to_goal_dist_start":0.13841,"object_z_max":0.04055,"peak_contact_force":13.90787,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1988.0,"raw_peak_contact_force":17.91582,"subtask_id":"push_through_channel","tcp_end":[0.50456,-0.02092,0.03788],"tcp_start":[0.50808,0.08693,0.04708],"tcp_to_object_dist_end":0.03789,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":863.0,"n_steps_budget":1000.0,"object_pos_end":[0.496,-0.07361,0.02422],"object_pos_start":[0.49673,-0.05792,0.03998],"object_to_goal_dist_end":0.01748,"object_to_goal_dist_start":0.02232,"object_z_max":0.04013,"peak_contact_force":0.65535,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1567.0,"raw_peak_contact_force":21.19106,"tcp_end":[0.50128,-0.0208,0.12436],"tcp_start":[0.50456,-0.02092,0.03788],"tcp_to_object_dist_end":0.11333,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `cae0d95026bac46aa2e5d95cffd531753a79751757c4f25fa56c1ec6e19c2175`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38636,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.0325,"approach_peg.lateral_offset":-0.01776,"approach_peg.speed":0.07422,"contact_peg.contact_force":6.08389,"push_along_channel.force_threshold":28.51786,"push_along_channel.push_distance":0.15433,"push_along_channel.push_lateral":-0.00768,"push_along_channel.push_speed":0.05777,"push_along_channel.retry_lateral":-0.00147,"retract_from_channel.retract_height":0.11176,"retract_from_channel.speed":0.03912},"optimized_scores":{"best_composite_score":0.19289,"best_fitness_score":0.46955,"best_task_score":0.1491},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":15.0,"contact_point_centroid":[0.50297,-0.01815,0.03792],"force_p95":16.37155,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.8309,"mean_force":3.06563,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49856,-0.00722,0.03852]},{"body_a":"attachment","body_b":"peg","contact_count":977.0,"contact_point_centroid":[0.50392,0.02685,0.04219],"force_p95":23.853,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.6065,"mean_force":13.87193,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50096,0.03818,0.04256]},{"body_a":"peg","body_b":"channel_base_body","contact_count":994.0,"contact_point_centroid":[0.49868,-0.06407,0.00825],"force_p95":0.7524,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.41778,"mean_force":0.70772,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49575,-0.00704,0.08897]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50585,0.00464,0.00983],"force_p95":22.29831,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.81633,"mean_force":13.31373,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50105,0.03925,0.04272]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":264.0,"contact_point_centroid":[0.525,0.00018,0.02344],"force_p95":7.862,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.27673,"mean_force":5.95286,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50032,0.01872,0.04097]},{"body_a":"peg","body_b":"channel_base_body","contact_count":290.0,"contact_point_centroid":[0.50614,0.05646,0.00938],"force_p95":0.55422,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.19274,"mean_force":0.57987,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50885,0.10287,0.06364]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50655,0.0745,0.05573],"force_p95":7.1542,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.76043,"mean_force":3.43066,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50617,0.08648,0.05107]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52519,-0.04391,0.0248],"force_p95":5.82297,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.11436,"mean_force":1.99059,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49589,-0.00706,0.04859]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":21.0,"contact_point_centroid":[0.47496,-0.08456,0.02862],"force_p95":5.96811,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.05318,"mean_force":2.62616,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49574,-0.00705,0.07487]},{"body_a":"peg","body_b":"channel_base_body","contact_count":721.0,"contact_point_centroid":[0.50591,0.05661,0.00936],"force_p95":0.61917,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56858,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50641,0.15875,0.18521]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49976,0.19841,0.29591]}],"total_contact_groups":11},"final_pose_error":0.01098,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49861,-0.06682,0.02415],"final_tcp_position":[0.4959,-0.00702,0.13965],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":26.8309,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":750.0,"n_steps_budget":1000.0,"object_pos_end":[0.50612,0.05666,0.03379],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13693,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54721,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":758.0,"raw_peak_contact_force":4.44541,"subtask_id":"reach_peg","tcp_end":[0.51414,0.12046,0.0802],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":290.0,"n_steps_budget":600.0,"object_pos_end":[0.50614,0.05639,0.03388],"object_pos_start":[0.50612,0.05666,0.03379],"object_to_goal_dist_end":0.13667,"object_to_goal_dist_start":0.13693,"object_z_max":0.03381,"peak_contact_force":8.19274,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":293.0,"raw_peak_contact_force":8.19274,"tcp_end":[0.50614,0.08623,0.05089],"tcp_start":[0.51414,0.12046,0.0802],"tcp_to_object_dist_end":0.03434,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50646,-0.04387,0.04016],"object_pos_start":[0.50614,0.05639,0.03388],"object_to_goal_dist_end":0.03671,"object_to_goal_dist_start":0.13667,"object_z_max":0.04047,"peak_contact_force":21.28498,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2241.0,"raw_peak_contact_force":26.6065,"subtask_id":"push_through_channel","tcp_end":[0.49909,-0.00706,0.0384],"tcp_start":[0.50614,0.08623,0.05089],"tcp_to_object_dist_end":0.03758,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49861,-0.06682,0.02415],"object_pos_start":[0.50646,-0.04387,0.04016],"object_to_goal_dist_end":0.02066,"object_to_goal_dist_start":0.03671,"object_z_max":0.04022,"peak_contact_force":0.5683,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1049.0,"raw_peak_contact_force":26.8309,"tcp_end":[0.4959,-0.00702,0.13965],"tcp_start":[0.49909,-0.00706,0.0384],"tcp_to_object_dist_end":0.13009,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fd7ada9a67242f1adcdb6e23860d1223cdc8a17daf859e94e1687ff0564d9575`; realized-scene SHA-256: `8df62a5afc1e0110114ab6e06b493b5783d0c746729f7f7f1f2cb046babeda91`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47029,0.07994,0.04]},{"name":"goal","value":[0.47029,-0.08006,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,0.07994,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.47029,-0.08006,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66337,"average_solve_count":101.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.04155,"approach_peg.lateral_offset":0.0001,"approach_peg.speed":0.08086,"contact_peg.contact_force":8.02546,"push_along_channel.force_threshold":31.41219,"push_along_channel.push_distance":0.16049,"push_along_channel.push_lateral":-0.00457,"push_along_channel.push_speed":0.05836,"push_along_channel.retry_lateral":0.00587,"retract_from_channel.retract_height":0.08912,"retract_from_channel.speed":0.07112},"optimized_scores":{"best_composite_score":-0.22092,"best_fitness_score":0.13908,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47499,0.10073,0.05992],"force_p95":72.31257,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.07303,"mean_force":54.03231,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4773,0.11238,0.05955]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.10093,0.05999],"force_p95":69.52033,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.52033,"mean_force":69.52033,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.47719,0.11261,0.05972]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.47499,0.10053,0.05991],"force_p95":64.77457,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":65.96572,"mean_force":50.05889,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.47742,0.11213,0.05952]},{"body_a":"peg","body_b":"channel_base_body","contact_count":643.0,"contact_point_centroid":[0.49404,0.07993,0.00937],"force_p95":0.58449,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.56633,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4834,0.17025,0.19086]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49907,0.19869,0.29604]},{"body_a":"peg","body_b":"channel_base_body","contact_count":675.0,"contact_point_centroid":[0.49378,0.07995,0.00938],"force_p95":0.58347,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63281,"mean_force":0.54639,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.47436,0.11152,0.09941]},{"body_a":"peg","body_b":"channel_base_body","contact_count":277.0,"contact_point_centroid":[0.49375,0.08002,0.00938],"force_p95":0.58015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58702,"mean_force":0.54627,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.4719,0.12768,0.07404]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.50263,0.07845,0.00938],"force_p95":0.5823,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58271,"mean_force":0.55576,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4773,0.11238,0.05955]}],"total_contact_groups":8},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49382,0.08,0.03378],"final_tcp_position":[0.47434,0.11155,0.13912],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":76.07303,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":671.0,"n_steps_budget":1000.0,"object_pos_end":[0.49383,0.07994,0.03378],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.54265,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":678.0,"raw_peak_contact_force":3.77147,"subtask_id":"reach_peg","tcp_end":[0.46914,0.14277,0.09079],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08836,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":277.0,"n_steps_budget":600.0,"object_pos_end":[0.49383,0.07995,0.03377],"object_pos_start":[0.49383,0.07994,0.03378],"object_to_goal_dist_end":0.16019,"object_to_goal_dist_start":0.16018,"object_z_max":0.0338,"peak_contact_force":69.52033,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":278.0,"raw_peak_contact_force":69.52033,"tcp_end":[0.47724,0.1125,0.05962],"tcp_start":[0.46914,0.14277,0.09079],"tcp_to_object_dist_end":0.04476,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.49384,0.07995,0.03377],"object_pos_start":[0.49383,0.07995,0.03377],"object_to_goal_dist_end":0.16019,"object_to_goal_dist_start":0.16019,"object_z_max":0.03377,"peak_contact_force":42.11497,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":76.07303,"subtask_id":"push_through_channel","tcp_end":[0.47739,0.11222,0.05949],"tcp_start":[0.47736,0.11227,0.05951],"tcp_to_object_dist_end":0.04442,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":675.0,"n_steps_budget":810.0,"object_pos_end":[0.49382,0.08,0.03378],"object_pos_start":[0.4938,0.07996,0.03377],"object_to_goal_dist_end":0.16024,"object_to_goal_dist_start":0.1602,"object_z_max":0.03382,"peak_contact_force":0.57669,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":680.0,"raw_peak_contact_force":65.96572,"tcp_end":[0.47434,0.11155,0.13912],"tcp_start":[0.47739,0.11222,0.05949],"tcp_to_object_dist_end":0.11168,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```