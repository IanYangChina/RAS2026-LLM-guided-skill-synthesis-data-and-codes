## Search State

- **Seed**: 8
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.3826 | 0.47 | ❌ rejected |
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3295 | 0.32 | ❌ rejected |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.0664 | 0.00 | ❌ rejected |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.3662 | 0.43 | ❌ rejected |
| 0 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.4029 | 0.50 | ✅ accepted |

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

## Current Skill (Q=0.383) — your mutation base

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

- **Composite score**: 0.383
- **task_score** (E): 0.471
- **fitness_score**: 0.593  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2067 |
| descend_1 | 1.00 | 0.67 | 0.0782 |
| push_1 | 1.00 | 1.00 | 0.1434 |
| retract_1 | 1.00 | 1.00 | 0.1389 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.133, 0.108) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.545 | 3.526 |
| descend_1 | descend | 1.00 / step_budget | (0.513, 0.133, 0.108)→(0.500, 0.107, 0.037) | (0.503, 0.080, 0.034)→(0.503, 0.077, 0.035) | 0.160→0.157 | 0.67 / 1.000 | 0.859 | 106.469 |
| push_1 | push | 1.00 / step_budget | (0.500, 0.107, 0.037)→(0.497, -0.037, 0.033) | (0.503, 0.077, 0.035)→(0.504, -0.061, 0.036) | 0.157→0.027 | 1.00 / 3.000 | 2.027 | 75.374 |
| retract_1 | retract | 1.00 / step_budget | (0.497, -0.037, 0.033)→(0.494, -0.036, 0.171) | (0.504, -0.061, 0.036)→(0.502, -0.065, 0.031) | 0.027→0.021 | 1.00 / 1.000 | 0.584 | 153.743 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.837
- phase_score: 0.485
- phase_breakdown.pre_contact_score: 0.865
- phase_breakdown.push_complete_score: 0.322

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.626
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.837
- **Median Q (composite search score)**: 0.399
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Parameters at upper bound**: push_1.push_speed
- **Final σ (mean)**: 0.285


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3814,"average_solve_count":215.0,"average_success_count":215.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.02386,"push_1.push_distance":0.16469,"push_1.push_speed":0.08003},"optimized_scores":{"best_composite_score":0.4159,"best_fitness_score":0.6259,"best_task_score":0.83713},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":147.0,"contact_point_centroid":[0.47496,-0.00064,0.04536],"force_p95":366.2908,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":399.30517,"mean_force":221.6918,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48677,-0.00061,0.04348]},{"body_a":"attachment","body_b":"peg","contact_count":417.0,"contact_point_centroid":[0.49532,0.04672,0.033],"force_p95":116.13334,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":134.42142,"mean_force":56.75304,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48774,0.05421,0.03157]},{"body_a":"attachment","body_b":"peg","contact_count":86.0,"contact_point_centroid":[0.49665,-0.0049,0.03541],"force_p95":110.34482,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":114.44077,"mean_force":56.46823,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48678,-0.00058,0.03688]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":311.0,"contact_point_centroid":[0.52571,0.01874,0.02944],"force_p95":89.35503,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":103.51618,"mean_force":48.60638,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48742,0.03644,0.03148]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":126.0,"contact_point_centroid":[0.52677,-0.01332,0.03206],"force_p95":94.828,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":98.62358,"mean_force":36.61325,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48678,-0.00057,0.03967]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":38.0,"contact_point_centroid":[0.475,0.00775,0.03347],"force_p95":88.48494,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":96.13389,"mean_force":68.82042,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48685,0.00773,0.03159]},{"body_a":"peg","body_b":"channel_base_body","contact_count":416.0,"contact_point_centroid":[0.50646,0.02277,0.00955],"force_p95":89.10976,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.99519,"mean_force":47.30897,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48772,0.05331,0.03153]},{"body_a":"peg","body_b":"channel_base_body","contact_count":817.0,"contact_point_centroid":[0.5001,-0.03865,0.00836],"force_p95":12.80897,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.05456,"mean_force":2.41014,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48426,-0.0006,0.10427]},{"body_a":"peg","body_b":"link7","contact_count":351.0,"contact_point_centroid":[0.51385,0.02192,0.06844],"force_p95":47.29983,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.21477,"mean_force":30.21335,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48749,0.0407,0.03146]},{"body_a":"peg","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.51489,-0.01933,0.0694],"force_p95":38.41053,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.1356,"mean_force":21.89081,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48676,-0.00081,0.03282]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.47492,0.0759,0.05942],"force_p95":22.47594,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.94015,"mean_force":18.21549,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48821,0.10497,0.03089]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.475,-0.06739,0.02434],"force_p95":8.46694,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.57182,"mean_force":3.00024,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48384,-0.00059,0.15818]},{"body_a":"attachment","body_b":"peg","contact_count":30.0,"contact_point_centroid":[0.49447,0.13481,0.05391],"force_p95":6.08176,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.62103,"mean_force":2.39995,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49057,0.14665,0.03973]},{"body_a":"peg","body_b":"channel_base_body","contact_count":452.0,"contact_point_centroid":[0.49665,0.11676,0.00948],"force_p95":1.31282,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.48391,"mean_force":0.68246,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48635,0.15719,0.07057]},{"body_a":"peg","body_b":"channel_base_body","contact_count":609.0,"contact_point_centroid":[0.49625,0.11915,0.00941],"force_p95":0.60155,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55409,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49106,0.18435,0.20128]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49948,0.19934,0.29809]}],"total_contact_groups":16},"final_pose_error":0.01125,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49471,-0.04348,0.02414],"final_tcp_position":[0.48398,-0.00058,0.1707],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":399.30517,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":634.0,"n_steps_budget":1000.0,"object_pos_end":[0.496,0.119,0.03383],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19913,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.53793,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":633.0,"raw_peak_contact_force":2.24822,"subtask_id":"pre_contact","tcp_end":[0.48406,0.17014,0.10965],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":458.0,"n_steps_budget":600.0,"object_pos_end":[0.49804,0.11555,0.03559],"object_pos_start":[0.496,0.119,0.03383],"object_to_goal_dist_end":0.19561,"object_to_goal_dist_start":0.19913,"object_z_max":0.03559,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":482.0,"raw_peak_contact_force":6.62103,"subtask_id":"pre_contact","tcp_end":[0.49125,0.145,0.03492],"tcp_start":[0.48406,0.17014,0.10965],"tcp_to_object_dist_end":0.03023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":477.0,"n_steps_budget":1000.0,"object_pos_end":[0.51072,-0.01759,0.03879],"object_pos_start":[0.49804,0.11555,0.03559],"object_to_goal_dist_end":0.06334,"object_to_goal_dist_start":0.19561,"object_z_max":0.0397,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1538.0,"raw_peak_contact_force":134.42142,"subtask_id":"push_complete","tcp_end":[0.48684,-0.0006,0.03158],"tcp_start":[0.49125,0.145,0.03492],"tcp_to_object_dist_end":0.03018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":873.0,"n_steps_budget":960.0,"object_pos_end":[0.49471,-0.04348,0.02414],"object_pos_start":[0.51072,-0.01759,0.03879],"object_to_goal_dist_end":0.04016,"object_to_goal_dist_start":0.06334,"object_z_max":0.04134,"peak_contact_force":0.67086,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1218.0,"raw_peak_contact_force":399.30517,"tcp_end":[0.48398,-0.00058,0.1707],"tcp_start":[0.48684,-0.0006,0.03158],"tcp_to_object_dist_end":0.15309,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75926,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07807,"push_1.push_distance":0.16082,"push_1.push_speed":0.06404},"optimized_scores":{"best_composite_score":0.39884,"best_fitness_score":0.60884,"best_task_score":0.35984},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":237.0,"contact_point_centroid":[0.50406,0.00551,0.04604],"force_p95":35.17217,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.49368,"mean_force":6.86482,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50089,0.01721,0.03325]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":154.0,"contact_point_centroid":[0.52534,-0.0274,0.03629],"force_p95":35.90977,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.46575,"mean_force":7.08492,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50065,0.00184,0.03301]},{"body_a":"peg","body_b":"channel_base_body","contact_count":151.0,"contact_point_centroid":[0.50257,-0.01285,0.0097],"force_p95":19.16905,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.39319,"mean_force":4.87972,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50121,0.02906,0.03362]},{"body_a":"peg","body_b":"channel_base_body","contact_count":335.0,"contact_point_centroid":[0.50576,0.06201,0.0094],"force_p95":0.57383,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.58645,"mean_force":0.68466,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51354,0.10435,0.07168]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.50594,0.08026,0.04703],"force_p95":14.15578,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.17211,"mean_force":4.59111,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50527,0.09224,0.04122]},{"body_a":"peg","body_b":"channel_base_body","contact_count":861.0,"contact_point_centroid":[0.50607,-0.08157,0.0094],"force_p95":0.55664,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.45053,"mean_force":0.55091,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49745,-0.05096,0.10243]},{"body_a":"peg","body_b":"channel_base_body","contact_count":659.0,"contact_point_centroid":[0.5058,0.06302,0.00936],"force_p95":0.56023,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.5671,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51172,0.15717,0.19877]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50372,-0.0635,0.05095],"force_p95":2.24646,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.32129,"mean_force":0.47638,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49929,-0.05158,0.0358]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49993,0.1984,0.29643]},{"body_a":"peg","body_b":"channel_base_body","contact_count":38.0,"contact_point_centroid":[0.50652,-0.10034,0.03502],"force_p95":0.76387,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.95953,"mean_force":0.27073,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4991,-0.05186,0.03623]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52501,-0.08127,0.01106],"force_p95":0.23113,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23181,"mean_force":0.225,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50025,-0.052,0.03296]}],"total_contact_groups":11},"final_pose_error":0.01157,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5062,-0.0817,0.03379],"final_tcp_position":[0.49781,-0.05092,0.17166],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":40.49368,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":687.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.06295,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.551,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":693.0,"raw_peak_contact_force":3.88411,"subtask_id":"pre_contact","tcp_end":[0.52442,0.11749,0.10694],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09306,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":335.0,"n_steps_budget":600.0,"object_pos_end":[0.50482,0.06096,0.03454],"object_pos_start":[0.50602,0.06295,0.03381],"object_to_goal_dist_end":0.14115,"object_to_goal_dist_start":0.14321,"object_z_max":0.03451,"peak_contact_force":2.18664,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":346.0,"raw_peak_contact_force":15.58645,"subtask_id":"pre_contact","tcp_end":[0.50431,0.09079,0.03755],"tcp_start":[0.52442,0.11749,0.10694],"tcp_to_object_dist_end":0.02998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":368.0,"n_steps_budget":1000.0,"object_pos_end":[0.50687,-0.08059,0.03552],"object_pos_start":[0.50482,0.06096,0.03454],"object_to_goal_dist_end":0.00823,"object_to_goal_dist_start":0.14115,"object_z_max":0.03756,"peak_contact_force":4.68533,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":542.0,"raw_peak_contact_force":40.49368,"subtask_id":"push_complete","tcp_end":[0.50072,-0.05119,0.03286],"tcp_start":[0.50431,0.09079,0.03755],"tcp_to_object_dist_end":0.03015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":873.0,"n_steps_budget":960.0,"object_pos_end":[0.5062,-0.0817,0.03379],"object_pos_start":[0.50687,-0.08059,0.03552],"object_to_goal_dist_end":0.00893,"object_to_goal_dist_start":0.00823,"object_z_max":0.03576,"peak_contact_force":0.54177,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":909.0,"raw_peak_contact_force":4.45053,"tcp_end":[0.49781,-0.05092,0.17166],"tcp_start":[0.50072,-0.05119,0.03286],"tcp_to_object_dist_end":0.14151,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42857,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05108,"push_1.push_distance":0.16136,"push_1.push_speed":0.1},"optimized_scores":{"best_composite_score":0.3332,"best_fitness_score":0.5432,"best_task_score":0.21573},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52522,0.09403,0.05996],"force_p95":295.82497,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":297.19831,"mean_force":190.46624,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51334,0.09413,0.06088]},{"body_a":"peg","body_b":"channel_base_body","contact_count":315.0,"contact_point_centroid":[0.49261,-0.10072,0.0605],"force_p95":31.82296,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.47357,"mean_force":20.49989,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49926,-0.05488,0.05681]},{"body_a":"attachment","body_b":"peg","contact_count":305.0,"contact_point_centroid":[0.4973,-0.06626,0.05628],"force_p95":31.69476,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.39132,"mean_force":21.18226,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49926,-0.05484,0.05599]},{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.49307,-0.10071,0.04552],"force_p95":49.93057,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.20699,"mean_force":27.73465,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50241,-0.05528,0.03336]},{"body_a":"attachment","body_b":"peg","contact_count":230.0,"contact_point_centroid":[0.50136,0.00074,0.0449],"force_p95":47.00372,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.18674,"mean_force":12.69764,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50256,0.01173,0.03381]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":141.0,"contact_point_centroid":[0.47454,-0.04857,0.04005],"force_p95":45.80385,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.11743,"mean_force":16.38055,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50265,-0.0213,0.0336]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":118.0,"contact_point_centroid":[0.4749,-0.0826,0.05483],"force_p95":11.52448,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.93168,"mean_force":3.60984,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49925,-0.05498,0.0515]},{"body_a":"peg","body_b":"channel_base_body","contact_count":141.0,"contact_point_centroid":[0.50269,-0.01653,0.00966],"force_p95":10.0379,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.42783,"mean_force":2.68941,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50264,0.02133,0.03402]},{"body_a":"peg","body_b":"channel_base_body","contact_count":338.0,"contact_point_centroid":[0.50637,0.05612,0.00939],"force_p95":0.5537,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.35262,"mean_force":0.60763,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51725,0.09824,0.07136]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50648,0.07395,0.04526],"force_p95":8.27732,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.93221,"mean_force":3.09413,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50641,0.08593,0.04091]},{"body_a":"peg","body_b":"channel_base_body","contact_count":530.0,"contact_point_centroid":[0.50474,-0.07014,0.00936],"force_p95":0.71275,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.5195,"mean_force":0.59384,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4992,-0.05733,0.12939]},{"body_a":"peg","body_b":"channel_base_body","contact_count":724.0,"contact_point_centroid":[0.50595,0.05665,0.00936],"force_p95":0.60041,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56853,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51496,0.15411,0.19869]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49993,0.19828,0.29629]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.52512,0.01688,0.04482],"force_p95":1.74962,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.23353,"mean_force":0.7755,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50219,0.04765,0.0336]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":31.0,"contact_point_centroid":[0.52538,-0.07018,0.05821],"force_p95":0.81882,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86003,"mean_force":0.23852,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.499,-0.05715,0.09729]}],"total_contact_groups":15},"final_pose_error":0.01162,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50558,-0.06943,0.03425],"final_tcp_position":[0.49954,-0.05742,0.17212],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":297.19831,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":753.0,"n_steps_budget":1000.0,"object_pos_end":[0.50616,0.05658,0.0338],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13686,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54661,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":761.0,"raw_peak_contact_force":4.44541,"subtask_id":"pre_contact","tcp_end":[0.53088,0.1115,0.10667],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":338.0,"n_steps_budget":600.0,"object_pos_end":[0.50488,0.05432,0.03463],"object_pos_start":[0.50616,0.05658,0.0338],"object_to_goal_dist_end":0.13451,"object_to_goal_dist_start":0.13686,"object_z_max":0.0346,"peak_contact_force":0.38988,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":360.0,"raw_peak_contact_force":297.19831,"subtask_id":"pre_contact","tcp_end":[0.50526,0.08457,0.03763],"tcp_start":[0.53088,0.1115,0.10667],"tcp_to_object_dist_end":0.03041,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":354.0,"n_steps_budget":1000.0,"object_pos_end":[0.49322,-0.08457,0.03509],"object_pos_start":[0.50488,0.05432,0.03463],"object_to_goal_dist_end":0.00954,"object_to_goal_dist_start":0.13451,"object_z_max":0.03973,"peak_contact_force":1.39436,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":544.0,"raw_peak_contact_force":51.20699,"subtask_id":"push_complete","tcp_end":[0.50246,-0.05772,0.03337],"tcp_start":[0.50526,0.08457,0.03763],"tcp_to_object_dist_end":0.02845,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":873.0,"n_steps_budget":960.0,"object_pos_end":[0.50558,-0.06943,0.03425],"object_pos_start":[0.49322,-0.08457,0.03509],"object_to_goal_dist_end":0.01326,"object_to_goal_dist_start":0.00954,"object_z_max":0.05938,"peak_contact_force":0.53873,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1299.0,"raw_peak_contact_force":57.47357,"tcp_end":[0.49954,-0.05742,0.17212],"tcp_start":[0.50246,-0.05772,0.03337],"tcp_to_object_dist_end":0.13853,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```