## Search State

- **Seed**: 5
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | align → approach → contact → insert → retract | arc_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.0600 | 0.84 | ❌ rejected |
| 3 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.0893 | 0.87 | ❌ rejected |
| 2 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | 0.2253 | 0.85 | ❌ rejected |
| 1 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.0898 | 0.87 | ✅ accepted |
| 0 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | force_exceeded | pose_tolerance | 5 | -0.2770 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.84 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.060) — your mutation base

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

- **Composite score**: -0.060
- **task_score** (E): 0.840
- **fitness_score**: 0.380  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.690

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 0.00 | 1.00 | 0.1272 |
| approach_1 | 0.00 | 0.67 | 0.1122 |
| contact_1 | 1.00 | 1.00 | 0.0020 |
| insert_1 | 1.00 | 1.00 | 0.1075 |
| retract_1 | 0.00 | 1.00 | 0.0352 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.457, 0.033, 0.186) | (0.504, -0.000, 0.340)→(0.493, 0.031, 0.168) | 0.260→0.094 | 1.00 / 1.333 | 245.085 | 1254.510 |
| approach_1 | approach | 0.00 / step_budget | (0.457, 0.033, 0.186)→(0.529, 0.068, 0.241) | (0.493, 0.031, 0.168)→(0.553, 0.056, 0.212) | 0.094→0.164 | 0.67 / 0.667 | 143.777 | 604.993 |
| contact_1 | contact | 1.00 / force_exceeded | (0.530, 0.064, 0.244)→(0.530, 0.063, 0.245) | (0.553, 0.056, 0.212)→(0.553, 0.053, 0.214) | 0.164→0.164 | 1.00 / 1.000 | 612.725 | 747.166 |
| insert_1 | insert | 1.00 / time_limit | (0.530, 0.063, 0.245)→(0.570, 0.003, 0.321) | (0.554, 0.051, 0.216)→(0.584, -0.001, 0.284) | 0.166→0.223 | 1.00 / 1.000 | 265.096 | 687.966 |
| retract_1 | retract | 0.00 / step_budget | (0.570, 0.003, 0.321)→(0.544, 0.008, 0.322) | (0.584, -0.001, 0.284)→(0.561, 0.006, 0.286) | 0.223→0.219 | 1.00 / 1.000 | 270.293 | 274.366 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.847
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.847
- phase_score: 0.077
- phase_breakdown.align_score: 0.004
- phase_breakdown.insert_score: 0.111
- phase_breakdown.contact_score: 0.063
- phase_breakdown.approach_score: 0.044

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.385
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.847
- **Median Q (composite search score)**: -0.056
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.253


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.4527,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.arc_height":0.14465,"align_1.speed":0.07403,"approach_1.arc_height":0.01585,"approach_1.speed":0.04338,"contact_1.force_threshold":4.85603,"contact_1.speed":0.00511,"insert_1.insertion_depth":0.07079,"insert_1.max_time":8.51542,"insert_1.speed":0.02194,"retract_1.arc_height":0.06799,"retract_1.retract_height":0.14484,"retract_1.speed":0.04417},"optimized_scores":{"best_composite_score":-0.05502,"best_fitness_score":0.38498,"best_task_score":0.84658},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.46611,0.01624,0.07865],"force_p95":1042.88597,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1088.16708,"mean_force":251.32459,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45886,0.01622,0.09071]},{"body_a":"peg_socket","body_b":"link6","contact_count":902.0,"contact_point_centroid":[0.58419,0.03305,0.07975],"force_p95":363.35227,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":935.87256,"mean_force":277.99767,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4735,0.06021,0.20263]},{"body_a":"peg_socket","body_b":"link7","contact_count":48.0,"contact_point_centroid":[0.56564,0.01632,0.07854],"force_p95":661.886,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":828.66958,"mean_force":215.28449,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4522,0.01787,0.11569]},{"body_a":"peg_socket","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.55316,-0.00551,0.07903],"force_p95":719.111,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":781.22993,"mean_force":246.27117,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45574,0.01647,0.09704]},{"body_a":"peg_socket","body_b":"link6","contact_count":567.0,"contact_point_centroid":[0.58436,0.02492,0.07982],"force_p95":277.68967,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":647.89673,"mean_force":249.93049,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4536,0.02625,0.17045]},{"body_a":"peg_socket","body_b":"link6","contact_count":974.0,"contact_point_centroid":[0.58438,-0.03532,0.07995],"force_p95":293.77706,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":643.65639,"mean_force":259.09246,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.59257,-0.04415,0.32872]},{"body_a":"peg_socket","body_b":"link7","contact_count":37.0,"contact_point_centroid":[0.58431,0.07587,0.07988],"force_p95":514.36629,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":609.75904,"mean_force":305.18217,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49637,0.10674,0.18287]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.58395,-0.03477,0.07958],"force_p95":563.10504,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":564.05623,"mean_force":553.30846,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.57932,0.00968,0.28912]},{"body_a":"peg_socket","body_b":"link6","contact_count":987.0,"contact_point_centroid":[0.58438,-0.03533,0.07992],"force_p95":247.5312,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":249.76715,"mean_force":227.73201,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54586,-0.04472,0.33549]}],"total_contact_groups":9},"final_pose_error":0.18189,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.52792,-0.05213,0.33469],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":1088.16708,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":696.0,"n_steps_budget":870.0,"object_pos_end":[0.50083,0.03109,0.17599],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.1009,"object_to_goal_dist_start":0.26034,"object_z_max":0.34476,"peak_contact_force":255.09819,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":644.0,"raw_peak_contact_force":1088.16708,"subtask_id":"align","tcp_end":[0.46576,0.03175,0.19521],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.6001,0.00397,0.2554],"object_pos_start":[0.50083,0.03109,0.17599],"object_to_goal_dist_end":0.20199,"object_to_goal_dist_start":0.1009,"object_z_max":0.25503,"peak_contact_force":312.75563,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":939.0,"raw_peak_contact_force":935.87256,"subtask_id":"approach","tcp_end":[0.57892,0.0113,0.28853],"tcp_start":[0.46576,0.03175,0.19521],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.60042,0.0025,0.25589],"object_pos_start":[0.6001,0.00397,0.2554],"object_to_goal_dist_end":0.20256,"object_to_goal_dist_start":0.20199,"object_z_max":0.25651,"peak_contact_force":541.32477,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":564.05623,"subtask_id":"contact","tcp_end":[0.58021,0.00621,0.29053],"tcp_start":[0.57974,0.00799,0.28976],"tcp_to_object_dist_end":0.04028,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59324,-0.0421,0.29197],"object_pos_start":[0.60116,-0.00087,0.2572],"object_to_goal_dist_end":0.23537,"object_to_goal_dist_start":0.20405,"object_z_max":0.29196,"peak_contact_force":252.15709,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":974.0,"raw_peak_contact_force":643.65639,"subtask_id":"insert","tcp_end":[0.58396,-0.03922,0.33077],"tcp_start":[0.58021,0.00621,0.29053],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5438,-0.05064,0.29801],"object_pos_start":[0.59324,-0.0421,0.29197],"object_to_goal_dist_end":0.22806,"object_to_goal_dist_start":0.23537,"object_z_max":0.29947,"peak_contact_force":246.53235,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":987.0,"raw_peak_contact_force":249.76715,"tcp_end":[0.52792,-0.05213,0.33469],"tcp_start":[0.58396,-0.03922,0.33077],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.0,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.arc_height":0.09361,"align_1.speed":0.04943,"approach_1.arc_height":0.05051,"approach_1.speed":0.04122,"contact_1.force_threshold":5.77517,"contact_1.speed":0.01682,"insert_1.insertion_depth":0.05617,"insert_1.max_time":5.23332,"insert_1.speed":0.0172,"retract_1.arc_height":0.05724,"retract_1.retract_height":0.10462,"retract_1.speed":0.08446},"optimized_scores":{"best_composite_score":-0.06908,"best_fitness_score":0.37092,"best_task_score":0.84388},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":411.0,"contact_point_centroid":[0.56295,0.01591,0.0794],"force_p95":842.62842,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1603.05516,"mean_force":306.57709,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44728,0.01867,0.16312]},{"body_a":"peg_socket","body_b":"link7","contact_count":898.0,"contact_point_centroid":[0.56202,0.01992,0.07987],"force_p95":397.23956,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1524.25378,"mean_force":254.12766,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44989,0.01723,0.16009]},{"body_a":"peg_socket","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.56164,-0.06834,0.07898],"force_p95":1319.1821,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1324.53411,"mean_force":1174.31683,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53438,0.06539,0.22114]},{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.45731,0.01129,0.07811],"force_p95":1039.56124,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1089.45542,"mean_force":161.21184,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45284,0.01132,0.09051]},{"body_a":"peg_socket","body_b":"link6","contact_count":981.0,"contact_point_centroid":[0.56296,-0.0524,0.07992],"force_p95":375.49854,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":838.43818,"mean_force":282.77168,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.58665,0.02557,0.30921]},{"body_a":"peg_socket","body_b":"link6","contact_count":737.0,"contact_point_centroid":[0.56299,0.01165,0.07991],"force_p95":335.87467,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":536.75331,"mean_force":274.56091,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46106,0.04704,0.18372]},{"body_a":"world","body_b":"link6","contact_count":19.0,"contact_point_centroid":[0.67146,0.00971,-0.00034],"force_p95":499.46583,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":534.40186,"mean_force":334.15698,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51882,0.09063,0.19037]},{"body_a":"peg_socket","body_b":"link7","contact_count":199.0,"contact_point_centroid":[0.56292,0.03969,0.07993],"force_p95":342.3673,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":491.17525,"mean_force":262.55676,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49581,0.08034,0.18131]},{"body_a":"peg_socket","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.56303,-0.037,0.07998],"force_p95":276.88385,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":306.3478,"mean_force":268.29127,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.56772,0.03403,0.31349]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.65307,-0.00688,-9e-05],"force_p95":93.64179,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":96.45206,"mean_force":71.08077,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53405,0.06604,0.22041]}],"total_contact_groups":10},"final_pose_error":0.19872,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.55715,0.03558,0.31468],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":1603.05516,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48868,0.01913,0.15422],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.07748,"object_to_goal_dist_start":0.26034,"object_z_max":0.34452,"peak_contact_force":218.49901,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1322.0,"raw_peak_contact_force":1603.05516,"subtask_id":"align","tcp_end":[0.45128,0.02188,0.16814],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55575,0.06002,0.18466],"object_pos_start":[0.48868,0.01913,0.15422],"object_to_goal_dist_end":0.13291,"object_to_goal_dist_start":0.07748,"object_z_max":0.18415,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":955.0,"raw_peak_contact_force":536.75331,"subtask_id":"approach","tcp_end":[0.53191,0.07265,0.21419],"tcp_start":[0.45128,0.02188,0.16814],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.55671,0.0539,0.18977],"object_pos_start":[0.55575,0.06002,0.18466],"object_to_goal_dist_end":0.13479,"object_to_goal_dist_start":0.13291,"object_z_max":0.1923,"peak_contact_force":953.71137,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":7.0,"raw_peak_contact_force":1324.53411,"subtask_id":"contact","tcp_end":[0.53615,0.06235,0.22479],"tcp_start":[0.53464,0.06467,0.22188],"tcp_to_object_dist_end":0.04148,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59897,0.02184,0.27727],"object_pos_start":[0.55824,0.05063,0.19357],"object_to_goal_dist_end":0.22179,"object_to_goal_dist_start":0.13731,"object_z_max":0.27727,"peak_contact_force":283.65511,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":981.0,"raw_peak_contact_force":838.43818,"subtask_id":"insert","tcp_end":[0.58258,0.02517,0.31361],"tcp_start":[0.53615,0.06235,0.22479],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57611,0.03435,0.27947],"object_pos_start":[0.59897,0.02184,0.27727],"object_to_goal_dist_end":0.21625,"object_to_goal_dist_start":0.22179,"object_z_max":0.27946,"peak_contact_force":306.3478,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1000.0,"raw_peak_contact_force":306.3478,"tcp_end":[0.55715,0.03558,0.31468],"tcp_start":[0.58258,0.02517,0.31361],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.77108,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.arc_height":0.11748,"align_1.speed":0.05113,"approach_1.arc_height":0.04055,"approach_1.speed":0.01536,"contact_1.force_threshold":5.73657,"contact_1.speed":0.01726,"insert_1.insertion_depth":0.04904,"insert_1.max_time":6.11193,"insert_1.speed":0.02009,"retract_1.arc_height":0.04809,"retract_1.retract_height":0.10329,"retract_1.speed":0.04867},"optimized_scores":{"best_composite_score":-0.05575,"best_fitness_score":0.38425,"best_task_score":0.82938},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.45728,0.01772,0.0786],"force_p95":1022.81958,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1072.30657,"mean_force":246.78493,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45275,0.01769,0.09149]},{"body_a":"peg_socket","body_b":"link7","contact_count":99.0,"contact_point_centroid":[0.56279,0.01993,0.07918],"force_p95":529.68862,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":821.15263,"mean_force":298.08426,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44939,0.02142,0.13262]},{"body_a":"peg_socket","body_b":"link6","contact_count":994.0,"contact_point_centroid":[0.56996,-0.02639,0.07993],"force_p95":264.05275,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":581.80447,"mean_force":263.70917,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.54307,0.02588,0.31291]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.56998,0.04624,0.07997],"force_p95":352.41223,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":352.90825,"mean_force":347.99864,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47494,0.11981,0.22097]},{"body_a":"peg_socket","body_b":"link6","contact_count":987.0,"contact_point_centroid":[0.56995,0.04267,0.07989],"force_p95":306.98056,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":342.35186,"mean_force":262.17607,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44762,0.08843,0.1951]},{"body_a":"peg_socket","body_b":"link6","contact_count":792.0,"contact_point_centroid":[0.56997,0.03385,0.0799],"force_p95":273.97907,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":309.00219,"mean_force":254.06253,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44467,0.03567,0.17317]},{"body_a":"peg_socket","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.56999,-0.02822,0.07997],"force_p95":260.98117,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":266.98414,"mean_force":258.07437,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54653,0.03191,0.31766]}],"total_contact_groups":7},"final_pose_error":0.19295,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.54816,0.04183,0.31716],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1072.30657,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":998.0,"n_steps_budget":1000.0,"object_pos_end":[0.4891,0.04263,0.17503],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10472,"object_to_goal_dist_start":0.26034,"object_z_max":0.34449,"peak_contact_force":261.65906,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":903.0,"raw_peak_contact_force":1072.30657,"subtask_id":"align","tcp_end":[0.45413,0.04432,0.19438],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50241,0.10327,0.19705],"object_pos_start":[0.4891,0.04263,0.17503],"object_to_goal_dist_end":0.15611,"object_to_goal_dist_start":0.10472,"object_z_max":0.19708,"peak_contact_force":118.57399,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":987.0,"raw_peak_contact_force":342.35186,"subtask_id":"approach","tcp_end":[0.47492,0.11977,0.22097],"tcp_start":[0.45413,0.04432,0.19438],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50242,0.10331,0.19704],"object_pos_start":[0.50241,0.10327,0.19705],"object_to_goal_dist_end":0.15613,"object_to_goal_dist_start":0.15611,"object_z_max":0.19705,"peak_contact_force":343.13963,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":352.90825,"subtask_id":"contact","tcp_end":[0.47502,0.11986,0.22101],"tcp_start":[0.47497,0.11984,0.22098],"tcp_to_object_dist_end":0.03999,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56084,0.01712,0.28204],"object_pos_start":[0.50247,0.1033,0.19709],"object_to_goal_dist_end":0.2117,"object_to_goal_dist_start":0.15616,"object_z_max":0.28204,"peak_contact_force":259.47686,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":994.0,"raw_peak_contact_force":581.80447,"subtask_id":"insert","tcp_end":[0.5449,0.02174,0.31844],"tcp_start":[0.47502,0.11986,0.22101],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56335,0.03548,0.28071],"object_pos_start":[0.56084,0.01712,0.28204],"object_to_goal_dist_end":0.21344,"object_to_goal_dist_start":0.2117,"object_z_max":0.28206,"peak_contact_force":257.99778,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1000.0,"raw_peak_contact_force":266.98414,"tcp_end":[0.54816,0.04183,0.31716],"tcp_start":[0.5449,0.02174,0.31844],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```