## Search State

- **Seed**: 5
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | force_exceeded | pose_tolerance | 8 | 0.1457 | 0.87 | ✅ accepted |
| 5 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.0893 | 0.87 | ❌ rejected |
| 4 | align → approach → contact → insert → retract | arc_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.0600 | 0.84 | ❌ rejected |
| 3 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.0893 | 0.87 | ❌ rejected |
| 2 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | 0.2253 | 0.85 | ❌ rejected |

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

## Current Skill (Q=0.146) — your mutation base

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
    - 0.15
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
    - 0.1
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
  generator: impedance_motion
  control: impedance_control
  termination: contact_detected
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
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: contact
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.08
    offset_along_axis:
      distance: 0.04
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
    bottom_force:
      type: scalar
      range:
      - 10.0
      - 35.0
      default: 20.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    insertion_depth:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.04
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
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings: none
- **approach_1** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.08], tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_fail, when=after_phase, predicate=force_below, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **insert_1** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.08], offset_along_axis={axis=world_z, distance=0.04, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - bottom_force: status=consumed; consumers=termination.force_threshold (replace)
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

- **Composite score**: 0.146
- **task_score** (E): 0.873
- **fitness_score**: 0.436  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 0.33 | 1.00 | 0.1137 |
| approach_1 | 0.00 | 1.00 | 0.0658 |
| contact_1 | 1.00 | 1.00 | 0.0213 |
| insert_1 | 1.00 | 1.00 | 0.0020 |
| retract_1 | 0.00 | 1.00 | 0.0559 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.468, 0.012, 0.193) | (0.504, -0.000, 0.340)→(0.503, 0.012, 0.173) | 0.260→0.095 | 1.00 / 1.000 | 296.065 | 1256.059 |
| approach_1 | approach | 0.00 / step_budget | (0.468, 0.012, 0.193)→(0.489, 0.052, 0.188) | (0.503, 0.012, 0.173)→(0.521, 0.046, 0.167) | 0.095→0.114 | 1.00 / 1.000 | 391.339 | 472.321 |
| contact_1 | contact | 1.00 / step_budget | (0.566, 0.020, 0.335)→(0.556, 0.005, 0.338) | (0.521, 0.046, 0.167)→(0.511, 0.049, 0.178) | 0.114→0.157 | 1.00 / 1.000 | 509.413 | 800.698 |
| insert_1 | insert | 1.00 / force_exceeded | (0.556, 0.005, 0.338)→(0.556, 0.005, 0.339) | (0.570, 0.009, 0.301)→(0.568, 0.008, 0.301) | 0.234→0.233 | 1.00 / 1.000 | 264.331 | 291.993 |
| retract_1 | retract | 0.00 / step_budget | (0.556, 0.005, 0.339)→(0.531, 0.053, 0.338) | (0.568, 0.008, 0.301)→(0.544, 0.053, 0.300) | 0.233→0.234 | 1.00 / 1.000 | 257.436 | 509.001 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.873
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.873
- phase_score: 0.218
- phase_breakdown.align_score: 0.003
- phase_breakdown.insert_score: 0.321
- phase_breakdown.contact_score: 0.276
- phase_breakdown.approach_score: 0.012

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.480
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.881
- **Median Q (composite search score)**: 0.125
- **K-run variance**: 0.0010
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.324


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.09744,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.03264,"contact_1.speed":0.01236,"insert_1.bottom_force":16.12332,"insert_1.insertion_depth":0.05002,"insert_1.speed":0.00647,"retract_1.arc_height":0.09059,"retract_1.retract_height":0.16647,"retract_1.speed":0.03244},"optimized_scores":{"best_composite_score":0.1246,"best_fitness_score":0.4146,"best_task_score":0.88092},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":15.0,"contact_point_centroid":[0.47001,0.00483,0.07785],"force_p95":1076.69711,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1122.95484,"mean_force":208.92235,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46525,0.00479,0.08991]},{"body_a":"world","body_b":"link6","contact_count":85.0,"contact_point_centroid":[0.65859,0.11553,-0.00017],"force_p95":745.11126,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":849.16755,"mean_force":423.79487,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47516,0.15567,0.16873]},{"body_a":"peg_socket","body_b":"link7","contact_count":185.0,"contact_point_centroid":[0.5796,0.01064,0.07951],"force_p95":413.05054,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":838.23761,"mean_force":279.19128,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46503,0.00726,0.13827]},{"body_a":"peg_socket","body_b":"link6","contact_count":2654.0,"contact_point_centroid":[0.58377,0.0465,0.07985],"force_p95":482.75938,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":803.87633,"mean_force":331.49103,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50857,0.08007,0.2473]},{"body_a":"peg_socket","body_b":"link6","contact_count":252.0,"contact_point_centroid":[0.54979,-0.02137,0.07981],"force_p95":391.81259,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":497.16639,"mean_force":133.74479,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5211,-0.0501,0.33436]},{"body_a":"peg_socket","body_b":"link6","contact_count":959.0,"contact_point_centroid":[0.58432,0.02964,0.07986],"force_p95":338.02803,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":424.75209,"mean_force":274.98303,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47034,0.05349,0.19579]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.5844,0.00468,0.07967],"force_p95":402.56338,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":402.56338,"mean_force":402.56338,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.57596,0.00038,0.33414]},{"body_a":"peg_socket","body_b":"link6","contact_count":984.0,"contact_point_centroid":[0.5844,0.0244,0.07995],"force_p95":282.54739,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":383.88926,"mean_force":259.30534,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5726,0.0298,0.33454]},{"body_a":"peg_socket","body_b":"link6","contact_count":403.0,"contact_point_centroid":[0.58434,0.01256,0.07982],"force_p95":309.6776,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":335.37673,"mean_force":257.21423,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46375,0.01434,0.17119]},{"body_a":"peg_socket","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.55435,-0.00537,0.07993],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46257,0.0048,0.09246]}],"total_contact_groups":10},"final_pose_error":0.15108,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.56464,0.05711,0.33342],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":1122.95484,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":695.0,"n_steps_budget":840.0,"object_pos_end":[0.51208,0.02079,0.17554],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09852,"object_to_goal_dist_start":0.26034,"object_z_max":0.34492,"peak_contact_force":306.36852,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":609.0,"raw_peak_contact_force":1122.95484,"subtask_id":"align","tcp_end":[0.47798,0.0213,0.19646],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52654,0.09377,0.16914],"object_pos_start":[0.51208,0.02079,0.17554],"object_to_goal_dist_end":0.13207,"object_to_goal_dist_start":0.09852,"object_z_max":0.19047,"peak_contact_force":332.91137,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":959.0,"raw_peak_contact_force":424.75209,"subtask_id":"approach","tcp_end":[0.49422,0.10494,0.18989],"tcp_start":[0.47798,0.0213,0.19646],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2902.0,"n_steps_budget":1000.0,"object_pos_end":[0.51126,0.12004,0.18259],"object_pos_start":[0.52654,0.09377,0.16914],"object_to_goal_dist_end":0.15831,"object_to_goal_dist_start":0.13207,"object_z_max":0.3081,"peak_contact_force":499.52656,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2991.0,"raw_peak_contact_force":849.16755,"subtask_id":"contact","tcp_end":[0.57596,0.00038,0.33414],"tcp_start":[0.5763,0.00879,0.32651],"tcp_to_object_dist_end":0.20365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.59091,0.00934,0.29828],"object_pos_start":[0.5909,0.00928,0.29812],"object_to_goal_dist_end":0.23664,"object_to_goal_dist_start":0.23648,"object_z_max":0.29812,"peak_contact_force":402.56338,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":402.56338,"subtask_id":"insert","tcp_end":[0.57599,0.00045,0.33432],"tcp_start":[0.57596,0.00038,0.33414],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57959,0.06207,0.29665],"object_pos_start":[0.59091,0.00934,0.29828],"object_to_goal_dist_end":0.23901,"object_to_goal_dist_start":0.23664,"object_z_max":0.29895,"peak_contact_force":275.53189,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":984.0,"raw_peak_contact_force":383.88926,"tcp_end":[0.56464,0.05711,0.33342],"tcp_start":[0.57599,0.00045,0.33432],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.6,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.03156,"contact_1.speed":0.02961,"insert_1.bottom_force":18.40101,"insert_1.insertion_depth":0.03814,"insert_1.speed":0.01775,"retract_1.arc_height":0.04341,"retract_1.retract_height":0.18164,"retract_1.speed":0.05937},"optimized_scores":{"best_composite_score":0.19011,"best_fitness_score":0.48011,"best_task_score":0.87287},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":504.0,"contact_point_centroid":[0.56226,-0.00307,0.07969],"force_p95":321.95801,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1533.98864,"mean_force":279.66028,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45805,-0.00535,0.15833]},{"body_a":"attachment","body_b":"peg_socket","contact_count":16.0,"contact_point_centroid":[0.46198,-0.00404,0.07713],"force_p95":953.98815,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1062.00065,"mean_force":123.74904,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45751,-0.00266,0.08807]},{"body_a":"peg_socket","body_b":"link5","contact_count":1171.0,"contact_point_centroid":[0.46606,-0.00545,0.07991],"force_p95":640.10829,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":781.76976,"mean_force":397.84475,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52605,-0.02866,0.34208]},{"body_a":"peg_socket","body_b":"link6","contact_count":1395.0,"contact_point_centroid":[0.56273,-0.024,0.07985],"force_p95":403.47353,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":779.99112,"mean_force":285.32081,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48708,-0.05975,0.25502]},{"body_a":"peg_socket","body_b":"link5","contact_count":406.0,"contact_point_centroid":[0.48577,0.01751,0.07988],"force_p95":680.88127,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":765.12165,"mean_force":564.23008,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54462,-0.02992,0.34218]},{"body_a":"peg_socket","body_b":"link6","contact_count":969.0,"contact_point_centroid":[0.54334,0.00872,0.07992],"force_p95":296.47212,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":619.56964,"mean_force":186.6425,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49261,0.0244,0.34343]},{"body_a":"peg_socket","body_b":"link5","contact_count":134.0,"contact_point_centroid":[0.56144,0.04373,0.07968],"force_p95":453.53216,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":546.33756,"mean_force":274.37506,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48914,-0.11247,0.23918]},{"body_a":"peg_socket","body_b":"link6","contact_count":63.0,"contact_point_centroid":[0.56292,-0.00984,0.07971],"force_p95":316.79492,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":351.09639,"mean_force":285.83952,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45866,-0.0085,0.17965]},{"body_a":"peg_socket","body_b":"link6","contact_count":992.0,"contact_point_centroid":[0.56301,-0.01128,0.07994],"force_p95":310.1164,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":330.219,"mean_force":274.88024,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46056,-0.01476,0.19047]},{"body_a":"peg_socket","body_b":"link5","contact_count":661.0,"contact_point_centroid":[0.44306,-0.00111,0.07997],"force_p95":254.44679,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":313.24569,"mean_force":174.4116,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49253,0.02522,0.3433]},{"body_a":"peg_socket","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.47218,-0.00404,0.07994],"force_p95":208.53492,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":208.53492,"mean_force":208.53492,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.52883,-0.01873,0.34898]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.5518,0.00076,0.07996],"force_p95":125.54971,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":125.54971,"mean_force":125.54971,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.52943,-0.01704,0.34754]},{"body_a":"peg_socket","body_b":"link5","contact_count":19.0,"contact_point_centroid":[0.49799,-0.0427,0.07978],"force_p95":39.92724,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":46.82935,"mean_force":20.41625,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49905,-0.10442,0.32605]},{"body_a":"peg_socket","body_b":"link6","contact_count":57.0,"contact_point_centroid":[0.53304,0.02092,0.0799],"force_p95":0.0,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47885,0.03862,0.34175]}],"total_contact_groups":14},"final_pose_error":0.14705,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.47809,0.03813,0.34241],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":1533.98864,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":665.0,"n_steps_budget":810.0,"object_pos_end":[0.49635,-0.00876,0.16433],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08486,"object_to_goal_dist_start":0.26034,"object_z_max":0.34481,"peak_contact_force":286.25074,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":583.0,"raw_peak_contact_force":1533.98864,"subtask_id":"align","tcp_end":[0.46086,-0.00886,0.18277],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50987,-0.02781,0.18154],"object_pos_start":[0.49635,-0.00876,0.16433],"object_to_goal_dist_end":0.10574,"object_to_goal_dist_start":0.08486,"object_z_max":0.18512,"peak_contact_force":262.17637,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":992.0,"raw_peak_contact_force":330.219,"subtask_id":"approach","tcp_end":[0.47933,-0.03199,0.20703],"tcp_start":[0.46086,-0.00886,0.18277],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2902.0,"n_steps_budget":1000.0,"object_pos_end":[0.51111,-0.10955,0.1829],"object_pos_start":[0.50987,-0.02781,0.18154],"object_to_goal_dist_end":0.15071,"object_to_goal_dist_start":0.10574,"object_z_max":0.31106,"peak_contact_force":640.27739,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3125.0,"raw_peak_contact_force":781.76976,"subtask_id":"contact","tcp_end":[0.52883,-0.01873,0.34898],"tcp_start":[0.56131,0.00107,0.34593],"tcp_to_object_dist_end":0.19012,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":26.0,"n_steps_budget":1000.0,"object_pos_end":[0.53727,-0.01533,0.30822],"object_pos_start":[0.54132,-0.01605,0.31107],"object_to_goal_dist_end":0.23175,"object_to_goal_dist_start":0.23528,"object_z_max":0.31218,"peak_contact_force":125.54971,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":208.53492,"subtask_id":"insert","tcp_end":[0.52946,-0.017,0.34742],"tcp_start":[0.52883,-0.01873,0.34898],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49101,0.03465,0.30472],"object_pos_start":[0.53727,-0.01533,0.30822],"object_to_goal_dist_end":0.22755,"object_to_goal_dist_start":0.23175,"object_z_max":0.30851,"peak_contact_force":246.87164,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1687.0,"raw_peak_contact_force":619.56964,"tcp_end":[0.47809,0.03813,0.34241],"tcp_start":[0.52946,-0.017,0.34742],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.48333,"average_solve_count":180.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06198,"contact_1.speed":0.01793,"insert_1.bottom_force":24.7041,"insert_1.insertion_depth":0.03518,"insert_1.speed":0.02127,"retract_1.arc_height":0.06192,"retract_1.retract_height":0.13596,"retract_1.speed":0.04628},"optimized_scores":{"best_composite_score":0.12253,"best_fitness_score":0.41253,"best_task_score":0.86575},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":14.0,"contact_point_centroid":[0.46452,0.00549,0.07795],"force_p95":1064.88456,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1111.23402,"mean_force":220.97201,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4598,0.00545,0.09013]},{"body_a":"peg_socket","body_b":"link7","contact_count":250.0,"contact_point_centroid":[0.56776,0.01361,0.07961],"force_p95":374.82501,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":836.10761,"mean_force":288.50796,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45974,0.00987,0.14954]},{"body_a":"peg_socket","body_b":"link6","contact_count":2625.0,"contact_point_centroid":[0.56986,0.0502,0.07986],"force_p95":496.38774,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":771.1559,"mean_force":347.11587,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51788,0.07882,0.28407]},{"body_a":"peg_socket","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.56996,0.04823,0.07991],"force_p95":606.46189,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":661.99241,"mean_force":413.18385,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48793,0.07139,0.18425]},{"body_a":"peg_socket","body_b":"link6","contact_count":338.0,"contact_point_centroid":[0.56992,0.0178,0.0798],"force_p95":309.8557,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":547.4356,"mean_force":270.42116,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4555,0.0191,0.17946]},{"body_a":"peg_socket","body_b":"link7","contact_count":65.0,"contact_point_centroid":[0.56995,0.062,0.07988],"force_p95":529.19692,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":541.66767,"mean_force":364.57344,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48926,0.10511,0.17669]},{"body_a":"peg_socket","body_b":"link6","contact_count":975.0,"contact_point_centroid":[0.56999,0.02262,0.07988],"force_p95":296.78748,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":523.54481,"mean_force":263.64057,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55711,0.04862,0.33524]},{"body_a":"peg_socket","body_b":"link6","contact_count":699.0,"contact_point_centroid":[0.56994,0.02731,0.07988],"force_p95":312.27902,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":426.56199,"mean_force":273.84446,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46364,0.03076,0.20145]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.57,0.00069,0.07996],"force_p95":263.98818,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":264.88034,"mean_force":255.95873,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.56226,0.03331,0.33312]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.48002,0.00177,0.07998],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46032,0.00541,0.08831]}],"total_contact_groups":10},"final_pose_error":0.18301,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.54965,0.06365,0.33675],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1111.23402,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":694.0,"n_steps_budget":810.0,"object_pos_end":[0.50009,0.02342,0.17826],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10101,"object_to_goal_dist_start":0.26034,"object_z_max":0.34474,"peak_contact_force":295.57643,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":603.0,"raw_peak_contact_force":1111.23402,"subtask_id":"align","tcp_end":[0.46664,0.02336,0.20019],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":784.0,"n_steps_budget":900.0,"object_pos_end":[0.52729,0.07333,0.15086],"object_pos_start":[0.50009,0.02342,0.17826],"object_to_goal_dist_end":0.10556,"object_to_goal_dist_start":0.10101,"object_z_max":0.19307,"peak_contact_force":578.92824,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":732.0,"raw_peak_contact_force":661.99241,"subtask_id":"approach","tcp_end":[0.49305,0.08432,0.1684],"tcp_start":[0.46664,0.02336,0.20019],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2902.0,"n_steps_budget":1000.0,"object_pos_end":[0.51206,0.1354,0.16964],"object_pos_start":[0.52729,0.07333,0.15086],"object_to_goal_dist_end":0.16283,"object_to_goal_dist_start":0.10556,"object_z_max":0.30687,"peak_contact_force":388.4363,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2690.0,"raw_peak_contact_force":771.1559,"subtask_id":"contact","tcp_end":[0.562,0.0344,0.33207],"tcp_start":[0.56068,0.04877,0.33208],"tcp_to_object_dist_end":0.19768,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":10.0,"n_steps_budget":1000.0,"object_pos_end":[0.57652,0.03102,0.29676],"object_pos_start":[0.5776,0.03296,0.29526],"object_to_goal_dist_end":0.23195,"object_to_goal_dist_start":0.23119,"object_z_max":0.29682,"peak_contact_force":264.88034,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":264.88034,"subtask_id":"insert","tcp_end":[0.56269,0.03206,0.33428],"tcp_start":[0.562,0.0344,0.33207],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56279,0.06369,0.29897],"object_pos_start":[0.57652,0.03102,0.29676],"object_to_goal_dist_end":0.23654,"object_to_goal_dist_start":0.23195,"object_z_max":0.29915,"peak_contact_force":249.90583,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":975.0,"raw_peak_contact_force":523.54481,"tcp_end":[0.54965,0.06365,0.33675],"tcp_start":[0.56269,0.03206,0.33428],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```