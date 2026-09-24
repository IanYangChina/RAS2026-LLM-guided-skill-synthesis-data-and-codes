## Search State

- **Seed**: 7
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.0671 | 0.31 | ❌ rejected |
| 1 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1237 | 0.42 | ✅ accepted |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.2119 | 0.23 | ✅ accepted |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`
- Frozen object start: [0.5100076373283734, 0.11177710407756605, 0.04]
- Frozen task target: [0.5100076373283734, -0.04822289592243395, 0.04]
- Goal object position: (0.5100076373283734, -0.04822289592243395, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5100076373283734, 0.11177710407756605, 0.04)
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
  frozen_object_start: [0.51, 0.1118, 0.04]
  frozen_task_target: [0.51, -0.0482, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5100076373283734, 0.11177710407756605, 0.04]}
  frozen_targets: {'channel_exit': [0.5100076373283734, -0.04822289592243395, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415

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
| `object` | offset from object initial position (0.5100076373283734, 0.11177710407756605, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5100076373283734, -0.04822289592243395, 0.04) | final destination targets |
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

## Current Skill (Q=0.067) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: align_standoff
  anchor: object
  offset:
  - 0.0
  - 0.025
  - 0.05
  weight: 0.3
- id: push_goal
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
    - 0.025
    - 0.05
    tolerance: 0.005
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: align_standoff
- id: contact_1
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
    - 0.025
    - 0.005
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: align_standoff
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - -0.02
    tolerance: 0.005
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
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
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: continue
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: push_goal
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.01
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.025, 0.05], tolerance=0.005
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.025, 0.005]
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **align_1** (`align`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, -0.02], tolerance=0.005
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.01
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=continue, threshold=40.0
  - retries: max_attempts=1, strategy=reduce_speed
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.067
- **task_score** (E): 0.313
- **fitness_score**: 0.307  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.67 | 1.00 | 0.1989 |
| contact_1 | 1.00 | 1.00 | 0.0573 |
| align_1 | 1.00 | 1.00 | 0.0158 |
| push_1 | 0.00 | 1.00 | 0.0325 |
| retract_1 | 0.00 | 1.00 | 0.0206 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.67 / step_budget | (0.500, 0.200, 0.300)→(0.502, 0.136, 0.113) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.527 | 2.732 |
| contact_1 | contact | 1.00 / force_exceeded | (0.502, 0.136, 0.113)→(0.497, 0.124, 0.058) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 2.000 | 17.313 | 17.313 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.124, 0.058)→(0.495, 0.127, 0.043) | (0.502, 0.098, 0.034)→(0.503, 0.097, 0.034) | 0.178→0.177 | 1.00 / 2.333 | 122.116 | 202.111 |
| push_1 | push | 0.00 / step_budget | (0.495, 0.127, 0.043)→(0.506, 0.100, 0.047) | (0.503, 0.097, 0.034)→(0.503, 0.058, 0.029) | 0.177→0.139 | 1.00 / 4.000 | 292.937 | 739.151 |
| retract_1 | retract | 0.00 / step_budget | (0.506, 0.100, 0.047)→(0.506, 0.082, 0.049) | (0.503, 0.058, 0.029)→(0.502, 0.039, 0.027) | 0.139→0.120 | 1.00 / 2.333 | 261.445 | 279.482 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.566
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.566
- phase_score: 0.485
- phase_breakdown.push_goal_score: 0.454
- phase_breakdown.align_standoff_score: 0.556

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.517
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.566
- **Median Q (composite search score)**: 0.020
- **K-run variance**: 0.0243
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at lower bound**: contact_1.speed
- **Parameters at upper bound**: approach_1.speed
- **Final σ (mean)**: 0.226


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.8883,"average_solve_count":188.0,"average_success_count":188.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.01751,"approach_1.speed":0.1,"contact_1.contact_force":2.68642,"contact_1.speed":0.01925,"push_1.push_distance":0.14537,"push_1.push_speed":0.04789,"retract_1.retract_speed":0.03049},"optimized_scores":{"best_composite_score":0.27714,"best_fitness_score":0.51714,"best_task_score":0.56598},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":884.0,"contact_point_centroid":[0.48935,0.16762,-5e-05],"force_p95":238.73766,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1170.7046,"mean_force":203.73285,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50262,0.1034,0.04893]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47488,0.1199,0.02261],"force_p95":931.36292,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":940.2537,"mean_force":577.10376,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48518,0.11952,0.0167]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.55496,0.11987,0.05953],"force_p95":719.99517,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":752.17841,"mean_force":437.36093,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50973,0.12767,0.03085]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52514,0.11969,0.05997],"force_p95":585.3221,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":613.70395,"mean_force":368.95392,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50912,0.1276,0.03561]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":137.0,"contact_point_centroid":[0.47351,0.1199,0.06],"force_p95":309.43415,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":435.86945,"mean_force":264.58111,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50454,0.08111,0.05065]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.49558,0.11987,0.0099],"force_p95":263.6423,"geom_a":"pusher_tip","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":307.45948,"mean_force":137.89301,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48531,0.11991,0.01595]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1000.0,"contact_point_centroid":[0.47309,0.11995,0.06],"force_p95":186.09603,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":193.64541,"mean_force":165.63624,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50485,0.08204,0.04987]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50441,0.12092,0.04358],"force_p95":169.57206,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":172.22105,"mean_force":65.18884,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50391,0.13242,0.04333]},{"body_a":"peg","body_b":"channel_base_body","contact_count":962.0,"contact_point_centroid":[0.50051,0.02442,0.00824],"force_p95":0.77123,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":171.14449,"mean_force":1.0858,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50233,0.10447,0.04773]},{"body_a":"peg","body_b":"channel_base_body","contact_count":139.0,"contact_point_centroid":[0.50439,0.1117,0.00871],"force_p95":93.88967,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":101.22106,"mean_force":46.89502,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50078,0.13761,0.05558]},{"body_a":"attachment","body_b":"peg","contact_count":105.0,"contact_point_centroid":[0.50782,0.12886,0.05574],"force_p95":94.41628,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":100.67118,"mean_force":61.43161,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50101,0.13761,0.05726]},{"body_a":"world","body_b":"link7","contact_count":92.0,"contact_point_centroid":[0.48959,0.1448,-1e-05],"force_p95":39.46166,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":56.22816,"mean_force":21.76838,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5048,0.08162,0.05073]},{"body_a":"peg","body_b":"channel_base_body","contact_count":179.0,"contact_point_centroid":[0.50357,0.11154,0.00941],"force_p95":0.59937,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.78457,"mean_force":0.69612,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5027,0.13728,0.07755]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50954,0.12887,0.05872],"force_p95":27.25312,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.25312,"mean_force":27.25312,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50109,0.13662,0.06219]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50474,0.02116,0.00803],"force_p95":0.72552,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.16506,"mean_force":0.64589,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50485,0.08204,0.04987]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":40.0,"contact_point_centroid":[0.526,0.07192,0.03201],"force_p95":1.57188,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.80755,"mean_force":0.83647,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50779,0.12198,0.0342]}],"total_contact_groups":20},"final_pose_error":0.16814,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50522,0.02122,0.02409],"final_tcp_position":[0.50566,0.08289,0.04871],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":1170.7046,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.11172,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19186,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.52515,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":994.0,"raw_peak_contact_force":2.06328,"subtask_id":"align_standoff","tcp_end":[0.50595,0.13843,0.09345],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06539,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":179.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.11179,0.03382],"object_pos_start":[0.50374,0.11172,0.0338],"object_to_goal_dist_end":0.19193,"object_to_goal_dist_start":0.19186,"object_z_max":0.03386,"peak_contact_force":27.78457,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":180.0,"raw_peak_contact_force":27.78457,"subtask_id":"align_standoff","tcp_end":[0.50109,0.13662,0.06203],"tcp_start":[0.50595,0.13843,0.09345],"tcp_to_object_dist_end":0.03768,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":139.0,"n_steps_budget":720.0,"object_pos_end":[0.50277,0.10638,0.03553],"object_pos_start":[0.50376,0.11179,0.03382],"object_to_goal_dist_end":0.18646,"object_to_goal_dist_start":0.19193,"object_z_max":0.03546,"peak_contact_force":0.4067,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":244.0,"raw_peak_contact_force":101.22106,"tcp_end":[0.49897,0.13691,0.04646],"tcp_start":[0.50109,0.13662,0.06203],"tcp_to_object_dist_end":0.03264,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50619,0.02037,0.02414],"object_pos_start":[0.50277,0.10638,0.03553],"object_to_goal_dist_end":0.10181,"object_to_goal_dist_start":0.18646,"object_z_max":0.04081,"peak_contact_force":255.88144,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2076.0,"raw_peak_contact_force":1170.7046,"subtask_id":"push_goal","tcp_end":[0.5048,0.08149,0.05068],"tcp_start":[0.49897,0.13691,0.04646],"tcp_to_object_dist_end":0.06665,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50522,0.02122,0.02409],"object_pos_start":[0.50619,0.02037,0.02414],"object_to_goal_dist_end":0.1026,"object_to_goal_dist_start":0.10181,"object_z_max":0.02465,"peak_contact_force":184.7533,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2104.0,"raw_peak_contact_force":193.64541,"tcp_end":[0.50566,0.08289,0.04871],"tcp_start":[0.5048,0.08149,0.05068],"tcp_to_object_dist_end":0.0664,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.75697,"average_solve_count":251.0,"average_success_count":251.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.0135,"approach_1.speed":0.06839,"contact_1.contact_force":6.40103,"contact_1.speed":0.005,"push_1.push_distance":0.13966,"push_1.push_speed":0.03689,"retract_1.retract_speed":0.06508},"optimized_scores":{"best_composite_score":0.01952,"best_fitness_score":0.25952,"best_task_score":0.32489},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"attachment","body_b":"world","contact_count":28.0,"contact_point_centroid":[0.471,0.17871,-0.00078],"force_p95":405.05541,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":415.97098,"mean_force":251.42946,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46652,0.17229,0.0074]},{"body_a":"peg","body_b":"channel_base_body","contact_count":931.0,"contact_point_centroid":[0.50108,0.11987,0.00976],"force_p95":70.30411,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":327.7941,"mean_force":16.56771,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49486,0.15574,0.04061]},{"body_a":"attachment","body_b":"peg","contact_count":959.0,"contact_point_centroid":[0.49627,0.15711,0.0322],"force_p95":73.08154,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":327.53002,"mean_force":26.85975,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49448,0.15611,0.04015]},{"body_a":"world","body_b":"link7","contact_count":901.0,"contact_point_centroid":[0.47618,0.22093,-5e-05],"force_p95":274.80266,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":300.30258,"mean_force":239.31645,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49555,0.15572,0.04141]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":665.0,"contact_point_centroid":[0.46672,0.11994,0.05999],"force_p95":183.89256,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":186.33525,"mean_force":166.57582,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4975,0.08147,0.04958]},{"body_a":"peg","body_b":"channel_base_body","contact_count":406.0,"contact_point_centroid":[0.49302,0.11905,0.00799],"force_p95":109.8837,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":122.67506,"mean_force":83.85606,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48587,0.1488,0.05126]},{"body_a":"attachment","body_b":"peg","contact_count":406.0,"contact_point_centroid":[0.49336,0.14092,0.04929],"force_p95":109.37581,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":121.89445,"mean_force":83.3632,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48587,0.1488,0.05126]},{"body_a":"world","body_b":"link7","contact_count":76.0,"contact_point_centroid":[0.47702,0.19374,-0.0],"force_p95":70.56833,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":95.43533,"mean_force":58.50979,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49859,0.13034,0.04225]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":302.0,"contact_point_centroid":[0.47468,0.11982,0.02675],"force_p95":20.25429,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.84512,"mean_force":16.79581,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49857,0.14192,0.04256]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":785.0,"contact_point_centroid":[0.52527,0.11231,0.02268],"force_p95":28.83929,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":64.25056,"mean_force":16.3325,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49678,0.15476,0.04281]},{"body_a":"attachment","body_b":"peg","contact_count":225.0,"contact_point_centroid":[0.50321,0.11317,0.04271],"force_p95":41.8502,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.10915,"mean_force":7.20189,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49767,0.11239,0.04447]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":63.0,"contact_point_centroid":[0.47468,0.11986,0.02768],"force_p95":38.22798,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.99892,"mean_force":18.14914,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49907,0.13539,0.04183]},{"body_a":"peg","body_b":"world","contact_count":82.0,"contact_point_centroid":[0.48773,0.15624,-0.00063],"force_p95":18.06027,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.24093,"mean_force":2.83571,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48485,0.16775,0.03023]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":45.0,"contact_point_centroid":[0.52513,0.09137,0.02842],"force_p95":16.28598,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.95881,"mean_force":10.98454,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49912,0.13429,0.04205]},{"body_a":"peg","body_b":"channel_base_body","contact_count":278.0,"contact_point_centroid":[0.49596,0.1195,0.00944],"force_p95":0.60266,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.43315,"mean_force":0.59427,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48352,0.1446,0.07767]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49484,0.13706,0.05877],"force_p95":14.92105,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.92105,"mean_force":14.92105,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48587,0.14395,0.06273]}],"total_contact_groups":19},"final_pose_error":0.16746,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49553,0.0543,0.02413],"final_tcp_position":[0.49899,0.08241,0.04917],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":415.97098,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.11905,0.03392],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19919,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50789,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":999.0,"raw_peak_contact_force":2.24822,"subtask_id":"align_standoff","tcp_end":[0.48339,0.14598,0.09638],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":278.0,"n_steps_budget":1000.0,"object_pos_end":[0.49606,0.11904,0.03384],"object_pos_start":[0.49603,0.11905,0.03392],"object_to_goal_dist_end":0.19917,"object_to_goal_dist_start":0.19919,"object_z_max":0.03406,"peak_contact_force":15.43315,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":279.0,"raw_peak_contact_force":15.43315,"subtask_id":"align_standoff","tcp_end":[0.48589,0.14395,0.06264],"tcp_start":[0.48339,0.14598,0.09638],"tcp_to_object_dist_end":0.03941,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":406.0,"n_steps_budget":930.0,"object_pos_end":[0.49892,0.12302,0.03126],"object_pos_start":[0.49606,0.11904,0.03384],"object_to_goal_dist_end":0.20321,"object_to_goal_dist_start":0.19917,"object_z_max":0.03384,"peak_contact_force":93.26644,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":812.0,"raw_peak_contact_force":122.67506,"tcp_end":[0.48661,0.15202,0.04652],"tcp_start":[0.48589,0.14395,0.06264],"tcp_to_object_dist_end":0.03501,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4986,0.11054,0.02839],"object_pos_start":[0.49892,0.12302,0.03126],"object_to_goal_dist_end":0.1909,"object_to_goal_dist_start":0.20321,"object_z_max":0.03126,"peak_contact_force":240.70151,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3988.0,"raw_peak_contact_force":415.97098,"subtask_id":"push_goal","tcp_end":[0.49953,0.13832,0.0415],"tcp_start":[0.48661,0.15202,0.04652],"tcp_to_object_dist_end":0.03073,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49553,0.0543,0.02413],"object_pos_start":[0.4986,0.11054,0.02839],"object_to_goal_dist_end":0.13531,"object_to_goal_dist_start":0.1909,"object_z_max":0.02845,"peak_contact_force":181.40697,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2048.0,"raw_peak_contact_force":186.33525,"tcp_end":[0.49899,0.08241,0.04917],"tcp_start":[0.49953,0.13832,0.0415],"tcp_to_object_dist_end":0.0378,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.6229,"average_solve_count":297.0,"average_success_count":297.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.02052,"approach_1.speed":0.03598,"contact_1.contact_force":6.30956,"contact_1.speed":0.02034,"push_1.push_distance":0.16387,"push_1.push_speed":0.03391,"retract_1.retract_speed":0.05318},"optimized_scores":{"best_composite_score":-0.09544,"best_fitness_score":0.14456,"best_task_score":0.04771},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":308.0,"contact_point_centroid":[0.53025,0.11875,0.05998],"force_p95":405.3759,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":630.77708,"mean_force":164.21169,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50963,0.08077,0.05069]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":29.0,"contact_point_centroid":[0.52506,0.08427,0.05348],"force_p95":575.69645,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":614.08554,"mean_force":199.64403,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50889,0.08323,0.04572]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1000.0,"contact_point_centroid":[0.47495,0.11992,0.05849],"force_p95":428.64859,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":458.46558,"mean_force":341.12431,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51316,0.08032,0.04968]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":68.0,"contact_point_centroid":[0.54543,0.09213,0.05981],"force_p95":380.44868,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":382.43555,"mean_force":317.09038,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50069,0.09177,0.03604]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":147.0,"contact_point_centroid":[0.47498,0.11996,0.05728],"force_p95":242.70802,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":382.22699,"mean_force":184.29815,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51268,0.07928,0.04999]},{"body_a":"world","body_b":"link7","contact_count":849.0,"contact_point_centroid":[0.49777,0.14626,-7e-05],"force_p95":305.33181,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":372.2824,"mean_force":250.56312,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51073,0.08192,0.04975]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1000.0,"contact_point_centroid":[0.52506,0.08144,0.04974],"force_p95":248.10785,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":263.98861,"mean_force":185.77256,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51316,0.08032,0.04968]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":46.0,"contact_point_centroid":[0.52503,0.09193,0.05999],"force_p95":229.26795,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":231.09694,"mean_force":171.54303,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50078,0.09179,0.03608]},{"body_a":"world","body_b":"link7","contact_count":85.0,"contact_point_centroid":[0.49792,0.14309,-2e-05],"force_p95":71.97316,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":110.64262,"mean_force":39.62619,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51312,0.07942,0.0501]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50498,0.04224,0.00942],"force_p95":0.62889,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.61843,"mean_force":0.5971,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51009,0.08207,0.05043]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.50444,0.07922,0.04255],"force_p95":26.18535,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.1164,"mean_force":5.17867,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50076,0.09105,0.0371]},{"body_a":"peg","body_b":"channel_base_body","contact_count":585.0,"contact_point_centroid":[0.50592,0.06258,0.00938],"force_p95":0.55277,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.72188,"mean_force":0.57121,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50907,0.10722,0.0991]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50559,0.08076,0.05526],"force_p95":7.70465,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.49101,"mean_force":3.21753,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50368,0.0927,0.05152]},{"body_a":"peg","body_b":"channel_base_body","contact_count":145.0,"contact_point_centroid":[0.50662,0.04938,0.00972],"force_p95":5.21354,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.05847,"mean_force":1.16869,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50113,0.0918,0.03982]},{"body_a":"attachment","body_b":"peg","contact_count":67.0,"contact_point_centroid":[0.50544,0.07988,0.04722],"force_p95":7.17848,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.74656,"mean_force":1.66933,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50097,0.09179,0.03838]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50586,0.06296,0.00937],"force_p95":0.55508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56049,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50791,0.15919,0.22036]}],"total_contact_groups":19},"final_pose_error":0.16757,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50506,0.04264,0.03378],"final_tcp_position":[0.51323,0.08204,0.04943],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":630.77708,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54709,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1006.0,"raw_peak_contact_force":3.88411,"subtask_id":"align_standoff","tcp_end":[0.51706,0.12223,0.15059],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13143,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":585.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.06256,0.03433],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.1428,"object_to_goal_dist_start":0.14323,"object_z_max":0.03429,"peak_contact_force":8.72188,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":590.0,"raw_peak_contact_force":8.72188,"subtask_id":"align_standoff","tcp_end":[0.50349,0.09218,0.04978],"tcp_start":[0.51706,0.12223,0.15059],"tcp_to_object_dist_end":0.0335,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":145.0,"n_steps_budget":630.0,"object_pos_end":[0.50592,0.06196,0.03458],"object_pos_start":[0.50598,0.06256,0.03433],"object_to_goal_dist_end":0.14219,"object_to_goal_dist_start":0.1428,"object_z_max":0.03511,"peak_contact_force":272.67389,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":326.0,"raw_peak_contact_force":382.43555,"tcp_end":[0.50086,0.09182,0.03643],"tcp_start":[0.50349,0.09218,0.04978],"tcp_to_object_dist_end":0.03034,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50505,0.04271,0.03382],"object_pos_start":[0.50592,0.06196,0.03458],"object_to_goal_dist_end":0.12297,"object_to_goal_dist_start":0.14219,"object_z_max":0.03922,"peak_contact_force":382.22699,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2358.0,"raw_peak_contact_force":630.77708,"subtask_id":"push_goal","tcp_end":[0.5132,0.0794,0.05003],"tcp_start":[0.50086,0.09182,0.03643],"tcp_to_object_dist_end":0.04094,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50506,0.04264,0.03378],"object_pos_start":[0.50505,0.04271,0.03382],"object_to_goal_dist_end":0.1229,"object_to_goal_dist_start":0.12297,"object_z_max":0.03382,"peak_contact_force":418.17348,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3085.0,"raw_peak_contact_force":458.46558,"tcp_end":[0.51323,0.08204,0.04943],"tcp_start":[0.5132,0.0794,0.05003],"tcp_to_object_dist_end":0.04318,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```