## Search State

- **Seed**: 7
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.3097 | 0.49 | ✅ accepted |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1068 | 0.23 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.3019 | 0.39 | ✅ accepted |

**Proposal policy**: task_score is 0.49 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_channel
- Frozen realised-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`
- Frozen object start: [0.5100076373283734, 0.11177710407756605, 0.04]
- Frozen task target: [0.5100076373283734, -0.04822289592243395, 0.04]
- Goal object position: (0.5100076373283734, -0.04822289592243395, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5100076373283734, 0.11177710407756605, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.51, 0.1118, 0.04]
  frozen_task_target: [0.51, -0.0482, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5100076373283734, 0.11177710407756605, 0.04]}
  frozen_targets: {'channel_exit': [0.5100076373283734, -0.04822289592243395, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.04, 0.00) | distance | — |
| contact | object | (0.00, 0.02, 0.00) | distance | — |
| push | world | (0.50, -0.08, 0.04) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.310) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.04
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
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
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.01
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
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
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.18
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.025
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: push_contact
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0]
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.01, 0.0]
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=push_contact, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=reduce_speed

## Design Metrics

- **Composite score**: 0.310
- **task_score** (E): 0.489
- **fitness_score**: 0.529  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2553 |
| contact_1 | 0.33 | 1.00 | 0.0237 |
| push_1 | 0.67 | 1.00 | 0.1494 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.142, 0.053) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.333 | 139.637 | 156.586 |
| contact_1 | contact | 0.33 / step_budget | (0.505, 0.142, 0.053)→(0.506, 0.122, 0.041) | (0.502, 0.098, 0.034)→(0.504, 0.087, 0.035) | 0.178→0.167 | 1.00 / 2.000 | 18.001 | 19.669 |
| push_1 | push | 0.67 / step_budget | (0.506, 0.122, 0.041)→(0.510, -0.027, 0.040) | (0.504, 0.087, 0.035)→(0.507, -0.036, 0.035) | 0.167→0.054 | 1.00 / 3.333 | 164.287 | 165.407 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.701
- phase_breakdown.approach_score: 0.821
- phase_breakdown.contact_score: 0.716
- phase_breakdown.push_score: 0.657

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.821
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.272
- **K-run variance**: 0.0183
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.475


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24286,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.14121,"contact_1.contact_force":9.47665,"contact_1.speed":0.01925,"push_1.push_distance":0.17893,"push_1.push_speed":0.06808,"push_1.push_tolerance":0.02061},"optimized_scores":{"best_composite_score":0.49085,"best_fitness_score":0.82085,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":460.0,"contact_point_centroid":[0.50372,0.00065,0.04789],"force_p95":137.16354,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":141.0949,"mean_force":32.21896,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49819,0.01178,0.02815]},{"body_a":"peg","body_b":"channel_base_body","contact_count":106.0,"contact_point_centroid":[0.50765,-0.10181,0.05991],"force_p95":132.82271,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":133.9478,"mean_force":105.69616,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49879,-0.05935,0.0288]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":392.0,"contact_point_centroid":[0.52534,-0.03067,0.04273],"force_p95":30.94905,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.22733,"mean_force":10.36327,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49817,-0.00263,0.02816]},{"body_a":"peg","body_b":"channel_base_body","contact_count":226.0,"contact_point_centroid":[0.50675,-0.03156,0.00987],"force_p95":14.04104,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.18389,"mean_force":4.75948,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49829,0.01137,0.02818]},{"body_a":"peg","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.52032,0.06546,0.06414],"force_p95":5.87495,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.92986,"mean_force":1.71301,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49737,0.08836,0.0269]},{"body_a":"peg","body_b":"channel_base_body","contact_count":771.0,"contact_point_centroid":[0.50268,0.08949,0.00986],"force_p95":2.93492,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.60577,"mean_force":2.06435,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.501,0.13482,0.03587]},{"body_a":"attachment","body_b":"peg","contact_count":647.0,"contact_point_centroid":[0.50248,0.12019,0.04177],"force_p95":2.7374,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.28044,"mean_force":2.02115,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50062,0.13213,0.03437]},{"body_a":"peg","body_b":"channel_base_body","contact_count":730.0,"contact_point_centroid":[0.50358,0.1117,0.00938],"force_p95":0.62126,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55477,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50219,0.1758,0.16995]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49965,0.19971,0.29876]}],"total_contact_groups":9},"final_pose_error":0.02468,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50773,-0.08633,0.03526],"final_tcp_position":[0.49907,-0.0624,0.02854],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":141.0949,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":752.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11179,0.03392],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.52774,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":746.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50584,0.15325,0.04884],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04412,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":787.0,"n_steps_budget":1000.0,"object_pos_end":[0.5034,0.09313,0.03505],"object_pos_start":[0.50371,0.11179,0.03392],"object_to_goal_dist_end":0.17323,"object_to_goal_dist_start":0.19192,"object_z_max":0.03515,"peak_contact_force":1.83715,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1418.0,"raw_peak_contact_force":5.60577,"subtask_id":"contact","tcp_end":[0.49995,0.12297,0.03003],"tcp_start":[0.50584,0.15325,0.04884],"tcp_to_object_dist_end":0.03046,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":553.0,"n_steps_budget":1000.0,"object_pos_end":[0.50773,-0.08633,0.03526],"object_pos_start":[0.5034,0.09313,0.03505],"object_to_goal_dist_end":0.01106,"object_to_goal_dist_start":0.17323,"object_z_max":0.03834,"peak_contact_force":139.3867,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1211.0,"raw_peak_contact_force":141.0949,"subtask_id":"push","tcp_end":[0.49907,-0.0624,0.02854],"tcp_start":[0.49995,0.12297,0.03003],"tcp_to_object_dist_end":0.02633,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09942,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.18295,"contact_1.contact_force":6.38772,"contact_1.speed":0.01735,"push_1.push_distance":0.17654,"push_1.push_speed":0.04197,"push_1.push_tolerance":0.0138},"optimized_scores":{"best_composite_score":0.27246,"best_fitness_score":0.60246,"best_task_score":0.46758},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":686.0,"contact_point_centroid":[0.50019,0.01444,0.04211],"force_p95":74.97156,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.89831,"mean_force":16.78409,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49334,0.02503,0.02905]},{"body_a":"peg","body_b":"channel_base_body","contact_count":105.0,"contact_point_centroid":[0.50706,-0.10111,0.06032],"force_p95":81.30103,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":81.95953,"mean_force":65.02074,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49805,-0.05662,0.03042]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":671.0,"contact_point_centroid":[0.52521,0.00237,0.03348],"force_p95":23.05437,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.27409,"mean_force":5.13606,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49302,0.02856,0.02887]},{"body_a":"peg","body_b":"channel_base_body","contact_count":458.0,"contact_point_centroid":[0.50964,-0.01203,0.00993],"force_p95":16.00631,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.18161,"mean_force":7.0648,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49318,0.02849,0.02898]},{"body_a":"peg","body_b":"link7","contact_count":100.0,"contact_point_centroid":[0.5206,0.05874,0.06356],"force_p95":16.91226,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.88414,"mean_force":7.67605,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4901,0.07484,0.02777]},{"body_a":"peg","body_b":"channel_base_body","contact_count":980.0,"contact_point_centroid":[0.50152,0.10301,0.0098],"force_p95":2.54564,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.14316,"mean_force":1.50843,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48617,0.14368,0.03725]},{"body_a":"attachment","body_b":"peg","contact_count":653.0,"contact_point_centroid":[0.49368,0.12805,0.04911],"force_p95":2.26571,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.69916,"mean_force":1.62492,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48773,0.13941,0.03491]},{"body_a":"peg","body_b":"channel_base_body","contact_count":658.0,"contact_point_centroid":[0.49626,0.11903,0.0094],"force_p95":0.60862,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55386,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49079,0.17899,0.16932]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49931,0.19959,0.2969]}],"total_contact_groups":9},"final_pose_error":0.01622,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50636,-0.08454,0.03569],"final_tcp_position":[0.49828,-0.05851,0.03016],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":84.89831,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":683.0,"n_steps_budget":900.0,"object_pos_end":[0.49607,0.11906,0.03397],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19919,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.51597,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":682.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48348,0.1601,0.04946],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04564,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50258,0.10342,0.03575],"object_pos_start":[0.49607,0.11906,0.03397],"object_to_goal_dist_end":0.18349,"object_to_goal_dist_start":0.19919,"object_z_max":0.03584,"peak_contact_force":1.90785,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1633.0,"raw_peak_contact_force":3.14316,"subtask_id":"contact","tcp_end":[0.49096,0.1314,0.03086],"tcp_start":[0.48348,0.1601,0.04946],"tcp_to_object_dist_end":0.03068,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":873.0,"n_steps_budget":1000.0,"object_pos_end":[0.50636,-0.08454,0.03569],"object_pos_start":[0.50258,0.10342,0.03575],"object_to_goal_dist_end":0.00892,"object_to_goal_dist_start":0.18349,"object_z_max":0.03745,"peak_contact_force":84.89831,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2020.0,"raw_peak_contact_force":84.89831,"subtask_id":"push","tcp_end":[0.49828,-0.05851,0.03016],"tcp_start":[0.49096,0.1314,0.03086],"tcp_to_object_dist_end":0.02782,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01026,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05369,"contact_1.contact_force":3.97286,"contact_1.speed":0.03665,"push_1.push_distance":0.15066,"push_1.push_speed":0.03276,"push_1.push_tolerance":0.04565},"optimized_scores":{"best_composite_score":0.16578,"best_fitness_score":0.16245,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":116.0,"contact_point_centroid":[0.53666,0.11202,0.05981],"force_p95":447.01868,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":465.44716,"mean_force":410.42723,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5248,0.11176,0.06136]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":968.0,"contact_point_centroid":[0.54058,0.04356,0.05996],"force_p95":266.19868,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":270.2273,"mean_force":238.26765,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53042,0.04926,0.0609]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.53793,0.11226,0.05994],"force_p95":50.25721,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":50.25721,"mean_force":50.25721,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52608,0.11174,0.06167]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50586,0.06296,0.00937],"force_p95":0.55508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56049,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51232,0.14996,0.16307]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49942,0.19953,0.29669]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50598,0.06305,0.00939],"force_p95":0.55181,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54648,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53034,0.05028,0.06091]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.48884,0.05768,0.00938],"force_p95":0.54764,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54764,"mean_force":0.54764,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52608,0.11174,0.06167]}],"total_contact_groups":7},"final_pose_error":0.13225,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50607,0.06298,0.03384],"final_tcp_position":[0.53173,0.03921,0.06081],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":465.44716,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":417.86696,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1122.0,"raw_peak_contact_force":465.44716,"subtask_id":"approach","tcp_end":[0.52608,0.11174,0.06167],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05967,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":900.0,"object_pos_end":[0.50593,0.063,0.0338],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14323,"object_z_max":0.0338,"peak_contact_force":50.25721,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":50.25721,"subtask_id":"contact","tcp_end":[0.52609,0.11173,0.06166],"tcp_start":[0.52608,0.11174,0.06167],"tcp_to_object_dist_end":0.05964,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50607,0.06298,0.03384],"object_pos_start":[0.50593,0.063,0.0338],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.14326,"object_z_max":0.03385,"peak_contact_force":268.57645,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1968.0,"raw_peak_contact_force":270.2273,"subtask_id":"push","tcp_end":[0.53173,0.03921,0.06081],"tcp_start":[0.52609,0.11173,0.06166],"tcp_to_object_dist_end":0.04416,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```