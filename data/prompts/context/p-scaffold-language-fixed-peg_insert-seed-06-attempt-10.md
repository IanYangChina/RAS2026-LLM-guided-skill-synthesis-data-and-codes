## Search State

- **Seed**: 6
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 8 | 0.2452 | 0.84 | ❌ rejected |
| 9 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 8 | 0.0599 | 0.82 | ❌ rejected |
| 8 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1407 | 0.94 | ✅ accepted |
| 7 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 8 | -0.1379 | 0.88 | ❌ rejected |
| 6 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 8 | 0.1385 | 0.90 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `72d0fc56eb607f902ea78d3570decababa6da9acffffae87b8c65460ac3ff15e`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5030531481177555, -0.012538330414932925, 0.08]
- Frozen socket pose: [0.5030531481177555, -0.012538330414932925, 0.025] (static fixture for this episode)
- Goal object position: (0.5030531481177555, -0.012538330414932925, 0.025)
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
  frozen_task_target: [0.5031, -0.0125, 0.08]
  frozen_socket_position: [0.5031, -0.0125, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5030531481177555, -0.012538330414932925, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5030531481177555, -0.012538330414932925, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 72d0fc56eb607f902ea78d3570decababa6da9acffffae87b8c65460ac3ff15e

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

## Current Skill (Q=0.245) — your mutation base

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
    - 0.105
    tolerance: 0.01
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
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
    - 0.055
    tolerance: 0.01
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: scale
  subtask_id: approach
- id: contact_1
  type: contact
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
    - 0.04
    tolerance: 0.005
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: scale
  subtask_id: contact
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: admittance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.055
    offset_along_axis:
      distance: 0.05
      axis: channel_axis
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
      tolerance: 0.05
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insertion_force:
      type: scalar
      range:
      - 10.0
      - 40.0
      default: 30.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.002
    - 0.002
    - 0.0
  subtask_id: insert
- id: retract_1
  type: retract
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
    - 0.105
    tolerance: 0.01
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: scale

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_1** (`align`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.105], tolerance=0.01
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
- **approach_1** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055], tolerance=0.01
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (scale)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.04], tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (scale)
- **insert_1** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055], offset_along_axis={axis=channel_axis, distance=0.05, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insertion_force: status=consumed; consumers=termination.force_threshold (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.002, 0.002, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.105], tolerance=0.01
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (scale)

## Design Metrics

- **Composite score**: 0.245
- **task_score** (E): 0.836
- **fitness_score**: 0.335  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.400
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 0.00 | 0.1637 |
| approach_1 | 1.00 | 0.00 | 0.0136 |
| contact_1 | 1.00 | 1.00 | 0.1153 |
| insert_1 | 1.00 | 1.00 | 0.0024 |
| retract_1 | 0.33 | 0.67 | 0.0364 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.499, 0.016, 0.139) | (0.504, -0.000, 0.340)→(0.510, 0.016, 0.177) | 0.260→0.101 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_1 | approach | 1.00 / step_budget | (0.499, 0.016, 0.139)→(0.496, 0.018, 0.126) | (0.510, 0.016, 0.177)→(0.508, 0.018, 0.164) | 0.101→0.089 | 0.00 / 0.000 | 0.000 | 0.000 |
| contact_1 | contact | 1.00 / force_exceeded | (0.496, 0.018, 0.126)→(0.557, 0.019, 0.029) | (0.508, 0.018, 0.164)→(0.580, 0.022, 0.061) | 0.089→0.097 | 1.00 / 1.333 | 3534.657 | 3534.657 |
| insert_1 | insert | 1.00 / force_exceeded | (0.557, 0.019, 0.029)→(0.557, 0.019, 0.027) | (0.580, 0.022, 0.061)→(0.580, 0.022, 0.059) | 0.097→0.097 | 1.00 / 1.333 | 4227.727 | 4227.727 |
| retract_1 | retract | 0.33 / step_budget | (0.557, 0.019, 0.027)→(0.547, 0.020, 0.061) | (0.580, 0.022, 0.059)→(0.570, 0.023, 0.092) | 0.097→0.093 | 0.67 / 0.667 | 49.041 | 5358.722 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.928
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.928
- phase_score: 0.002
- phase_breakdown.contact_score: 0.002
- phase_breakdown.align_score: 0.001
- phase_breakdown.approach_score: 0.002
- phase_breakdown.insert_score: 0.002

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.373
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.928
- **Median Q (composite search score)**: 0.230
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.311


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2bcd5d362bce9ed2c176357e9c3237720ebba2a98dd8bfe48970c9fba5840ac0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ac7031668c6a08077e83f2359534923b723fe0e5a20a177feb2fc3bf67104f66`; realized-scene SHA-256: `72d0fc56eb607f902ea78d3570decababa6da9acffffae87b8c65460ac3ff15e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50305,-0.01254,0.025]},{"name":"target","value":[0.50305,-0.01254,0.025]},{"name":"socket","value":[0.50305,-0.01254,0.025]},{"name":"goal","value":[0.50305,-0.01254,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,-0.01254,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50305,-0.01254,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.68037,"average_solve_count":219.0,"average_success_count":219.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00186,"align_1.lateral_offset_y":0.00365,"approach_1.speed":0.04105,"contact_1.contact_force":6.24121,"contact_1.speed":0.09084,"insert_1.insertion_depth":0.05703,"insert_1.insertion_force":19.66564,"retract_1.speed":0.05758},"optimized_scores":{"best_composite_score":0.22966,"best_fitness_score":0.31966,"best_task_score":0.79787},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.59955,0.00059,-0.00083],"force_p95":1619.79723,"geom_a":"peg_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1619.79723,"mean_force":1619.79723,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.58815,-0.00207,0.00771]},{"body_a":"attachment","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.59814,0.00037,-0.00284],"force_p95":1395.38566,"geom_a":"peg_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1395.38566,"mean_force":1395.38566,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.58684,-0.00226,0.00384]},{"body_a":"attachment","body_b":"world","contact_count":56.0,"contact_point_centroid":[0.59072,-0.00189,-0.00321],"force_p95":781.78268,"geom_a":"peg_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1252.04963,"mean_force":198.64731,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58029,-0.00422,0.00411]},{"body_a":"attachment","body_b":"peg_socket","contact_count":887.0,"contact_point_centroid":[0.56299,-0.0013,0.03324],"force_p95":80.34094,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":97.34147,"mean_force":73.80327,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57443,-0.0032,0.02381]}],"total_contact_groups":4},"final_pose_error":0.11815,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.57457,-0.00257,0.03648],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":1619.79723,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":503.0,"n_steps_budget":1000.0,"object_pos_end":[0.5094,-0.0082,0.17739],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09819,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"align","tcp_end":[0.49772,-0.00817,0.13914],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.50958,-0.01072,0.16453],"object_pos_start":[0.5094,-0.0082,0.17739],"object_to_goal_dist_end":0.08574,"object_to_goal_dist_start":0.09819,"object_z_max":0.17739,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.49748,-0.01069,0.1264],"tcp_start":[0.49772,-0.00817,0.13914],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":58.0,"n_steps_budget":690.0,"object_pos_end":[0.61149,0.0037,0.03477],"object_pos_start":[0.50958,-0.01072,0.16453],"object_to_goal_dist_end":0.12037,"object_to_goal_dist_start":0.08574,"object_z_max":0.16453,"peak_contact_force":1619.79723,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":1619.79723,"subtask_id":"contact","tcp_end":[0.58684,-0.00226,0.00384],"tcp_start":[0.49748,-0.01069,0.1264],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.61082,0.00348,0.0315],"object_pos_start":[0.61149,0.0037,0.03477],"object_to_goal_dist_end":0.12102,"object_to_goal_dist_start":0.12037,"object_z_max":0.03477,"peak_contact_force":1395.38566,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":1395.38566,"subtask_id":"insert","tcp_end":[0.5858,-0.00257,0.00088],"tcp_start":[0.58684,-0.00226,0.00384],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59966,0.00346,0.06705],"object_pos_start":[0.61082,0.00348,0.0315],"object_to_goal_dist_end":0.10056,"object_to_goal_dist_start":0.12102,"object_z_max":0.06701,"peak_contact_force":75.9789,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":943.0,"raw_peak_contact_force":1252.04963,"tcp_end":[0.57457,-0.00257,0.03648],"tcp_start":[0.5858,-0.00257,0.00088],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4cf364ad7cdeb78864f76dd2c5686ed9e91b61eb5e5b2735897d619cb8f6dad4`; realized-scene SHA-256: `5286851552083a7c8a4164a2656d1a38f2da41529a3a0236ff73d4d9a02dc20c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.51001,0.03178,0.025]},{"name":"target","value":[0.51001,0.03178,0.025]},{"name":"socket","value":[0.51001,0.03178,0.025]},{"name":"goal","value":[0.51001,0.03178,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.03178,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.51001,0.03178,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":10.0,"average_failure_rate":0.0339,"average_mean_iterations":8.71864,"average_solve_count":295.0,"average_success_count":285.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00536,"align_1.lateral_offset_y":0.00179,"approach_1.speed":0.02972,"contact_1.contact_force":6.742,"contact_1.speed":0.05889,"insert_1.insertion_depth":0.06175,"insert_1.insertion_force":25.27418,"retract_1.speed":0.06092},"optimized_scores":{"best_composite_score":0.28251,"best_fitness_score":0.37251,"best_task_score":0.92847},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.54309,0.02864,0.08],"force_p95":1291.04981,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1291.04981,"mean_force":1291.04981,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53089,0.02317,0.08678]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.54252,0.02879,0.0788],"force_p95":1084.65579,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1084.65579,"mean_force":1084.65579,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.53051,0.02311,0.08456]},{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.54165,0.02488,0.07902],"force_p95":712.63523,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":811.04496,"mean_force":316.34773,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52692,0.02241,0.07955]},{"body_a":"attachment","body_b":"peg_socket","contact_count":18.0,"contact_point_centroid":[0.50291,0.00122,0.07669],"force_p95":160.9213,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":171.02139,"mean_force":71.99838,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49989,0.01475,0.07255]}],"total_contact_groups":4},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.50816,0.03042,0.12029],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1291.04981,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":528.0,"n_steps_budget":1000.0,"object_pos_end":[0.52135,0.03072,0.17698],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10395,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"align","tcp_end":[0.51078,0.03068,0.1384],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.51825,0.03115,0.16441],"object_pos_start":[0.52135,0.03072,0.17698],"object_to_goal_dist_end":0.0918,"object_to_goal_dist_start":0.10395,"object_z_max":0.17698,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.50697,0.03108,0.12603],"tcp_start":[0.51078,0.03068,0.1384],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":32.0,"n_steps_budget":1000.0,"object_pos_end":[0.54729,0.03101,0.12],"object_pos_start":[0.51825,0.03115,0.16441],"object_to_goal_dist_end":0.06927,"object_to_goal_dist_start":0.0918,"object_z_max":0.16441,"peak_contact_force":1291.04981,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":1291.04981,"subtask_id":"contact","tcp_end":[0.53051,0.02311,0.08456],"tcp_start":[0.50697,0.03108,0.12603],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":630.0,"object_pos_end":[0.54734,0.03141,0.11809],"object_pos_start":[0.54729,0.03101,0.12],"object_to_goal_dist_end":0.0684,"object_to_goal_dist_start":0.06927,"object_z_max":0.12,"peak_contact_force":1084.65579,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":1084.65579,"subtask_id":"insert","tcp_end":[0.53026,0.02301,0.08291],"tcp_start":[0.53051,0.02311,0.08456],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":697.0,"n_steps_budget":1000.0,"object_pos_end":[0.52655,0.03874,0.15482],"object_pos_start":[0.54734,0.03141,0.11809],"object_to_goal_dist_end":0.08834,"object_to_goal_dist_start":0.0684,"object_z_max":0.15474,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":27.0,"raw_peak_contact_force":811.04496,"tcp_end":[0.50816,0.03042,0.12029],"tcp_start":[0.53026,0.02301,0.08291],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `989b6885a6cc20cf657766879d873fa27d37f906fbac12db49d02020abcc24a4`; realized-scene SHA-256: `b9bf2317193e958308a6e071da8e3f166f4f6aad2cd63fb849fb719630631480`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48616,0.03898,0.025]},{"name":"target","value":[0.48616,0.03898,0.025]},{"name":"socket","value":[0.48616,0.03898,0.025]},{"name":"goal","value":[0.48616,0.03898,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.03898,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48616,0.03898,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.52133,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00351,"align_1.lateral_offset_y":-0.00995,"approach_1.speed":0.03507,"contact_1.contact_force":4.14244,"contact_1.speed":0.09307,"insert_1.insertion_depth":0.04892,"insert_1.insertion_force":31.18203,"retract_1.speed":0.09087},"optimized_scores":{"best_composite_score":0.22347,"best_fitness_score":0.31347,"best_task_score":0.78242},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"world","contact_count":73.0,"contact_point_centroid":[0.56619,0.03321,-0.00292],"force_p95":13532.23198,"geom_a":"peg_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":14013.07081,"mean_force":3186.3372,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55598,0.03506,0.00499]},{"body_a":"attachment","body_b":"peg_socket","contact_count":943.0,"contact_point_centroid":[0.54604,0.03218,0.02408],"force_p95":92.06151,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":13650.85716,"mean_force":308.40554,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55717,0.03382,0.0143]},{"body_a":"attachment","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.56537,0.03294,-0.00539],"force_p95":10203.13893,"geom_a":"peg_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":10203.13893,"mean_force":10203.13893,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.55471,0.03491,-0.00043]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.54493,0.03319,0.00961],"force_p95":9277.09239,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":9277.09239,"mean_force":9277.09239,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.55471,0.03491,-0.00043]},{"body_a":"attachment","body_b":"world","contact_count":2.0,"contact_point_centroid":[0.5675,0.03249,-0.003],"force_p95":7387.4275,"geom_a":"peg_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7693.12384,"mean_force":4636.16043,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.55665,0.0345,0.00415]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.54546,0.03297,0.01225],"force_p95":6689.11714,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6689.11714,"mean_force":6689.11714,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.55589,0.03463,0.00233]}],"total_contact_groups":6},"final_pose_error":0.12719,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.55757,0.03229,0.02496],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":14013.07081,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":508.0,"n_steps_budget":1000.0,"object_pos_end":[0.49966,0.02662,0.17713],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10071,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"align","tcp_end":[0.48717,0.02646,0.13913],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.49648,0.03376,0.16425],"object_pos_start":[0.49966,0.02662,0.17713],"object_to_goal_dist_end":0.09083,"object_to_goal_dist_start":0.10071,"object_z_max":0.17713,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.48329,0.03353,0.12649],"tcp_start":[0.48717,0.02646,0.13913],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":59.0,"n_steps_budget":660.0,"object_pos_end":[0.58187,0.02985,0.0285],"object_pos_start":[0.49648,0.03376,0.16425],"object_to_goal_dist_end":0.10123,"object_to_goal_dist_start":0.09083,"object_z_max":0.16425,"peak_contact_force":7693.12384,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":7693.12384,"subtask_id":"contact","tcp_end":[0.55471,0.03491,-0.00043],"tcp_start":[0.48329,0.03353,0.12649],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.58113,0.03001,0.02606],"object_pos_start":[0.58187,0.02985,0.0285],"object_to_goal_dist_end":0.10194,"object_to_goal_dist_start":0.10123,"object_z_max":0.0285,"peak_contact_force":10203.13893,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":10203.13893,"subtask_id":"insert","tcp_end":[0.55359,0.03513,-0.00249],"tcp_start":[0.55471,0.03491,-0.00043],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5833,0.02735,0.05519],"object_pos_start":[0.58113,0.03001,0.02606],"object_to_goal_dist_end":0.09112,"object_to_goal_dist_start":0.10194,"object_z_max":0.05516,"peak_contact_force":71.14543,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1016.0,"raw_peak_contact_force":14013.07081,"tcp_end":[0.55757,0.03229,0.02496],"tcp_start":[0.55359,0.03513,-0.00249],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```