## Search State

- **Seed**: 5
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → approach → contact → insert → retract | arc_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.0043 | 0.82 | ❌ rejected |
| 11 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.0815 | 0.86 | ❌ rejected |
| 10 | align → approach → contact → insert → retract | arc_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.0264 | 0.85 | ❌ rejected |
| 9 | align → approach → contact → insert → retract | arc_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 11 | 0.1266 | 0.82 | ❌ rejected |
| 8 | align → approach → contact → insert → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 11 | 0.1295 | 0.84 | ❌ rejected |

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

## Current Skill (Q=-0.004) — your mutation base

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

- **Composite score**: -0.004
- **task_score** (E): 0.819
- **fitness_score**: 0.386  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.590

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| lateral_approach | 0.00 | 1.00 | 0.1304 |
| vertical_descent | 0.00 | 1.00 | 0.1161 |
| probe_hole | 1.00 | 1.00 | 0.0019 |
| insert_into_hole | 0.00 | 0.67 | 0.1184 |
| retract_peg | 0.00 | 1.00 | 0.0382 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| lateral_approach | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.450, 0.038, 0.188) | (0.504, -0.000, 0.340)→(0.486, 0.036, 0.171) | 0.260→0.099 | 1.00 / 1.333 | 238.739 | 1087.129 |
| vertical_descent | approach | 0.00 / step_budget | (0.450, 0.038, 0.188)→(0.507, 0.078, 0.245) | (0.486, 0.036, 0.171)→(0.531, 0.064, 0.218) | 0.099→0.175 | 1.00 / 1.000 | 290.361 | 473.879 |
| probe_hole | contact | 1.00 / force_exceeded | (0.508, 0.076, 0.246)→(0.509, 0.075, 0.247) | (0.531, 0.064, 0.218)→(0.531, 0.063, 0.218) | 0.175→0.175 | 1.00 / 1.000 | 370.165 | 400.106 |
| insert_into_hole | insert | 0.00 / step_budget | (0.509, 0.075, 0.247)→(0.535, -0.004, 0.328) | (0.532, 0.061, 0.219)→(0.548, -0.005, 0.290) | 0.177→0.223 | 0.67 / 0.667 | 170.910 | 515.099 |
| retract_peg | retract | 0.00 / step_budget | (0.535, -0.004, 0.328)→(0.544, 0.030, 0.328) | (0.548, -0.005, 0.290)→(0.557, 0.027, 0.291) | 0.223→0.233 | 1.00 / 1.000 | 284.605 | 318.898 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.820
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.820
- phase_score: 0.121
- phase_breakdown.align_score: 0.003
- phase_breakdown.insert_score: 0.232
- phase_breakdown.contact_score: 0.013
- phase_breakdown.approach_score: 0.009

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.401
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.846
- **Median Q (composite search score)**: -0.009
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.333


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.97661,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"insert_into_hole.insertion_depth":0.0419,"insert_into_hole.speed":0.00806,"lateral_approach.arc_height":0.06622,"lateral_approach.speed":0.03378,"probe_hole.contact_force":16.8275,"probe_hole.speed":0.01316,"retract_peg.arc_height":0.08777,"retract_peg.retract_height":0.11059,"retract_peg.speed":0.05415,"vertical_descent.speed":0.01567},"optimized_scores":{"best_composite_score":0.01055,"best_fitness_score":0.40055,"best_task_score":0.82034},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.55476,0.01626,0.07794],"force_p95":650.91148,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1112.30362,"mean_force":155.57731,"phase_index":0.0,"phase_name":"lateral_approach","phase_type":"approach","tcp_position_centroid":[0.44221,0.01807,0.10368]},{"body_a":"peg_socket","body_b":"link6","contact_count":944.0,"contact_point_centroid":[0.57307,0.053,0.07991],"force_p95":437.3945,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":477.87631,"mean_force":323.65791,"phase_index":3.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.51339,0.07599,0.33144]},{"body_a":"peg_socket","body_b":"link6","contact_count":989.0,"contact_point_centroid":[0.58434,0.03807,0.07989],"force_p95":303.14034,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":454.36577,"mean_force":263.87749,"phase_index":1.0,"phase_name":"vertical_descent","phase_type":"approach","tcp_position_centroid":[0.45229,0.08716,0.19439]},{"body_a":"peg_socket","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.53828,-0.0057,0.07778],"force_p95":293.13731,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":436.6771,"mean_force":50.35197,"phase_index":0.0,"phase_name":"lateral_approach","phase_type":"approach","tcp_position_centroid":[0.44175,0.01799,0.10033]},{"body_a":"peg_socket","body_b":"link6","contact_count":890.0,"contact_point_centroid":[0.58426,0.02837,0.07989],"force_p95":257.48988,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":408.06123,"mean_force":238.47086,"phase_index":0.0,"phase_name":"lateral_approach","phase_type":"approach","tcp_position_centroid":[0.44135,0.0315,0.16097]},{"body_a":"peg_socket","body_b":"link6","contact_count":967.0,"contact_point_centroid":[0.57862,0.07856,0.07991],"force_p95":346.88502,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":404.96626,"mean_force":312.60389,"phase_index":4.0,"phase_name":"retract_peg","phase_type":"retract","tcp_position_centroid":[0.50443,0.07817,0.33504]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.58432,0.04523,0.07991],"force_p95":326.31065,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":326.47223,"mean_force":324.67777,"phase_index":2.0,"phase_name":"probe_hole","phase_type":"contact","tcp_position_centroid":[0.48204,0.11937,0.22544]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.46444,0.01775,0.07986],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"lateral_approach","phase_type":"approach","tcp_position_centroid":[0.44759,0.01765,0.09022]}],"total_contact_groups":8},"final_pose_error":0.21901,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.5183,0.11498,0.33501],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":1112.30362,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48776,0.04078,0.17129],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10073,"object_to_goal_dist_start":0.26034,"object_z_max":0.34443,"peak_contact_force":242.85093,"phase_name":"lateral_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":958.0,"raw_peak_contact_force":1112.30362,"subtask_id":"align","tcp_end":[0.45127,0.04274,0.18757],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50988,0.10335,0.20153],"object_pos_start":[0.48776,0.04078,0.17129],"object_to_goal_dist_end":0.15984,"object_to_goal_dist_start":0.10073,"object_z_max":0.20277,"peak_contact_force":287.62556,"phase_name":"vertical_descent","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":989.0,"raw_peak_contact_force":454.36577,"subtask_id":"approach","tcp_end":[0.48206,0.11927,0.22547],"tcp_start":[0.45127,0.04274,0.18757],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50985,0.10342,0.20151],"object_pos_start":[0.50988,0.10335,0.20153],"object_to_goal_dist_end":0.15987,"object_to_goal_dist_start":0.15984,"object_z_max":0.20153,"peak_contact_force":322.70467,"phase_name":"probe_hole","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":326.47223,"subtask_id":"contact","tcp_end":[0.48206,0.11962,0.22543],"tcp_start":[0.48204,0.11948,0.22541],"tcp_to_object_dist_end":0.04009,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50676,0.04234,0.29741],"object_pos_start":[0.50986,0.10358,0.20155],"object_to_goal_dist_end":0.2216,"object_to_goal_dist_start":0.16,"object_z_max":0.30336,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":944.0,"raw_peak_contact_force":477.87631,"subtask_id":"insert","tcp_end":[0.49016,0.0361,0.33327],"tcp_start":[0.48206,0.11962,0.22543],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5326,0.11564,0.29766],"object_pos_start":[0.50676,0.04234,0.29741],"object_to_goal_dist_end":0.24862,"object_to_goal_dist_start":0.2216,"object_z_max":0.29987,"peak_contact_force":349.28067,"phase_name":"retract_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":967.0,"raw_peak_contact_force":404.96626,"tcp_end":[0.5183,0.11498,0.33501],"tcp_start":[0.49016,0.0361,0.33327],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.19863,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"insert_into_hole.insertion_depth":0.02016,"insert_into_hole.speed":0.0096,"lateral_approach.arc_height":0.05806,"lateral_approach.speed":0.07973,"probe_hole.contact_force":8.42161,"probe_hole.speed":0.01216,"retract_peg.arc_height":0.06967,"retract_peg.retract_height":0.05215,"retract_peg.speed":0.03039,"vertical_descent.speed":0.02901},"optimized_scores":{"best_composite_score":-0.00909,"best_fitness_score":0.38091,"best_task_score":0.84564},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.46289,0.01505,0.07835],"force_p95":1047.91517,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1094.68509,"mean_force":294.63673,"phase_index":0.0,"phase_name":"lateral_approach","phase_type":"approach","tcp_position_centroid":[0.45814,0.015,0.0909]},{"body_a":"peg_socket","body_b":"link6","contact_count":131.0,"contact_point_centroid":[0.56288,0.0137,0.0792],"force_p95":988.35318,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1050.3352,"mean_force":362.35245,"phase_index":0.0,"phase_name":"lateral_approach","phase_type":"approach","tcp_position_centroid":[0.45527,0.01375,0.17328]},{"body_a":"peg_socket","body_b":"link7","contact_count":375.0,"contact_point_centroid":[0.56176,0.01777,0.07975],"force_p95":627.12759,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":932.48294,"mean_force":304.28005,"phase_index":0.0,"phase_name":"lateral_approach","phase_type":"approach","tcp_position_centroid":[0.45712,0.01617,0.16041]},{"body_a":"peg_socket","body_b":"link6","contact_count":964.0,"contact_point_centroid":[0.56295,0.00884,0.07988],"force_p95":376.63207,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":648.16453,"mean_force":290.98396,"phase_index":1.0,"phase_name":"vertical_descent","phase_type":"approach","tcp_position_centroid":[0.46542,0.04388,0.18758]},{"body_a":"peg_socket","body_b":"link6","contact_count":985.0,"contact_point_centroid":[0.56303,-0.07249,0.07996],"force_p95":290.3328,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":588.39005,"mean_force":257.65622,"phase_index":3.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.58172,-0.07106,0.32512]},{"body_a":"peg_socket","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.56301,-0.07248,0.07997],"force_p95":551.30158,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":553.96403,"mean_force":512.36027,"phase_index":2.0,"phase_name":"probe_hole","phase_type":"contact","tcp_position_centroid":[0.57056,-0.02678,0.29269]},{"body_a":"peg_socket","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.56161,0.00939,0.07993],"force_p95":454.1166,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":460.28644,"mean_force":279.48919,"phase_index":1.0,"phase_name":"vertical_descent","phase_type":"approach","tcp_position_centroid":[0.45342,0.01922,0.17111]},{"body_a":"peg_socket","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.56304,-0.0725,0.07997],"force_p95":253.51075,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":255.78092,"mean_force":248.30854,"phase_index":4.0,"phase_name":"retract_peg","phase_type":"retract","tcp_position_centroid":[0.56902,-0.06643,0.32651]},{"body_a":"attachment","body_b":"peg_socket","contact_count":8.0,"contact_point_centroid":[0.47318,0.01753,0.07965],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"lateral_approach","phase_type":"approach","tcp_position_centroid":[0.4601,0.01495,0.09033]}],"total_contact_groups":9},"final_pose_error":0.26312,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.56712,-0.0667,0.32654],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":1094.68509,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":485.0,"n_steps_budget":630.0,"object_pos_end":[0.49091,0.0141,0.15645],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.07827,"object_to_goal_dist_start":0.26034,"object_z_max":0.34456,"peak_contact_force":217.61112,"phase_name":"lateral_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":527.0,"raw_peak_contact_force":1094.68509,"subtask_id":"align","tcp_end":[0.45389,0.01546,0.17155],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58485,-0.03117,0.25549],"object_pos_start":[0.49091,0.0141,0.15645],"object_to_goal_dist_end":0.1974,"object_to_goal_dist_start":0.07827,"object_z_max":0.25529,"peak_contact_force":291.69326,"phase_name":"vertical_descent","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1000.0,"raw_peak_contact_force":648.16453,"subtask_id":"approach","tcp_end":[0.56898,-0.02278,0.29123],"tcp_start":[0.45389,0.01546,0.17155],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.58524,-0.03254,0.25581],"object_pos_start":[0.58485,-0.03117,0.25549],"object_to_goal_dist_end":0.19807,"object_to_goal_dist_start":0.1974,"object_z_max":0.25861,"peak_contact_force":472.20661,"phase_name":"probe_hole","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":553.96403,"subtask_id":"contact","tcp_end":[0.57315,-0.03269,0.29554],"tcp_start":[0.57113,-0.02822,0.2931],"tcp_to_object_dist_end":0.04153,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58214,-0.06971,0.28757],"object_pos_start":[0.58774,-0.04046,0.25911],"object_to_goal_dist_end":0.23387,"object_to_goal_dist_start":0.20351,"object_z_max":0.28757,"peak_contact_force":254.49358,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":985.0,"raw_peak_contact_force":588.39005,"subtask_id":"insert","tcp_end":[0.57356,-0.06579,0.32645],"tcp_start":[0.57315,-0.03269,0.29554],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57672,-0.07021,0.28786],"object_pos_start":[0.58214,-0.06971,0.28757],"object_to_goal_dist_end":0.23243,"object_to_goal_dist_start":0.23387,"object_z_max":0.28787,"peak_contact_force":252.8822,"phase_name":"retract_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1000.0,"raw_peak_contact_force":255.78092,"tcp_end":[0.56712,-0.0667,0.32654],"tcp_start":[0.57356,-0.06579,0.32645],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.65294,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"insert_into_hole.insertion_depth":0.03906,"insert_into_hole.speed":0.00742,"lateral_approach.arc_height":0.04069,"lateral_approach.speed":0.04166,"probe_hole.contact_force":17.626,"probe_hole.speed":0.01061,"retract_peg.arc_height":0.09356,"retract_peg.retract_height":0.07218,"retract_peg.speed":0.01898,"vertical_descent.speed":0.01661},"optimized_scores":{"best_composite_score":-0.01443,"best_fitness_score":0.37557,"best_task_score":0.79113},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":255.0,"contact_point_centroid":[0.56524,0.02921,0.0796],"force_p95":664.78463,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1054.39772,"mean_force":216.65786,"phase_index":0.0,"phase_name":"lateral_approach","phase_type":"approach","tcp_position_centroid":[0.44177,0.02302,0.13946]},{"body_a":"peg_socket","body_b":"link6","contact_count":869.0,"contact_point_centroid":[0.56997,0.04242,0.07992],"force_p95":290.06676,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1016.94088,"mean_force":243.93988,"phase_index":0.0,"phase_name":"lateral_approach","phase_type":"approach","tcp_position_centroid":[0.43673,0.04107,0.17243]},{"body_a":"peg_socket","body_b":"link7","contact_count":26.0,"contact_point_centroid":[0.52866,0.00148,0.07795],"force_p95":443.08804,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":484.30713,"mean_force":70.6924,"phase_index":0.0,"phase_name":"lateral_approach","phase_type":"approach","tcp_position_centroid":[0.4325,0.02264,0.10344]},{"body_a":"peg_socket","body_b":"link6","contact_count":994.0,"contact_point_centroid":[0.56997,-0.02617,0.07994],"force_p95":286.9734,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":479.03099,"mean_force":262.47536,"phase_index":3.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.53902,0.02313,0.31678]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.56999,0.05641,0.07998],"force_p95":319.6857,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":319.88095,"mean_force":317.79778,"phase_index":2.0,"phase_name":"probe_hole","phase_type":"contact","tcp_position_centroid":[0.47013,0.13734,0.21965]},{"body_a":"peg_socket","body_b":"link6","contact_count":997.0,"contact_point_centroid":[0.56997,0.04764,0.07992],"force_p95":290.33419,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":319.10808,"mean_force":267.60185,"phase_index":1.0,"phase_name":"vertical_descent","phase_type":"approach","tcp_position_centroid":[0.43843,0.09497,0.19729]},{"body_a":"peg_socket","body_b":"link6","contact_count":993.0,"contact_point_centroid":[0.56999,-0.02817,0.07994],"force_p95":259.66473,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":295.94575,"mean_force":248.49649,"phase_index":4.0,"phase_name":"retract_peg","phase_type":"retract","tcp_position_centroid":[0.54528,0.0289,0.32286]}],"total_contact_groups":7},"final_pose_error":0.2298,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.54802,0.04049,0.32364],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1054.39772,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48051,0.05372,0.18391],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.11858,"object_to_goal_dist_start":0.26034,"object_z_max":0.34416,"peak_contact_force":255.75549,"phase_name":"lateral_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1150.0,"raw_peak_contact_force":1054.39772,"subtask_id":"align","tcp_end":[0.4461,0.05502,0.20426],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49743,0.11901,0.19688],"object_pos_start":[0.48051,0.05372,0.18391],"object_to_goal_dist_end":0.16683,"object_to_goal_dist_start":0.11858,"object_z_max":0.19682,"peak_contact_force":291.76376,"phase_name":"vertical_descent","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":997.0,"raw_peak_contact_force":319.10808,"subtask_id":"approach","tcp_end":[0.47001,0.13729,0.21956],"tcp_start":[0.4461,0.05502,0.20426],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.4975,0.11903,0.19695],"object_pos_start":[0.49743,0.11901,0.19688],"object_to_goal_dist_end":0.16689,"object_to_goal_dist_start":0.16683,"object_z_max":0.19704,"peak_contact_force":315.58389,"phase_name":"probe_hole","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":319.88095,"subtask_id":"contact","tcp_end":[0.47042,0.13747,0.21988],"tcp_start":[0.47025,0.13739,0.21975],"tcp_to_object_dist_end":0.03999,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55622,0.01288,0.28616],"object_pos_start":[0.49772,0.11907,0.19715],"object_to_goal_dist_end":0.21408,"object_to_goal_dist_start":0.16706,"object_z_max":0.28616,"peak_contact_force":258.23641,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":994.0,"raw_peak_contact_force":479.03099,"subtask_id":"insert","tcp_end":[0.54076,0.01722,0.3228],"tcp_start":[0.47042,0.13747,0.21988],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56217,0.03492,0.28664],"object_pos_start":[0.55622,0.01288,0.28616],"object_to_goal_dist_end":0.2186,"object_to_goal_dist_start":0.21408,"object_z_max":0.28666,"peak_contact_force":251.65283,"phase_name":"retract_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":993.0,"raw_peak_contact_force":295.94575,"tcp_end":[0.54802,0.04049,0.32364],"tcp_start":[0.54076,0.01722,0.3228],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```