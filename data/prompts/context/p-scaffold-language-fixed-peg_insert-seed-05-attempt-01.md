## Search State

- **Seed**: 5
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.0898 | 0.87 | ✅ accepted |
| 0 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | force_exceeded | pose_tolerance | 5 | -0.2770 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.87 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `3a693f0216d44408acf55cd4ed5e7511210ea06892083b191557e74fdeb42bf8`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5244002338996304, 0.024635263178919502, 0.08]
- Frozen socket pose: [0.5244002338996304, 0.024635263178919502, 0.025] (static fixture for this episode)
- Goal object position: (0.5244002338996304, 0.024635263178919502, 0.025)
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
  frozen_task_target: [0.5244, 0.0246, 0.08]
  frozen_socket_position: [0.5244, 0.0246, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5244002338996304, 0.024635263178919502, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5244002338996304, 0.024635263178919502, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 3a693f0216d44408acf55cd4ed5e7511210ea06892083b191557e74fdeb42bf8

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

## Current Skill (Q=0.090) — your mutation base

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
    - 0.12
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
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
    - 0.085
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
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
  subtask_id: approach
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.08
    tolerance: 0.005
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    force_threshold:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
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
  guards:
  - id: contact_fail
    when: after_phase
    predicate: force_below
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.003
  subtask_id: contact
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.08
    offset_along_axis:
      distance: 0.055
      axis: world_z
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
      tolerance: 0.1
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.055
      binds_to:
      - path: target.offset_along_axis.distance
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
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: insert
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_1** (`align`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings: none
- **approach_1** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.085], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.08], tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_fail, when=after_phase, predicate=force_below, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.003]
- **insert_1** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.08], offset_along_axis={axis=world_z, distance=0.055, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=reduce_speed
- **retract_1** (`retract`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.090
- **task_score** (E): 0.870
- **fitness_score**: 0.380  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 0.33 | 0.67 | 0.1117 |
| approach_1 | 0.00 | 1.00 | 0.0927 |
| contact_1 | 1.00 | 1.00 | 0.0050 |
| insert_1 | 0.00 | 1.00 | 0.0633 |
| retract_1 | 0.00 | 1.00 | 0.0197 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.480, 0.014, 0.193) | (0.504, -0.000, 0.340)→(0.514, 0.013, 0.171) | 0.260→0.095 | 0.67 / 0.667 | 179.071 | 1667.331 |
| approach_1 | approach | 0.00 / step_budget | (0.480, 0.014, 0.193)→(0.512, 0.001, 0.236) | (0.514, 0.013, 0.171)→(0.533, -0.002, 0.205) | 0.095→0.148 | 1.00 / 1.333 | 309.775 | 788.419 |
| contact_1 | contact | 1.00 / force_exceeded | (0.513, 0.002, 0.237)→(0.514, 0.007, 0.239) | (0.533, -0.002, 0.205)→(0.534, -0.001, 0.205) | 0.148→0.148 | 1.00 / 2.333 | 1197.626 | 1254.225 |
| insert_1 | insert | 0.00 / step_budget | (0.514, 0.007, 0.239)→(0.535, -0.016, 0.282) | (0.534, 0.004, 0.207)→(0.548, -0.016, 0.245) | 0.149→0.178 | 1.00 / 1.667 | 390.118 | 1400.346 |
| retract_1 | retract | 0.00 / step_budget | (0.535, -0.016, 0.282)→(0.538, -0.010, 0.276) | (0.548, -0.016, 0.245)→(0.549, -0.009, 0.238) | 0.178→0.175 | 1.00 / 1.667 | 222.078 | 294.043 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.866
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.866
- phase_score: 0.069
- phase_breakdown.align_score: 0.005
- phase_breakdown.insert_score: 0.130
- phase_breakdown.contact_score: 0.011
- phase_breakdown.approach_score: 0.008

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.388
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.873
- **Median Q (composite search score)**: 0.090
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.335


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `5dab308f3f0d3a4c4fc859445abf2870fb989899bfcd82caf016befc5af88e16`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `195061a138fd9757490665621e9d85a89af1c36de72bed7c93df67d7bd9941b0`; realized-scene SHA-256: `3a693f0216d44408acf55cd4ed5e7511210ea06892083b191557e74fdeb42bf8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.5244,0.02464,0.025]},{"name":"target","value":[0.5244,0.02464,0.025]},{"name":"socket","value":[0.5244,0.02464,0.025]},{"name":"goal","value":[0.5244,0.02464,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.02464,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.5244,0.02464,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.07143,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06646,"contact_1.force_threshold":5.95916,"contact_1.speed":0.0156,"insert_1.insertion_depth":0.05024,"insert_1.speed":0.02004,"retract_1.arc_height":0.07177,"retract_1.retract_height":0.06773,"retract_1.speed":0.0448},"optimized_scores":{"best_composite_score":0.08161,"best_fitness_score":0.37161,"best_task_score":0.87223},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":238.0,"contact_point_centroid":[0.57982,0.00995,0.07956],"force_p95":461.3063,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2351.09468,"mean_force":317.86456,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46785,0.0081,0.14488]},{"body_a":"peg_socket","body_b":"link6","contact_count":523.0,"contact_point_centroid":[0.58434,0.01052,0.07982],"force_p95":320.80666,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1634.20569,"mean_force":265.26848,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4663,0.01278,0.17391]},{"body_a":"peg_socket","body_b":"link6","contact_count":441.0,"contact_point_centroid":[0.58347,0.01142,0.07982],"force_p95":496.65243,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1379.89727,"mean_force":324.91284,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49633,0.03473,0.21078]},{"body_a":"peg_socket","body_b":"link7","contact_count":39.0,"contact_point_centroid":[0.58369,0.03021,0.07936],"force_p95":1206.99425,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1229.23671,"mean_force":432.22652,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47905,0.01912,0.17113]},{"body_a":"attachment","body_b":"peg_socket","contact_count":14.0,"contact_point_centroid":[0.46746,0.00337,0.07809],"force_p95":1065.61426,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1111.2538,"mean_force":221.10604,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46209,0.00336,0.09014]},{"body_a":"world","body_b":"link6","contact_count":80.0,"contact_point_centroid":[0.60637,-0.08265,-0.00057],"force_p95":859.74542,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1013.84524,"mean_force":359.08609,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.54705,-0.0732,0.26063]},{"body_a":"world","body_b":"link6","contact_count":969.0,"contact_point_centroid":[0.53399,-0.08913,-5e-05],"force_p95":584.7816,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":716.34855,"mean_force":356.98065,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.52472,-0.07947,0.26946]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.54501,-0.03526,0.07999],"force_p95":611.96067,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":626.09576,"mean_force":484.74485,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53817,-0.07411,0.26221]},{"body_a":"world","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.59912,-0.08004,-0.00014],"force_p95":522.15506,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":548.31233,"mean_force":319.44618,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53837,-0.07374,0.26131]},{"body_a":"peg_socket","body_b":"link6","contact_count":957.0,"contact_point_centroid":[0.49857,-0.03532,0.08],"force_p95":316.38893,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":516.21481,"mean_force":250.68511,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.52465,-0.07951,0.26948]},{"body_a":"peg_socket","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.55395,-0.00545,0.07944],"force_p95":355.51279,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":376.53418,"mean_force":197.10015,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45979,0.00335,0.09759]},{"body_a":"world","body_b":"link6","contact_count":757.0,"contact_point_centroid":[0.53582,-0.08832,-2e-05],"force_p95":209.0095,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":264.25249,"mean_force":149.3799,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52494,-0.08218,0.26963]},{"body_a":"peg_socket","body_b":"link6","contact_count":995.0,"contact_point_centroid":[0.50126,-0.03533,0.07657],"force_p95":213.10682,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":233.6536,"mean_force":160.92849,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52601,-0.08087,0.26966]},{"body_a":"peg_socket","body_b":"link6","contact_count":36.0,"contact_point_centroid":[0.49439,-0.03528,0.08],"force_p95":54.34499,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":229.00301,"mean_force":34.07526,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.52278,-0.08245,0.26964]}],"total_contact_groups":14},"final_pose_error":0.20806,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.52206,-0.08491,0.2696],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":2351.09468,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":874.0,"n_steps_budget":990.0,"object_pos_end":[0.52172,0.02095,0.15724],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08293,"object_to_goal_dist_start":0.26034,"object_z_max":0.34481,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":795.0,"raw_peak_contact_force":2351.09468,"subtask_id":"align","tcp_end":[0.48542,0.02219,0.174],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":604.0,"n_steps_budget":720.0,"object_pos_end":[0.55345,-0.07524,0.22284],"object_pos_start":[0.52172,0.02095,0.15724],"object_to_goal_dist_end":0.17006,"object_to_goal_dist_start":0.08293,"object_z_max":0.24674,"peak_contact_force":276.47538,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":560.0,"raw_peak_contact_force":1379.89727,"subtask_id":"approach","tcp_end":[0.53868,-0.07312,0.25995],"tcp_start":[0.48542,0.02219,0.174],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":12.0,"n_steps_budget":1000.0,"object_pos_end":[0.55341,-0.07536,0.22302],"object_pos_start":[0.55345,-0.07524,0.22284],"object_to_goal_dist_end":0.17025,"object_to_goal_dist_start":0.17006,"object_z_max":0.22454,"peak_contact_force":626.09576,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":7.0,"raw_peak_contact_force":626.09576,"subtask_id":"contact","tcp_end":[0.53795,-0.07438,0.26255],"tcp_start":[0.53814,-0.07414,0.26228],"tcp_to_object_dist_end":0.04246,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53771,-0.07716,0.22975],"object_pos_start":[0.55091,-0.07606,0.22475],"object_to_goal_dist_end":0.17263,"object_to_goal_dist_start":0.17126,"object_z_max":0.23021,"peak_contact_force":583.86169,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1962.0,"raw_peak_contact_force":716.34855,"subtask_id":"insert","tcp_end":[0.53243,-0.07556,0.26936],"tcp_start":[0.53795,-0.07438,0.26255],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52836,-0.08461,0.2301],"object_pos_start":[0.53771,-0.07716,0.22975],"object_to_goal_dist_end":0.17463,"object_to_goal_dist_start":0.17263,"object_z_max":0.23026,"peak_contact_force":168.71887,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1752.0,"raw_peak_contact_force":264.25249,"tcp_end":[0.52206,-0.08491,0.2696],"tcp_start":[0.53243,-0.07556,0.26936],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2449f4fe819a4bbdd9aec1335ce72ae3bc4ae0ee808de76617a31b3392ec72d5`; realized-scene SHA-256: `72d0fc56eb607f902ea78d3570decababa6da9acffffae87b8c65460ac3ff15e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50305,-0.01254,0.025]},{"name":"target","value":[0.50305,-0.01254,0.025]},{"name":"socket","value":[0.50305,-0.01254,0.025]},{"name":"goal","value":[0.50305,-0.01254,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,-0.01254,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50305,-0.01254,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.59603,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04616,"contact_1.force_threshold":6.03688,"contact_1.speed":0.01519,"insert_1.insertion_depth":0.03223,"insert_1.speed":0.01742,"retract_1.arc_height":0.03623,"retract_1.retract_height":0.14894,"retract_1.speed":0.05922},"optimized_scores":{"best_composite_score":0.08985,"best_fitness_score":0.37985,"best_task_score":0.87303},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link5","contact_count":989.0,"contact_point_centroid":[0.49319,0.04735,0.05927],"force_p95":443.01158,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2864.59993,"mean_force":333.5936,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5173,-0.00221,0.26586]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.56274,0.03951,0.07982],"force_p95":2697.05694,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2744.90472,"mean_force":2397.28653,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5232,-0.01539,0.24247]},{"body_a":"peg_socket","body_b":"link5","contact_count":7.0,"contact_point_centroid":[0.50139,0.04709,0.05525],"force_p95":2517.26136,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2575.10703,"mean_force":1240.37323,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52015,-0.02291,0.2405]},{"body_a":"peg_socket","body_b":"link6","contact_count":968.0,"contact_point_centroid":[0.56301,0.04746,0.07998],"force_p95":496.00422,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1899.34533,"mean_force":238.07964,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51724,-0.0021,0.26601]},{"body_a":"peg_socket","body_b":"link7","contact_count":544.0,"contact_point_centroid":[0.56234,-0.00188,0.07971],"force_p95":313.81044,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1538.47512,"mean_force":280.95323,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45823,-0.00435,0.15878]},{"body_a":"world","body_b":"link5","contact_count":7.0,"contact_point_centroid":[0.50837,0.10561,-0.00025],"force_p95":1500.31782,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1518.76958,"mean_force":1026.9309,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.52498,-0.01188,0.24416]},{"body_a":"world","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.51054,0.10735,-0.00012],"force_p95":1202.92931,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1202.92931,"mean_force":1202.92931,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52367,-0.01429,0.24278]},{"body_a":"attachment","body_b":"peg_socket","contact_count":16.0,"contact_point_centroid":[0.4619,-0.00355,0.0771],"force_p95":955.57667,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1063.58624,"mean_force":123.94748,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45743,-0.00217,0.08802]},{"body_a":"peg_socket","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.55972,-0.06679,0.07954],"force_p95":564.7961,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":584.91964,"mean_force":461.41281,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48597,-0.06258,0.1946]},{"body_a":"peg_socket","body_b":"link6","contact_count":919.0,"contact_point_centroid":[0.56299,-0.01377,0.07991],"force_p95":325.00575,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":580.84693,"mean_force":280.08444,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46669,-0.02208,0.19895]},{"body_a":"peg_socket","body_b":"link5","contact_count":12.0,"contact_point_centroid":[0.55553,0.04699,0.07992],"force_p95":506.65362,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":517.10115,"mean_force":298.44339,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50806,-0.04598,0.23183]},{"body_a":"peg_socket","body_b":"link5","contact_count":8.0,"contact_point_centroid":[0.51973,0.04722,0.06339],"force_p95":453.74417,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":459.5016,"mean_force":367.92086,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51303,-0.03847,0.23619]},{"body_a":"peg_socket","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.50714,0.04742,0.04999],"force_p95":368.13182,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":368.13182,"mean_force":368.13182,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51591,-0.03293,0.238]},{"body_a":"peg_socket","body_b":"link6","contact_count":198.0,"contact_point_centroid":[0.56296,-0.00926,0.07984],"force_p95":322.32382,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":337.08969,"mean_force":288.43003,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46661,-0.00812,0.18864]},{"body_a":"peg_socket","body_b":"link5","contact_count":90.0,"contact_point_centroid":[0.49983,0.04717,0.04997],"force_p95":237.52882,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":327.91619,"mean_force":40.05719,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.52118,-0.00777,0.25714]},{"body_a":"peg_socket","body_b":"link6","contact_count":389.0,"contact_point_centroid":[0.56302,0.04745,0.07998],"force_p95":227.91646,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":315.86826,"mean_force":161.47709,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53503,0.02148,0.25745]}],"total_contact_groups":19},"final_pose_error":0.09484,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.5425,0.02255,0.25273],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":2864.59993,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":845.0,"n_steps_budget":990.0,"object_pos_end":[0.50714,-0.00958,0.17614],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09688,"object_to_goal_dist_start":0.26034,"object_z_max":0.34481,"peak_contact_force":281.03779,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":758.0,"raw_peak_contact_force":1538.47512,"subtask_id":"align","tcp_end":[0.47502,-0.0099,0.19997],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53746,-0.02079,0.20578],"object_pos_start":[0.50714,-0.00958,0.17614],"object_to_goal_dist_end":0.13287,"object_to_goal_dist_start":0.09688,"object_z_max":0.20551,"peak_contact_force":368.13182,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":976.0,"raw_peak_contact_force":584.91964,"subtask_id":"approach","tcp_end":[0.51673,-0.03117,0.23837],"tcp_start":[0.47502,-0.0099,0.19997],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":12.0,"n_steps_budget":1000.0,"object_pos_end":[0.53805,-0.01903,0.20607],"object_pos_start":[0.53746,-0.02079,0.20578],"object_to_goal_dist_end":0.13306,"object_to_goal_dist_start":0.13287,"object_z_max":0.20886,"peak_contact_force":2575.10703,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":15.0,"raw_peak_contact_force":2744.90472,"subtask_id":"contact","tcp_end":[0.52408,-0.01345,0.24315],"tcp_start":[0.519,-0.02596,0.23973],"tcp_to_object_dist_end":0.04001,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53696,0.01398,0.23323],"object_pos_start":[0.54229,-0.00291,0.20913],"object_to_goal_dist_end":0.15824,"object_to_goal_dist_start":0.13591,"object_z_max":0.23322,"peak_contact_force":328.59968,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2054.0,"raw_peak_contact_force":2864.59993,"subtask_id":"insert","tcp_end":[0.51978,0.00539,0.26831],"tcp_start":[0.52408,-0.01345,0.24315],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":840.0,"n_steps_budget":1000.0,"object_pos_end":[0.55495,0.03375,0.2164],"object_pos_start":[0.53696,0.01398,0.23323],"object_to_goal_dist_end":0.15088,"object_to_goal_dist_start":0.15824,"object_z_max":0.23323,"peak_contact_force":227.6034,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1063.0,"raw_peak_contact_force":315.86826,"tcp_end":[0.5425,0.02255,0.25273],"tcp_start":[0.51978,0.00539,0.26831],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c3c1e2ca75f8f9fa89b5aa82a3db3edf9cebca69b40eef83389e8297541d8019`; realized-scene SHA-256: `5286851552083a7c8a4164a2656d1a38f2da41529a3a0236ff73d4d9a02dc20c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.51001,0.03178,0.025]},{"name":"target","value":[0.51001,0.03178,0.025]},{"name":"socket","value":[0.51001,0.03178,0.025]},{"name":"goal","value":[0.51001,0.03178,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.03178,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.51001,0.03178,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.74843,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.01752,"contact_1.force_threshold":2.00664,"contact_1.speed":0.00615,"insert_1.insertion_depth":0.03094,"insert_1.speed":0.01606,"retract_1.arc_height":0.07238,"retract_1.retract_height":0.12059,"retract_1.speed":0.0982},"optimized_scores":{"best_composite_score":0.09794,"best_fitness_score":0.38794,"best_task_score":0.86582},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":14.0,"contact_point_centroid":[0.46414,0.00444,0.07792],"force_p95":1066.25685,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1112.4241,"mean_force":221.21777,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45943,0.00437,0.09005]},{"body_a":"peg_socket","body_b":"link7","contact_count":275.0,"contact_point_centroid":[0.56785,0.01171,0.07961],"force_p95":425.42797,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":838.61184,"mean_force":285.13904,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45921,0.00813,0.14989]},{"body_a":"peg_socket","body_b":"link6","contact_count":496.0,"contact_point_centroid":[0.56993,0.01586,0.07984],"force_p95":314.24562,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":713.66818,"mean_force":271.45118,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46144,0.01766,0.18624]},{"body_a":"peg_socket","body_b":"link6","contact_count":995.0,"contact_point_centroid":[0.56994,-0.02672,0.07993],"force_p95":262.6336,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":620.08803,"mean_force":262.67508,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.55004,0.02596,0.30346]},{"body_a":"peg_socket","body_b":"link6","contact_count":993.0,"contact_point_centroid":[0.56995,0.03166,0.0799],"force_p95":333.29244,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":400.44138,"mean_force":279.75137,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45679,0.05827,0.19227]},{"body_a":"peg_socket","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.56998,0.03959,0.07996],"force_p95":386.32789,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":391.67395,"mean_force":362.15289,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48084,0.10741,0.20954]},{"body_a":"peg_socket","body_b":"link6","contact_count":963.0,"contact_point_centroid":[0.56998,-0.0282,0.07995],"force_p95":273.64061,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":302.0071,"mean_force":255.13829,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55544,0.03479,0.30553]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.48003,0.00176,0.07993],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45956,0.00437,0.08829]}],"total_contact_groups":8},"final_pose_error":0.16437,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.55063,0.03304,0.30485],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1112.4241,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":874.0,"n_steps_budget":990.0,"object_pos_end":[0.51248,0.02805,0.18034],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10493,"object_to_goal_dist_start":0.26034,"object_z_max":0.34474,"peak_contact_force":256.17639,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":789.0,"raw_peak_contact_force":1112.4241,"subtask_id":"align","tcp_end":[0.48087,0.02877,0.20485],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50902,0.09083,0.18638],"object_pos_start":[0.51248,0.02805,0.18034],"object_to_goal_dist_end":0.14017,"object_to_goal_dist_start":0.10493,"object_z_max":0.18763,"peak_contact_force":284.71683,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":993.0,"raw_peak_contact_force":400.44138,"subtask_id":"approach","tcp_end":[0.48073,0.10717,0.20946],"tcp_start":[0.48087,0.02877,0.20485],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.50907,0.09093,0.1864],"object_pos_start":[0.50902,0.09083,0.18638],"object_to_goal_dist_end":0.14026,"object_to_goal_dist_start":0.14017,"object_z_max":0.18663,"peak_contact_force":391.67395,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":391.67395,"subtask_id":"contact","tcp_end":[0.48106,0.10786,0.20988],"tcp_start":[0.48087,0.10743,0.20951],"tcp_to_object_dist_end":0.04028,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56823,0.01532,0.27171],"object_pos_start":[0.50917,0.09129,0.18675],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.14076,"object_z_max":0.27187,"peak_contact_force":257.89246,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":995.0,"raw_peak_contact_force":620.08803,"subtask_id":"insert","tcp_end":[0.55235,0.02096,0.30798],"tcp_start":[0.48106,0.10786,0.20988],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":971.0,"n_steps_budget":1000.0,"object_pos_end":[0.56505,0.02415,0.26862],"object_pos_start":[0.56823,0.01532,0.27171],"object_to_goal_dist_end":0.20098,"object_to_goal_dist_start":0.20406,"object_z_max":0.27171,"peak_contact_force":269.91145,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":963.0,"raw_peak_contact_force":302.0071,"tcp_end":[0.55063,0.03304,0.30485],"tcp_start":[0.55235,0.02096,0.30798],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```