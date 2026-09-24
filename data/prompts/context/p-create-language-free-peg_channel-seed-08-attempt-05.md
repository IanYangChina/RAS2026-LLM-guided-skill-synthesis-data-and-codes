## Search State

- **Seed**: 8
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.0207 | 0.32 | ❌ rejected |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.3826 | 0.47 | ❌ rejected |
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3295 | 0.32 | ❌ rejected |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.0664 | 0.00 | ❌ rejected |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.3662 | 0.43 | ❌ rejected |

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

## Current Skill (Q=-0.021) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.025
  - 0.0
  weight: 0.3
- id: push_complete
  offset:
  - 0.0
  - 0.025
  - 0.0
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
    - 0.05
    - 0.06
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_contact
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
    - 0.025
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  subtask_id: pre_contact
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.09
      - 0.18
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_complete
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.06], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.025, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.021
- **task_score** (E): 0.321
- **fitness_score**: 0.189  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2067 |
| descend_1 | 1.00 | 1.00 | 0.0782 |
| push_1 | 0.00 | 1.00 | 0.0561 |
| retract_1 | 1.00 | 1.00 | 0.1400 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.133, 0.108) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.554 | 3.526 |
| descend_1 | descend | 1.00 / step_budget | (0.513, 0.133, 0.108)→(0.500, 0.107, 0.037) | (0.503, 0.080, 0.034)→(0.503, 0.077, 0.035) | 0.160→0.157 | 1.00 / 1.000 | 0.514 | 111.347 |
| push_1 | push | 0.00 / step_budget | (0.500, 0.107, 0.037)→(0.525, 0.082, 0.075) | (0.503, 0.077, 0.035)→(0.502, -0.027, 0.024) | 0.157→0.056 | 1.00 / 2.000 | 299.334 | 1537.047 |
| retract_1 | retract | 1.00 / step_budget | (0.525, 0.082, 0.075)→(0.523, 0.082, 0.215) | (0.502, -0.027, 0.024)→(0.502, -0.027, 0.024) | 0.056→0.056 | 1.00 / 1.000 | 0.607 | 81.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.767
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.578
- phase_score: 0.100
- phase_breakdown.pre_contact_score: 0.271
- phase_breakdown.push_complete_score: 0.026

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.291
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.578
- **Median Q (composite search score)**: -0.058
- **K-run variance**: 0.0053
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.531


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47059,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04707,"push_1.push_distance":0.1581,"push_1.push_speed":0.10672},"optimized_scores":{"best_composite_score":0.08119,"best_fitness_score":0.29119,"best_task_score":0.57816},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.5469,0.1197,0.05917],"force_p95":1680.09172,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1725.55122,"mean_force":883.17001,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51092,0.12861,0.01464]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52549,0.11945,0.02111],"force_p95":1226.71729,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1249.83212,"mean_force":541.79708,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51784,0.12744,0.01981]},{"body_a":"world","body_b":"link7","contact_count":607.0,"contact_point_centroid":[0.49616,0.17095,-7e-05],"force_p95":326.34702,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":988.72115,"mean_force":280.49589,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50234,0.10846,0.04674]},{"body_a":"attachment","body_b":"world","contact_count":23.0,"contact_point_centroid":[0.5042,0.13537,-0.00076],"force_p95":787.32,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":821.39513,"mean_force":355.97183,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5022,0.12727,0.00694]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.51139,0.1198,0.00987],"force_p95":727.13648,"geom_a":"pusher_tip","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":735.67118,"mean_force":476.96691,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49963,0.12186,0.00931]},{"body_a":"world","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.49336,0.16179,-2e-05],"force_p95":86.67486,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.64005,"mean_force":68.98819,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50604,0.10143,0.04965]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.49855,0.1296,0.04422],"force_p95":36.73158,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.91017,"mean_force":15.64165,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49622,0.14118,0.0323]},{"body_a":"peg","body_b":"channel_base_body","contact_count":656.0,"contact_point_centroid":[0.49742,0.00162,0.00834],"force_p95":0.94893,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.86931,"mean_force":0.84075,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50233,0.10989,0.04461]},{"body_a":"peg","body_b":"channel_base_body","contact_count":454.0,"contact_point_centroid":[0.49662,0.11616,0.00949],"force_p95":4.45355,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.27422,"mean_force":0.90091,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48638,0.15718,0.07047]},{"body_a":"attachment","body_b":"peg","contact_count":30.0,"contact_point_centroid":[0.49395,0.13499,0.05138],"force_p95":9.31733,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.06827,"mean_force":5.77354,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49056,0.14687,0.04009]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47477,0.01807,0.04015],"force_p95":8.27775,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.14621,"mean_force":1.50028,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50182,0.11902,0.03036]},{"body_a":"peg","body_b":"channel_base_body","contact_count":843.0,"contact_point_centroid":[0.49601,-0.00377,0.00805],"force_p95":0.69706,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.45308,"mean_force":0.61508,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50419,0.10078,0.11932]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.475,0.01974,0.02421],"force_p95":7.36088,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.13405,"mean_force":2.97931,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50395,0.10058,0.0978]},{"body_a":"peg","body_b":"channel_base_body","contact_count":604.0,"contact_point_centroid":[0.49621,0.11908,0.00941],"force_p95":0.61197,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.5544,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49105,0.18433,0.20116]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":27.0,"contact_point_centroid":[0.5256,0.05648,0.03291],"force_p95":1.50307,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.61123,"mean_force":0.7343,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51167,0.12522,0.02442]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49951,0.19933,0.29797]}],"total_contact_groups":17},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4968,-0.0037,0.02414],"final_tcp_position":[0.50443,0.10118,0.18978],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":1725.55122,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":629.0,"n_steps_budget":1000.0,"object_pos_end":[0.496,0.11905,0.03385],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19919,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.55246,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":628.0,"raw_peak_contact_force":2.24822,"subtask_id":"pre_contact","tcp_end":[0.48406,0.17015,0.10968],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09222,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":458.0,"n_steps_budget":600.0,"object_pos_end":[0.49736,0.11576,0.03526],"object_pos_start":[0.496,0.11905,0.03385],"object_to_goal_dist_end":0.19584,"object_to_goal_dist_start":0.19919,"object_z_max":0.03548,"peak_contact_force":0.48022,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":484.0,"raw_peak_contact_force":13.27422,"subtask_id":"pre_contact","tcp_end":[0.49129,0.1452,0.03502],"tcp_start":[0.48406,0.17015,0.10968],"tcp_to_object_dist_end":0.03006,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":700.0,"n_steps_budget":930.0,"object_pos_end":[0.49706,-0.00381,0.02413],"object_pos_start":[0.49736,0.11576,0.03526],"object_to_goal_dist_end":0.07788,"object_to_goal_dist_start":0.19584,"object_z_max":0.04073,"peak_contact_force":273.21656,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1383.0,"raw_peak_contact_force":1725.55122,"subtask_id":"push_complete","tcp_end":[0.50605,0.10145,0.04963],"tcp_start":[0.49129,0.1452,0.03502],"tcp_to_object_dist_end":0.10868,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.4968,-0.0037,0.02414],"object_pos_start":[0.49706,-0.00381,0.02413],"object_to_goal_dist_end":0.078,"object_to_goal_dist_start":0.07788,"object_z_max":0.02432,"peak_contact_force":0.59384,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":848.0,"raw_peak_contact_force":88.64005,"tcp_end":[0.50443,0.10118,0.18978],"tcp_start":[0.50605,0.10145,0.04963],"tcp_to_object_dist_end":0.1962,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68841,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.09896,"push_1.push_distance":0.09196,"push_1.push_speed":0.04645},"optimized_scores":{"best_composite_score":-0.05793,"best_fitness_score":0.15207,"best_task_score":0.22454},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.52596,0.08175,0.05983],"force_p95":1325.50177,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1438.60991,"mean_force":754.30885,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50957,0.07775,0.03263]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":547.0,"contact_point_centroid":[0.52577,0.11973,0.05994],"force_p95":455.04609,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":638.26822,"mean_force":361.60918,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52404,0.0733,0.08329]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.52501,0.11995,0.05995],"force_p95":74.15121,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.21124,"mean_force":60.22038,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52965,0.07534,0.08513]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50665,0.07721,0.04693],"force_p95":40.59071,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.33115,"mean_force":20.45384,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50586,0.08898,0.03615]},{"body_a":"peg","body_b":"channel_base_body","contact_count":533.0,"contact_point_centroid":[0.50295,-0.03005,0.00819],"force_p95":1.97772,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.3762,"mean_force":1.22257,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52443,0.07361,0.08394]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":42.0,"contact_point_centroid":[0.47449,-0.02307,0.03576],"force_p95":17.60724,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.52405,"mean_force":4.18885,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51091,0.07035,0.05868]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.50611,0.07995,0.04877],"force_p95":13.90129,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.27481,"mean_force":6.89831,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50499,0.09196,0.04026]},{"body_a":"peg","body_b":"channel_base_body","contact_count":334.0,"contact_point_centroid":[0.50586,0.06177,0.00941],"force_p95":0.5541,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.27182,"mean_force":0.8027,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51354,0.10443,0.07182]},{"body_a":"peg","body_b":"channel_base_body","contact_count":843.0,"contact_point_centroid":[0.50443,-0.02843,0.00805],"force_p95":0.6834,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.10846,"mean_force":0.62501,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52777,0.07495,0.15451]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.525,-0.00402,0.02427],"force_p95":8.58503,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.6471,"mean_force":3.63849,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52798,0.07526,0.22081]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":27.0,"contact_point_centroid":[0.5252,0.01352,0.02187],"force_p95":8.38584,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.42545,"mean_force":2.52016,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52024,0.0755,0.06722]},{"body_a":"peg","body_b":"channel_base_body","contact_count":643.0,"contact_point_centroid":[0.50577,0.06294,0.00936],"force_p95":0.56061,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.5676,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51177,0.15714,0.19871]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49996,0.19829,0.29616]}],"total_contact_groups":13},"final_pose_error":0.01027,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50606,-0.02795,0.02434],"final_tcp_position":[0.52803,0.07529,0.22495],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":1438.60991,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":671.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.06301,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14327,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54796,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":677.0,"raw_peak_contact_force":3.88411,"subtask_id":"pre_contact","tcp_end":[0.52444,0.11752,0.10702],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":336.0,"n_steps_budget":600.0,"object_pos_end":[0.50516,0.06073,0.03483],"object_pos_start":[0.50594,0.06301,0.0338],"object_to_goal_dist_end":0.14092,"object_to_goal_dist_start":0.14327,"object_z_max":0.03506,"peak_contact_force":0.59084,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":347.0,"raw_peak_contact_force":14.27481,"subtask_id":"pre_contact","tcp_end":[0.50423,0.09085,0.03743],"tcp_start":[0.52444,0.11752,0.10702],"tcp_to_object_dist_end":0.03025,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":599.0,"n_steps_budget":1000.0,"object_pos_end":[0.50465,-0.02834,0.02413],"object_pos_start":[0.50516,0.06073,0.03483],"object_to_goal_dist_end":0.05424,"object_to_goal_dist_start":0.14092,"object_z_max":0.04099,"peak_contact_force":315.77617,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1172.0,"raw_peak_contact_force":1438.60991,"subtask_id":"push_complete","tcp_end":[0.52965,0.07533,0.08509],"tcp_start":[0.50423,0.09085,0.03743],"tcp_to_object_dist_end":0.12284,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.50606,-0.02795,0.02434],"object_pos_start":[0.50465,-0.02834,0.02413],"object_to_goal_dist_end":0.0547,"object_to_goal_dist_start":0.05424,"object_z_max":0.0244,"peak_contact_force":0.66527,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":852.0,"raw_peak_contact_force":75.21124,"tcp_end":[0.52803,0.07529,0.22495],"tcp_start":[0.52965,0.07533,0.08509],"tcp_to_object_dist_end":0.22668,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44792,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04356,"push_1.push_distance":0.14841,"push_1.push_speed":0.08456},"optimized_scores":{"best_composite_score":-0.08523,"best_fitness_score":0.12477,"best_task_score":0.15979},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.52596,0.07551,0.05983],"force_p95":1325.83418,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1446.98125,"mean_force":772.52826,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50948,0.07165,0.03231]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":700.0,"contact_point_centroid":[0.52698,0.11965,0.05994],"force_p95":454.77612,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":651.08224,"mean_force":363.28684,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52927,0.06619,0.08945]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52523,0.09405,0.05995],"force_p95":306.07051,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":306.49261,"mean_force":201.20198,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51335,0.09415,0.06082]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.52509,-0.00859,0.02899],"force_p95":18.51052,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":81.11291,"mean_force":6.44955,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52104,0.06738,0.07733]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50802,0.06966,0.04338],"force_p95":69.32518,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":80.33898,"mean_force":26.48068,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50812,0.08104,0.03529]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.525,0.11996,0.05996],"force_p95":79.42485,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.5638,"mean_force":70.79929,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53836,0.06965,0.09001]},{"body_a":"peg","body_b":"channel_base_body","contact_count":709.0,"contact_point_centroid":[0.50322,-0.04236,0.0084],"force_p95":0.83686,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.32743,"mean_force":0.74411,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.529,0.06628,0.08898]},{"body_a":"peg","body_b":"channel_base_body","contact_count":339.0,"contact_point_centroid":[0.50624,0.05596,0.00939],"force_p95":0.60987,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.7854,"mean_force":0.66315,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51723,0.09821,0.07121]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50661,0.07411,0.04443],"force_p95":11.98342,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.42342,"mean_force":6.17437,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50648,0.08611,0.04115]},{"body_a":"peg","body_b":"channel_base_body","contact_count":843.0,"contact_point_centroid":[0.50379,-0.04808,0.00804],"force_p95":0.72554,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.45392,"mean_force":0.62141,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53655,0.06939,0.15945]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.525,-0.02533,0.02416],"force_p95":7.20048,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.2176,"mean_force":3.80205,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53627,0.06912,0.12067]},{"body_a":"peg","body_b":"channel_base_body","contact_count":728.0,"contact_point_centroid":[0.50593,0.05662,0.00936],"force_p95":0.60172,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56837,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51497,0.15408,0.19861]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49989,0.19832,0.29638]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":25.0,"contact_point_centroid":[0.47392,0.00584,0.05668],"force_p95":1.97097,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.52428,"mean_force":0.69776,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50883,0.06576,0.04652]}],"total_contact_groups":14},"final_pose_error":0.01017,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50333,-0.04786,0.0241],"final_tcp_position":[0.53679,0.06972,0.22991],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":1446.98125,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":757.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.05665,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13692,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.56037,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":765.0,"raw_peak_contact_force":4.44541,"subtask_id":"pre_contact","tcp_end":[0.53091,0.11141,0.10648],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09435,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.50592,0.05435,0.0347],"object_pos_start":[0.50611,0.05665,0.03377],"object_to_goal_dist_end":0.13459,"object_to_goal_dist_start":0.13692,"object_z_max":0.03468,"peak_contact_force":0.47217,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":362.0,"raw_peak_contact_force":306.49261,"subtask_id":"pre_contact","tcp_end":[0.50521,0.08467,0.03761],"tcp_start":[0.53091,0.11141,0.10648],"tcp_to_object_dist_end":0.03046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":750.0,"n_steps_budget":1000.0,"object_pos_end":[0.50404,-0.0484,0.02414],"object_pos_start":[0.50592,0.05435,0.0347],"object_to_goal_dist_end":0.03559,"object_to_goal_dist_start":0.13459,"object_z_max":0.042,"peak_contact_force":309.00866,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1475.0,"raw_peak_contact_force":1446.98125,"subtask_id":"push_complete","tcp_end":[0.53836,0.06964,0.08995],"tcp_start":[0.50521,0.08467,0.03761],"tcp_to_object_dist_end":0.13944,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.50333,-0.04786,0.0241],"object_pos_start":[0.50404,-0.0484,0.02414],"object_to_goal_dist_end":0.03601,"object_to_goal_dist_start":0.03559,"object_z_max":0.02437,"peak_contact_force":0.56202,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":851.0,"raw_peak_contact_force":79.5638,"tcp_end":[0.53679,0.06972,0.22991],"tcp_start":[0.53836,0.06964,0.08995],"tcp_to_object_dist_end":0.23938,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```