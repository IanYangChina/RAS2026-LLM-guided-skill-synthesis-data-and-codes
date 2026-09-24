## Search State

- **Seed**: 5
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1666 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`
- Frozen object start: [0.5244002338996304, 0.1046352631789195, 0.04]
- Frozen task target: [0.5244002338996304, -0.05536473682108051, 0.04]
- Goal object position: (0.5244002338996304, -0.05536473682108051, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5244002338996304, 0.1046352631789195, 0.04)
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
  frozen_object_start: [0.5244, 0.1046, 0.04]
  frozen_task_target: [0.5244, -0.0554, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5244002338996304, 0.1046352631789195, 0.04]}
  frozen_targets: {'channel_exit': [0.5244002338996304, -0.05536473682108051, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e

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
| `object` | offset from object initial position (0.5244002338996304, 0.1046352631789195, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5244002338996304, -0.05536473682108051, 0.04) | final destination targets |
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

## Current Skill (Q=0.167) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_contact
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.0
  weight: 0.4
- id: push_complete
  weight: 0.6
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
    - 0.0
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
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
  subtask_id: approach_contact
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.04
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_contact
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
    tolerance: 0.015
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
  parameters:
    insert_depth:
      type: scalar
      range:
      - 0.14
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
    anchor: world
    offset:
    - 0.5
    - 0.2
    - 0.3
    tolerance: 0.02
    orientation:
      mode: keep_current
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.0], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.04, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.015
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis
  - parameter_bindings:
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.2, 0.3], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.167
- **task_score** (E): 0.225
- **fitness_score**: 0.277  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2477 |
| contact_1 | 1.00 | 1.00 | 0.0095 |
| push_1 | 0.00 | 1.00 | 0.0581 |
| retract_1 | 1.00 | 1.00 | 0.2560 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.509, 0.148, 0.059) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.540 | 2.488 |
| contact_1 | contact | 1.00 / force_exceeded | (0.509, 0.148, 0.059)→(0.506, 0.140, 0.054) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 2.000 | 15.151 | 15.151 |
| push_1 | push | 0.00 / step_budget | (0.506, 0.140, 0.054)→(0.506, 0.083, 0.051) | (0.504, 0.095, 0.034)→(0.503, 0.038, 0.028) | 0.175→0.119 | 1.00 / 2.333 | 295.594 | 425.419 |
| retract_1 | retract | 1.00 / step_budget | (0.506, 0.083, 0.051)→(0.499, 0.193, 0.281) | (0.503, 0.038, 0.028)→(0.503, 0.038, 0.027) | 0.119→0.119 | 1.00 / 1.000 | 0.579 | 205.429 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.484
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.345
- phase_score: 0.308
- phase_breakdown.push_complete_score: 0.038
- phase_breakdown.approach_contact_score: 0.713

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.323
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.345
- **Median Q (composite search score)**: 0.181
- **K-run variance**: 0.0020
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.355


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9b36d26f861d7a613dfb3d8c86d70470e42095a430c2befa4bd6e530468a8a7e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2af86d8f59685db6584febc0596b9044223ae39cea3120c112c665a54a1c4732`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17447,"average_solve_count":235.0,"average_success_count":235.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05883,"contact_1.contact_force":12.03959,"contact_1.speed":0.02938,"push_1.insert_depth":0.16698,"push_1.push_speed":0.06677,"retract_1.speed":0.06073},"optimized_scores":{"best_composite_score":0.18117,"best_fitness_score":0.29117,"best_task_score":0.26146},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":115.0,"contact_point_centroid":[0.52501,0.11983,0.05999],"force_p95":481.01148,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":555.29538,"mean_force":243.88765,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51315,0.07881,0.05207]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":152.0,"contact_point_centroid":[0.47495,0.11993,0.05409],"force_p95":473.39305,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":549.557,"mean_force":359.14348,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51321,0.07911,0.05196]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":766.0,"contact_point_centroid":[0.52503,0.10914,0.05695],"force_p95":311.8159,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":505.39156,"mean_force":202.30733,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51438,0.10844,0.05275]},{"body_a":"world","body_b":"link7","contact_count":183.0,"contact_point_centroid":[0.51482,0.18476,-2e-05],"force_p95":327.24701,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":429.65068,"mean_force":145.68909,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51524,0.12217,0.05311]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.47495,0.11991,0.05435],"force_p95":367.92999,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":397.76993,"mean_force":192.92999,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51305,0.07949,0.05157]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52505,0.0804,0.05163],"force_p95":299.61195,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":304.64073,"mean_force":213.45791,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51313,0.07943,0.05157]},{"body_a":"attachment","body_b":"peg","contact_count":550.0,"contact_point_centroid":[0.50466,0.11852,0.04894],"force_p95":1.46581,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.06481,"mean_force":0.85674,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51479,0.11913,0.05304]},{"body_a":"peg","body_b":"channel_base_body","contact_count":968.0,"contact_point_centroid":[0.5036,0.07602,0.00953],"force_p95":1.24509,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":61.87246,"mean_force":0.91229,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51464,0.11301,0.05289]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.51797,0.21311,-1e-05],"force_p95":13.65603,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":13.65603,"mean_force":13.65603,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5167,0.1511,0.05433]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":24.0,"contact_point_centroid":[0.52553,0.08001,0.03136],"force_p95":4.4693,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.01649,"mean_force":1.25951,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51297,0.10138,0.05136]},{"body_a":"peg","body_b":"channel_base_body","contact_count":511.0,"contact_point_centroid":[0.50564,0.10458,0.00937],"force_p95":0.57742,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56848,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50403,0.18434,0.17735]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50408,0.21887,0.29005]},{"body_a":"peg","body_b":"channel_base_body","contact_count":844.0,"contact_point_centroid":[0.50545,0.02281,0.00807],"force_p95":0.64358,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6446,"mean_force":0.60593,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50495,0.13614,0.16591]},{"body_a":"peg","body_b":"channel_base_body","contact_count":57.0,"contact_point_centroid":[0.50506,0.10545,0.00939],"force_p95":0.57564,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57647,"mean_force":0.54644,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51739,0.15369,0.05548]}],"total_contact_groups":14},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50598,0.02279,0.02415],"final_tcp_position":[0.4996,0.1928,0.2816],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":555.29538,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":538.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.10463,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18483,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55135,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":543.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach_contact","tcp_end":[0.51936,0.1572,0.05893],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":57.0,"n_steps_budget":870.0,"object_pos_end":[0.50597,0.10471,0.03384],"object_pos_start":[0.50583,0.10463,0.03383],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.18483,"object_z_max":0.03384,"peak_contact_force":13.65603,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":58.0,"raw_peak_contact_force":13.65603,"subtask_id":"approach_contact","tcp_end":[0.51669,0.15104,0.05431],"tcp_start":[0.51936,0.1572,0.05893],"tcp_to_object_dist_end":0.05177,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50514,0.0228,0.02416],"object_pos_start":[0.50597,0.10471,0.03384],"object_to_goal_dist_end":0.10414,"object_to_goal_dist_start":0.18491,"object_z_max":0.04083,"peak_contact_force":459.60847,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2758.0,"raw_peak_contact_force":555.29538,"subtask_id":"push_complete","tcp_end":[0.51322,0.07941,0.05159],"tcp_start":[0.51669,0.15104,0.05431],"tcp_to_object_dist_end":0.06342,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":844.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.02279,0.02415],"object_pos_start":[0.50514,0.0228,0.02416],"object_to_goal_dist_end":0.10418,"object_to_goal_dist_start":0.10414,"object_z_max":0.02416,"peak_contact_force":0.56826,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":853.0,"raw_peak_contact_force":397.76993,"tcp_end":[0.4996,0.1928,0.2816],"tcp_start":[0.51322,0.07941,0.05159],"tcp_to_object_dist_end":0.30859,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13793,"average_solve_count":261.0,"average_success_count":261.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.02558,"contact_1.contact_force":12.20845,"contact_1.speed":0.02568,"push_1.insert_depth":0.16588,"push_1.push_speed":0.05086,"retract_1.speed":0.06678},"optimized_scores":{"best_composite_score":0.10557,"best_fitness_score":0.21557,"best_task_score":0.06794},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":786.0,"contact_point_centroid":[0.46606,0.11992,0.06],"force_p95":221.45867,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":505.47598,"mean_force":209.5081,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4988,0.08271,0.0513]},{"body_a":"world","body_b":"link7","contact_count":174.0,"contact_point_centroid":[0.49749,0.15891,-1e-05],"force_p95":291.14197,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":387.45527,"mean_force":117.1996,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49678,0.09626,0.05357]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.46542,0.11994,0.06],"force_p95":99.37887,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":100.87791,"mean_force":62.08794,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50078,0.08562,0.04941]},{"body_a":"peg","body_b":"channel_base_body","contact_count":983.0,"contact_point_centroid":[0.50553,0.05849,0.00941],"force_p95":0.61906,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.10483,"mean_force":0.64727,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4984,0.08602,0.05176]},{"body_a":"attachment","body_b":"peg","contact_count":18.0,"contact_point_centroid":[0.50357,0.08353,0.04894],"force_p95":20.42001,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.89043,"mean_force":5.53636,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49679,0.08332,0.05342]},{"body_a":"world","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.49838,0.17694,-0.0],"force_p95":15.13294,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":18.29348,"mean_force":11.36926,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49712,0.11486,0.05424]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.525,0.11996,0.06],"force_p95":7.84523,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":17.43385,"mean_force":1.45282,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49676,0.07946,0.05334]},{"body_a":"peg","body_b":"channel_base_body","contact_count":552.0,"contact_point_centroid":[0.50308,0.0675,0.00934],"force_p95":0.55552,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56223,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49556,0.17041,0.18159]},{"body_a":"peg","body_b":"channel_base_body","contact_count":822.0,"contact_point_centroid":[0.50634,0.05668,0.00941],"force_p95":0.55069,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55246,"mean_force":0.54504,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49855,0.13933,0.16493]},{"body_a":"peg","body_b":"channel_base_body","contact_count":108.0,"contact_point_centroid":[0.50306,0.06745,0.00938],"force_p95":0.55061,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55089,"mean_force":0.54664,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4977,0.11796,0.05515]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":22.0,"contact_point_centroid":[0.52516,0.05557,0.05898],"force_p95":0.33288,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46127,"mean_force":0.09311,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49695,0.08017,0.0532]}],"total_contact_groups":11},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50599,0.05659,0.03404],"final_tcp_position":[0.49893,0.19306,0.28139],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":505.47598,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":568.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54514,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":552.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_contact","tcp_end":[0.50006,0.12344,0.05882],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06142,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":108.0,"n_steps_budget":990.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":18.29348,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":119.0,"raw_peak_contact_force":18.29348,"subtask_id":"approach_contact","tcp_end":[0.4971,0.11455,0.05423],"tcp_start":[0.50006,0.12344,0.05882],"tcp_to_object_dist_end":0.05171,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50647,0.05698,0.03404],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.13727,"object_to_goal_dist_start":0.14759,"object_z_max":0.0358,"peak_contact_force":221.47501,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1995.0,"raw_peak_contact_force":505.47598,"subtask_id":"push_complete","tcp_end":[0.50084,0.08558,0.04942],"tcp_start":[0.4971,0.11455,0.05423],"tcp_to_object_dist_end":0.03295,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":822.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.05659,0.03404],"object_pos_start":[0.50647,0.05698,0.03404],"object_to_goal_dist_end":0.13685,"object_to_goal_dist_start":0.13727,"object_z_max":0.03405,"peak_contact_force":0.54848,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":827.0,"raw_peak_contact_force":100.87791,"tcp_end":[0.49893,0.19306,0.28139],"tcp_start":[0.50084,0.08558,0.04942],"tcp_to_object_dist_end":0.28259,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25703,"average_solve_count":249.0,"average_success_count":249.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05078,"contact_1.contact_force":3.43035,"contact_1.speed":0.04385,"push_1.insert_depth":0.15308,"push_1.push_speed":0.03499,"retract_1.speed":0.08569},"optimized_scores":{"best_composite_score":0.21306,"best_fitness_score":0.32306,"best_task_score":0.34538},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":564.0,"contact_point_centroid":[0.47267,0.11992,0.06],"force_p95":205.73307,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":215.48436,"mean_force":190.7962,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50421,0.08145,0.05224]},{"body_a":"world","body_b":"link7","contact_count":291.0,"contact_point_centroid":[0.50349,0.18424,-1e-05],"force_p95":106.31192,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":122.63525,"mean_force":95.97638,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50284,0.12159,0.05357]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.47232,0.11994,0.06],"force_p95":115.21764,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":117.63862,"mean_force":72.30842,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50522,0.08288,0.051]},{"body_a":"peg","body_b":"channel_base_body","contact_count":980.0,"contact_point_centroid":[0.50087,0.07196,0.00964],"force_p95":33.37147,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.64039,"mean_force":5.07634,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50362,0.09765,0.05282]},{"body_a":"attachment","body_b":"peg","contact_count":524.0,"contact_point_centroid":[0.50065,0.08807,0.04203],"force_p95":40.86381,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.43138,"mean_force":8.56737,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50347,0.08776,0.05303]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50475,0.21764,-0.0],"force_p95":13.50249,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":13.50249,"mean_force":13.50249,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50352,0.15563,0.05431]},{"body_a":"peg","body_b":"channel_base_body","contact_count":793.0,"contact_point_centroid":[0.49855,0.03394,0.00802],"force_p95":0.77015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.51904,"mean_force":0.62958,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50085,0.13794,0.16572]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47496,0.06702,0.03344],"force_p95":5.06422,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.39491,"mean_force":1.27755,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50444,0.09275,0.05179]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.475,0.05434,0.02413],"force_p95":5.27002,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.34231,"mean_force":3.2437,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50126,0.14155,0.17359]},{"body_a":"peg","body_b":"channel_base_body","contact_count":516.0,"contact_point_centroid":[0.50354,0.11166,0.00938],"force_p95":0.61906,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55861,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49815,0.18781,0.17902]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.52515,0.06886,0.05735],"force_p95":0.4965,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.90185,"mean_force":0.15279,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5034,0.10162,0.05287]},{"body_a":"peg","body_b":"channel_base_body","contact_count":79.0,"contact_point_centroid":[0.50392,0.11141,0.00946],"force_p95":0.59901,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61413,"mean_force":0.53991,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50418,0.1591,0.0554]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50379,0.20566,0.2996]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.525,0.11991,0.06],"force_p95":0.0,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50321,0.07944,0.05364]}],"total_contact_groups":14},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49827,0.03439,0.02414],"final_tcp_position":[0.49921,0.19297,0.28149],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":215.48436,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":538.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11174,0.03396],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.5221,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":532.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach_contact","tcp_end":[0.50637,0.16363,0.05914],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":79.0,"n_steps_budget":600.0,"object_pos_end":[0.50372,0.11174,0.03385],"object_pos_start":[0.50372,0.11174,0.03396],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19187,"object_z_max":0.03403,"peak_contact_force":13.50249,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":80.0,"raw_peak_contact_force":13.50249,"subtask_id":"approach_contact","tcp_end":[0.50351,0.15555,0.05431],"tcp_start":[0.50637,0.16363,0.05914],"tcp_to_object_dist_end":0.04836,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49816,0.03376,0.02433],"object_pos_start":[0.50372,0.11174,0.03385],"object_to_goal_dist_end":0.11485,"object_to_goal_dist_start":0.19187,"object_z_max":0.0407,"peak_contact_force":205.6981,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2422.0,"raw_peak_contact_force":215.48436,"subtask_id":"push_complete","tcp_end":[0.50525,0.08285,0.05101],"tcp_start":[0.50351,0.15555,0.05431],"tcp_to_object_dist_end":0.05632,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":793.0,"n_steps_budget":1000.0,"object_pos_end":[0.49827,0.03439,0.02414],"object_pos_start":[0.49816,0.03376,0.02433],"object_to_goal_dist_end":0.1155,"object_to_goal_dist_start":0.11485,"object_z_max":0.02448,"peak_contact_force":0.61927,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":804.0,"raw_peak_contact_force":117.63862,"tcp_end":[0.49921,0.19297,0.28149],"tcp_start":[0.50525,0.08285,0.05101],"tcp_to_object_dist_end":0.30228,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```