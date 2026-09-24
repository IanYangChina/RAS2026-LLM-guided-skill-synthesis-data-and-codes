## Search State

- **Seed**: 6
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1392 | 0.94 | ❌ rejected |
| 11 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1418 | 0.94 | ✅ accepted |
| 10 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 8 | 0.2452 | 0.84 | ❌ rejected |
| 9 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 8 | 0.0599 | 0.82 | ❌ rejected |
| 8 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1407 | 0.94 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.94). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.139) — your mutation base

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

- **Composite score**: 0.139
- **task_score** (E): 0.936
- **fitness_score**: 0.379  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 0.00 | 0.1632 |
| approach_1 | 1.00 | 0.00 | 0.0518 |
| contact_1 | 0.67 | 0.33 | 0.0607 |
| insert_1 | 1.00 | 1.00 | 0.0184 |
| retract_1 | 0.67 | 0.33 | 0.0358 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.015, 0.139) | (0.504, -0.000, 0.340)→(0.506, 0.015, 0.177) | 0.260→0.100 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_1 | approach | 1.00 / step_budget | (0.494, 0.015, 0.139)→(0.495, 0.018, 0.088) | (0.506, 0.015, 0.177)→(0.508, 0.018, 0.126) | 0.100→0.055 | 0.00 / 0.000 | 0.000 | 0.000 |
| contact_1 | contact | 0.67 / step_budget | (0.495, 0.018, 0.088)→(0.511, 0.040, 0.143) | (0.508, 0.018, 0.126)→(0.523, 0.044, 0.156) | 0.055→0.096 | 0.33 / 0.333 | 117.086 | 757.040 |
| insert_1 | insert | 1.00 / force_exceeded | (0.511, 0.040, 0.143)→(0.523, 0.041, 0.137) | (0.523, 0.044, 0.156)→(0.536, 0.046, 0.150) | 0.096→0.095 | 1.00 / 1.333 | 1472.131 | 1472.131 |
| retract_1 | retract | 0.67 / step_budget | (0.523, 0.041, 0.137)→(0.511, 0.037, 0.165) | (0.536, 0.046, 0.150)→(0.524, 0.041, 0.177) | 0.095→0.114 | 0.33 / 0.333 | 73.674 | 2506.736 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.992
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.992
- phase_score: 0.002
- phase_breakdown.contact_score: 0.002
- phase_breakdown.align_score: 0.001
- phase_breakdown.approach_score: 0.001
- phase_breakdown.insert_score: 0.002

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.398
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.992
- **Median Q (composite search score)**: 0.143
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.346


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":144.0,"average_failure_rate":0.34204,"average_mean_iterations":69.99762,"average_solve_count":421.0,"average_success_count":277.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00768,"align_1.lateral_offset_y":0.00263,"approach_1.speed":0.05506,"contact_1.speed":0.03827,"insert_1.insertion_depth":0.05451,"insert_1.insertion_force":23.86922,"retract_1.speed":0.04782},"optimized_scores":{"best_composite_score":0.15767,"best_fitness_score":0.39767,"best_task_score":0.9918},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.53503,0.00577,0.0791],"force_p95":4021.93319,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4059.75161,"mean_force":1695.22563,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52095,0.00556,0.07909]},{"body_a":"attachment","body_b":"peg_socket","contact_count":29.0,"contact_point_centroid":[0.51365,0.01815,0.07997],"force_p95":3623.53287,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3765.70394,"mean_force":669.08706,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51326,0.00382,0.07968]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.53368,0.00588,0.07975],"force_p95":3259.26375,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3259.26375,"mean_force":3259.26375,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5177,0.00584,0.07822]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.51712,0.01881,0.08],"force_p95":2734.57652,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2844.58132,"mean_force":1744.53334,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51661,0.00515,0.07868]}],"total_contact_groups":4},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.50073,-0.01088,0.12044],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":4059.75161,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":501.0,"n_steps_budget":1000.0,"object_pos_end":[0.50451,-0.00913,0.17737],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.0979,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"align","tcp_end":[0.49239,-0.00909,0.13924],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":209.0,"n_steps_budget":1000.0,"object_pos_end":[0.51016,-0.01182,0.12561],"object_pos_start":[0.50451,-0.00913,0.17737],"object_to_goal_dist_end":0.0482,"object_to_goal_dist_start":0.0979,"object_z_max":0.17737,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.49702,-0.0118,0.08783],"tcp_start":[0.49239,-0.00909,0.13924],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.51016,-0.01182,0.12561],"object_pos_start":[0.51016,-0.01182,0.12561],"object_to_goal_dist_end":0.0482,"object_to_goal_dist_start":0.0482,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"contact","tcp_end":[0.49702,-0.0118,0.08783],"tcp_start":[0.49702,-0.0118,0.08783],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":16.0,"n_steps_budget":600.0,"object_pos_end":[0.5343,0.00718,0.1147],"object_pos_start":[0.51016,-0.01182,0.12561],"object_to_goal_dist_end":0.04932,"object_to_goal_dist_start":0.0482,"object_z_max":0.12561,"peak_contact_force":3259.26375,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":3259.26375,"subtask_id":"insert","tcp_end":[0.51941,0.0068,0.07758],"tcp_start":[0.49702,-0.0118,0.08783],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":648.0,"n_steps_budget":1000.0,"object_pos_end":[0.5164,-0.01015,0.15724],"object_pos_start":[0.5343,0.00718,0.1147],"object_to_goal_dist_end":0.07961,"object_to_goal_dist_start":0.04932,"object_z_max":0.15715,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":41.0,"raw_peak_contact_force":4059.75161,"tcp_end":[0.50073,-0.01088,0.12044],"tcp_start":[0.51941,0.0068,0.07758],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":90.0,"average_failure_rate":0.24523,"average_mean_iterations":50.82289,"average_solve_count":367.0,"average_success_count":277.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00984,"align_1.lateral_offset_y":-0.00993,"approach_1.speed":0.05238,"contact_1.speed":0.05901,"insert_1.insertion_depth":0.04547,"insert_1.insertion_force":10.15684,"retract_1.speed":0.07818},"optimized_scores":{"best_composite_score":0.11723,"best_fitness_score":0.35723,"best_task_score":0.89069},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":20.0,"contact_point_centroid":[0.54102,0.01655,0.07959],"force_p95":2560.40258,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2706.60639,"mean_force":821.54657,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52518,0.01657,0.07749]},{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.52548,0.00086,0.07854],"force_p95":2445.28259,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2536.28738,"mean_force":1217.23838,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52491,0.01496,0.07715]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.51963,0.00171,0.07998],"force_p95":758.47397,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":758.47397,"mean_force":758.47397,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51779,0.01653,0.08027]}],"total_contact_groups":3},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.50708,0.0301,0.12063],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":2706.60639,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":508.0,"n_steps_budget":1000.0,"object_pos_end":[0.50853,0.01996,0.17741],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.0998,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"align","tcp_end":[0.49679,0.01987,0.13917],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.51613,0.02917,0.12493],"object_pos_start":[0.50853,0.01996,0.17741],"object_to_goal_dist_end":0.05595,"object_to_goal_dist_start":0.0998,"object_z_max":0.17741,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.50355,0.02912,0.08696],"tcp_start":[0.49679,0.01987,0.13917],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.51613,0.02917,0.12493],"object_pos_start":[0.51613,0.02917,0.12493],"object_to_goal_dist_end":0.05595,"object_to_goal_dist_start":0.05595,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"contact","tcp_end":[0.50355,0.02912,0.08696],"tcp_start":[0.50355,0.02912,0.08696],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":13.0,"n_steps_budget":600.0,"object_pos_end":[0.53326,0.01619,0.11717],"object_pos_start":[0.51613,0.02917,0.12493],"object_to_goal_dist_end":0.05244,"object_to_goal_dist_start":0.05595,"object_z_max":0.12493,"peak_contact_force":758.47397,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":758.47397,"subtask_id":"insert","tcp_end":[0.51966,0.01533,0.07956],"tcp_start":[0.50355,0.02912,0.08696],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":576.0,"n_steps_budget":1000.0,"object_pos_end":[0.52083,0.03073,0.15819],"object_pos_start":[0.53326,0.01619,0.11717],"object_to_goal_dist_end":0.08656,"object_to_goal_dist_start":0.05244,"object_z_max":0.15812,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":33.0,"raw_peak_contact_force":2706.60639,"tcp_end":[0.50708,0.0301,0.12063],"tcp_start":[0.51966,0.01533,0.07956],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.4125,"average_solve_count":240.0,"average_success_count":240.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00987,"align_1.lateral_offset_y":-0.00264,"approach_1.speed":0.03276,"contact_1.speed":0.06058,"insert_1.insertion_depth":0.05469,"insert_1.insertion_force":31.81719,"retract_1.speed":0.07826},"optimized_scores":{"best_composite_score":0.14263,"best_fitness_score":0.38263,"best_task_score":0.92656},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":24.0,"contact_point_centroid":[0.51835,0.02287,0.07867],"force_p95":1662.55662,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2271.12042,"mean_force":542.4224,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50641,0.01988,0.08286]},{"body_a":"attachment","body_b":"peg_socket","contact_count":14.0,"contact_point_centroid":[0.512,0.00634,0.07958],"force_p95":1721.14979,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2147.04245,"mean_force":743.33828,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50617,0.01631,0.08225]},{"body_a":"world","body_b":"link6","contact_count":141.0,"contact_point_centroid":[0.58938,0.18645,-0.00057],"force_p95":424.49912,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1263.11727,"mean_force":266.67212,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54555,0.07643,0.23061]},{"body_a":"peg_socket","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.54558,0.0774,0.0786],"force_p95":774.22874,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1000.152,"mean_force":344.39044,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53024,-0.01469,0.13063]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.57212,0.16316,-6e-05],"force_p95":288.18059,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":753.84993,"mean_force":246.57005,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52613,0.09758,0.25469]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.57541,0.17318,-9e-05],"force_p95":398.65564,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":398.65564,"mean_force":398.65564,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.53136,0.10206,0.25427]},{"body_a":"world","body_b":"link5","contact_count":753.0,"contact_point_centroid":[0.47734,0.1768,-4e-05],"force_p95":347.21476,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":361.28002,"mean_force":300.75094,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53165,0.10254,0.25231]},{"body_a":"world","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.4786,0.17496,-5e-05],"force_p95":242.6523,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":242.6523,"mean_force":242.6523,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.53237,0.10185,0.25282]},{"body_a":"world","body_b":"link5","contact_count":362.0,"contact_point_centroid":[0.46731,0.16201,-1e-05],"force_p95":215.40336,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":235.36484,"mean_force":109.53906,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52536,0.1018,0.2556]}],"total_contact_groups":9},"final_pose_error":0.14001,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.52593,0.09147,0.25356],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":2271.12042,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":517.0,"n_steps_budget":1000.0,"object_pos_end":[0.50498,0.03336,0.1769],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.1026,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"align","tcp_end":[0.49298,0.0332,0.13874],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":186.0,"n_steps_budget":1000.0,"object_pos_end":[0.49823,0.0375,0.12686],"object_pos_start":[0.50498,0.03336,0.1769],"object_to_goal_dist_end":0.06005,"object_to_goal_dist_start":0.1026,"object_z_max":0.1769,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.48413,0.0373,0.08943],"tcp_start":[0.49298,0.0332,0.13874],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54336,0.11456,0.21653],"object_pos_start":[0.49823,0.0375,0.12686],"object_to_goal_dist_end":0.18342,"object_to_goal_dist_start":0.06005,"object_z_max":0.21652,"peak_contact_force":351.25817,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":968.0,"raw_peak_contact_force":2271.12042,"subtask_id":"contact","tcp_end":[0.53237,0.10185,0.25282],"tcp_start":[0.48413,0.0373,0.08943],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":10.0,"n_steps_budget":900.0,"object_pos_end":[0.54123,0.11365,0.21736],"object_pos_start":[0.54336,0.11456,0.21653],"object_to_goal_dist_end":0.18299,"object_to_goal_dist_start":0.18342,"object_z_max":0.21766,"peak_contact_force":398.65564,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":398.65564,"subtask_id":"insert","tcp_end":[0.53129,0.10211,0.25435],"tcp_start":[0.53237,0.10185,0.25282],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53618,0.10347,0.2168],"object_pos_start":[0.54123,0.11365,0.21736],"object_to_goal_dist_end":0.1753,"object_to_goal_dist_start":0.18299,"object_z_max":0.21944,"peak_contact_force":221.02088,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1362.0,"raw_peak_contact_force":753.84993,"tcp_end":[0.52593,0.09147,0.25356],"tcp_start":[0.53129,0.10211,0.25435],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```