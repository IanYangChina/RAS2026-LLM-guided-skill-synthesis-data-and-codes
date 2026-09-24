## Search State

- **Seed**: 5
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.0893 | 0.87 | ❌ rejected |
| 4 | align → approach → contact → insert → retract | arc_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.0600 | 0.84 | ❌ rejected |
| 3 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.0893 | 0.87 | ❌ rejected |
| 2 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | 0.2253 | 0.85 | ❌ rejected |
| 1 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.0898 | 0.87 | ✅ accepted |

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

## Current Skill (Q=0.089) — your mutation base

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

- **Composite score**: 0.089
- **task_score** (E): 0.870
- **fitness_score**: 0.379  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 0.33 | 0.67 | 0.1117 |
| approach_1 | 0.00 | 1.00 | 0.0924 |
| contact_1 | 1.00 | 1.00 | 0.0048 |
| insert_1 | 0.00 | 1.00 | 0.0655 |
| retract_1 | 0.00 | 1.00 | 0.0201 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.480, 0.014, 0.193) | (0.504, -0.000, 0.340)→(0.514, 0.013, 0.171) | 0.260→0.095 | 0.67 / 0.667 | 179.071 | 1667.331 |
| approach_1 | approach | 0.00 / step_budget | (0.480, 0.014, 0.193)→(0.512, 0.001, 0.236) | (0.514, 0.013, 0.171)→(0.533, -0.002, 0.205) | 0.095→0.148 | 1.00 / 1.333 | 309.543 | 788.419 |
| contact_1 | contact | 1.00 / force_exceeded | (0.513, 0.002, 0.237)→(0.514, 0.006, 0.238) | (0.533, -0.002, 0.205)→(0.534, -0.001, 0.205) | 0.148→0.148 | 1.00 / 2.333 | 1184.010 | 1243.097 |
| insert_1 | insert | 0.00 / step_budget | (0.514, 0.006, 0.238)→(0.536, -0.023, 0.280) | (0.534, 0.004, 0.207)→(0.548, -0.023, 0.243) | 0.149→0.176 | 1.00 / 1.667 | 395.261 | 1384.471 |
| retract_1 | retract | 0.00 / step_budget | (0.536, -0.023, 0.280)→(0.533, -0.019, 0.273) | (0.548, -0.023, 0.243)→(0.545, -0.017, 0.236) | 0.176→0.172 | 1.00 / 2.000 | 206.060 | 515.025 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.866
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.866
- phase_score: 0.067
- phase_breakdown.align_score: 0.005
- phase_breakdown.insert_score: 0.125
- phase_breakdown.contact_score: 0.011
- phase_breakdown.approach_score: 0.008

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.386
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.873
- **Median Q (composite search score)**: 0.090
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.297


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.37681,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06632,"contact_1.force_threshold":5.61263,"contact_1.speed":0.01814,"insert_1.insertion_depth":0.05071,"insert_1.speed":0.0155,"retract_1.arc_height":0.06588,"retract_1.retract_height":0.1465,"retract_1.speed":0.06052},"optimized_scores":{"best_composite_score":0.08148,"best_fitness_score":0.37148,"best_task_score":0.87223},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":238.0,"contact_point_centroid":[0.57982,0.00995,0.07956],"force_p95":461.3063,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2351.09468,"mean_force":317.86456,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46785,0.0081,0.14488]},{"body_a":"peg_socket","body_b":"link6","contact_count":523.0,"contact_point_centroid":[0.58434,0.01052,0.07982],"force_p95":320.80666,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1634.20569,"mean_force":265.26848,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4663,0.01278,0.17391]},{"body_a":"peg_socket","body_b":"link6","contact_count":441.0,"contact_point_centroid":[0.58347,0.01142,0.07982],"force_p95":496.65243,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1379.89727,"mean_force":324.91284,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49633,0.03473,0.21078]},{"body_a":"peg_socket","body_b":"link7","contact_count":39.0,"contact_point_centroid":[0.58369,0.03021,0.07936],"force_p95":1206.99425,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1229.23671,"mean_force":432.22652,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47905,0.01912,0.17113]},{"body_a":"attachment","body_b":"peg_socket","contact_count":14.0,"contact_point_centroid":[0.46746,0.00337,0.07809],"force_p95":1065.61426,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1111.2538,"mean_force":221.10604,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46209,0.00336,0.09014]},{"body_a":"world","body_b":"link6","contact_count":80.0,"contact_point_centroid":[0.60637,-0.08265,-0.00057],"force_p95":859.74542,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1013.84524,"mean_force":359.08609,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.54705,-0.0732,0.26063]},{"body_a":"world","body_b":"link6","contact_count":334.0,"contact_point_centroid":[0.52941,-0.08635,-7e-05],"force_p95":624.54184,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":973.81492,"mean_force":242.10685,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51643,-0.08695,0.26951]},{"body_a":"world","body_b":"link6","contact_count":967.0,"contact_point_centroid":[0.53407,-0.0893,-6e-05],"force_p95":589.0755,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":714.50247,"mean_force":349.853,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.52709,-0.07911,0.26949]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.54501,-0.03526,0.07999],"force_p95":611.96067,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":626.09576,"mean_force":484.74485,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53817,-0.07411,0.26221]},{"body_a":"world","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.59912,-0.08004,-0.00014],"force_p95":522.15506,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":548.31233,"mean_force":319.44618,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53837,-0.07374,0.26131]},{"body_a":"peg_socket","body_b":"link6","contact_count":956.0,"contact_point_centroid":[0.49935,-0.03533,0.08],"force_p95":323.34867,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":516.21481,"mean_force":250.5154,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.52702,-0.07914,0.26951]},{"body_a":"peg_socket","body_b":"link6","contact_count":364.0,"contact_point_centroid":[0.49435,-0.03532,0.05981],"force_p95":235.0712,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":478.68218,"mean_force":108.02517,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5166,-0.08662,0.26994]},{"body_a":"peg_socket","body_b":"link6","contact_count":982.0,"contact_point_centroid":[0.49867,-0.03526,0.0709],"force_p95":250.79067,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":470.87134,"mean_force":180.42054,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52255,-0.07968,0.27344]},{"body_a":"peg_socket","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.55395,-0.00545,0.07944],"force_p95":355.51279,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":376.53418,"mean_force":197.10015,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45979,0.00335,0.09759]},{"body_a":"peg_socket","body_b":"link6","contact_count":17.0,"contact_point_centroid":[0.4944,-0.03535,0.08],"force_p95":0.0,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.52494,-0.08221,0.26964]}],"total_contact_groups":15},"final_pose_error":0.14934,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.51474,-0.08762,0.26953],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":2351.09468,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":874.0,"n_steps_budget":990.0,"object_pos_end":[0.52172,0.02095,0.15724],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08293,"object_to_goal_dist_start":0.26034,"object_z_max":0.34481,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":795.0,"raw_peak_contact_force":2351.09468,"subtask_id":"align","tcp_end":[0.48542,0.02219,0.174],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":604.0,"n_steps_budget":720.0,"object_pos_end":[0.55345,-0.07524,0.22284],"object_pos_start":[0.52172,0.02095,0.15724],"object_to_goal_dist_end":0.17006,"object_to_goal_dist_start":0.08293,"object_z_max":0.24674,"peak_contact_force":276.47538,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":560.0,"raw_peak_contact_force":1379.89727,"subtask_id":"approach","tcp_end":[0.53868,-0.07312,0.25995],"tcp_start":[0.48542,0.02219,0.174],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":12.0,"n_steps_budget":1000.0,"object_pos_end":[0.55341,-0.07536,0.22302],"object_pos_start":[0.55345,-0.07524,0.22284],"object_to_goal_dist_end":0.17025,"object_to_goal_dist_start":0.17006,"object_z_max":0.22454,"peak_contact_force":626.09576,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":7.0,"raw_peak_contact_force":626.09576,"subtask_id":"contact","tcp_end":[0.53795,-0.07438,0.26255],"tcp_start":[0.53814,-0.07414,0.26228],"tcp_to_object_dist_end":0.04246,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54046,-0.07671,0.2296],"object_pos_start":[0.55091,-0.07606,0.22475],"object_to_goal_dist_end":0.17292,"object_to_goal_dist_start":0.17126,"object_z_max":0.23021,"peak_contact_force":601.37395,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1940.0,"raw_peak_contact_force":714.50247,"subtask_id":"insert","tcp_end":[0.53576,-0.07499,0.26929],"tcp_start":[0.53795,-0.07438,0.26255],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52131,-0.08683,0.23008],"object_pos_start":[0.54046,-0.07671,0.2296],"object_to_goal_dist_end":0.17469,"object_to_goal_dist_start":0.17292,"object_z_max":0.23805,"peak_contact_force":145.31511,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1680.0,"raw_peak_contact_force":973.81492,"tcp_end":[0.51474,-0.08762,0.26953],"tcp_start":[0.53576,-0.07499,0.26929],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.4625,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04672,"contact_1.force_threshold":3.65087,"contact_1.speed":0.02157,"insert_1.insertion_depth":0.02028,"insert_1.speed":0.02089,"retract_1.arc_height":0.05406,"retract_1.retract_height":0.14162,"retract_1.speed":0.04778},"optimized_scores":{"best_composite_score":0.08995,"best_fitness_score":0.37995,"best_task_score":0.87303},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link5","contact_count":991.0,"contact_point_centroid":[0.49307,0.04736,0.05948],"force_p95":405.15057,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2865.24801,"mean_force":332.31027,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51706,-0.00255,0.26598]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.56274,0.03951,0.07982],"force_p95":2697.05694,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2744.90472,"mean_force":2397.28653,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5232,-0.01539,0.24247]},{"body_a":"peg_socket","body_b":"link5","contact_count":7.0,"contact_point_centroid":[0.50139,0.04709,0.05525],"force_p95":2517.26136,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2575.10703,"mean_force":1240.37323,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52015,-0.02291,0.2405]},{"body_a":"peg_socket","body_b":"link6","contact_count":969.0,"contact_point_centroid":[0.563,0.04746,0.07997],"force_p95":491.55713,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1899.34533,"mean_force":239.76629,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.517,-0.00243,0.26613]},{"body_a":"peg_socket","body_b":"link7","contact_count":544.0,"contact_point_centroid":[0.56234,-0.00188,0.07971],"force_p95":313.81044,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1538.47512,"mean_force":280.95323,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45823,-0.00435,0.15878]},{"body_a":"world","body_b":"link5","contact_count":7.0,"contact_point_centroid":[0.50837,0.10561,-0.00025],"force_p95":1496.44059,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1513.55891,"mean_force":1022.17503,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.52498,-0.01187,0.24416]},{"body_a":"world","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.51054,0.10735,-0.00012],"force_p95":1202.92931,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1202.92931,"mean_force":1202.92931,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52367,-0.01429,0.24278]},{"body_a":"attachment","body_b":"peg_socket","contact_count":16.0,"contact_point_centroid":[0.4619,-0.00355,0.0771],"force_p95":955.57667,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1063.58624,"mean_force":123.94748,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45743,-0.00217,0.08802]},{"body_a":"peg_socket","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.55972,-0.06679,0.07954],"force_p95":564.7961,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":584.91964,"mean_force":461.41281,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48597,-0.06258,0.1946]},{"body_a":"peg_socket","body_b":"link6","contact_count":919.0,"contact_point_centroid":[0.56299,-0.01377,0.07991],"force_p95":325.00575,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":580.84693,"mean_force":280.08444,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46669,-0.02208,0.19895]},{"body_a":"peg_socket","body_b":"link5","contact_count":12.0,"contact_point_centroid":[0.55553,0.04699,0.07992],"force_p95":506.65362,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":517.10115,"mean_force":298.44339,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50806,-0.04598,0.23183]},{"body_a":"peg_socket","body_b":"link5","contact_count":8.0,"contact_point_centroid":[0.51973,0.04722,0.06339],"force_p95":453.74417,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":459.5016,"mean_force":367.92086,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51303,-0.03847,0.23619]},{"body_a":"peg_socket","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.50714,0.04742,0.04999],"force_p95":368.13182,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":368.13182,"mean_force":368.13182,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51591,-0.03293,0.238]},{"body_a":"peg_socket","body_b":"link6","contact_count":198.0,"contact_point_centroid":[0.56296,-0.00926,0.07984],"force_p95":322.32382,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":337.08969,"mean_force":288.43003,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46661,-0.00812,0.18864]},{"body_a":"peg_socket","body_b":"link5","contact_count":66.0,"contact_point_centroid":[0.49856,0.04711,0.04997],"force_p95":258.8287,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":308.93538,"mean_force":58.87687,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.52221,-0.00833,0.25472]},{"body_a":"world","body_b":"link5","contact_count":662.0,"contact_point_centroid":[0.49105,0.13497,-5e-05],"force_p95":286.99615,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":308.25009,"mean_force":237.55879,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53426,0.04179,0.25358]}],"total_contact_groups":20},"final_pose_error":0.09413,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.53171,0.02638,0.24739],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":2865.24801,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":845.0,"n_steps_budget":990.0,"object_pos_end":[0.50714,-0.00958,0.17614],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09688,"object_to_goal_dist_start":0.26034,"object_z_max":0.34481,"peak_contact_force":281.03779,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":758.0,"raw_peak_contact_force":1538.47512,"subtask_id":"align","tcp_end":[0.47502,-0.0099,0.19997],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53746,-0.02079,0.20578],"object_pos_start":[0.50714,-0.00958,0.17614],"object_to_goal_dist_end":0.13287,"object_to_goal_dist_start":0.09688,"object_z_max":0.20551,"peak_contact_force":368.13182,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":976.0,"raw_peak_contact_force":584.91964,"subtask_id":"approach","tcp_end":[0.51673,-0.03117,0.23837],"tcp_start":[0.47502,-0.0099,0.19997],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":12.0,"n_steps_budget":1000.0,"object_pos_end":[0.53805,-0.01903,0.20607],"object_pos_start":[0.53746,-0.02079,0.20578],"object_to_goal_dist_end":0.13306,"object_to_goal_dist_start":0.13287,"object_z_max":0.20886,"peak_contact_force":2575.10703,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":15.0,"raw_peak_contact_force":2744.90472,"subtask_id":"contact","tcp_end":[0.52408,-0.01345,0.24315],"tcp_start":[0.519,-0.02596,0.23973],"tcp_to_object_dist_end":0.04001,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53667,0.01352,0.2334],"object_pos_start":[0.54229,-0.00291,0.20913],"object_to_goal_dist_end":0.1583,"object_to_goal_dist_start":0.13591,"object_z_max":0.23339,"peak_contact_force":323.09702,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2033.0,"raw_peak_contact_force":2865.24801,"subtask_id":"insert","tcp_end":[0.51944,0.00491,0.26846],"tcp_start":[0.52408,-0.01345,0.24315],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5451,0.03879,0.2118],"object_pos_start":[0.53667,0.01352,0.2334],"object_to_goal_dist_end":0.14461,"object_to_goal_dist_start":0.1583,"object_z_max":0.2334,"peak_contact_force":211.83761,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1255.0,"raw_peak_contact_force":308.25009,"tcp_end":[0.53171,0.02638,0.24739],"tcp_start":[0.51944,0.00491,0.26846],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.40964,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.019,"contact_1.force_threshold":4.83591,"contact_1.speed":0.01798,"insert_1.insertion_depth":0.03784,"insert_1.speed":0.01524,"retract_1.arc_height":0.0547,"retract_1.retract_height":0.11841,"retract_1.speed":0.01393},"optimized_scores":{"best_composite_score":0.09642,"best_fitness_score":0.38642,"best_task_score":0.86582},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":14.0,"contact_point_centroid":[0.46414,0.00444,0.07792],"force_p95":1066.25685,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1112.4241,"mean_force":221.21777,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45943,0.00437,0.09005]},{"body_a":"peg_socket","body_b":"link7","contact_count":275.0,"contact_point_centroid":[0.56785,0.01171,0.07961],"force_p95":425.42797,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":838.61184,"mean_force":285.13904,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45921,0.00813,0.14989]},{"body_a":"peg_socket","body_b":"link6","contact_count":496.0,"contact_point_centroid":[0.56993,0.01586,0.07984],"force_p95":314.24562,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":713.66818,"mean_force":271.45118,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46144,0.01766,0.18624]},{"body_a":"peg_socket","body_b":"link6","contact_count":995.0,"contact_point_centroid":[0.56993,-0.0265,0.07992],"force_p95":275.38563,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":573.66381,"mean_force":266.24066,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.55089,0.00495,0.29882]},{"body_a":"peg_socket","body_b":"link6","contact_count":991.0,"contact_point_centroid":[0.56995,0.03147,0.0799],"force_p95":335.19975,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":400.44138,"mean_force":281.66021,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45714,0.05681,0.19311]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.56996,0.0404,0.07994],"force_p95":357.94118,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":358.29121,"mean_force":354.63638,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48122,0.10634,0.20948]},{"body_a":"peg_socket","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.56998,-0.02819,0.07997],"force_p95":261.40814,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":263.01033,"mean_force":250.78392,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55244,0.00196,0.30236]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.48003,0.00176,0.07993],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45956,0.00437,0.08829]}],"total_contact_groups":8},"final_pose_error":0.1671,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.55301,0.00294,0.30229],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1112.4241,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":874.0,"n_steps_budget":990.0,"object_pos_end":[0.51248,0.02805,0.18034],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10493,"object_to_goal_dist_start":0.26034,"object_z_max":0.34474,"peak_contact_force":256.17639,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":789.0,"raw_peak_contact_force":1112.4241,"subtask_id":"align","tcp_end":[0.48087,0.02877,0.20485],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50955,0.09031,0.18619],"object_pos_start":[0.51248,0.02805,0.18034],"object_to_goal_dist_end":0.13973,"object_to_goal_dist_start":0.10493,"object_z_max":0.18783,"peak_contact_force":284.02066,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":991.0,"raw_peak_contact_force":400.44138,"subtask_id":"approach","tcp_end":[0.48116,0.10623,0.20944],"tcp_start":[0.48087,0.02877,0.20485],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.5096,0.0904,0.18621],"object_pos_start":[0.50955,0.09031,0.18619],"object_to_goal_dist_end":0.1398,"object_to_goal_dist_start":0.13973,"object_z_max":0.18628,"peak_contact_force":350.82699,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":358.29121,"subtask_id":"contact","tcp_end":[0.48138,0.10652,0.20962],"tcp_start":[0.48129,0.10644,0.20952],"tcp_to_object_dist_end":0.04005,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56706,-0.00488,0.26628],"object_pos_start":[0.5097,0.09048,0.18638],"object_to_goal_dist_end":0.19804,"object_to_goal_dist_start":0.13999,"object_z_max":0.26767,"peak_contact_force":261.31246,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":995.0,"raw_peak_contact_force":573.66381,"subtask_id":"insert","tcp_end":[0.55156,0.00011,0.30282],"tcp_start":[0.48138,0.10652,0.20962],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56835,-0.00241,0.26573],"object_pos_start":[0.56706,-0.00488,0.26628],"object_to_goal_dist_end":0.19792,"object_to_goal_dist_start":0.19804,"object_z_max":0.26634,"peak_contact_force":261.02729,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1000.0,"raw_peak_contact_force":263.01033,"tcp_end":[0.55301,0.00294,0.30229],"tcp_start":[0.55156,0.00011,0.30282],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```