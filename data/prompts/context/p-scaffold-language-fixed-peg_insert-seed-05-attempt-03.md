## Search State

- **Seed**: 5
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.0893 | 0.87 | ❌ rejected |
| 2 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | 0.2253 | 0.85 | ❌ rejected |
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
| approach_1 | 0.00 | 1.00 | 0.0933 |
| contact_1 | 1.00 | 1.00 | 0.0033 |
| insert_1 | 0.00 | 1.00 | 0.0686 |
| retract_1 | 0.00 | 1.00 | 0.0248 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.480, 0.014, 0.193) | (0.504, -0.000, 0.340)→(0.514, 0.013, 0.171) | 0.260→0.095 | 0.67 / 0.667 | 179.071 | 1667.331 |
| approach_1 | approach | 0.00 / step_budget | (0.480, 0.014, 0.193)→(0.545, 0.019, 0.256) | (0.514, 0.013, 0.171)→(0.567, 0.015, 0.224) | 0.095→0.162 | 1.00 / 2.000 | 314.651 | 3255.142 |
| contact_1 | contact | 1.00 / force_exceeded | (0.547, 0.016, 0.258)→(0.546, 0.016, 0.260) | (0.567, 0.015, 0.224)→(0.567, 0.014, 0.225) | 0.162→0.162 | 1.00 / 1.667 | 697.842 | 728.368 |
| insert_1 | insert | 0.00 / step_budget | (0.546, 0.016, 0.260)→(0.554, -0.029, 0.285) | (0.567, 0.013, 0.227)→(0.566, -0.028, 0.248) | 0.164→0.186 | 1.00 / 1.667 | 364.584 | 1061.150 |
| retract_1 | retract | 0.00 / step_budget | (0.554, -0.029, 0.285)→(0.556, -0.025, 0.281) | (0.566, -0.028, 0.248)→(0.566, -0.022, 0.244) | 0.186→0.184 | 1.00 / 1.333 | 183.561 | 287.039 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.872
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.872
- phase_score: 0.064
- phase_breakdown.align_score: 0.003
- phase_breakdown.insert_score: 0.102
- phase_breakdown.contact_score: 0.040
- phase_breakdown.approach_score: 0.026

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.388
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.873
- **Median Q (composite search score)**: 0.088
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.313


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.7707,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.02229,"contact_1.force_threshold":7.56775,"contact_1.speed":0.00981,"insert_1.insertion_depth":0.03584,"insert_1.speed":0.02698,"retract_1.arc_height":0.0574,"retract_1.retract_height":0.07468,"retract_1.speed":0.04998},"optimized_scores":{"best_composite_score":0.09754,"best_fitness_score":0.38754,"best_task_score":0.87223},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":910.0,"contact_point_centroid":[0.58426,0.04432,0.07981],"force_p95":388.75843,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3146.53521,"mean_force":343.84771,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48563,0.08633,0.19781]},{"body_a":"peg_socket","body_b":"link7","contact_count":57.0,"contact_point_centroid":[0.58335,0.02594,0.07928],"force_p95":2908.28015,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2955.19028,"mean_force":1150.0709,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47638,0.01913,0.17024]},{"body_a":"peg_socket","body_b":"link7","contact_count":238.0,"contact_point_centroid":[0.57982,0.00995,0.07956],"force_p95":461.3063,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2351.09468,"mean_force":317.86456,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46785,0.0081,0.14488]},{"body_a":"peg_socket","body_b":"link6","contact_count":523.0,"contact_point_centroid":[0.58434,0.01052,0.07982],"force_p95":320.80666,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1634.20569,"mean_force":265.26848,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4663,0.01278,0.17391]},{"body_a":"attachment","body_b":"peg_socket","contact_count":14.0,"contact_point_centroid":[0.46746,0.00337,0.07809],"force_p95":1065.61426,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1111.2538,"mean_force":221.10604,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46209,0.00336,0.09014]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.58386,-0.03504,0.07954],"force_p95":584.18578,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":584.30924,"mean_force":583.12951,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5617,0.05492,0.26261]},{"body_a":"peg_socket","body_b":"link6","contact_count":980.0,"contact_point_centroid":[0.58437,-0.03532,0.07995],"force_p95":305.5557,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":510.51377,"mean_force":259.11255,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5961,-0.01974,0.32034]},{"body_a":"peg_socket","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.55395,-0.00545,0.07944],"force_p95":355.51279,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":376.53418,"mean_force":197.10015,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45979,0.00335,0.09759]},{"body_a":"peg_socket","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.58438,-0.03533,0.07996],"force_p95":251.70611,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":252.57339,"mean_force":249.04675,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58679,-0.01459,0.32196]}],"total_contact_groups":9},"final_pose_error":0.23359,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.58539,-0.0124,0.3221],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":3146.53521,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":874.0,"n_steps_budget":990.0,"object_pos_end":[0.52172,0.02095,0.15724],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08293,"object_to_goal_dist_start":0.26034,"object_z_max":0.34481,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":795.0,"raw_peak_contact_force":2351.09468,"subtask_id":"align","tcp_end":[0.48542,0.02219,0.174],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58098,0.04566,0.2286],"object_pos_start":[0.52172,0.02095,0.15724],"object_to_goal_dist_end":0.17528,"object_to_goal_dist_start":0.08293,"object_z_max":0.22715,"peak_contact_force":230.02418,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":967.0,"raw_peak_contact_force":3146.53521,"subtask_id":"approach","tcp_end":[0.56017,0.05667,0.26093],"tcp_start":[0.48542,0.02219,0.174],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.58235,0.04397,0.23012],"object_pos_start":[0.58098,0.04566,0.2286],"object_to_goal_dist_end":0.17678,"object_to_goal_dist_start":0.17528,"object_z_max":0.23174,"peak_contact_force":582.00458,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":584.30924,"subtask_id":"contact","tcp_end":[0.56491,0.05156,0.26615],"tcp_start":[0.56326,0.05319,0.26432],"tcp_to_object_dist_end":0.04074,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60153,-0.02048,0.28386],"object_pos_start":[0.58525,0.04077,0.23344],"object_to_goal_dist_end":0.22866,"object_to_goal_dist_start":0.1802,"object_z_max":0.28386,"peak_contact_force":252.2358,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":980.0,"raw_peak_contact_force":510.51377,"subtask_id":"insert","tcp_end":[0.59004,-0.01635,0.32195],"tcp_start":[0.56491,0.05156,0.26615],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59754,-0.01671,0.28423],"object_pos_start":[0.60153,-0.02048,0.28386],"object_to_goal_dist_end":0.22694,"object_to_goal_dist_start":0.22866,"object_z_max":0.28424,"peak_contact_force":250.59826,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1000.0,"raw_peak_contact_force":252.57339,"tcp_end":[0.58539,-0.0124,0.3221],"tcp_start":[0.59004,-0.01635,0.32195],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.51299,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05081,"contact_1.force_threshold":9.67372,"contact_1.speed":0.02738,"insert_1.insertion_depth":0.03775,"insert_1.speed":0.01617,"retract_1.arc_height":0.04519,"retract_1.retract_height":0.11354,"retract_1.speed":0.06621},"optimized_scores":{"best_composite_score":0.08807,"best_fitness_score":0.37807,"best_task_score":0.87303},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"link5","contact_count":49.0,"contact_point_centroid":[0.55419,0.0911,-0.00053],"force_p95":4829.21213,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5832.74543,"mean_force":1935.60753,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5232,-0.02758,0.23356]},{"body_a":"peg_socket","body_b":"link5","contact_count":48.0,"contact_point_centroid":[0.52511,0.04683,0.0474],"force_p95":4305.70455,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4610.92905,"mean_force":951.78216,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52339,-0.02658,0.23438]},{"body_a":"peg_socket","body_b":"link5","contact_count":44.0,"contact_point_centroid":[0.52724,0.04699,0.05007],"force_p95":2305.26675,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2376.04578,"mean_force":1083.32378,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52345,-0.02575,0.23509]},{"body_a":"peg_socket","body_b":"link6","contact_count":953.0,"contact_point_centroid":[0.563,0.04118,0.07997],"force_p95":699.64618,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1559.01874,"mean_force":264.3282,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51214,-0.00881,0.26289]},{"body_a":"peg_socket","body_b":"link7","contact_count":544.0,"contact_point_centroid":[0.56234,-0.00188,0.07971],"force_p95":313.81044,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1538.47512,"mean_force":280.95323,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45823,-0.00435,0.15878]},{"body_a":"peg_socket","body_b":"link5","contact_count":59.0,"contact_point_centroid":[0.54069,0.04699,0.05847],"force_p95":1337.26418,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1419.54377,"mean_force":229.53223,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52067,-0.03249,0.23019]},{"body_a":"peg_socket","body_b":"link5","contact_count":982.0,"contact_point_centroid":[0.49479,0.04739,0.05698],"force_p95":516.6009,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1093.40256,"mean_force":317.09241,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5121,-0.00905,0.26263]},{"body_a":"peg_socket","body_b":"link5","contact_count":5.0,"contact_point_centroid":[0.5221,0.04711,0.05039],"force_p95":991.52741,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1065.5548,"mean_force":665.12374,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51887,-0.0236,0.23718]},{"body_a":"attachment","body_b":"peg_socket","contact_count":16.0,"contact_point_centroid":[0.4619,-0.00355,0.0771],"force_p95":955.57667,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1063.58624,"mean_force":123.94748,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45743,-0.00217,0.08802]},{"body_a":"world","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.54875,0.08765,-5e-05],"force_p95":985.86578,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":996.67669,"mean_force":888.56752,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51815,-0.02296,0.23764]},{"body_a":"world","body_b":"link5","contact_count":9.0,"contact_point_centroid":[0.53114,0.1036,-0.00014],"force_p95":923.1919,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":947.61709,"mean_force":541.05659,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5144,-0.0203,0.24011]},{"body_a":"peg_socket","body_b":"link5","contact_count":111.0,"contact_point_centroid":[0.50244,0.04718,0.04906],"force_p95":573.09719,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":607.7749,"mean_force":205.81475,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51018,-0.01773,0.25314]},{"body_a":"peg_socket","body_b":"link7","contact_count":50.0,"contact_point_centroid":[0.56293,-0.04862,0.0798],"force_p95":494.50579,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":520.57908,"mean_force":341.0098,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48931,-0.06348,0.19353]},{"body_a":"peg_socket","body_b":"link6","contact_count":851.0,"contact_point_centroid":[0.56301,-0.01344,0.07993],"force_p95":322.29655,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":434.12675,"mean_force":281.14686,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46576,-0.01962,0.19821]},{"body_a":"peg_socket","body_b":"link6","contact_count":163.0,"contact_point_centroid":[0.56299,0.04745,0.07997],"force_p95":223.79503,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":407.72452,"mean_force":187.84252,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52219,0.00814,0.2609]},{"body_a":"world","body_b":"link5","contact_count":770.0,"contact_point_centroid":[0.50243,0.11882,-6e-05],"force_p95":334.7081,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":337.58884,"mean_force":298.82783,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55633,0.04557,0.25722]}],"total_contact_groups":22},"final_pose_error":0.1153,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.54603,0.01152,0.24279],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":5832.74543,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":845.0,"n_steps_budget":990.0,"object_pos_end":[0.50714,-0.00958,0.17614],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09688,"object_to_goal_dist_start":0.26034,"object_z_max":0.34481,"peak_contact_force":281.03779,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":758.0,"raw_peak_contact_force":1538.47512,"subtask_id":"align","tcp_end":[0.47502,-0.0099,0.19997],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54278,-0.01645,0.20497],"object_pos_start":[0.50714,-0.00958,0.17614],"object_to_goal_dist_end":0.13311,"object_to_goal_dist_start":0.09688,"object_z_max":0.20494,"peak_contact_force":434.08663,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1104.0,"raw_peak_contact_force":5832.74543,"subtask_id":"approach","tcp_end":[0.51965,-0.02446,0.2366],"tcp_start":[0.47502,-0.0099,0.19997],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.54263,-0.01636,0.20505],"object_pos_start":[0.54278,-0.01645,0.20497],"object_to_goal_dist_end":0.13312,"object_to_goal_dist_start":0.13311,"object_z_max":0.20667,"peak_contact_force":996.67669,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":15.0,"raw_peak_contact_force":1065.5548,"subtask_id":"contact","tcp_end":[0.51631,-0.02137,0.23874],"tcp_start":[0.51934,-0.02407,0.23684],"tcp_to_object_dist_end":0.04305,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53286,0.00438,0.23024],"object_pos_start":[0.53818,-0.01331,0.20623],"object_to_goal_dist_end":0.15386,"object_to_goal_dist_start":0.13255,"object_z_max":0.23024,"peak_contact_force":293.20489,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2055.0,"raw_peak_contact_force":1559.01874,"subtask_id":"insert","tcp_end":[0.51451,-0.00428,0.26471],"tcp_start":[0.51631,-0.02137,0.23874],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55937,0.02611,0.20802],"object_pos_start":[0.53286,0.00438,0.23024],"object_to_goal_dist_end":0.14351,"object_to_goal_dist_start":0.15386,"object_z_max":0.23024,"peak_contact_force":193.32023,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1018.0,"raw_peak_contact_force":407.72452,"tcp_end":[0.54603,0.01152,0.24279],"tcp_start":[0.51451,-0.00428,0.26471],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.1,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09441,"contact_1.force_threshold":7.76243,"contact_1.speed":0.02074,"insert_1.insertion_depth":0.07494,"insert_1.speed":0.00921,"retract_1.arc_height":0.06317,"retract_1.retract_height":0.18325,"retract_1.speed":0.02588},"optimized_scores":{"best_composite_score":0.08239,"best_fitness_score":0.37239,"best_task_score":0.86582},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":843.0,"contact_point_centroid":[0.55415,-0.07976,-7e-05],"force_p95":601.3693,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1113.91625,"mean_force":388.54625,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.56628,-0.08019,0.26903]},{"body_a":"attachment","body_b":"peg_socket","contact_count":14.0,"contact_point_centroid":[0.46414,0.00444,0.07792],"force_p95":1066.25685,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1112.4241,"mean_force":221.21777,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45943,0.00437,0.09005]},{"body_a":"peg_socket","body_b":"link6","contact_count":651.0,"contact_point_centroid":[0.56953,-0.02815,0.0761],"force_p95":454.3862,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1016.92836,"mean_force":284.6869,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.56462,-0.07047,0.2711]},{"body_a":"peg_socket","body_b":"link7","contact_count":275.0,"contact_point_centroid":[0.56785,0.01171,0.07961],"force_p95":425.42797,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":838.61184,"mean_force":285.13904,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45921,0.00813,0.14989]},{"body_a":"peg_socket","body_b":"link6","contact_count":522.0,"contact_point_centroid":[0.56979,0.02799,0.07975],"force_p95":419.03484,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":786.14403,"mean_force":300.50457,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47368,0.04048,0.204]},{"body_a":"peg_socket","body_b":"link6","contact_count":496.0,"contact_point_centroid":[0.56993,0.01586,0.07984],"force_p95":314.24562,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":713.66818,"mean_force":271.45118,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46144,0.01766,0.18624]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.56972,-0.02791,0.07976],"force_p95":534.25174,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":535.23916,"mean_force":525.14941,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.55645,0.02172,0.27258]},{"body_a":"peg_socket","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.56995,0.05047,0.07994],"force_p95":493.46414,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":525.72392,"mean_force":411.59128,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48793,0.07374,0.18941]},{"body_a":"peg_socket","body_b":"link6","contact_count":256.0,"contact_point_centroid":[0.52195,-0.02812,0.06732],"force_p95":341.05101,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":395.88609,"mean_force":268.70622,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.57651,-0.10162,0.26949]},{"body_a":"peg_socket","body_b":"link6","contact_count":989.0,"contact_point_centroid":[0.56853,-0.02819,0.07976],"force_p95":186.89621,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":200.81978,"mean_force":173.59202,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55393,-0.06634,0.27691]},{"body_a":"peg_socket","body_b":"link6","contact_count":99.0,"contact_point_centroid":[0.528,-0.0281,0.07151],"force_p95":124.66353,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":163.30893,"mean_force":53.14131,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53977,-0.07487,0.27814]},{"body_a":"world","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.55934,-0.06991,-3e-05],"force_p95":69.72201,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":72.76243,"mean_force":45.69559,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5589,-0.06549,0.26949]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.48003,0.00176,0.07993],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45956,0.00437,0.08829]}],"total_contact_groups":13},"final_pose_error":0.13073,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.53597,-0.075,0.27907],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1113.91625,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":874.0,"n_steps_budget":990.0,"object_pos_end":[0.51248,0.02805,0.18034],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10493,"object_to_goal_dist_start":0.26034,"object_z_max":0.34474,"peak_contact_force":256.17639,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":789.0,"raw_peak_contact_force":1112.4241,"subtask_id":"align","tcp_end":[0.48087,0.02877,0.20485],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.57597,0.01662,0.2381],"object_pos_start":[0.51248,0.02805,0.18034],"object_to_goal_dist_end":0.17619,"object_to_goal_dist_start":0.10493,"object_z_max":0.23757,"peak_contact_force":279.84188,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":555.0,"raw_peak_contact_force":786.14403,"subtask_id":"approach","tcp_end":[0.55564,0.02356,0.27184],"tcp_start":[0.48087,0.02877,0.20485],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.57665,0.01489,0.23872],"object_pos_start":[0.57597,0.01662,0.2381],"object_to_goal_dist_end":0.17689,"object_to_goal_dist_start":0.17619,"object_z_max":0.23945,"peak_contact_force":514.8441,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":535.23916,"subtask_id":"contact","tcp_end":[0.5582,0.01773,0.27427],"tcp_start":[0.55728,0.01983,0.27335],"tcp_to_object_dist_end":0.04015,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56279,-0.06663,0.22966],"object_pos_start":[0.57816,0.01097,0.24027],"object_to_goal_dist_end":0.17545,"object_to_goal_dist_start":0.17865,"object_z_max":0.25657,"peak_contact_force":548.3099,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1750.0,"raw_peak_contact_force":1113.91625,"subtask_id":"insert","tcp_end":[0.55891,-0.06542,0.26946],"tcp_start":[0.5582,0.01773,0.27427],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54193,-0.07425,0.23952],"object_pos_start":[0.56279,-0.06663,0.22966],"object_to_goal_dist_end":0.18088,"object_to_goal_dist_start":0.17545,"object_z_max":0.23951,"peak_contact_force":106.76336,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1094.0,"raw_peak_contact_force":200.81978,"tcp_end":[0.53597,-0.075,0.27907],"tcp_start":[0.55891,-0.06542,0.26946],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```