## Search State

- **Seed**: 5
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | 0.2275 | 0.87 | ✅ accepted |
| 6 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | force_exceeded | pose_tolerance | 8 | 0.1457 | 0.87 | ✅ accepted |
| 5 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.0893 | 0.87 | ❌ rejected |
| 4 | align → approach → contact → insert → retract | arc_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.0600 | 0.84 | ❌ rejected |
| 3 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.0893 | 0.87 | ❌ rejected |

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

## Current Skill (Q=0.228) — your mutation base

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
    contact_force:
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
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
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

- **Composite score**: 0.228
- **task_score** (E): 0.873
- **fitness_score**: 0.368  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.400
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 0.33 | 1.00 | 0.1137 |
| approach_1 | 0.00 | 1.00 | 0.1014 |
| contact_1 | 1.00 | 1.00 | 0.0055 |
| insert_1 | 1.00 | 1.00 | 0.0008 |
| retract_1 | 0.33 | 1.00 | 0.0471 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.468, 0.012, 0.193) | (0.504, -0.000, 0.340)→(0.503, 0.012, 0.173) | 0.260→0.095 | 1.00 / 1.000 | 296.065 | 1256.059 |
| approach_1 | approach | 0.00 / step_budget | (0.468, 0.012, 0.193)→(0.543, -0.029, 0.244) | (0.503, 0.012, 0.173)→(0.562, -0.032, 0.211) | 0.095→0.151 | 1.00 / 1.333 | 283.881 | 565.239 |
| contact_1 | contact | 1.00 / force_exceeded | (0.544, -0.032, 0.244)→(0.544, -0.037, 0.245) | (0.562, -0.032, 0.211)→(0.562, -0.034, 0.211) | 0.151→0.151 | 1.00 / 1.000 | 269.166 | 622.498 |
| insert_1 | insert | 1.00 / force_exceeded | (0.544, -0.037, 0.245)→(0.544, -0.038, 0.246) | (0.562, -0.040, 0.212)→(0.562, -0.040, 0.212) | 0.153→0.153 | 1.00 / 1.000 | 303.600 | 303.600 |
| retract_1 | retract | 0.33 / step_budget | (0.544, -0.038, 0.246)→(0.528, -0.055, 0.227) | (0.562, -0.040, 0.212)→(0.548, -0.053, 0.197) | 0.153→0.140 | 1.00 / 1.667 | 166.897 | 334.447 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.881
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.881
- phase_score: 0.043
- phase_breakdown.align_score: 0.004
- phase_breakdown.insert_score: 0.053
- phase_breakdown.contact_score: 0.045
- phase_breakdown.approach_score: 0.035

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.378
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.881
- **Median Q (composite search score)**: 0.227
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.303


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.70588,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06859,"contact_1.contact_force":7.47491,"contact_1.speed":0.01964,"insert_1.bottom_force":16.23987,"insert_1.insertion_depth":0.04016,"insert_1.speed":0.02553,"retract_1.arc_height":0.04134,"retract_1.retract_height":0.12135,"retract_1.speed":0.04562},"optimized_scores":{"best_composite_score":0.23806,"best_fitness_score":0.37806,"best_task_score":0.88092},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":15.0,"contact_point_centroid":[0.47001,0.00483,0.07785],"force_p95":1076.69711,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1122.95484,"mean_force":208.92235,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46525,0.00479,0.08991]},{"body_a":"peg_socket","body_b":"link7","contact_count":185.0,"contact_point_centroid":[0.5796,0.01064,0.07951],"force_p95":413.05054,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":838.23761,"mean_force":279.19128,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46503,0.00726,0.13827]},{"body_a":"peg_socket","body_b":"link6","contact_count":650.0,"contact_point_centroid":[0.58425,0.01556,0.07979],"force_p95":413.24341,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":595.5801,"mean_force":282.54539,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48232,0.03132,0.20794]},{"body_a":"peg_socket","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.56738,-0.03531,0.07999],"force_p95":358.90552,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":362.20581,"mean_force":305.25858,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.56393,-0.05796,0.27801]},{"body_a":"peg_socket","body_b":"link6","contact_count":960.0,"contact_point_centroid":[0.54787,-0.0353,0.08],"force_p95":228.00001,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":345.31479,"mean_force":173.46679,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5435,-0.07632,0.2695]},{"body_a":"peg_socket","body_b":"link6","contact_count":403.0,"contact_point_centroid":[0.58434,0.01256,0.07982],"force_p95":309.6776,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":335.37673,"mean_force":257.21423,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46375,0.01434,0.17119]},{"body_a":"world","body_b":"link6","contact_count":409.0,"contact_point_centroid":[0.58636,-0.09254,-4e-05],"force_p95":217.95448,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":278.93757,"mean_force":170.85129,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53597,-0.08103,0.2649]},{"body_a":"peg_socket","body_b":"link6","contact_count":145.0,"contact_point_centroid":[0.555,-0.03522,0.07999],"force_p95":204.91832,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":222.57518,"mean_force":118.91136,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55771,-0.06645,0.27501]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.55911,-0.03526,0.07999],"force_p95":188.31229,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":188.31229,"mean_force":188.31229,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.56467,-0.06284,0.27738]},{"body_a":"peg_socket","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.55435,-0.00537,0.07993],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46257,0.0048,0.09246]}],"total_contact_groups":10},"final_pose_error":0.15971,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.53454,-0.08202,0.26479],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":1122.95484,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":695.0,"n_steps_budget":840.0,"object_pos_end":[0.51208,0.02079,0.17554],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09852,"object_to_goal_dist_start":0.26034,"object_z_max":0.34492,"peak_contact_force":306.36852,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":609.0,"raw_peak_contact_force":1122.95484,"subtask_id":"align","tcp_end":[0.47798,0.0213,0.19646],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.57577,-0.05955,0.24072],"object_pos_start":[0.51208,0.02079,0.17554],"object_to_goal_dist_end":0.1874,"object_to_goal_dist_start":0.09852,"object_z_max":0.24931,"peak_contact_force":327.19707,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":650.0,"raw_peak_contact_force":595.5801,"subtask_id":"approach","tcp_end":[0.56368,-0.05495,0.27857],"tcp_start":[0.47798,0.0213,0.19646],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":10.0,"n_steps_budget":1000.0,"object_pos_end":[0.5755,-0.06181,0.23996],"object_pos_start":[0.57577,-0.05955,0.24072],"object_to_goal_dist_end":0.18737,"object_to_goal_dist_start":0.1874,"object_z_max":0.24072,"peak_contact_force":159.0793,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":362.20581,"subtask_id":"contact","tcp_end":[0.56467,-0.06284,0.27738],"tcp_start":[0.5639,-0.05843,0.2779],"tcp_to_object_dist_end":0.03897,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.57478,-0.06712,0.23876],"object_pos_start":[0.57486,-0.06656,0.23888],"object_to_goal_dist_end":0.18788,"object_to_goal_dist_start":0.18782,"object_z_max":0.23888,"peak_contact_force":188.31229,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":188.31229,"subtask_id":"insert","tcp_end":[0.56479,-0.06347,0.27732],"tcp_start":[0.56467,-0.06284,0.27738],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54649,-0.08332,0.22665],"object_pos_start":[0.57478,-0.06712,0.23876],"object_to_goal_dist_end":0.17495,"object_to_goal_dist_start":0.18788,"object_z_max":0.23876,"peak_contact_force":165.43879,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1514.0,"raw_peak_contact_force":345.31479,"tcp_end":[0.53454,-0.08202,0.26479],"tcp_start":[0.56479,-0.06347,0.27732],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.03297,"average_solve_count":91.0,"average_success_count":91.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07427,"contact_1.contact_force":5.61977,"contact_1.speed":0.0137,"insert_1.bottom_force":26.13863,"insert_1.insertion_depth":0.03985,"insert_1.speed":0.01757,"retract_1.arc_height":0.04529,"retract_1.retract_height":0.11333,"retract_1.speed":0.03552},"optimized_scores":{"best_composite_score":0.21748,"best_fitness_score":0.35748,"best_task_score":0.87287},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":504.0,"contact_point_centroid":[0.56226,-0.00307,0.07969],"force_p95":321.95801,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1533.98864,"mean_force":279.66028,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45805,-0.00535,0.15833]},{"body_a":"attachment","body_b":"peg_socket","contact_count":16.0,"contact_point_centroid":[0.46198,-0.00404,0.07713],"force_p95":953.98815,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1062.00065,"mean_force":123.74904,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45751,-0.00266,0.08807]},{"body_a":"peg_socket","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.56297,-0.02144,0.07989],"force_p95":492.31519,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":498.27487,"mean_force":448.51052,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48285,-0.02149,0.19525]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.56287,-0.02187,0.07976],"force_p95":441.7725,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":441.7725,"mean_force":441.7725,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48256,-0.02198,0.19539]},{"body_a":"peg_socket","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.56289,-0.0205,0.07982],"force_p95":426.19498,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":427.40757,"mean_force":307.06286,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48258,-0.02028,0.19568]},{"body_a":"peg_socket","body_b":"link6","contact_count":514.0,"contact_point_centroid":[0.563,-0.01104,0.07992],"force_p95":308.48887,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":413.38929,"mean_force":274.77115,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4637,-0.01114,0.18984]},{"body_a":"peg_socket","body_b":"link6","contact_count":63.0,"contact_point_centroid":[0.56292,-0.00984,0.07971],"force_p95":316.79492,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":351.09639,"mean_force":285.83952,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45866,-0.0085,0.17965]},{"body_a":"peg_socket","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.56301,-0.01133,0.07994],"force_p95":231.83032,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":282.06085,"mean_force":119.66482,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48669,-0.01356,0.17722]}],"total_contact_groups":8},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.49264,-0.00447,0.15314],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":1533.98864,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":665.0,"n_steps_budget":810.0,"object_pos_end":[0.49635,-0.00876,0.16433],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08486,"object_to_goal_dist_start":0.26034,"object_z_max":0.34481,"peak_contact_force":286.25074,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":583.0,"raw_peak_contact_force":1533.98864,"subtask_id":"align","tcp_end":[0.46086,-0.00886,0.18277],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.51502,-0.01975,0.17106],"object_pos_start":[0.49635,-0.00876,0.16433],"object_to_goal_dist_end":0.09438,"object_to_goal_dist_start":0.08486,"object_z_max":0.18077,"peak_contact_force":251.5794,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":528.0,"raw_peak_contact_force":427.40757,"subtask_id":"approach","tcp_end":[0.48308,-0.02097,0.19511],"tcp_start":[0.46086,-0.00886,0.18277],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.51465,-0.02049,0.17116],"object_pos_start":[0.51502,-0.01975,0.17106],"object_to_goal_dist_end":0.09457,"object_to_goal_dist_start":0.09438,"object_z_max":0.17121,"peak_contact_force":454.67736,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":498.27487,"subtask_id":"contact","tcp_end":[0.48256,-0.02198,0.19539],"tcp_start":[0.48266,-0.02183,0.19533],"tcp_to_object_dist_end":0.04024,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51432,-0.02094,0.17129],"object_pos_start":[0.51441,-0.02079,0.17123],"object_to_goal_dist_end":0.09475,"object_to_goal_dist_start":0.09467,"object_z_max":0.17123,"peak_contact_force":441.7725,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":441.7725,"subtask_id":"insert","tcp_end":[0.48247,-0.02212,0.19547],"tcp_start":[0.48256,-0.02198,0.19539],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":115.0,"n_steps_budget":1000.0,"object_pos_end":[0.53001,-0.0015,0.1392],"object_pos_start":[0.51432,-0.02094,0.17129],"object_to_goal_dist_end":0.06638,"object_to_goal_dist_start":0.09475,"object_z_max":0.17157,"peak_contact_force":93.15796,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":16.0,"raw_peak_contact_force":282.06085,"tcp_end":[0.49264,-0.00447,0.15314],"tcp_start":[0.48247,-0.02212,0.19547],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.59615,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04813,"contact_1.contact_force":3.34926,"contact_1.speed":0.01587,"insert_1.bottom_force":24.14599,"insert_1.insertion_depth":0.05164,"insert_1.speed":0.01631,"retract_1.arc_height":0.04028,"retract_1.retract_height":0.14142,"retract_1.speed":0.08409},"optimized_scores":{"best_composite_score":0.22702,"best_fitness_score":0.36702,"best_task_score":0.86575},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":14.0,"contact_point_centroid":[0.46452,0.00549,0.07795],"force_p95":1064.88456,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1111.23402,"mean_force":220.97201,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4598,0.00545,0.09013]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.56984,-0.02798,0.07996],"force_p95":1004.59623,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1007.01262,"mean_force":790.93727,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.58369,-0.01339,0.25942]},{"body_a":"peg_socket","body_b":"link7","contact_count":250.0,"contact_point_centroid":[0.56776,0.01361,0.07961],"force_p95":374.82501,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":836.10761,"mean_force":288.50796,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45974,0.00987,0.14954]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.62908,-0.05448,-0.00023],"force_p95":788.16544,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":812.56347,"mean_force":477.15932,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.58382,-0.01451,0.25976]},{"body_a":"world","body_b":"link6","contact_count":9.0,"contact_point_centroid":[0.64104,-0.04555,-0.00033],"force_p95":664.72109,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":672.73051,"mean_force":463.05496,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.57964,0.00045,0.25571]},{"body_a":"peg_socket","body_b":"link6","contact_count":916.0,"contact_point_centroid":[0.5699,0.02523,0.07988],"force_p95":328.93179,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":648.62894,"mean_force":275.38921,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46727,0.03373,0.20292]},{"body_a":"peg_socket","body_b":"link6","contact_count":338.0,"contact_point_centroid":[0.56992,0.0178,0.0798],"force_p95":309.8557,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":547.4356,"mean_force":270.42116,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4555,0.0191,0.17946]},{"body_a":"peg_socket","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.56996,0.05318,0.07992],"force_p95":437.14297,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":500.06937,"mean_force":336.73872,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48863,0.08258,0.1902]},{"body_a":"peg_socket","body_b":"link6","contact_count":861.0,"contact_point_centroid":[0.56999,-0.02815,0.06191],"force_p95":283.85603,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":375.96461,"mean_force":201.41796,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55784,-0.07491,0.26391]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.56997,-0.02813,0.07998],"force_p95":280.71667,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":280.71667,"mean_force":280.71667,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.58475,-0.02677,0.26372]},{"body_a":"peg_socket","body_b":"link6","contact_count":194.0,"contact_point_centroid":[0.57001,-0.02821,0.05],"force_p95":106.13102,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":252.7232,"mean_force":79.98561,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54882,-0.08744,0.26112]},{"body_a":"world","body_b":"link6","contact_count":539.0,"contact_point_centroid":[0.61561,-0.07059,-3e-05],"force_p95":155.96611,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":239.78965,"mean_force":108.36772,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55127,-0.08471,0.26163]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.48002,0.00177,0.07998],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46032,0.00541,0.08831]}],"total_contact_groups":13},"final_pose_error":0.15315,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.55624,-0.07714,0.26367],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1111.23402,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":694.0,"n_steps_budget":810.0,"object_pos_end":[0.50009,0.02342,0.17826],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10101,"object_to_goal_dist_start":0.26034,"object_z_max":0.34474,"peak_contact_force":295.57643,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":603.0,"raw_peak_contact_force":1111.23402,"subtask_id":"align","tcp_end":[0.46664,0.02336,0.20019],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":995.0,"n_steps_budget":1000.0,"object_pos_end":[0.59536,-0.01768,0.22121],"object_pos_start":[0.50009,0.02342,0.17826],"object_to_goal_dist_end":0.17131,"object_to_goal_dist_start":0.10101,"object_z_max":0.22069,"peak_contact_force":272.86638,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":956.0,"raw_peak_contact_force":672.73051,"subtask_id":"approach","tcp_end":[0.58335,-0.01111,0.2588],"tcp_start":[0.46664,0.02336,0.20019],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.59564,-0.01968,0.22175],"object_pos_start":[0.59536,-0.01768,0.22121],"object_to_goal_dist_end":0.17212,"object_to_goal_dist_start":0.17131,"object_z_max":0.22531,"peak_contact_force":193.74071,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":7.0,"raw_peak_contact_force":1007.01262,"subtask_id":"contact","tcp_end":[0.58475,-0.02677,0.26372],"tcp_start":[0.58399,-0.01566,0.26005],"tcp_to_object_dist_end":0.04394,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.59594,-0.03246,0.22586],"object_pos_start":[0.59595,-0.03124,0.22558],"object_to_goal_dist_end":0.17758,"object_to_goal_dist_start":0.17713,"object_z_max":0.22558,"peak_contact_force":280.71667,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":280.71667,"subtask_id":"insert","tcp_end":[0.58492,-0.02821,0.26408],"tcp_start":[0.58475,-0.02677,0.26372],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.56881,-0.07487,0.22576],"object_pos_start":[0.59594,-0.03246,0.22586],"object_to_goal_dist_end":0.17773,"object_to_goal_dist_start":0.17758,"object_z_max":0.23182,"peak_contact_force":242.09506,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1594.0,"raw_peak_contact_force":375.96461,"tcp_end":[0.55624,-0.07714,0.26367],"tcp_start":[0.58492,-0.02821,0.26408],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```