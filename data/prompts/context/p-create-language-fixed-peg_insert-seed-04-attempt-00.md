## Search State

- **Seed**: 4
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.2790 | 0.85 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `03ab66c73c39e70252b7764557f10cd17ad49cc08b28e1c3cb573bd8dcea88ba`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5354444884457894, 0.000906204225148928, 0.08]
- Frozen socket pose: [0.5354444884457894, 0.000906204225148928, 0.025] (static fixture for this episode)
- Goal object position: (0.5354444884457894, 0.000906204225148928, 0.025)
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
  frozen_task_target: [0.5354, 0.0009, 0.08]
  frozen_socket_position: [0.5354, 0.0009, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5354444884457894, 0.000906204225148928, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5354444884457894, 0.000906204225148928, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 03ab66c73c39e70252b7764557f10cd17ad49cc08b28e1c3cb573bd8dcea88ba

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

## Current Skill (Q=0.279) — your mutation base

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
    tolerance: 0.005
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
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
    - 0.09
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
    approach_speed:
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
    - 0.07
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
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
    - 0.06
    offset_along_axis:
      distance: 0.05
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.002
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
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
    - 0.12
    tolerance: 0.005
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_1** (`align`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.12], tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings: none
- **approach_1** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.09], tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.07]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **insert_1** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.06], offset_along_axis={axis=channel_axis, distance=0.05, mode=add_to_offset, sign=positive}, tolerance=0.002
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.12], tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.279
- **task_score** (E): 0.847
- **fitness_score**: 0.369  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.290

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 0.33 | 1.00 | 0.1166 |
| approach_1 | 0.00 | 1.00 | 0.0797 |
| contact_1 | 1.00 | 1.00 | 0.0007 |
| insert_1 | 0.00 | 1.00 | 0.1103 |
| retract_1 | 0.00 | 1.00 | 0.0471 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.485, 0.004, 0.186) | (0.504, -0.000, 0.340)→(0.520, 0.004, 0.166) | 0.260→0.090 | 1.00 / 1.000 | 354.151 | 1525.706 |
| approach_1 | approach | 0.00 / step_budget | (0.485, 0.004, 0.186)→(0.517, -0.012, 0.210) | (0.520, 0.004, 0.166)→(0.543, -0.014, 0.183) | 0.090→0.132 | 1.00 / 1.333 | 215.170 | 1277.674 |
| contact_1 | contact | 1.00 / force_exceeded | (0.517, -0.012, 0.210)→(0.517, -0.013, 0.210) | (0.543, -0.014, 0.183)→(0.543, -0.015, 0.183) | 0.132→0.133 | 1.00 / 1.333 | 372.824 | 428.492 |
| insert_1 | insert | 0.00 / step_budget | (0.517, -0.013, 0.210)→(0.573, -0.016, 0.298) | (0.543, -0.015, 0.183)→(0.587, -0.014, 0.262) | 0.133→0.212 | 1.00 / 1.667 | 413.787 | 997.869 |
| retract_1 | retract | 0.00 / step_budget | (0.573, -0.016, 0.298)→(0.535, -0.032, 0.315) | (0.587, -0.014, 0.262)→(0.548, -0.030, 0.277) | 0.212→0.212 | 1.00 / 1.333 | 508.113 | 846.861 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.847
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.847
- phase_score: 0.088
- phase_breakdown.align_score: 0.005
- phase_breakdown.approach_score: 0.008
- phase_breakdown.contact_score: 0.011
- phase_breakdown.insert_score: 0.168

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.392
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.854
- **Median Q (composite search score)**: 0.268
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.216


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9dafd9212fa57d4ed6b507cf5ac09991f034abfc2fa41dbd37d7c702246c6284`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5ab22a59b7a3c9c0e28c9743e3882e986d7ba7a97654ba206ec4bffa38a24163`; realized-scene SHA-256: `03ab66c73c39e70252b7764557f10cd17ad49cc08b28e1c3cb573bd8dcea88ba`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53544,0.00091,0.025]},{"name":"target","value":[0.53544,0.00091,0.025]},{"name":"socket","value":[0.53544,0.00091,0.025]},{"name":"goal","value":[0.53544,0.00091,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.00091,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53544,0.00091,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":2.0,"average_failure_rate":0.01471,"average_mean_iterations":8.71324,"average_solve_count":136.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04915,"contact_1.contact_force":11.55826,"insert_1.insert_speed":0.02407,"insert_1.insertion_depth":0.07999},"optimized_scores":{"best_composite_score":0.26839,"best_fitness_score":0.35839,"best_task_score":0.85426},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":43.0,"contact_point_centroid":[0.56818,0.00163,0.07796],"force_p95":720.1043,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1178.42856,"mean_force":143.57721,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44616,-0.00011,0.1061]},{"body_a":"peg_socket","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.5948,0.00533,0.0799],"force_p95":905.24631,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1110.20134,"mean_force":397.73023,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49488,-0.0029,0.18032]},{"body_a":"world","body_b":"link6","contact_count":246.0,"contact_point_centroid":[0.60531,-0.10647,-0.0002],"force_p95":744.74179,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":890.8206,"mean_force":365.76025,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.56606,-0.09694,0.26564]},{"body_a":"peg_socket","body_b":"link6","contact_count":751.0,"contact_point_centroid":[0.59501,-0.03032,0.07983],"force_p95":464.71641,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":850.14383,"mean_force":300.83162,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51254,-0.00737,0.22015]},{"body_a":"world","body_b":"link6","contact_count":917.0,"contact_point_centroid":[0.55954,-0.1016,-7e-05],"force_p95":739.59115,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":834.66033,"mean_force":512.43883,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55804,-0.09379,0.26887]},{"body_a":"world","body_b":"link6","contact_count":960.0,"contact_point_centroid":[0.56027,-0.10159,-7e-05],"force_p95":672.91618,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":827.63196,"mean_force":455.53705,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.56656,-0.09664,0.26921]},{"body_a":"peg_socket","body_b":"link6","contact_count":744.0,"contact_point_centroid":[0.59489,-0.00234,0.0798],"force_p95":298.37042,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":747.58106,"mean_force":242.237,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46344,0.00018,0.16664]},{"body_a":"peg_socket","body_b":"link6","contact_count":859.0,"contact_point_centroid":[0.57774,-0.05904,0.08],"force_p95":350.36881,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":435.91319,"mean_force":225.9172,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55858,-0.09417,0.26894]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.59544,-0.05903,0.07999],"force_p95":384.79319,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":407.49828,"mean_force":244.90202,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.56816,-0.08852,0.2657]},{"body_a":"peg_socket","body_b":"link6","contact_count":947.0,"contact_point_centroid":[0.58075,-0.05904,0.08],"force_p95":315.18296,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":355.12756,"mean_force":225.67745,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.56664,-0.0967,0.26921]},{"body_a":"world","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.60432,-0.10545,-3e-05],"force_p95":240.26122,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":240.49406,"mean_force":238.16564,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.56808,-0.08837,0.2656]},{"body_a":"peg_socket","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.5413,-0.02955,0.07724],"force_p95":167.13845,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":205.52003,"mean_force":19.21127,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44518,-0.0001,0.09814]},{"body_a":"peg_socket","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.53918,0.03111,0.07979],"force_p95":78.57268,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":80.82907,"mean_force":36.91187,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44449,-5e-05,0.09024]},{"body_a":"attachment","body_b":"peg_socket","contact_count":7.0,"contact_point_centroid":[0.47557,-2e-05,0.07958],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44895,-2e-05,0.08711]}],"total_contact_groups":14},"final_pose_error":0.15111,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.55438,-0.08595,0.26719],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1178.42856,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":872.0,"n_steps_budget":990.0,"object_pos_end":[0.53039,-0.0016,0.16215],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.0876,"object_to_goal_dist_start":0.26034,"object_z_max":0.34453,"peak_contact_force":423.2701,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":829.0,"raw_peak_contact_force":1178.42856,"subtask_id":"align","tcp_end":[0.49482,-0.00289,0.1804],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":903.0,"n_steps_budget":990.0,"object_pos_end":[0.57859,-0.09025,0.22683],"object_pos_start":[0.53039,-0.0016,0.16215],"object_to_goal_dist_end":0.18942,"object_to_goal_dist_start":0.0876,"object_z_max":0.24511,"peak_contact_force":0.81076,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1003.0,"raw_peak_contact_force":1110.20134,"subtask_id":"approach","tcp_end":[0.56776,-0.08776,0.26525],"tcp_start":[0.49482,-0.00289,0.1804],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.57837,-0.09143,0.22736],"object_pos_start":[0.57859,-0.09025,0.22683],"object_to_goal_dist_end":0.1903,"object_to_goal_dist_start":0.18942,"object_z_max":0.22731,"peak_contact_force":240.49406,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":407.49828,"subtask_id":"contact","tcp_end":[0.56848,-0.08916,0.26605],"tcp_start":[0.56776,-0.08776,0.26525],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57076,-0.0934,0.22946],"object_pos_start":[0.57837,-0.09143,0.22736],"object_to_goal_dist_end":0.18992,"object_to_goal_dist_start":0.1903,"object_z_max":0.22986,"peak_contact_force":612.92079,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1907.0,"raw_peak_contact_force":827.63196,"subtask_id":"insert","tcp_end":[0.56618,-0.09084,0.26912],"tcp_start":[0.56848,-0.08916,0.26605],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":961.0,"n_steps_budget":990.0,"object_pos_end":[0.56231,-0.08945,0.22814],"object_pos_start":[0.57076,-0.0934,0.22946],"object_to_goal_dist_end":0.18393,"object_to_goal_dist_start":0.18992,"object_z_max":0.22993,"peak_contact_force":506.97744,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1776.0,"raw_peak_contact_force":834.66033,"tcp_end":[0.55438,-0.08595,0.26719],"tcp_start":[0.56618,-0.09084,0.26912],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1cd3bcde9ecee8889beeec63bba6949652ce08dd1277aacff8bc717cc59ca677`; realized-scene SHA-256: `3a693f0216d44408acf55cd4ed5e7511210ea06892083b191557e74fdeb42bf8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.5244,0.02464,0.025]},{"name":"target","value":[0.5244,0.02464,0.025]},{"name":"socket","value":[0.5244,0.02464,0.025]},{"name":"goal","value":[0.5244,0.02464,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.02464,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.5244,0.02464,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":5.0,"average_failure_rate":0.03788,"average_mean_iterations":14.58333,"average_solve_count":132.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05954,"contact_1.contact_force":9.8421,"insert_1.insert_speed":0.01998,"insert_1.insertion_depth":0.08345},"optimized_scores":{"best_composite_score":0.26709,"best_fitness_score":0.35709,"best_task_score":0.84057},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":76.0,"contact_point_centroid":[0.57108,0.01005,0.07912],"force_p95":444.94116,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2326.24121,"mean_force":254.24772,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46612,0.01204,0.14164]},{"body_a":"peg_socket","body_b":"link6","contact_count":414.0,"contact_point_centroid":[0.5843,0.02954,0.07981],"force_p95":410.99501,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2212.70784,"mean_force":333.20621,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47591,0.04871,0.18475]},{"body_a":"peg_socket","body_b":"link7","contact_count":109.0,"contact_point_centroid":[0.58365,0.04272,0.07959],"force_p95":1643.42427,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2040.21785,"mean_force":419.82402,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48453,0.04967,0.17432]},{"body_a":"peg_socket","body_b":"link6","contact_count":956.0,"contact_point_centroid":[0.58439,-0.00219,0.07991],"force_p95":423.41966,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":996.35411,"mean_force":271.66717,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55779,0.00498,0.33457]},{"body_a":"peg_socket","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.53987,-0.00571,0.07789],"force_p95":783.52413,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":923.89276,"mean_force":179.19293,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44418,0.00165,0.10605]},{"body_a":"peg_socket","body_b":"link6","contact_count":784.0,"contact_point_centroid":[0.5843,0.00497,0.07984],"force_p95":303.25131,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":921.39491,"mean_force":253.846,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45998,0.00783,0.17148]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.46441,0.00146,0.07997],"force_p95":769.23529,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":770.11604,"mean_force":761.30847,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45524,0.00141,0.09256]},{"body_a":"peg_socket","body_b":"link6","contact_count":897.0,"contact_point_centroid":[0.58431,0.06657,0.07988],"force_p95":409.6801,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":659.2413,"mean_force":317.74417,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49591,0.12474,0.20967]},{"body_a":"peg_socket","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.58439,0.07197,0.07995],"force_p95":555.62596,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":648.59876,"mean_force":427.39044,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49527,0.09078,0.18135]},{"body_a":"world","body_b":"link6","contact_count":7.0,"contact_point_centroid":[0.65727,0.1159,-0.0003],"force_p95":472.01871,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":520.8216,"mean_force":319.47246,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.47384,0.16325,0.16676]},{"body_a":"peg_socket","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.5844,0.06459,0.07999],"force_p95":451.23851,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":453.73339,"mean_force":428.78458,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49669,0.08584,0.17883]},{"body_a":"peg_socket","body_b":"link6","contact_count":231.0,"contact_point_centroid":[0.5544,-0.01578,0.07996],"force_p95":155.8823,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":242.42582,"mean_force":58.14386,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52435,-0.00619,0.33316]}],"total_contact_groups":12},"final_pose_error":0.18879,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.52301,-0.00074,0.33207],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":2326.24121,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":961.0,"n_steps_budget":990.0,"object_pos_end":[0.52224,0.02189,0.15588],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08205,"object_to_goal_dist_start":0.26034,"object_z_max":0.34438,"peak_contact_force":385.99175,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":896.0,"raw_peak_contact_force":2326.24121,"subtask_id":"align","tcp_end":[0.48578,0.02299,0.1723],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":750.0,"object_pos_end":[0.53154,0.07875,0.16053],"object_pos_start":[0.52224,0.02189,0.15588],"object_to_goal_dist_end":0.11697,"object_to_goal_dist_start":0.08205,"object_z_max":0.18065,"peak_contact_force":308.79273,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":523.0,"raw_peak_contact_force":2212.70784,"subtask_id":"approach","tcp_end":[0.49669,0.08578,0.17888],"tcp_start":[0.48578,0.02299,0.1723],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":690.0,"object_pos_end":[0.53152,0.07899,0.16046],"object_pos_start":[0.53154,0.07875,0.16053],"object_to_goal_dist_end":0.11707,"object_to_goal_dist_start":0.11697,"object_z_max":0.16056,"peak_contact_force":453.73339,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":453.73339,"subtask_id":"contact","tcp_end":[0.49667,0.08602,0.17878],"tcp_start":[0.49669,0.08578,0.17888],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62066,0.03452,0.27086],"object_pos_start":[0.53152,0.07899,0.16046],"object_to_goal_dist_end":0.22843,"object_to_goal_dist_start":0.11707,"object_z_max":0.27109,"peak_contact_force":371.96558,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":917.0,"raw_peak_contact_force":659.2413,"subtask_id":"insert","tcp_end":[0.60201,0.03735,0.30613],"tcp_start":[0.49667,0.08602,0.17878],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54083,0.00292,0.29645],"object_pos_start":[0.62066,0.03452,0.27086],"object_to_goal_dist_end":0.22029,"object_to_goal_dist_start":0.22843,"object_z_max":0.29997,"peak_contact_force":379.01884,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1187.0,"raw_peak_contact_force":996.35411,"tcp_end":[0.52301,-0.00074,0.33207],"tcp_start":[0.60201,0.03735,0.30613],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `3a12d7f15d1e6c6a0af002631f15bc7a534f5434829fc9db32b3974b909f1f84`; realized-scene SHA-256: `72d0fc56eb607f902ea78d3570decababa6da9acffffae87b8c65460ac3ff15e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50305,-0.01254,0.025]},{"name":"target","value":[0.50305,-0.01254,0.025]},{"name":"socket","value":[0.50305,-0.01254,0.025]},{"name":"goal","value":[0.50305,-0.01254,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,-0.01254,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50305,-0.01254,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.89683,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.09498,"contact_1.contact_force":1.81399,"insert_1.insert_speed":0.03575,"insert_1.insertion_depth":0.06976},"optimized_scores":{"best_composite_score":0.30151,"best_fitness_score":0.39151,"best_task_score":0.84653},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":771.0,"contact_point_centroid":[0.56293,-0.05125,0.07982],"force_p95":361.32947,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1506.7339,"mean_force":300.67742,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.47421,-0.09251,0.19985]},{"body_a":"peg_socket","body_b":"link7","contact_count":39.0,"contact_point_centroid":[0.56265,-0.03807,0.07983],"force_p95":601.12007,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1210.04202,"mean_force":416.52628,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48262,-0.04324,0.18979]},{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.45585,-0.00135,0.07855],"force_p95":1020.56868,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1072.44788,"mean_force":228.00492,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45146,-0.0013,0.09142]},{"body_a":"peg_socket","body_b":"link7","contact_count":450.0,"contact_point_centroid":[0.56171,0.00038,0.07976],"force_p95":308.60265,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":826.47357,"mean_force":275.29249,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45489,-0.00262,0.15951]},{"body_a":"peg_socket","body_b":"link5","contact_count":676.0,"contact_point_centroid":[0.46986,0.03266,0.07995],"force_p95":647.46401,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":709.56995,"mean_force":361.73316,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54176,0.01149,0.34186]},{"body_a":"peg_socket","body_b":"link5","contact_count":118.0,"contact_point_centroid":[0.55243,0.0466,0.07975],"force_p95":490.80549,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":705.63928,"mean_force":330.80651,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5352,-0.04307,0.28322]},{"body_a":"peg_socket","body_b":"link6","contact_count":490.0,"contact_point_centroid":[0.56295,0.04609,0.0799],"force_p95":250.83199,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":577.79193,"mean_force":210.99964,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55559,0.02983,0.33929]},{"body_a":"peg_socket","body_b":"link5","contact_count":152.0,"contact_point_centroid":[0.48525,0.03823,0.0799],"force_p95":469.05399,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":546.32539,"mean_force":225.42314,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55776,0.03044,0.33724]},{"body_a":"peg_socket","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.56301,-0.02303,0.07995],"force_p95":372.74115,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":510.11176,"mean_force":326.59615,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48474,-0.02877,0.19136]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.56304,-0.02491,0.07997],"force_p95":424.24427,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":424.24427,"mean_force":424.24427,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48731,-0.03452,0.18522]},{"body_a":"peg_socket","body_b":"link6","contact_count":495.0,"contact_point_centroid":[0.56299,-0.01046,0.07991],"force_p95":325.89463,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":391.98768,"mean_force":286.444,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46763,-0.01246,0.20176]},{"body_a":"peg_socket","body_b":"link6","contact_count":378.0,"contact_point_centroid":[0.56299,-0.007,0.07988],"force_p95":314.14682,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":332.14335,"mean_force":275.14659,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46058,-0.00582,0.18669]},{"body_a":"peg_socket","body_b":"link5","contact_count":34.0,"contact_point_centroid":[0.53304,0.04731,0.07986],"force_p95":50.65839,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":68.25579,"mean_force":8.32826,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.54939,0.00022,0.31757]},{"body_a":"peg_socket","body_b":"link5","contact_count":7.0,"contact_point_centroid":[0.53544,0.04735,0.07988],"force_p95":0.0,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5517,0.00815,0.32296]}],"total_contact_groups":14},"final_pose_error":0.20158,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.52792,-0.00807,0.34499],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":1506.7339,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":932.0,"n_steps_budget":990.0,"object_pos_end":[0.50712,-0.00828,0.18033],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10092,"object_to_goal_dist_start":0.26034,"object_z_max":0.34442,"peak_contact_force":253.19135,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":841.0,"raw_peak_contact_force":1072.44788,"subtask_id":"align","tcp_end":[0.47583,-0.00868,0.20524],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":572.0,"n_steps_budget":630.0,"object_pos_end":[0.52019,-0.03119,0.16268],"object_pos_start":[0.50712,-0.00828,0.18033],"object_to_goal_dist_end":0.09064,"object_to_goal_dist_start":0.10092,"object_z_max":0.18572,"peak_contact_force":335.90779,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":539.0,"raw_peak_contact_force":510.11176,"subtask_id":"approach","tcp_end":[0.48731,-0.03452,0.18522],"tcp_start":[0.47583,-0.00868,0.20524],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.52021,-0.03138,0.16267],"object_pos_start":[0.52019,-0.03119,0.16268],"object_to_goal_dist_end":0.09071,"object_to_goal_dist_start":0.09064,"object_z_max":0.16268,"peak_contact_force":424.24427,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":424.24427,"subtask_id":"contact","tcp_end":[0.48733,-0.03473,0.1852],"tcp_start":[0.48731,-0.03452,0.18522],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56991,0.0154,0.28573],"object_pos_start":[0.52021,-0.03138,0.16267],"object_to_goal_dist_end":0.21783,"object_to_goal_dist_start":0.09071,"object_z_max":0.28563,"peak_contact_force":256.47414,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":962.0,"raw_peak_contact_force":1506.7339,"subtask_id":"insert","tcp_end":[0.55132,0.00573,0.3198],"tcp_start":[0.48733,-0.03473,0.1852],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53994,-0.00308,0.30717],"object_pos_start":[0.56991,0.0154,0.28573],"object_to_goal_dist_end":0.23067,"object_to_goal_dist_start":0.21783,"object_z_max":0.30716,"peak_contact_force":638.3425,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1325.0,"raw_peak_contact_force":709.56995,"tcp_end":[0.52792,-0.00807,0.34499],"tcp_start":[0.55132,0.00573,0.3198],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```