## Search State

- **Seed**: 5
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | align → approach → contact → insert → retract | arc_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.0264 | 0.85 | ❌ rejected |
| 9 | align → approach → contact → insert → retract | arc_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 11 | 0.1266 | 0.82 | ❌ rejected |
| 8 | align → approach → contact → insert → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 11 | 0.1295 | 0.84 | ❌ rejected |
| 7 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | 0.2275 | 0.87 | ✅ accepted |
| 6 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | force_exceeded | pose_tolerance | 8 | 0.1457 | 0.87 | ✅ accepted |

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

## Current Skill (Q=-0.026) — your mutation base

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

- **Composite score**: -0.026
- **task_score** (E): 0.849
- **fitness_score**: 0.364  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.590

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 0.00 | 1.00 | 0.1501 |
| approach_1 | 0.00 | 1.00 | 0.1209 |
| contact_1 | 1.00 | 1.00 | 0.0026 |
| insert_1 | 0.00 | 1.00 | 0.0011 |
| retract_1 | 0.33 | 0.67 | 0.0563 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.454, 0.012, 0.159) | (0.504, -0.000, 0.340)→(0.493, 0.012, 0.148) | 0.260→0.072 | 1.00 / 1.333 | 242.194 | 1074.203 |
| approach_1 | approach | 0.00 / step_budget | (0.454, 0.012, 0.159)→(0.530, -0.011, 0.249) | (0.493, 0.012, 0.148)→(0.550, -0.016, 0.217) | 0.072→0.149 | 1.00 / 1.000 | 217.800 | 847.700 |
| contact_1 | contact | 1.00 / force_exceeded | (0.531, -0.013, 0.250)→(0.532, -0.015, 0.251) | (0.550, -0.016, 0.217)→(0.550, -0.016, 0.217) | 0.149→0.149 | 1.00 / 1.000 | 407.419 | 427.724 |
| insert_1 | insert | 0.00 / guard_failure | (0.532, -0.015, 0.251)→(0.533, -0.015, 0.251) | (0.552, -0.019, 0.218)→(0.552, -0.020, 0.218) | 0.151→0.151 | 1.00 / 1.000 | 404.530 | 404.530 |
| retract_1 | retract | 0.33 / step_budget | (0.533, -0.015, 0.251)→(0.537, -0.049, 0.235) | (0.552, -0.020, 0.218)→(0.558, -0.048, 0.206) | 0.151→0.148 | 0.67 / 1.333 | 255.352 | 468.091 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.865
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.865
- phase_score: 0.054
- phase_breakdown.align_score: 0.002
- phase_breakdown.insert_score: 0.069
- phase_breakdown.contact_score: 0.058
- phase_breakdown.approach_score: 0.039

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.378
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.865
- **Median Q (composite search score)**: -0.027
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.265


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.90588,"average_solve_count":85.0,"average_success_count":85.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.arc_height":0.13239,"align_1.speed":0.07117,"approach_1.speed":0.02846,"contact_1.contact_force":4.31013,"contact_1.speed":0.01141,"insert_1.insertion_depth":0.03889,"insert_1.speed":0.00663,"retract_1.arc_height":0.04306,"retract_1.retract_height":0.20138,"retract_1.speed":0.09224},"optimized_scores":{"best_composite_score":-0.01152,"best_fitness_score":0.37848,"best_task_score":0.86489},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.46859,0.01442,0.07848],"force_p95":1022.31494,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1077.41735,"mean_force":158.6921,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4643,0.01439,0.09131]},{"body_a":"peg_socket","body_b":"link7","contact_count":90.0,"contact_point_centroid":[0.57482,0.01692,0.07893],"force_p95":563.36122,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":960.49797,"mean_force":307.15305,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46135,0.01678,0.12768]},{"body_a":"world","body_b":"link6","contact_count":27.0,"contact_point_centroid":[0.61158,-0.07236,-0.00041],"force_p95":668.77127,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":670.10268,"mean_force":561.11848,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57978,-0.06701,0.26685]},{"body_a":"peg_socket","body_b":"link6","contact_count":436.0,"contact_point_centroid":[0.58434,-0.03526,0.07996],"force_p95":359.75948,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":531.42164,"mean_force":263.70075,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.56586,-0.03724,0.28261]},{"body_a":"peg_socket","body_b":"link6","contact_count":969.0,"contact_point_centroid":[0.58432,0.02372,0.07986],"force_p95":320.85364,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":488.97178,"mean_force":260.14986,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46903,0.03559,0.1851]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.58408,-0.035,0.07976],"force_p95":392.07129,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":395.07007,"mean_force":369.72151,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.55885,0.004,0.27296]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58416,-0.03508,0.07982],"force_p95":376.85913,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":376.85913,"mean_force":376.85913,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.56101,0.00162,0.27449]},{"body_a":"peg_socket","body_b":"link6","contact_count":88.0,"contact_point_centroid":[0.58435,0.02085,0.07979],"force_p95":291.48709,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":309.0416,"mean_force":258.02041,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46032,0.02041,0.15561]},{"body_a":"peg_socket","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.55419,-0.0054,0.07975],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46162,0.01447,0.09514]}],"total_contact_groups":9},"final_pose_error":0.11395,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.57922,-0.06661,0.26705],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":1077.41735,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":281.0,"n_steps_budget":600.0,"object_pos_end":[0.49476,0.02174,0.14427],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.06805,"object_to_goal_dist_start":0.26034,"object_z_max":0.34533,"peak_contact_force":233.08334,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":201.0,"raw_peak_contact_force":1077.41735,"subtask_id":"align","tcp_end":[0.45569,0.02128,0.15284],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57252,-0.00534,0.2366],"object_pos_start":[0.49476,0.02174,0.14427],"object_to_goal_dist_end":0.17266,"object_to_goal_dist_start":0.06805,"object_z_max":0.23617,"peak_contact_force":214.55515,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":969.0,"raw_peak_contact_force":488.97178,"subtask_id":"approach","tcp_end":[0.55777,0.00518,0.27226],"tcp_start":[0.45569,0.02128,0.15284],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.57337,-0.0064,0.23714],"object_pos_start":[0.57252,-0.00534,0.2366],"object_to_goal_dist_end":0.17354,"object_to_goal_dist_start":0.17266,"object_z_max":0.23776,"peak_contact_force":395.07007,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":395.07007,"subtask_id":"contact","tcp_end":[0.56101,0.00162,0.27449],"tcp_start":[0.55993,0.00281,0.27368],"tcp_to_object_dist_end":0.04016,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.5759,-0.00964,0.23912],"object_pos_start":[0.57506,-0.00853,0.23845],"object_to_goal_dist_end":0.17656,"object_to_goal_dist_start":0.17553,"object_z_max":0.23845,"peak_contact_force":376.85913,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":376.85913,"subtask_id":"insert","tcp_end":[0.56209,0.0004,0.2753],"tcp_start":[0.56101,0.00162,0.27449],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.58783,-0.06789,0.228],"object_pos_start":[0.5759,-0.00964,0.23912],"object_to_goal_dist_end":0.18501,"object_to_goal_dist_start":0.17656,"object_z_max":0.24962,"peak_contact_force":556.53047,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":463.0,"raw_peak_contact_force":670.10268,"tcp_end":[0.57922,-0.06661,0.26705],"tcp_start":[0.56209,0.0004,0.2753],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.07955,"average_solve_count":88.0,"average_success_count":88.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.arc_height":0.1413,"align_1.speed":0.06775,"approach_1.speed":0.02381,"contact_1.contact_force":4.98815,"contact_1.speed":0.00805,"insert_1.insertion_depth":0.04612,"insert_1.speed":0.01394,"retract_1.arc_height":0.03793,"retract_1.retract_height":0.13191,"retract_1.speed":0.06598},"optimized_scores":{"best_composite_score":-0.04055,"best_fitness_score":0.34945,"best_task_score":0.84741},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":738.0,"contact_point_centroid":[0.563,-0.01577,0.07991],"force_p95":319.08638,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1110.0845,"mean_force":282.03929,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46069,-0.01677,0.18748]},{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.45782,-0.00806,0.07853],"force_p95":1028.29963,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1079.62132,"mean_force":229.66974,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45335,-0.00799,0.09137]},{"body_a":"peg_socket","body_b":"link7","contact_count":275.0,"contact_point_centroid":[0.56292,-0.00807,0.07996],"force_p95":264.92844,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1003.87792,"mean_force":259.99928,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45203,-0.01215,0.16459]},{"body_a":"peg_socket","body_b":"link7","contact_count":180.0,"contact_point_centroid":[0.56019,-0.00927,0.07952],"force_p95":436.87701,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":825.83954,"mean_force":282.6149,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45121,-0.01008,0.14506]},{"body_a":"peg_socket","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.56301,-0.02115,0.07995],"force_p95":432.16207,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":436.42405,"mean_force":405.93899,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47571,-0.02485,0.20871]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.56293,-0.02149,0.07985],"force_p95":423.18889,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":423.18889,"mean_force":423.18889,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.47557,-0.02518,0.20885]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.56295,-0.02169,0.07988],"force_p95":118.08045,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":121.94017,"mean_force":95.68032,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47559,-0.02535,0.20896]}],"total_contact_groups":7},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.50132,-0.01188,0.17672],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":1110.0845,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":281.0,"n_steps_budget":600.0,"object_pos_end":[0.49218,-0.01124,0.15077],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.07208,"object_to_goal_dist_start":0.26034,"object_z_max":0.34464,"peak_contact_force":264.29788,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":193.0,"raw_peak_contact_force":1079.62132,"subtask_id":"align","tcp_end":[0.45436,-0.01091,0.16379],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50655,-0.02225,0.18322],"object_pos_start":[0.49218,-0.01124,0.15077],"object_to_goal_dist_end":0.1058,"object_to_goal_dist_start":0.07208,"object_z_max":0.18321,"peak_contact_force":167.17772,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1013.0,"raw_peak_contact_force":1110.0845,"subtask_id":"approach","tcp_end":[0.47574,-0.02468,0.20863],"tcp_start":[0.45436,-0.01091,0.16379],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.50655,-0.02232,0.18326],"object_pos_start":[0.50655,-0.02225,0.18322],"object_to_goal_dist_end":0.10585,"object_to_goal_dist_start":0.1058,"object_z_max":0.18332,"peak_contact_force":436.42405,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":436.42405,"subtask_id":"contact","tcp_end":[0.47557,-0.02518,0.20885],"tcp_start":[0.47563,-0.02506,0.20879],"tcp_to_object_dist_end":0.04028,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50624,-0.02287,0.1834],"object_pos_start":[0.5063,-0.02276,0.18335],"object_to_goal_dist_end":0.10609,"object_to_goal_dist_start":0.10602,"object_z_max":0.18335,"peak_contact_force":423.18889,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":423.18889,"subtask_id":"insert","tcp_end":[0.47553,-0.02529,0.20891],"tcp_start":[0.47557,-0.02518,0.20885],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":110.0,"n_steps_budget":600.0,"object_pos_end":[0.53932,-0.00733,0.1651],"object_pos_start":[0.50624,-0.02287,0.1834],"object_to_goal_dist_end":0.09403,"object_to_goal_dist_start":0.10609,"object_z_max":0.18359,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3.0,"raw_peak_contact_force":121.94017,"tcp_end":[0.50132,-0.01188,0.17672],"tcp_start":[0.47553,-0.02529,0.20891],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.47872,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.arc_height":0.12735,"align_1.speed":0.10149,"approach_1.speed":0.03876,"contact_1.contact_force":5.68189,"contact_1.speed":0.01265,"insert_1.insertion_depth":0.04404,"insert_1.speed":0.01082,"retract_1.arc_height":0.05333,"retract_1.retract_height":0.19594,"retract_1.speed":0.05797},"optimized_scores":{"best_composite_score":-0.02713,"best_fitness_score":0.36287,"best_task_score":0.83579},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.45912,0.01737,0.07859],"force_p95":1014.25393,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1065.56949,"mean_force":169.81983,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45474,0.01732,0.09151]},{"body_a":"peg_socket","body_b":"link7","contact_count":179.0,"contact_point_centroid":[0.56589,0.02082,0.07942],"force_p95":470.55712,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":950.70088,"mean_force":247.60372,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45206,0.02274,0.1453]},{"body_a":"peg_socket","body_b":"link6","contact_count":906.0,"contact_point_centroid":[0.5698,0.02866,0.07946],"force_p95":592.70421,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":944.04391,"mean_force":366.7402,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46873,0.03776,0.17994]},{"body_a":"peg_socket","body_b":"link7","contact_count":631.0,"contact_point_centroid":[0.56899,0.03371,0.07994],"force_p95":557.45372,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":771.39069,"mean_force":266.14365,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45836,0.03367,0.16799]},{"body_a":"world","body_b":"link6","contact_count":154.0,"contact_point_centroid":[0.59267,-0.06788,-9e-05],"force_p95":579.0669,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":612.22966,"mean_force":280.78229,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53148,-0.06966,0.26144]},{"body_a":"peg_socket","body_b":"link6","contact_count":787.0,"contact_point_centroid":[0.56998,-0.02814,0.07998],"force_p95":309.96752,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":514.5962,"mean_force":239.59888,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5362,-0.05027,0.27383]},{"body_a":"peg_socket","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.56997,-0.02815,0.07997],"force_p95":450.37734,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":451.67753,"mean_force":428.79242,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.55711,-0.01541,0.26712]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.56996,-0.02812,0.07997],"force_p95":413.54295,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":413.54295,"mean_force":413.54295,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5599,-0.02039,0.26849]},{"body_a":"peg_socket","body_b":"link6","contact_count":86.0,"contact_point_centroid":[0.56986,0.0266,0.07934],"force_p95":302.94969,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":345.6791,"mean_force":264.7276,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45367,0.02551,0.16258]}],"total_contact_groups":9},"final_pose_error":0.11064,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.53163,-0.06886,0.26152],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1065.56949,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":310.0,"n_steps_budget":600.0,"object_pos_end":[0.49063,0.02677,0.14895],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.07455,"object_to_goal_dist_start":0.26034,"object_z_max":0.34475,"peak_contact_force":229.19981,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":277.0,"raw_peak_contact_force":1065.56949,"subtask_id":"align","tcp_end":[0.45229,0.02611,0.16033],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":936.0,"n_steps_budget":1000.0,"object_pos_end":[0.57103,-0.01949,0.2301],"object_pos_start":[0.49063,0.02677,0.14895],"object_to_goal_dist_end":0.1672,"object_to_goal_dist_start":0.07455,"object_z_max":0.23002,"peak_contact_force":271.66821,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1537.0,"raw_peak_contact_force":944.04391,"subtask_id":"approach","tcp_end":[0.55581,-0.01289,0.2665],"tcp_start":[0.45229,0.02611,0.16033],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.57145,-0.02061,0.23026],"object_pos_start":[0.57103,-0.01949,0.2301],"object_to_goal_dist_end":0.16766,"object_to_goal_dist_start":0.1672,"object_z_max":0.23125,"peak_contact_force":390.76376,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":451.67753,"subtask_id":"contact","tcp_end":[0.5599,-0.02039,0.26849],"tcp_start":[0.55706,-0.01545,0.26708],"tcp_to_object_dist_end":0.03993,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.57418,-0.02759,0.23172],"object_pos_start":[0.57373,-0.02646,0.23145],"object_to_goal_dist_end":0.17112,"object_to_goal_dist_start":0.17051,"object_z_max":0.23145,"peak_contact_force":413.54295,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":413.54295,"subtask_id":"insert","tcp_end":[0.56062,-0.02161,0.26887],"tcp_start":[0.5599,-0.02039,0.26849],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":844.0,"n_steps_budget":960.0,"object_pos_end":[0.54567,-0.06925,0.22407],"object_pos_start":[0.57418,-0.02759,0.23172],"object_to_goal_dist_end":0.16624,"object_to_goal_dist_start":0.17112,"object_z_max":0.2447,"peak_contact_force":209.52665,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":941.0,"raw_peak_contact_force":612.22966,"tcp_end":[0.53163,-0.06886,0.26152],"tcp_start":[0.56062,-0.02161,0.26887],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```