## Search State

- **Seed**: 2
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1441 | 0.17 | ❌ rejected |
| 9 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.0752 | 0.00 | ❌ rejected |
| 8 | approach → descend → align → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.2044 | 0.12 | ❌ rejected |
| 7 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1107 | 0.04 | ❌ rejected |
| 6 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1482 | 0.18 | ✅ accepted |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.144) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.15
- id: center_at_channel
  anchor: fixture
  weight: 0.15
- id: traverse_channel
  weight: 0.7
phases:
- id: approach_peg
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.2
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_peg
- id: descend_to_peg
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_force:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: contact_confirm
    when: after_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: reach_peg
- id: center_at_channel
  type: align
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: body
    entity: channel_base_body
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    align_height:
      type: scalar
      range:
      - 0.08
      - 0.16
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: center_at_channel
- id: push_through_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.14
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: traverse_channel
- id: retract_up
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.2
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_force: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=contact_confirm, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **center_at_channel** (`align`)
  - target: source=yaml, anchor=body, entity=channel_base_body, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - align_height: status=consumed; consumers=target.offset.z (replace)
- **push_through_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **retract_up** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.144
- **task_score** (E): 0.170
- **fitness_score**: 0.234  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.290

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1705 |
| descend_to_peg | 1.00 | 1.00 | 0.0918 |
| center_at_channel | 0.67 | 1.00 | 0.0443 |
| push_through_channel | 0.67 | 1.00 | 0.1081 |
| retract_up | 1.00 | 1.00 | 0.0891 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.493, 0.076, 0.187) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.543 | 3.659 |
| descend_to_peg | descend | 1.00 / force_exceeded | (0.493, 0.076, 0.187)→(0.491, 0.070, 0.097) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.000 | 47.145 | 47.145 |
| center_at_channel | align | 0.67 / step_budget | (0.491, 0.070, 0.097)→(0.504, 0.030, 0.093) | (0.498, 0.068, 0.034)→(0.500, 0.060, 0.035) | 0.148→0.140 | 1.00 / 1.667 | 27.621 | 239.424 |
| push_through_channel | push | 0.67 / step_budget | (0.504, 0.030, 0.093)→(0.509, -0.078, 0.089) | (0.500, 0.060, 0.035)→(0.495, -0.005, 0.024) | 0.140→0.076 | 1.00 / 2.333 | 334.435 | 364.832 |
| retract_up | retract | 1.00 / step_budget | (0.509, -0.078, 0.089)→(0.507, -0.078, 0.178) | (0.495, -0.005, 0.024)→(0.496, -0.006, 0.024) | 0.076→0.076 | 1.00 / 1.000 | 0.651 | 113.798 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.425
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.257
- phase_score: 0.252
- phase_breakdown.center_at_channel_score: 0.000
- phase_breakdown.reach_peg_score: 0.190
- phase_breakdown.traverse_channel_score: 0.320

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.254
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.257
- **Median Q (composite search score)**: 0.148
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.385


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6269840a353345700ffa70ea476a3ad730b138bf2ec3c52304c054f0e194e023`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a2936262b79fcd5a49fda15d77b54223f43c58bfee2e71dc505f8a2f79369706`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.936,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.11057,"center_at_channel.align_height":0.09415,"descend_to_peg.descend_force":5.02521,"push_through_channel.push_distance":0.14415},"optimized_scores":{"best_composite_score":0.16429,"best_fitness_score":0.25429,"best_task_score":0.25742},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":80.0,"contact_point_centroid":[0.52501,-0.03019,0.05998],"force_p95":286.58861,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":299.32861,"mean_force":240.41521,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50245,-0.08328,0.09609]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":200.0,"contact_point_centroid":[0.47498,0.11856,0.05995],"force_p95":263.4314,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":290.44121,"mean_force":181.42679,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.49072,0.05525,0.10402]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":47.0,"contact_point_centroid":[0.47499,0.05076,0.05999],"force_p95":145.93252,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":160.95385,"mean_force":103.14844,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50128,-0.0351,0.09679]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":62.0,"contact_point_centroid":[0.47499,0.09843,0.05999],"force_p95":135.58025,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":140.46271,"mean_force":61.30251,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50192,-0.06609,0.09635]},{"body_a":"peg","body_b":"channel_base_body","contact_count":240.0,"contact_point_centroid":[0.49809,0.00276,0.00832],"force_p95":85.79319,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":101.94222,"mean_force":14.6185,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50171,-0.04829,0.0967]},{"body_a":"peg","body_b":"link7","contact_count":48.0,"contact_point_centroid":[0.49607,0.05383,0.06415],"force_p95":97.14846,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":101.78488,"mean_force":69.97802,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50067,0.0098,0.0979]},{"body_a":"peg","body_b":"channel_base_body","contact_count":264.0,"contact_point_centroid":[0.49593,0.05985,0.00942],"force_p95":81.91333,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":91.18558,"mean_force":12.87962,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.49191,0.05138,0.10336]},{"body_a":"peg","body_b":"link7","contact_count":51.0,"contact_point_centroid":[0.49504,0.07408,0.06003],"force_p95":86.7772,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":90.94196,"mean_force":64.0049,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.49839,0.02642,0.09903]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.52504,-0.03826,0.05995],"force_p95":79.84357,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":87.21725,"mean_force":31.31916,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50333,-0.09196,0.09572]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.475,0.11997,0.05998],"force_p95":53.3386,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":53.3386,"mean_force":53.3386,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48389,0.0671,0.10723]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49557,-0.00426,0.00805],"force_p95":0.68341,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.89326,"mean_force":0.62101,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50113,-0.09213,0.13973]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.475,0.0199,0.02429],"force_p95":7.3226,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.54241,"mean_force":2.42348,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50098,-0.09214,0.14946]},{"body_a":"peg","body_b":"channel_base_body","contact_count":655.0,"contact_point_centroid":[0.49527,0.06391,0.00937],"force_p95":0.56691,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55855,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48666,0.14347,0.22239]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50405,0.21533,0.29299]},{"body_a":"peg","body_b":"channel_base_body","contact_count":252.0,"contact_point_centroid":[0.49507,0.06383,0.0094],"force_p95":0.55041,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55239,"mean_force":0.5454,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48115,0.06915,0.13107]}],"total_contact_groups":15},"final_pose_error":0.01115,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49597,-0.00416,0.02414],"final_tcp_position":[0.5012,-0.09211,0.18474],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":299.32861,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":682.0,"n_steps_budget":1000.0,"object_pos_end":[0.49506,0.06365,0.03397],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14386,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54268,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":683.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_peg","tcp_end":[0.48004,0.07194,0.15614],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12337,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":252.0,"n_steps_budget":660.0,"object_pos_end":[0.49509,0.0636,0.034],"object_pos_start":[0.49506,0.06365,0.03397],"object_to_goal_dist_end":0.14381,"object_to_goal_dist_start":0.14386,"object_z_max":0.034,"peak_contact_force":53.3386,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":253.0,"raw_peak_contact_force":53.3386,"subtask_id":"reach_peg","tcp_end":[0.48392,0.0671,0.10707],"tcp_start":[0.48004,0.07194,0.15614],"tcp_to_object_dist_end":0.074,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":264.0,"n_steps_budget":600.0,"object_pos_end":[0.49644,0.05086,0.03543],"object_pos_start":[0.49509,0.0636,0.034],"object_to_goal_dist_end":0.13098,"object_to_goal_dist_start":0.14381,"object_z_max":0.03541,"peak_contact_force":81.3029,"phase_name":"center_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":515.0,"raw_peak_contact_force":290.44121,"subtask_id":"center_at_channel","tcp_end":[0.49984,0.01948,0.09779],"tcp_start":[0.48392,0.0671,0.10707],"tcp_to_object_dist_end":0.06989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":265.0,"n_steps_budget":900.0,"object_pos_end":[0.49773,-0.0042,0.02413],"object_pos_start":[0.49644,0.05086,0.03543],"object_to_goal_dist_end":0.07748,"object_to_goal_dist_start":0.13098,"object_z_max":0.04045,"peak_contact_force":281.88712,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":477.0,"raw_peak_contact_force":299.32861,"subtask_id":"traverse_channel","tcp_end":[0.50338,-0.09193,0.09567],"tcp_start":[0.49984,0.01948,0.09779],"tcp_to_object_dist_end":0.11335,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49597,-0.00416,0.02414],"object_pos_start":[0.49773,-0.0042,0.02413],"object_to_goal_dist_end":0.07759,"object_to_goal_dist_start":0.07748,"object_z_max":0.02432,"peak_contact_force":0.61315,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":551.0,"raw_peak_contact_force":87.21725,"tcp_end":[0.5012,-0.09211,0.18474],"tcp_start":[0.50338,-0.09193,0.09567],"tcp_to_object_dist_end":0.18318,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93798,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.17085,"center_at_channel.align_height":0.09041,"descend_to_peg.descend_force":10.836,"push_through_channel.push_distance":0.14191},"optimized_scores":{"best_composite_score":0.12033,"best_fitness_score":0.21033,"best_task_score":0.1454},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":253.0,"contact_point_centroid":[0.52503,-0.0087,0.05997],"force_p95":327.26155,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":370.03806,"mean_force":257.71672,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50396,-0.06268,0.09597]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":114.0,"contact_point_centroid":[0.47498,0.11427,0.05998],"force_p95":188.65419,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":222.95033,"mean_force":133.17764,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.49091,0.04083,0.10537]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":39.0,"contact_point_centroid":[0.47499,0.05646,0.05998],"force_p95":146.36312,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":214.47359,"mean_force":91.80053,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50159,-0.02985,0.09645]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":128.0,"contact_point_centroid":[0.475,0.09118,0.05999],"force_p95":122.09966,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":139.47685,"mean_force":55.07844,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50423,-0.06122,0.09606]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.475,0.06951,0.05999],"force_p95":121.55467,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":124.77453,"mean_force":92.57591,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50682,-0.07052,0.0962]},{"body_a":"peg","body_b":"channel_base_body","contact_count":170.0,"contact_point_centroid":[0.49581,0.05412,0.00939],"force_p95":91.61546,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":107.08383,"mean_force":15.59191,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.49115,0.04034,0.10521]},{"body_a":"peg","body_b":"link7","contact_count":43.0,"contact_point_centroid":[0.49445,0.07151,0.0591],"force_p95":97.7135,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":107.03051,"mean_force":59.63691,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.49817,0.02346,0.09908]},{"body_a":"peg","body_b":"channel_base_body","contact_count":366.0,"contact_point_centroid":[0.49386,-0.00231,0.00836],"force_p95":84.31219,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":100.39067,"mean_force":12.36486,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50324,-0.04799,0.09629]},{"body_a":"peg","body_b":"link7","contact_count":59.0,"contact_point_centroid":[0.4968,0.0513,0.06273],"force_p95":96.28142,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":100.35707,"mean_force":72.26426,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50125,0.00649,0.0975]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47498,0.11999,0.05998],"force_p95":66.1358,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":66.1358,"mean_force":66.1358,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48084,0.06169,0.11343]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.52504,-0.0153,0.05995],"force_p95":11.86303,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":13.9565,"mean_force":3.48913,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50681,-0.07055,0.09626]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":14.0,"contact_point_centroid":[0.475,-0.03334,0.02427],"force_p95":9.8783,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.12382,"mean_force":3.56728,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5023,-0.04727,0.09618]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49344,-0.00898,0.00806],"force_p95":0.68611,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.84718,"mean_force":0.63811,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50461,-0.0708,0.14025]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.475,-0.03392,0.02422],"force_p95":9.25494,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.34836,"mean_force":2.90988,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50457,-0.07079,0.15959]},{"body_a":"peg","body_b":"channel_base_body","contact_count":597.0,"contact_point_centroid":[0.49441,0.05902,0.00936],"force_p95":0.56412,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57071,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48055,0.14237,0.2482]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50221,0.22049,0.28755]}],"total_contact_groups":17},"final_pose_error":0.01115,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49333,-0.00914,0.02412],"final_tcp_position":[0.50467,-0.07077,0.18525],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":370.03806,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":626.0,"n_steps_budget":1000.0,"object_pos_end":[0.49402,0.05904,0.03388],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.1393,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54246,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":632.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_peg","tcp_end":[0.46763,0.06853,0.21325],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.18155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":533.0,"n_steps_budget":1000.0,"object_pos_end":[0.49425,0.05913,0.03395],"object_pos_start":[0.49402,0.05904,0.03388],"object_to_goal_dist_end":0.13938,"object_to_goal_dist_start":0.1393,"object_z_max":0.03395,"peak_contact_force":66.1358,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":534.0,"raw_peak_contact_force":66.1358,"subtask_id":"reach_peg","tcp_end":[0.48088,0.06169,0.11325],"tcp_start":[0.46763,0.06853,0.21325],"tcp_to_object_dist_end":0.08046,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":170.0,"n_steps_budget":600.0,"object_pos_end":[0.49558,0.04948,0.03459],"object_pos_start":[0.49425,0.05913,0.03395],"object_to_goal_dist_end":0.12967,"object_to_goal_dist_start":0.13938,"object_z_max":0.03457,"peak_contact_force":0.98354,"phase_name":"center_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":327.0,"raw_peak_contact_force":222.95033,"subtask_id":"center_at_channel","tcp_end":[0.50021,0.01872,0.09738],"tcp_start":[0.48088,0.06169,0.11325],"tcp_to_object_dist_end":0.07007,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":383.0,"n_steps_budget":900.0,"object_pos_end":[0.49328,-0.00894,0.02413],"object_pos_start":[0.49558,0.04948,0.03459],"object_to_goal_dist_end":0.07312,"object_to_goal_dist_start":0.12967,"object_z_max":0.04045,"peak_contact_force":298.21379,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":859.0,"raw_peak_contact_force":370.03806,"subtask_id":"traverse_channel","tcp_end":[0.50684,-0.0705,0.09618],"tcp_start":[0.50021,0.01872,0.09738],"tcp_to_object_dist_end":0.09573,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49333,-0.00914,0.02412],"object_pos_start":[0.49328,-0.00894,0.02413],"object_to_goal_dist_end":0.07293,"object_to_goal_dist_start":0.07312,"object_z_max":0.02442,"peak_contact_force":0.73896,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":556.0,"raw_peak_contact_force":124.77453,"tcp_end":[0.50467,-0.07077,0.18525],"tcp_start":[0.50684,-0.0705,0.09618],"tcp_to_object_dist_end":0.17289,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95035,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.14985,"center_at_channel.align_height":0.13201,"descend_to_peg.descend_force":11.12833,"push_through_channel.push_distance":0.16409},"optimized_scores":{"best_composite_score":0.14764,"best_fitness_score":0.23764,"best_task_score":0.10762},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":98.0,"contact_point_centroid":[0.52503,-0.00643,0.05996],"force_p95":424.90034,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":425.12952,"mean_force":352.14169,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51496,-0.06925,0.07892]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":365.0,"contact_point_centroid":[0.47496,0.11993,0.05996],"force_p95":148.55132,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":204.87977,"mean_force":68.84119,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.51007,0.07554,0.07013]},{"body_a":"peg","body_b":"link7","contact_count":171.0,"contact_point_centroid":[0.50445,0.06079,0.06176],"force_p95":145.94068,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":152.14896,"mean_force":114.9511,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51451,0.003,0.08457]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":431.0,"contact_point_centroid":[0.52501,0.11988,0.05965],"force_p95":123.07742,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":144.52288,"mean_force":70.33558,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.51085,0.07388,0.07075]},{"body_a":"peg","body_b":"channel_base_body","contact_count":318.0,"contact_point_centroid":[0.5029,0.02486,0.0087],"force_p95":131.13365,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":138.43517,"mean_force":57.24139,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51445,-0.02183,0.08269]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.52503,-0.00708,0.05995],"force_p95":112.90438,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":129.40205,"mean_force":37.30428,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51681,-0.07109,0.0757]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":162.0,"contact_point_centroid":[0.5251,0.05129,0.04666],"force_p95":44.31255,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.44132,"mean_force":28.8679,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51436,0.00662,0.08449]},{"body_a":"peg","body_b":"channel_base_body","contact_count":515.0,"contact_point_centroid":[0.5103,0.0764,0.0095],"force_p95":33.93354,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.25265,"mean_force":19.53193,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.5108,0.07357,0.07104]},{"body_a":"attachment","body_b":"peg","contact_count":434.0,"contact_point_centroid":[0.50994,0.07863,0.05868],"force_p95":33.48196,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.89831,"mean_force":22.60772,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.51019,0.07555,0.07004]},{"body_a":"peg","body_b":"channel_base_body","contact_count":527.0,"contact_point_centroid":[0.50601,0.08086,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.96126,"mean_force":0.58741,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.5182,0.08447,0.13139]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50683,0.09883,0.05871],"force_p95":21.54432,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.54432,"mean_force":21.54432,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50683,0.08076,0.07079]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":273.0,"contact_point_centroid":[0.52506,0.07963,0.03743],"force_p95":6.63105,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.52917,"mean_force":2.04712,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.51303,0.07149,0.0708]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":14.0,"contact_point_centroid":[0.47492,-0.02623,0.02432],"force_p95":8.5668,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.95204,"mean_force":2.57508,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51454,-0.06906,0.07978]},{"body_a":"peg","body_b":"channel_base_body","contact_count":587.0,"contact_point_centroid":[0.5057,0.08086,0.00936],"force_p95":0.55707,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57276,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50958,0.1521,0.23897]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50278,0.22142,0.28712]},{"body_a":"peg","body_b":"channel_base_body","contact_count":573.0,"contact_point_centroid":[0.49699,-0.00336,0.00805],"force_p95":0.68341,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69521,"mean_force":0.60629,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51427,-0.07124,0.11964]}],"total_contact_groups":16},"final_pose_error":0.01107,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49866,-0.00346,0.02413],"final_tcp_position":[0.51435,-0.0712,0.16493],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":425.12952,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":616.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54526,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":623.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.53068,0.08893,0.19281],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16114,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":527.0,"n_steps_budget":900.0,"object_pos_end":[0.50594,0.08088,0.03377],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16111,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":21.96126,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":528.0,"raw_peak_contact_force":21.96126,"subtask_id":"reach_peg","tcp_end":[0.50679,0.08075,0.07056],"tcp_start":[0.53068,0.08893,0.19281],"tcp_to_object_dist_end":0.0368,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":515.0,"n_steps_budget":660.0,"object_pos_end":[0.50698,0.07939,0.03399],"object_pos_start":[0.50594,0.08088,0.03377],"object_to_goal_dist_end":0.15966,"object_to_goal_dist_start":0.16111,"object_z_max":0.0347,"peak_contact_force":0.57761,"phase_name":"center_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2018.0,"raw_peak_contact_force":204.87977,"subtask_id":"center_at_channel","tcp_end":[0.51274,0.0521,0.08373],"tcp_start":[0.50679,0.08075,0.07056],"tcp_to_object_dist_end":0.05702,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":329.0,"n_steps_budget":1000.0,"object_pos_end":[0.49512,-0.00318,0.02434],"object_pos_start":[0.50698,0.07939,0.03399],"object_to_goal_dist_end":0.07855,"object_to_goal_dist_start":0.15966,"object_z_max":0.0381,"peak_contact_force":423.20451,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":763.0,"raw_peak_contact_force":425.12952,"subtask_id":"traverse_channel","tcp_end":[0.51685,-0.07102,0.07571],"tcp_start":[0.51274,0.0521,0.08373],"tcp_to_object_dist_end":0.08782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.49866,-0.00346,0.02413],"object_pos_start":[0.49512,-0.00318,0.02434],"object_to_goal_dist_end":0.07818,"object_to_goal_dist_start":0.07855,"object_z_max":0.02434,"peak_contact_force":0.60163,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":577.0,"raw_peak_contact_force":129.40205,"tcp_end":[0.51435,-0.0712,0.16493],"tcp_start":[0.51685,-0.07102,0.07571],"tcp_to_object_dist_end":0.15703,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```