## Search State

- **Seed**: 5
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | 0.2253 | 0.85 | ❌ rejected |
| 1 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.0898 | 0.87 | ✅ accepted |
| 0 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | force_exceeded | pose_tolerance | 5 | -0.2770 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.85 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.225) — your mutation base

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

- **Composite score**: 0.225
- **task_score** (E): 0.854
- **fitness_score**: 0.365  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.400
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_high | 0.00 | 1.00 | 0.1491 |
| approach_descend | 0.00 | 1.00 | 0.1100 |
| contact_probe | 1.00 | 1.00 | 0.0010 |
| insert_down | 1.00 | 1.00 | 0.0011 |
| retract_up | 0.33 | 0.67 | 0.0311 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_high | align | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.454, 0.013, 0.160) | (0.504, -0.000, 0.340)→(0.492, 0.013, 0.149) | 0.260→0.073 | 1.00 / 1.000 | 253.430 | 1084.851 |
| approach_descend | approach | 0.00 / step_budget | (0.454, 0.013, 0.160)→(0.519, 0.009, 0.246) | (0.492, 0.013, 0.149)→(0.543, 0.011, 0.216) | 0.073→0.146 | 1.00 / 1.667 | 553.531 | 1215.570 |
| contact_probe | contact | 1.00 / force_exceeded | (0.520, 0.008, 0.247)→(0.520, 0.008, 0.247) | (0.543, 0.011, 0.216)→(0.543, 0.011, 0.216) | 0.146→0.147 | 1.00 / 1.667 | 664.451 | 728.791 |
| insert_down | insert | 1.00 / force_exceeded | (0.520, 0.008, 0.247)→(0.520, 0.008, 0.248) | (0.544, 0.010, 0.217)→(0.544, 0.009, 0.217) | 0.148→0.148 | 1.00 / 1.667 | 638.922 | 638.922 |
| retract_up | retract | 0.33 / step_budget | (0.520, 0.008, 0.248)→(0.534, 0.016, 0.226) | (0.544, 0.009, 0.217)→(0.558, 0.020, 0.198) | 0.148→0.135 | 0.67 / 1.000 | 167.706 | 314.164 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.871
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.871
- phase_score: 0.053
- phase_breakdown.align_score: 0.002
- phase_breakdown.insert_score: 0.068
- phase_breakdown.contact_score: 0.056
- phase_breakdown.approach_score: 0.037

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.380
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.871
- **Median Q (composite search score)**: 0.226
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.294


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.75342,"average_solve_count":73.0,"average_success_count":73.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_descend.speed":0.06809,"contact_probe.force_threshold":6.7846,"contact_probe.speed":0.01466,"insert_down.force_limit":23.37592,"insert_down.insertion_depth":0.03967,"insert_down.speed":0.01722,"retract_up.arc_height":0.072,"retract_up.retract_height":0.16375,"retract_up.speed":0.06644},"optimized_scores":{"best_composite_score":0.24008,"best_fitness_score":0.38008,"best_task_score":0.87092},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":510.0,"contact_point_centroid":[0.58433,0.0287,0.07987],"force_p95":337.96667,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1623.20757,"mean_force":272.01502,"phase_index":1.0,"phase_name":"approach_descend","phase_type":"approach","tcp_position_centroid":[0.47042,0.02491,0.18454]},{"body_a":"peg_socket","body_b":"link5","contact_count":5.0,"contact_point_centroid":[0.50514,0.08375,0.06879],"force_p95":1541.99353,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1574.19728,"mean_force":1360.50292,"phase_index":1.0,"phase_name":"approach_descend","phase_type":"approach","tcp_position_centroid":[0.52345,0.02577,0.2635]},{"body_a":"peg_socket","body_b":"link7","contact_count":67.0,"contact_point_centroid":[0.58431,0.03104,0.0799],"force_p95":578.98296,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1294.41871,"mean_force":396.312,"phase_index":1.0,"phase_name":"approach_descend","phase_type":"approach","tcp_position_centroid":[0.49225,0.03277,0.17883]},{"body_a":"peg_socket","body_b":"link5","contact_count":3.0,"contact_point_centroid":[0.50517,0.08303,0.06929],"force_p95":1210.13132,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1217.86814,"mean_force":1146.56984,"phase_index":2.0,"phase_name":"contact_probe","phase_type":"contact","tcp_position_centroid":[0.52482,0.02779,0.2649]},{"body_a":"attachment","body_b":"peg_socket","contact_count":14.0,"contact_point_centroid":[0.47025,0.01325,0.07827],"force_p95":1043.32211,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1097.33657,"mean_force":217.25277,"phase_index":0.0,"phase_name":"align_high","phase_type":"align","tcp_position_centroid":[0.4658,0.01321,0.09084]},{"body_a":"peg_socket","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.50531,0.083,0.06957],"force_p95":1030.01267,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1030.01267,"mean_force":1030.01267,"phase_index":3.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.52486,0.02906,0.26557]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.58394,0.08459,0.07971],"force_p95":912.8542,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":922.64008,"mean_force":843.2378,"phase_index":2.0,"phase_name":"contact_probe","phase_type":"contact","tcp_position_centroid":[0.52482,0.02779,0.2649]},{"body_a":"peg_socket","body_b":"link7","contact_count":104.0,"contact_point_centroid":[0.57688,0.01751,0.07909],"force_p95":527.09261,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":836.26384,"mean_force":298.24452,"phase_index":0.0,"phase_name":"align_high","phase_type":"align","tcp_position_centroid":[0.46252,0.01606,0.13067]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58408,0.0846,0.07979],"force_p95":745.49917,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":745.49917,"mean_force":745.49917,"phase_index":3.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.52486,0.02906,0.26557]},{"body_a":"peg_socket","body_b":"link6","contact_count":501.0,"contact_point_centroid":[0.58437,0.08462,0.07998],"force_p95":208.73897,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":494.96235,"mean_force":126.09686,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.54364,0.04656,0.25473]},{"body_a":"peg_socket","body_b":"link5","contact_count":12.0,"contact_point_centroid":[0.50564,0.08377,0.06996],"force_p95":315.71218,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":323.43629,"mean_force":179.09952,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.52481,0.03181,0.26633]},{"body_a":"peg_socket","body_b":"link6","contact_count":73.0,"contact_point_centroid":[0.58436,0.02028,0.07985],"force_p95":289.1541,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":300.96839,"mean_force":255.65247,"phase_index":0.0,"phase_name":"align_high","phase_type":"align","tcp_position_centroid":[0.46,0.01989,0.15498]},{"body_a":"world","body_b":"link5","contact_count":387.0,"contact_point_centroid":[0.5206,0.15146,-5e-05],"force_p95":278.41521,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":291.14705,"mean_force":186.87755,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.5475,0.04842,0.25236]},{"body_a":"peg_socket","body_b":"link5","contact_count":4.0,"contact_point_centroid":[0.52364,0.08444,0.04994],"force_p95":43.3561,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":51.00718,"mean_force":12.75179,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.52471,0.03065,0.2664]},{"body_a":"peg_socket","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.52283,0.08423,0.04988],"force_p95":13.47797,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":13.47797,"mean_force":13.47797,"phase_index":3.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.52486,0.02906,0.26557]},{"body_a":"peg_socket","body_b":"link5","contact_count":3.0,"contact_point_centroid":[0.52227,0.08423,0.04988],"force_p95":13.16097,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":13.47636,"mean_force":7.93292,"phase_index":2.0,"phase_name":"contact_probe","phase_type":"contact","tcp_position_centroid":[0.52482,0.02779,0.2649]}],"total_contact_groups":17},"final_pose_error":0.06952,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.55151,0.04419,0.24972],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":1623.20757,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":281.0,"n_steps_budget":600.0,"object_pos_end":[0.49497,0.02134,0.14394],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.0676,"object_to_goal_dist_start":0.26034,"object_z_max":0.34532,"peak_contact_force":233.24506,"phase_name":"align_high","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":191.0,"raw_peak_contact_force":1097.33657,"subtask_id":"align","tcp_end":[0.45585,0.02085,0.15229],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.54442,0.03768,0.23138],"object_pos_start":[0.49497,0.02134,0.14394],"object_to_goal_dist_end":0.1622,"object_to_goal_dist_start":0.0676,"object_z_max":0.23113,"peak_contact_force":1156.60893,"phase_name":"approach_descend","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":584.0,"raw_peak_contact_force":1623.20757,"subtask_id":"approach","tcp_end":[0.5247,0.02725,0.26458],"tcp_start":[0.45585,0.02085,0.15229],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.54455,0.03814,0.23166],"object_pos_start":[0.54442,0.03768,0.23138],"object_to_goal_dist_end":0.16261,"object_to_goal_dist_start":0.1622,"object_z_max":0.23197,"peak_contact_force":1081.34147,"phase_name":"contact_probe","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":9.0,"raw_peak_contact_force":1217.86814,"subtask_id":"contact","tcp_end":[0.52486,0.02906,0.26557],"tcp_start":[0.5249,0.02836,0.26522],"tcp_to_object_dist_end":0.04025,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.54449,0.03998,0.23268],"object_pos_start":[0.54457,0.03929,0.23231],"object_to_goal_dist_end":0.16398,"object_to_goal_dist_start":0.16349,"object_z_max":0.23231,"peak_contact_force":1030.01267,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":1030.01267,"subtask_id":"insert","tcp_end":[0.52474,0.02985,0.26595],"tcp_start":[0.52486,0.02906,0.26557],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":553.0,"n_steps_budget":750.0,"object_pos_end":[0.5669,0.05773,0.21537],"object_pos_start":[0.54449,0.03998,0.23268],"object_to_goal_dist_end":0.16166,"object_to_goal_dist_start":0.16398,"object_z_max":0.23357,"peak_contact_force":183.38252,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":904.0,"raw_peak_contact_force":494.96235,"tcp_end":[0.55151,0.04419,0.24972],"tcp_start":[0.52474,0.02985,0.26595],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.38384,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_descend.speed":0.02468,"contact_probe.force_threshold":4.80185,"contact_probe.speed":0.01553,"insert_down.force_limit":21.44447,"insert_down.insertion_depth":0.05088,"insert_down.speed":0.01256,"retract_up.arc_height":0.06859,"retract_up.retract_height":0.12052,"retract_up.speed":0.04489},"optimized_scores":{"best_composite_score":0.20993,"best_fitness_score":0.34993,"best_task_score":0.84868},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":741.0,"contact_point_centroid":[0.563,-0.0145,0.07991],"force_p95":310.0626,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1115.19606,"mean_force":280.4703,"phase_index":1.0,"phase_name":"approach_descend","phase_type":"approach","tcp_position_centroid":[0.4609,-0.0152,0.18773]},{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.45768,-0.00706,0.07845],"force_p95":1031.27881,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1082.15407,"mean_force":230.27353,"phase_index":0.0,"phase_name":"align_high","phase_type":"align","tcp_position_centroid":[0.45322,-0.00699,0.0912]},{"body_a":"peg_socket","body_b":"link7","contact_count":272.0,"contact_point_centroid":[0.56291,-0.00706,0.07996],"force_p95":264.85458,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1009.89348,"mean_force":259.19936,"phase_index":1.0,"phase_name":"approach_descend","phase_type":"approach","tcp_position_centroid":[0.45206,-0.01107,0.16489]},{"body_a":"peg_socket","body_b":"link7","contact_count":180.0,"contact_point_centroid":[0.56016,-0.00821,0.07952],"force_p95":437.08694,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":828.95547,"mean_force":282.98188,"phase_index":0.0,"phase_name":"align_high","phase_type":"align","tcp_position_centroid":[0.45116,-0.00915,0.14533]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.5629,-0.0195,0.07981],"force_p95":416.82156,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":419.55777,"mean_force":398.21306,"phase_index":2.0,"phase_name":"contact_probe","phase_type":"contact","tcp_position_centroid":[0.47592,-0.02256,0.20851]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.56288,-0.01969,0.0798],"force_p95":373.48444,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":373.48444,"mean_force":373.48444,"phase_index":3.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.47587,-0.02272,0.20838]},{"body_a":"peg_socket","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.56293,-0.01978,0.07985],"force_p95":120.74092,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":121.11709,"mean_force":101.01207,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.47593,-0.02278,0.20835]}],"total_contact_groups":7},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.49089,-0.00616,0.15985],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":1115.19606,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":281.0,"n_steps_budget":600.0,"object_pos_end":[0.49212,-0.01034,0.15097],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.07215,"object_to_goal_dist_start":0.26034,"object_z_max":0.34463,"peak_contact_force":265.15805,"phase_name":"align_high","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":193.0,"raw_peak_contact_force":1082.15407,"subtask_id":"align","tcp_end":[0.45433,-0.01004,0.16406],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50668,-0.02042,0.18308],"object_pos_start":[0.49212,-0.01034,0.15097],"object_to_goal_dist_end":0.10529,"object_to_goal_dist_start":0.07215,"object_z_max":0.18334,"peak_contact_force":209.16105,"phase_name":"approach_descend","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1013.0,"raw_peak_contact_force":1115.19606,"subtask_id":"approach","tcp_end":[0.47594,-0.02249,0.20858],"tcp_start":[0.45433,-0.01004,0.16406],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50667,-0.02049,0.183],"object_pos_start":[0.50668,-0.02042,0.18308],"object_to_goal_dist_end":0.10523,"object_to_goal_dist_start":0.10529,"object_z_max":0.18308,"peak_contact_force":382.88567,"phase_name":"contact_probe","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":419.55777,"subtask_id":"contact","tcp_end":[0.47587,-0.02272,0.20838],"tcp_start":[0.47589,-0.02264,0.20843],"tcp_to_object_dist_end":0.03997,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50661,-0.02073,0.18287],"object_pos_start":[0.50663,-0.02065,0.1829],"object_to_goal_dist_end":0.10514,"object_to_goal_dist_start":0.10516,"object_z_max":0.1829,"peak_contact_force":373.48444,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":373.48444,"subtask_id":"insert","tcp_end":[0.47584,-0.0228,0.20834],"tcp_start":[0.47587,-0.02272,0.20838],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":123.0,"n_steps_budget":960.0,"object_pos_end":[0.52788,-0.00193,0.14522],"object_pos_start":[0.50661,-0.02073,0.18287],"object_to_goal_dist_end":0.07096,"object_to_goal_dist_start":0.10514,"object_z_max":0.18293,"peak_contact_force":0.0,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":8.0,"raw_peak_contact_force":121.11709,"tcp_end":[0.49089,-0.00616,0.15985],"tcp_start":[0.47584,-0.0228,0.20834],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.86316,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_descend.speed":0.05106,"contact_probe.force_threshold":7.91562,"contact_probe.speed":0.01858,"insert_down.force_limit":32.67477,"insert_down.insertion_depth":0.04785,"insert_down.speed":0.01539,"retract_up.arc_height":0.06269,"retract_up.retract_height":0.12733,"retract_up.speed":0.03164},"optimized_scores":{"best_composite_score":0.22581,"best_fitness_score":0.36581,"best_task_score":0.84235},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.46195,0.01572,0.07881],"force_p95":1017.12255,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1075.06092,"mean_force":228.01173,"phase_index":0.0,"phase_name":"align_high","phase_type":"align","tcp_position_centroid":[0.45739,0.01568,0.0919]},{"body_a":"peg_socket","body_b":"link6","contact_count":746.0,"contact_point_centroid":[0.56983,0.03036,0.07979],"force_p95":331.23853,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":908.30736,"mean_force":274.3341,"phase_index":1.0,"phase_name":"approach_descend","phase_type":"approach","tcp_position_centroid":[0.46525,0.03708,0.19061]},{"body_a":"peg_socket","body_b":"link7","contact_count":144.0,"contact_point_centroid":[0.56585,0.01876,0.07943],"force_p95":478.83644,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":810.81446,"mean_force":293.51112,"phase_index":0.0,"phase_name":"align_high","phase_type":"align","tcp_position_centroid":[0.45358,0.02056,0.14052]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.56963,-0.02782,0.07969],"force_p95":547.9708,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":548.94721,"mean_force":539.0854,"phase_index":2.0,"phase_name":"contact_probe","phase_type":"contact","tcp_position_centroid":[0.55785,0.02113,0.26664]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.5698,-0.02799,0.07983],"force_p95":513.26965,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":513.26965,"mean_force":513.26965,"phase_index":3.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.55943,0.0176,0.26822]},{"body_a":"peg_socket","body_b":"link7","contact_count":47.0,"contact_point_centroid":[0.56997,0.05106,0.07995],"force_p95":472.65459,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":511.33394,"mean_force":379.55332,"phase_index":1.0,"phase_name":"approach_descend","phase_type":"approach","tcp_position_centroid":[0.48822,0.07407,0.18886]},{"body_a":"peg_socket","body_b":"link6","contact_count":948.0,"contact_point_centroid":[0.56997,-0.02817,0.07997],"force_p95":321.29685,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":326.41323,"mean_force":261.48158,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.56075,0.01344,0.26744]},{"body_a":"peg_socket","body_b":"link6","contact_count":60.0,"contact_point_centroid":[0.56996,0.0271,0.07983],"force_p95":296.93691,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":306.49426,"mean_force":270.21107,"phase_index":0.0,"phase_name":"align_high","phase_type":"align","tcp_position_centroid":[0.45284,0.02593,0.16476]}],"total_contact_groups":8},"final_pose_error":0.12729,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.55853,0.01085,0.26814],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1075.06092,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":310.0,"n_steps_budget":600.0,"object_pos_end":[0.48864,0.02789,0.15227],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.0783,"object_to_goal_dist_start":0.26034,"object_z_max":0.34477,"peak_contact_force":261.88599,"phase_name":"align_high","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":217.0,"raw_peak_contact_force":1075.06092,"subtask_id":"align","tcp_end":[0.45058,0.02712,0.16456],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":844.0,"n_steps_budget":960.0,"object_pos_end":[0.57753,0.01566,0.2323],"object_pos_start":[0.48864,0.02789,0.15227],"object_to_goal_dist_end":0.17161,"object_to_goal_dist_start":0.0783,"object_z_max":0.23183,"peak_contact_force":294.82226,"phase_name":"approach_descend","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":793.0,"raw_peak_contact_force":908.30736,"subtask_id":"approach","tcp_end":[0.55714,0.02273,0.26597],"tcp_start":[0.45058,0.02712,0.16456],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.57812,0.01417,0.23286],"object_pos_start":[0.57753,0.01566,0.2323],"object_to_goal_dist_end":0.17225,"object_to_goal_dist_start":0.17161,"object_z_max":0.23353,"peak_contact_force":529.12586,"phase_name":"contact_probe","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":548.94721,"subtask_id":"contact","tcp_end":[0.55943,0.0176,0.26822],"tcp_start":[0.55858,0.01947,0.26735],"tcp_to_object_dist_end":0.04014,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.58022,0.00892,0.23513],"object_pos_start":[0.57948,0.01072,0.2343],"object_to_goal_dist_end":0.17487,"object_to_goal_dist_start":0.17389,"object_z_max":0.2343,"peak_contact_force":513.26965,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":513.26965,"subtask_id":"insert","tcp_end":[0.56033,0.01575,0.26915],"tcp_start":[0.55943,0.0176,0.26822],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57851,0.00462,0.23406],"object_pos_start":[0.58022,0.00892,0.23513],"object_to_goal_dist_end":0.17297,"object_to_goal_dist_start":0.17487,"object_z_max":0.23765,"peak_contact_force":319.73653,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":948.0,"raw_peak_contact_force":326.41323,"tcp_end":[0.55853,0.01085,0.26814],"tcp_start":[0.56033,0.01575,0.26915],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```