## Search State

- **Seed**: 5
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | align → approach → contact → insert → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 11 | 0.1295 | 0.84 | ❌ rejected |
| 7 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | 0.2275 | 0.87 | ✅ accepted |
| 6 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | force_exceeded | pose_tolerance | 8 | 0.1457 | 0.87 | ✅ accepted |
| 5 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.0893 | 0.87 | ❌ rejected |
| 4 | align → approach → contact → insert → retract | arc_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | -0.0600 | 0.84 | ❌ rejected |

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

## Current Skill (Q=0.129) — your mutation base

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

- **Composite score**: 0.129
- **task_score** (E): 0.845
- **fitness_score**: 0.369  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.400
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.640

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 0.00 | 1.00 | 0.1163 |
| approach_1 | 0.00 | 1.00 | 0.1488 |
| contact_1 | 1.00 | 1.00 | 0.0029 |
| insert_1 | 1.00 | 1.00 | 0.0054 |
| retract_1 | 0.00 | 1.00 | 0.0598 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.458, 0.025, 0.196) | (0.504, -0.000, 0.340)→(0.492, 0.024, 0.176) | 0.260→0.100 | 1.00 / 1.000 | 266.342 | 1086.697 |
| approach_1 | approach | 0.00 / step_budget | (0.458, 0.025, 0.196)→(0.574, -0.013, 0.280) | (0.492, 0.024, 0.176)→(0.591, -0.019, 0.244) | 0.100→0.189 | 1.00 / 1.000 | 276.062 | 864.039 |
| contact_1 | contact | 1.00 / force_exceeded | (0.575, -0.015, 0.280)→(0.576, -0.017, 0.281) | (0.591, -0.019, 0.244)→(0.591, -0.020, 0.244) | 0.189→0.190 | 1.00 / 1.000 | 544.301 | 575.672 |
| insert_1 | insert | 1.00 / force_exceeded | (0.576, -0.017, 0.281)→(0.578, -0.021, 0.284) | (0.592, -0.023, 0.246)→(0.594, -0.027, 0.248) | 0.192→0.195 | 1.00 / 1.000 | 530.711 | 578.891 |
| retract_1 | retract | 0.00 / step_budget | (0.578, -0.021, 0.284)→(0.533, -0.052, 0.280) | (0.594, -0.027, 0.248)→(0.552, -0.052, 0.245) | 0.195→0.185 | 1.00 / 2.000 | 237.999 | 539.897 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.850
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.850
- phase_score: 0.058
- phase_breakdown.align_score: 0.005
- phase_breakdown.insert_score: 0.074
- phase_breakdown.contact_score: 0.061
- phase_breakdown.approach_score: 0.042

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.375
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.850
- **Median Q (composite search score)**: 0.133
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.368


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.01961,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.arc_height":0.18484,"align_1.speed":0.05806,"approach_1.speed":0.05386,"contact_1.contact_force":9.84589,"contact_1.speed":0.02307,"insert_1.bottom_force":34.94716,"insert_1.insertion_depth":0.04715,"insert_1.speed":0.0084,"retract_1.arc_height":0.04835,"retract_1.retract_height":0.19985,"retract_1.speed":0.09427},"optimized_scores":{"best_composite_score":0.13499,"best_fitness_score":0.37499,"best_task_score":0.8505},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.46586,0.01253,0.07876],"force_p95":1043.21324,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1085.04156,"mean_force":273.18443,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45797,0.01253,0.09072]},{"body_a":"peg_socket","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.55183,-0.00556,0.07869],"force_p95":852.0356,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":892.93145,"mean_force":165.55891,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45441,0.01293,0.09795]},{"body_a":"peg_socket","body_b":"link7","contact_count":49.0,"contact_point_centroid":[0.56514,0.01163,0.07855],"force_p95":693.1007,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":826.50831,"mean_force":202.15833,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4508,0.01392,0.11618]},{"body_a":"peg_socket","body_b":"link6","contact_count":940.0,"contact_point_centroid":[0.5842,0.02747,0.07975],"force_p95":361.40256,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":746.22625,"mean_force":283.37414,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4777,0.06023,0.21098]},{"body_a":"peg_socket","body_b":"link6","contact_count":773.0,"contact_point_centroid":[0.58434,0.02036,0.07981],"force_p95":282.12838,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":637.6517,"mean_force":249.57065,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45228,0.02307,0.17166]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.58433,-0.03528,0.07995],"force_p95":608.24318,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":609.40952,"mean_force":597.74615,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5808,0.00156,0.289]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.58425,-0.03519,0.07988],"force_p95":608.56741,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":609.14551,"mean_force":602.93644,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.57894,0.0053,0.28655]},{"body_a":"peg_socket","body_b":"link6","contact_count":502.0,"contact_point_centroid":[0.58429,-0.03525,0.07992],"force_p95":381.07356,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":451.29084,"mean_force":297.6077,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54747,-0.0139,0.30166]}],"total_contact_groups":8},"final_pose_error":0.08718,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.54587,-0.00516,0.30392],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":1085.04156,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":907.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.03133,0.18105],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.1058,"object_to_goal_dist_start":0.26034,"object_z_max":0.34476,"peak_contact_force":256.36588,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":853.0,"raw_peak_contact_force":1085.04156,"subtask_id":"align","tcp_end":[0.46692,0.03282,0.20165],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59861,0.00042,0.252],"object_pos_start":[0.50118,0.03133,0.18105],"object_to_goal_dist_end":0.19827,"object_to_goal_dist_start":0.1058,"object_z_max":0.25193,"peak_contact_force":283.71452,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":940.0,"raw_peak_contact_force":746.22625,"subtask_id":"approach","tcp_end":[0.57872,0.00583,0.28628],"tcp_start":[0.46692,0.03282,0.20165],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.59878,-0.0,0.2522],"object_pos_start":[0.59861,0.00042,0.252],"object_to_goal_dist_end":0.19852,"object_to_goal_dist_start":0.19827,"object_z_max":0.25253,"peak_contact_force":596.29927,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":609.14551,"subtask_id":"contact","tcp_end":[0.57958,0.00378,0.28737],"tcp_start":[0.5792,0.0047,0.28686],"tcp_to_object_dist_end":0.04025,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.60118,-0.0065,0.25633],"object_pos_start":[0.59932,-0.00152,0.25299],"object_to_goal_dist_end":0.2034,"object_to_goal_dist_start":0.19948,"object_z_max":0.25572,"peak_contact_force":609.40952,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":609.40952,"subtask_id":"insert","tcp_end":[0.58259,-0.00138,0.29137],"tcp_start":[0.57958,0.00378,0.28737],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":535.0,"n_steps_budget":630.0,"object_pos_end":[0.56773,-0.00702,0.27047],"object_pos_start":[0.60118,-0.0065,0.25633],"object_to_goal_dist_end":0.20228,"object_to_goal_dist_start":0.2034,"object_z_max":0.27135,"peak_contact_force":274.01965,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":502.0,"raw_peak_contact_force":451.29084,"tcp_end":[0.54587,-0.00516,0.30392],"tcp_start":[0.58259,-0.00138,0.29137],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.15966,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.arc_height":0.07993,"align_1.speed":0.06206,"approach_1.speed":0.05797,"contact_1.contact_force":3.77282,"contact_1.speed":0.0126,"insert_1.bottom_force":28.23635,"insert_1.insertion_depth":0.0562,"insert_1.speed":0.01073,"retract_1.arc_height":0.03401,"retract_1.retract_height":0.11872,"retract_1.speed":0.05297},"optimized_scores":{"best_composite_score":0.12095,"best_fitness_score":0.36095,"best_task_score":0.84089},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":915.0,"contact_point_centroid":[0.56297,0.00226,0.07992],"force_p95":308.63803,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1349.19965,"mean_force":279.82571,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46765,0.01964,0.21125]},{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.46088,0.01466,0.07864],"force_p95":1032.51407,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1085.86114,"mean_force":291.27418,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45617,0.01461,0.09151]},{"body_a":"world","body_b":"link6","contact_count":11.0,"contact_point_centroid":[0.64088,-0.02973,-0.00078],"force_p95":749.57584,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":782.31716,"mean_force":497.25635,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51563,0.04671,0.21166]},{"body_a":"peg_socket","body_b":"link7","contact_count":428.0,"contact_point_centroid":[0.56209,0.02453,0.07981],"force_p95":322.46265,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":709.18285,"mean_force":275.17385,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45395,0.02035,0.15812]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.56303,-0.07251,0.07999],"force_p95":668.14735,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":675.37435,"mean_force":603.1044,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.57773,-0.04018,0.27302]},{"body_a":"peg_socket","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.56298,-0.07245,0.07995],"force_p95":601.01411,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":601.07318,"mean_force":553.19794,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5744,-0.03369,0.26975]},{"body_a":"peg_socket","body_b":"link7","contact_count":38.0,"contact_point_centroid":[0.56303,0.02308,0.07997],"force_p95":428.1475,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":445.77726,"mean_force":350.46208,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49527,0.06328,0.19373]},{"body_a":"peg_socket","body_b":"link6","contact_count":974.0,"contact_point_centroid":[0.56301,-0.07248,0.07997],"force_p95":367.49386,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":401.8919,"mean_force":311.82076,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54475,-0.05902,0.27446]},{"body_a":"peg_socket","body_b":"link6","contact_count":273.0,"contact_point_centroid":[0.56298,0.0133,0.07984],"force_p95":306.8686,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":327.10476,"mean_force":276.57868,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44752,0.01487,0.18237]}],"total_contact_groups":9},"final_pose_error":0.14153,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.53666,-0.05773,0.27356],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":1349.19965,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":816.0,"n_steps_budget":990.0,"object_pos_end":[0.48663,0.00807,0.17957],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10078,"object_to_goal_dist_start":0.26034,"object_z_max":0.34452,"peak_contact_force":277.11238,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":714.0,"raw_peak_contact_force":1085.86114,"subtask_id":"align","tcp_end":[0.45273,0.00894,0.20078],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59063,-0.03872,0.23353],"object_pos_start":[0.48663,0.00807,0.17957],"object_to_goal_dist_end":0.18244,"object_to_goal_dist_start":0.10078,"object_z_max":0.23324,"peak_contact_force":278.88231,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":964.0,"raw_peak_contact_force":1349.19965,"subtask_id":"approach","tcp_end":[0.57318,-0.03087,0.26865],"tcp_start":[0.45273,0.00894,0.20078],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.59108,-0.04002,0.23391],"object_pos_start":[0.59063,-0.03872,0.23353],"object_to_goal_dist_end":0.18326,"object_to_goal_dist_start":0.18244,"object_z_max":0.23598,"peak_contact_force":600.67941,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":601.07318,"subtask_id":"contact","tcp_end":[0.57703,-0.03899,0.27228],"tcp_start":[0.57434,-0.03383,0.26966],"tcp_to_object_dist_end":0.04087,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.59479,-0.04979,0.23846],"object_pos_start":[0.59347,-0.04637,0.23657],"object_to_goal_dist_end":0.19125,"object_to_goal_dist_start":0.18815,"object_z_max":0.23782,"peak_contact_force":530.83445,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":675.37435,"subtask_id":"insert","tcp_end":[0.57906,-0.04257,0.27452],"tcp_start":[0.57703,-0.03899,0.27228],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55799,-0.06037,0.23983],"object_pos_start":[0.59479,-0.04979,0.23846],"object_to_goal_dist_end":0.18042,"object_to_goal_dist_start":0.19125,"object_z_max":0.2412,"peak_contact_force":294.54482,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":974.0,"raw_peak_contact_force":401.8919,"tcp_end":[0.53666,-0.05773,0.27356],"tcp_start":[0.57906,-0.04257,0.27452],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.31304,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.arc_height":0.19361,"align_1.speed":0.06846,"approach_1.speed":0.04386,"contact_1.contact_force":2.73322,"contact_1.speed":0.0181,"insert_1.bottom_force":31.21238,"insert_1.insertion_depth":0.05399,"insert_1.speed":0.00625,"retract_1.arc_height":0.07617,"retract_1.retract_height":0.10657,"retract_1.speed":0.0546},"optimized_scores":{"best_composite_score":0.13252,"best_fitness_score":0.37252,"best_task_score":0.84337},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.45929,0.014,0.07815],"force_p95":1039.37575,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1089.18777,"mean_force":161.18119,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45479,0.01397,0.09059]},{"body_a":"peg_socket","body_b":"link7","contact_count":163.0,"contact_point_centroid":[0.56588,0.01745,0.0794],"force_p95":478.69214,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":961.91969,"mean_force":294.04768,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4542,0.01902,0.14344]},{"body_a":"world","body_b":"link6","contact_count":189.0,"contact_point_centroid":[0.5798,-0.07161,-8e-05],"force_p95":676.72084,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":766.50926,"mean_force":253.80503,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51738,-0.09314,0.26161]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.56989,-0.02805,0.07993],"force_p95":516.33471,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":516.79807,"mean_force":488.29531,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.56991,-0.01455,0.28431]},{"body_a":"peg_socket","body_b":"link6","contact_count":966.0,"contact_point_centroid":[0.56989,0.02941,0.07985],"force_p95":340.47339,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":496.69178,"mean_force":276.6154,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46647,0.04897,0.20568]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.57,-0.0282,0.07999],"force_p95":448.12395,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":451.88934,"mean_force":414.23544,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.57177,-0.01747,0.28558]},{"body_a":"peg_socket","body_b":"link6","contact_count":201.0,"contact_point_centroid":[0.57001,-0.0282,0.04901],"force_p95":357.14724,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":448.57657,"mean_force":172.01268,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51743,-0.09313,0.26165]},{"body_a":"peg_socket","body_b":"link6","contact_count":940.0,"contact_point_centroid":[0.5692,-0.02814,0.07123],"force_p95":293.74018,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":362.53625,"mean_force":201.32341,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53481,-0.0669,0.28188]},{"body_a":"peg_socket","body_b":"link6","contact_count":488.0,"contact_point_centroid":[0.56997,0.02838,0.07989],"force_p95":277.15378,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":309.93349,"mean_force":254.7475,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44779,0.02906,0.16932]},{"body_a":"peg_socket","body_b":"link6","contact_count":37.0,"contact_point_centroid":[0.54001,-0.02821,0.05244],"force_p95":47.82065,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":61.80469,"mean_force":32.12693,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51767,-0.09306,0.26171]}],"total_contact_groups":10},"final_pose_error":0.18045,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.51741,-0.09289,0.26183],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1089.18777,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":756.0,"n_steps_budget":930.0,"object_pos_end":[0.48962,0.03302,0.16757],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09416,"object_to_goal_dist_start":0.26034,"object_z_max":0.34457,"peak_contact_force":265.54853,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":664.0,"raw_peak_contact_force":1089.18777,"subtask_id":"align","tcp_end":[0.45359,0.03348,0.18494],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58345,-0.01898,0.24697],"object_pos_start":[0.48962,0.03302,0.16757],"object_to_goal_dist_end":0.18762,"object_to_goal_dist_start":0.09416,"object_z_max":0.24693,"peak_contact_force":265.58908,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":966.0,"raw_peak_contact_force":496.69178,"subtask_id":"approach","tcp_end":[0.56953,-0.01387,0.28412],"tcp_start":[0.45359,0.03348,0.18494],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.58372,-0.01957,0.24709],"object_pos_start":[0.58345,-0.01898,0.24697],"object_to_goal_dist_end":0.18791,"object_to_goal_dist_start":0.18762,"object_z_max":0.2473,"peak_contact_force":435.9234,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":516.79807,"subtask_id":"contact","tcp_end":[0.57091,-0.01613,0.28483],"tcp_start":[0.57033,-0.01529,0.28453],"tcp_to_object_dist_end":0.04001,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.5856,-0.02417,0.24904],"object_pos_start":[0.58451,-0.02111,0.24755],"object_to_goal_dist_end":0.19101,"object_to_goal_dist_start":0.18884,"object_z_max":0.24876,"peak_contact_force":451.88934,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":451.88934,"subtask_id":"insert","tcp_end":[0.57293,-0.01937,0.28668],"tcp_start":[0.57091,-0.01613,0.28483],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53079,-0.0888,0.22436],"object_pos_start":[0.5856,-0.02417,0.24904],"object_to_goal_dist_end":0.17226,"object_to_goal_dist_start":0.19101,"object_z_max":0.25703,"peak_contact_force":145.43248,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1367.0,"raw_peak_contact_force":766.50926,"tcp_end":[0.51741,-0.09289,0.26183],"tcp_start":[0.57293,-0.01937,0.28668],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```