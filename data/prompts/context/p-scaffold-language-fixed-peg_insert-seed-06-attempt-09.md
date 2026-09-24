## Search State

- **Seed**: 6
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 8 | 0.0599 | 0.82 | ❌ rejected |
| 8 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1407 | 0.94 | ✅ accepted |
| 7 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 8 | -0.1379 | 0.88 | ❌ rejected |
| 6 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 8 | 0.1385 | 0.90 | ❌ rejected |
| 5 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7 | 0.0556 | 0.90 | ✅ accepted |

**Proposal policy**: task_score is 0.82 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_insert
- Frozen realised-scene SHA-256: `72d0fc56eb607f902ea78d3570decababa6da9acffffae87b8c65460ac3ff15e`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5030531481177555, -0.012538330414932925, 0.08]
- Frozen socket pose: [0.5030531481177555, -0.012538330414932925, 0.025] (static fixture for this episode)
- Goal object position: (0.5030531481177555, -0.012538330414932925, 0.025)
- Object initial pose: (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Channel axis: `(0.0, 0.0, -1.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

## Scene Entities

robot:
  model: panda_peg
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: peg_socket
    role: fixture
    dynamics: static
    geometry: box_with_hole
    base_dimensions_m: [0.12, 0.12, 0.05]
    hole_entry_height_m: 0.08
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    note: peg is a fixed end-effector attachment on the panda_peg arm
task_landmarks:
  frozen_object_start: [0.504, -0, 0.3403]
  frozen_task_target: [0.5031, -0.0125, 0.08]
  frozen_socket_position: [0.5031, -0.0125, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5030531481177555, -0.012538330414932925, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5030531481177555, -0.012538330414932925, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 72d0fc56eb607f902ea78d3570decababa6da9acffffae87b8c65460ac3ff15e

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| align | object | (0.00, 0.00, 0.12) | distance | — |
| approach | object | (0.00, 0.00, 0.09) | distance | — |
| contact | object | (0.00, 0.00, 0.07) | distance | — |
| insert | object | (0.00, 0.00, 0.06) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.060) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.105
    tolerance: 0.01
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  subtask_id: align
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.055
    tolerance: 0.01
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: scale
  subtask_id: approach
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.04
    tolerance: 0.005
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: scale
  subtask_id: contact
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: admittance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.055
    offset_along_axis:
      distance: 0.05
      axis: channel_axis
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insertion_force:
      type: scalar
      range:
      - 10.0
      - 40.0
      default: 30.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.002
    - 0.002
    - 0.0
  subtask_id: insert
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.105
    tolerance: 0.01
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: scale

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_1** (`align`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.105], tolerance=0.01
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
- **approach_1** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055], tolerance=0.01
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (scale)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.04], tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (scale)
- **insert_1** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055], offset_along_axis={axis=channel_axis, distance=0.05, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insertion_force: status=consumed; consumers=termination.force_threshold (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.002, 0.002, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.105], tolerance=0.01
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (scale)

## Design Metrics

- **Composite score**: 0.060
- **task_score** (E): 0.819
- **fitness_score**: 0.350  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 0.00 | 0.1634 |
| approach_1 | 0.00 | 1.00 | 0.1498 |
| contact_1 | 1.00 | 1.00 | 0.0010 |
| insert_1 | 0.00 | 0.67 | 0.0006 |
| retract_1 | 0.00 | 1.00 | 0.0057 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.017, 0.139) | (0.504, -0.000, 0.340)→(0.509, 0.017, 0.177) | 0.260→0.100 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_1 | approach | 0.00 / step_budget | (0.497, 0.017, 0.139)→(0.535, 0.051, 0.264) | (0.509, 0.017, 0.177)→(0.546, 0.054, 0.226) | 0.100→0.174 | 1.00 / 2.000 | 304.026 | 9250.588 |
| contact_1 | contact | 1.00 / force_exceeded | (0.535, 0.051, 0.264)→(0.535, 0.051, 0.264) | (0.546, 0.054, 0.226)→(0.546, 0.054, 0.226) | 0.174→0.175 | 1.00 / 1.000 | 334.346 | 491.234 |
| insert_1 | insert | 0.00 / guard_failure | (0.535, 0.051, 0.265)→(0.535, 0.051, 0.265) | (0.546, 0.054, 0.226)→(0.546, 0.054, 0.227) | 0.175→0.175 | 0.67 / 0.667 | 232.745 | 461.182 |
| retract_1 | retract | 0.00 / step_budget | (0.535, 0.051, 0.265)→(0.535, 0.047, 0.263) | (0.546, 0.054, 0.227)→(0.545, 0.050, 0.225) | 0.176→0.172 | 1.00 / 2.000 | 190.870 | 300.134 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.944
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.944
- phase_score: 0.021
- phase_breakdown.contact_score: 0.023
- phase_breakdown.align_score: 0.001
- phase_breakdown.approach_score: 0.017
- phase_breakdown.insert_score: 0.026

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.390
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.944
- **Median Q (composite search score)**: 0.041
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.321


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2bcd5d362bce9ed2c176357e9c3237720ebba2a98dd8bfe48970c9fba5840ac0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ac7031668c6a08077e83f2359534923b723fe0e5a20a177feb2fc3bf67104f66`; realized-scene SHA-256: `72d0fc56eb607f902ea78d3570decababa6da9acffffae87b8c65460ac3ff15e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50305,-0.01254,0.025]},{"name":"target","value":[0.50305,-0.01254,0.025]},{"name":"socket","value":[0.50305,-0.01254,0.025]},{"name":"goal","value":[0.50305,-0.01254,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,-0.01254,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50305,-0.01254,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.50781,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00992,"align_1.lateral_offset_y":0.00908,"approach_1.speed":0.07255,"contact_1.contact_force":2.39001,"contact_1.speed":0.02774,"insert_1.insertion_depth":0.01381,"insert_1.insertion_force":13.35581,"retract_1.speed":0.06257},"optimized_scores":{"best_composite_score":0.04054,"best_fitness_score":0.33054,"best_task_score":0.76414},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"world","contact_count":560.0,"contact_point_centroid":[0.57865,-0.01613,-0.00039],"force_p95":819.56945,"geom_a":"peg_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":11764.34607,"mean_force":504.26036,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.57116,-0.01747,0.01206]},{"body_a":"attachment","body_b":"peg_socket","contact_count":508.0,"contact_point_centroid":[0.56289,-0.01471,0.02396],"force_p95":956.29268,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":11240.9737,"mean_force":610.75413,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.57098,-0.01847,0.01242]},{"body_a":"peg_socket","body_b":"link5","contact_count":218.0,"contact_point_centroid":[0.49227,0.04732,0.0608],"force_p95":821.04691,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":990.77335,"mean_force":291.48529,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.54851,0.04313,0.25956]},{"body_a":"world","body_b":"link5","contact_count":169.0,"contact_point_centroid":[0.48374,0.10225,-7e-05],"force_p95":871.49884,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":967.57373,"mean_force":380.96255,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.54341,0.05292,0.26309]},{"body_a":"world","body_b":"link6","contact_count":87.0,"contact_point_centroid":[0.62942,0.10925,-0.00085],"force_p95":566.04647,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":804.28887,"mean_force":282.81681,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.58087,-0.0219,0.19595]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.56257,-0.0031,0.07746],"force_p95":585.74232,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":589.85123,"mean_force":548.76205,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.57467,-0.00323,0.0693]},{"body_a":"peg_socket","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.49545,0.0474,0.054],"force_p95":565.51603,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":567.88751,"mean_force":544.1727,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54042,0.05918,0.26549]},{"body_a":"world","body_b":"link7","contact_count":32.0,"contact_point_centroid":[0.69814,-0.02093,-0.00016],"force_p95":474.86161,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":546.08324,"mean_force":265.72059,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.57544,-0.04318,0.02163]},{"body_a":"peg_socket","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.49471,0.04742,0.05492],"force_p95":502.20456,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":504.74583,"mean_force":479.33316,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.54042,0.06004,0.26604]},{"body_a":"world","body_b":"link5","contact_count":986.0,"contact_point_centroid":[0.47646,0.10232,-5e-05],"force_p95":288.45533,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":392.2819,"mean_force":204.543,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5383,0.05881,0.26391]},{"body_a":"world","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.48344,0.10151,-4e-05],"force_p95":282.45817,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":282.45817,"mean_force":282.45817,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54042,0.059,0.26534]},{"body_a":"peg_socket","body_b":"link5","contact_count":518.0,"contact_point_centroid":[0.48809,0.04743,0.05359],"force_p95":247.55595,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":253.66466,"mean_force":210.67362,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53793,0.057,0.26368]},{"body_a":"peg_socket","body_b":"link5","contact_count":15.0,"contact_point_centroid":[0.49325,0.0474,0.04998],"force_p95":0.0,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.54952,0.04099,0.25814]}],"total_contact_groups":13},"final_pose_error":0.15364,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.53782,0.05553,0.26328],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":11764.34607,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":499.0,"n_steps_budget":1000.0,"object_pos_end":[0.50262,-0.00322,0.17739],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09748,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"align","tcp_end":[0.49034,-0.00321,0.13932],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55257,0.06564,0.22781],"object_pos_start":[0.50262,-0.00322,0.17739],"object_to_goal_dist_end":0.17006,"object_to_goal_dist_start":0.09748,"object_z_max":0.22781,"peak_contact_force":247.65195,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1591.0,"raw_peak_contact_force":11764.34607,"subtask_id":"approach","tcp_end":[0.54042,0.059,0.26534],"tcp_start":[0.49034,-0.00321,0.13932],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.55242,0.06635,0.22832],"object_pos_start":[0.55257,0.06564,0.22781],"object_to_goal_dist_end":0.17073,"object_to_goal_dist_start":0.17006,"object_z_max":0.22809,"peak_contact_force":567.88751,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":567.88751,"subtask_id":"contact","tcp_end":[0.54041,0.05978,0.26591],"tcp_start":[0.54042,0.059,0.26534],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.55235,0.06684,0.22855],"object_pos_start":[0.55242,0.06635,0.22832],"object_to_goal_dist_end":0.1711,"object_to_goal_dist_start":0.17073,"object_z_max":0.22878,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":504.74583,"subtask_id":"insert","tcp_end":[0.54059,0.06131,0.26669],"tcp_start":[0.54049,0.06086,0.26643],"tcp_to_object_dist_end":0.04029,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54912,0.06254,0.22555],"object_pos_start":[0.55224,0.06786,0.22899],"object_to_goal_dist_end":0.16586,"object_to_goal_dist_start":0.17185,"object_z_max":0.22899,"peak_contact_force":236.18715,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1504.0,"raw_peak_contact_force":392.2819,"tcp_end":[0.53782,0.05553,0.26328],"tcp_start":[0.54059,0.06131,0.26669],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4cf364ad7cdeb78864f76dd2c5686ed9e91b61eb5e5b2735897d619cb8f6dad4`; realized-scene SHA-256: `5286851552083a7c8a4164a2656d1a38f2da41529a3a0236ff73d4d9a02dc20c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.51001,0.03178,0.025]},{"name":"target","value":[0.51001,0.03178,0.025]},{"name":"socket","value":[0.51001,0.03178,0.025]},{"name":"goal","value":[0.51001,0.03178,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.03178,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.51001,0.03178,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.19841,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00587,"align_1.lateral_offset_y":-0.00279,"approach_1.speed":0.0527,"contact_1.contact_force":9.53992,"contact_1.speed":0.034,"insert_1.insertion_depth":0.04419,"insert_1.insertion_force":26.80732,"retract_1.speed":0.07908},"optimized_scores":{"best_composite_score":0.10021,"best_fitness_score":0.39021,"best_task_score":0.94401},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.47924,0.02293,0.0705],"force_p95":2216.84225,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2329.04394,"mean_force":918.94981,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48995,0.01699,0.0629]},{"body_a":"peg_socket","body_b":"link7","contact_count":163.0,"contact_point_centroid":[0.56984,0.08452,0.07979],"force_p95":1131.69523,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2068.53453,"mean_force":497.88806,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51427,0.00453,0.08336]},{"body_a":"world","body_b":"link5","contact_count":204.0,"contact_point_centroid":[0.46422,0.14224,-0.00023],"force_p95":953.95664,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1677.22457,"mean_force":449.41348,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53589,0.12297,0.26355]},{"body_a":"peg_socket","body_b":"link5","contact_count":367.0,"contact_point_centroid":[0.48323,0.09157,0.0799],"force_p95":338.18741,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1620.31125,"mean_force":164.17682,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.56164,0.08515,0.27171]},{"body_a":"peg_socket","body_b":"link5","contact_count":630.0,"contact_point_centroid":[0.47499,0.0917,0.07247],"force_p95":420.4739,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1510.02663,"mean_force":237.16708,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5458,0.10924,0.28142]},{"body_a":"attachment","body_b":"peg_socket","contact_count":8.0,"contact_point_centroid":[0.54132,0.02492,0.0793],"force_p95":1390.04995,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1460.48077,"mean_force":801.49324,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52589,0.02249,0.07991]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.49673,0.02244,0.0498],"force_p95":1387.33288,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1409.56354,"mean_force":1123.06511,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48972,0.01715,0.06176]},{"body_a":"attachment","body_b":"peg_socket","contact_count":107.0,"contact_point_centroid":[0.50838,0.00154,0.07805],"force_p95":783.55007,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1314.18379,"mean_force":414.20868,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50049,0.01281,0.07602]},{"body_a":"peg_socket","body_b":"link6","contact_count":10.0,"contact_point_centroid":[0.56981,0.09173,0.07992],"force_p95":1185.55008,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1240.84381,"mean_force":689.80266,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.61556,-0.04314,0.11677]},{"body_a":"peg_socket","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.46433,0.09176,0.0568],"force_p95":554.15321,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":562.43826,"mean_force":479.58784,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.53582,0.12293,0.26453]},{"body_a":"peg_socket","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.46503,0.09175,0.05577],"force_p95":534.4807,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":534.4807,"mean_force":534.4807,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53588,0.12226,0.26392]},{"body_a":"world","body_b":"link5","contact_count":916.0,"contact_point_centroid":[0.45953,0.14239,-4e-05],"force_p95":276.87317,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":284.77654,"mean_force":142.05081,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53444,0.12079,0.26273]},{"body_a":"peg_socket","body_b":"link5","contact_count":847.0,"contact_point_centroid":[0.4599,0.09175,0.05572],"force_p95":230.85558,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":260.62489,"mean_force":183.6593,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53441,0.12006,0.26269]},{"body_a":"world","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.46443,0.14238,-3e-05],"force_p95":231.75292,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":233.80344,"mean_force":213.29821,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53587,0.12232,0.26395]},{"body_a":"world","body_b":"link6","contact_count":506.0,"contact_point_centroid":[0.572,0.15642,-4e-05],"force_p95":152.22218,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":201.08216,"mean_force":86.7454,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53443,0.11944,0.26253]},{"body_a":"world","body_b":"link6","contact_count":22.0,"contact_point_centroid":[0.57689,0.15813,-0.00041],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53612,0.12455,0.26178]}],"total_contact_groups":16},"final_pose_error":0.15948,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.53426,0.11738,0.26236],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":2329.04394,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":526.0,"n_steps_budget":1000.0,"object_pos_end":[0.52179,0.02652,0.17698],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10288,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"align","tcp_end":[0.51124,0.02648,0.1384],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54534,0.12931,0.2257],"object_pos_start":[0.52179,0.02652,0.17698],"object_to_goal_dist_end":0.20001,"object_to_goal_dist_start":0.10288,"object_z_max":0.25835,"peak_contact_force":367.82746,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1525.0,"raw_peak_contact_force":2329.04394,"subtask_id":"approach","tcp_end":[0.53588,0.12226,0.26392],"tcp_start":[0.51124,0.02648,0.1384],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.54525,0.12962,0.22599],"object_pos_start":[0.54534,0.12931,0.2257],"object_to_goal_dist_end":0.2004,"object_to_goal_dist_start":0.20001,"object_z_max":0.22576,"peak_contact_force":192.79297,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":534.4807,"subtask_id":"contact","tcp_end":[0.53585,0.12259,0.26424],"tcp_start":[0.53588,0.12226,0.26392],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.54514,0.12999,0.22625],"object_pos_start":[0.54525,0.12962,0.22599],"object_to_goal_dist_end":0.20081,"object_to_goal_dist_start":0.2004,"object_z_max":0.22653,"peak_contact_force":396.73743,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":562.43826,"subtask_id":"insert","tcp_end":[0.5358,0.12363,0.26512],"tcp_start":[0.53579,0.12327,0.26483],"tcp_to_object_dist_end":0.04048,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54319,0.12486,0.22409],"object_pos_start":[0.54494,0.13056,0.2268],"object_to_goal_dist_end":0.19549,"object_to_goal_dist_start":0.20153,"object_z_max":0.22685,"peak_contact_force":164.56186,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2269.0,"raw_peak_contact_force":284.77654,"tcp_end":[0.53426,0.11738,0.26236],"tcp_start":[0.5358,0.12363,0.26512],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `989b6885a6cc20cf657766879d873fa27d37f906fbac12db49d02020abcc24a4`; realized-scene SHA-256: `b9bf2317193e958308a6e071da8e3f166f4f6aad2cd63fb849fb719630631480`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48616,0.03898,0.025]},{"name":"target","value":[0.48616,0.03898,0.025]},{"name":"socket","value":[0.48616,0.03898,0.025]},{"name":"goal","value":[0.48616,0.03898,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.03898,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48616,0.03898,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90625,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.0056,"align_1.lateral_offset_y":-0.00948,"approach_1.speed":0.03903,"contact_1.contact_force":8.12502,"contact_1.speed":0.02106,"insert_1.insertion_depth":0.05842,"insert_1.insertion_force":26.24223,"retract_1.speed":0.0629},"optimized_scores":{"best_composite_score":0.03901,"best_fitness_score":0.32901,"best_task_score":0.74803},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"world","contact_count":226.0,"contact_point_centroid":[0.56101,0.0387,-0.00084],"force_p95":10245.47852,"geom_a":"peg_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":13658.3752,"mean_force":1194.58579,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.55419,0.0407,0.01143]},{"body_a":"attachment","body_b":"peg_socket","contact_count":229.0,"contact_point_centroid":[0.54596,0.03552,0.02247],"force_p95":10025.74512,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":13234.79004,"mean_force":1240.07173,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.55409,0.0414,0.01187]},{"body_a":"world","body_b":"link6","contact_count":580.0,"contact_point_centroid":[0.58482,-0.06152,-0.00017],"force_p95":386.90713,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":756.95091,"mean_force":274.15361,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53984,-0.0123,0.24943]},{"body_a":"world","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.63088,-0.00612,-0.00069],"force_p95":484.45456,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":523.36117,"mean_force":279.43171,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.56539,0.07272,0.02455]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.54615,-0.021,0.08],"force_p95":364.88564,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":371.3345,"mean_force":306.8459,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52794,-0.02941,0.26219]},{"body_a":"peg_socket","body_b":"link6","contact_count":326.0,"contact_point_centroid":[0.54613,-0.02099,0.07999],"force_p95":264.49834,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":344.01457,"mean_force":119.7282,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52826,-0.02869,0.26196]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.54611,-0.02095,0.07998],"force_p95":314.87437,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.36066,"mean_force":304.58458,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.52898,-0.03009,0.26331]},{"body_a":"world","body_b":"link6","contact_count":992.0,"contact_point_centroid":[0.5733,-0.05817,-5e-05],"force_p95":219.03206,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":223.34496,"mean_force":190.35003,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52944,-0.03276,0.26319]},{"body_a":"peg_socket","body_b":"link6","contact_count":668.0,"contact_point_centroid":[0.54615,-0.021,0.08],"force_p95":143.06956,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":150.48319,"mean_force":105.6331,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52969,-0.03263,0.26334]},{"body_a":"world","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.57805,-0.05338,-3e-05],"force_p95":132.35687,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":135.60388,"mean_force":103.13381,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52774,-0.02925,0.26184]}],"total_contact_groups":10},"final_pose_error":0.15864,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.53162,-0.0329,0.26391],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":13658.3752,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":509.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.02705,0.17715],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10086,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"align","tcp_end":[0.48908,0.02689,0.1391],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5388,-0.03392,0.22366],"object_pos_start":[0.50142,0.02705,0.17715],"object_to_goal_dist_end":0.15263,"object_to_goal_dist_start":0.10086,"object_z_max":0.22392,"peak_contact_force":296.59873,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1379.0,"raw_peak_contact_force":13658.3752,"subtask_id":"approach","tcp_end":[0.52765,-0.0292,0.26178],"tcp_start":[0.48908,0.02689,0.1391],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.53938,-0.03441,0.22472],"object_pos_start":[0.5388,-0.03392,0.22366],"object_to_goal_dist_end":0.15388,"object_to_goal_dist_start":0.15263,"object_z_max":0.22441,"peak_contact_force":242.35731,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":371.3345,"subtask_id":"contact","tcp_end":[0.52856,-0.02979,0.26295],"tcp_start":[0.52765,-0.0292,0.26178],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":930.0,"object_pos_end":[0.53964,-0.03465,0.22503],"object_pos_start":[0.53938,-0.03441,0.22472],"object_to_goal_dist_end":0.15429,"object_to_goal_dist_start":0.15388,"object_z_max":0.22534,"peak_contact_force":301.49773,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":316.36066,"subtask_id":"insert","tcp_end":[0.52984,-0.0308,0.26402],"tcp_start":[0.5294,-0.03041,0.26366],"tcp_to_object_dist_end":0.04039,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54121,-0.03737,0.22533],"object_pos_start":[0.54022,-0.03532,0.22565],"object_to_goal_dist_end":0.15562,"object_to_goal_dist_start":0.15517,"object_z_max":0.22575,"peak_contact_force":171.86138,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1660.0,"raw_peak_contact_force":223.34496,"tcp_end":[0.53162,-0.0329,0.26391],"tcp_start":[0.52984,-0.0308,0.26402],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```