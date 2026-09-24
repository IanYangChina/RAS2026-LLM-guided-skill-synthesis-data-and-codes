## Search State

- **Seed**: 2
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1390 | 0.19 | ✅ accepted |
| 13 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.0258 | 0.00 | ❌ rejected |
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 4 | 0.2612 | 0.00 | ❌ rejected |
| 11 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | force_threshold_switch | position_control | pose_tolerance | force_exceeded | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.0941 | 0.02 | ❌ rejected |
| 10 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1441 | 0.17 | ❌ rejected |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.139) — your mutation base

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

- **Composite score**: 0.139
- **task_score** (E): 0.192
- **fitness_score**: 0.229  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.290

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1583 |
| descend_to_peg | 1.00 | 1.00 | 0.1085 |
| center_at_channel | 0.67 | 1.00 | 0.0482 |
| push_through_channel | 0.67 | 1.00 | 0.1025 |
| retract_up | 1.00 | 1.00 | 0.0892 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.493, 0.077, 0.204) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.547 | 3.659 |
| descend_to_peg | descend | 1.00 / force_exceeded | (0.493, 0.077, 0.204)→(0.491, 0.070, 0.097) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.000 | 56.904 | 56.904 |
| center_at_channel | align | 0.67 / step_budget | (0.491, 0.070, 0.097)→(0.503, 0.027, 0.095) | (0.498, 0.068, 0.034)→(0.500, 0.060, 0.035) | 0.148→0.140 | 1.00 / 2.000 | 67.119 | 268.455 |
| push_through_channel | push | 0.67 / step_budget | (0.503, 0.027, 0.095)→(0.508, -0.076, 0.094) | (0.500, 0.060, 0.035)→(0.496, -0.009, 0.025) | 0.140→0.072 | 1.00 / 2.000 | 230.665 | 302.785 |
| retract_up | retract | 1.00 / step_budget | (0.508, -0.076, 0.094)→(0.506, -0.076, 0.183) | (0.496, -0.009, 0.025)→(0.498, -0.009, 0.024) | 0.072→0.073 | 1.00 / 1.000 | 0.597 | 84.173 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.406
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.261
- phase_score: 0.253
- phase_breakdown.center_at_channel_score: 0.000
- phase_breakdown.reach_peg_score: 0.188
- phase_breakdown.traverse_channel_score: 0.321

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.256
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.261
- **Median Q (composite search score)**: 0.136
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.375


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93798,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.15899,"center_at_channel.align_height":0.09465,"descend_to_peg.descend_force":9.71396,"push_through_channel.push_distance":0.14076},"optimized_scores":{"best_composite_score":0.16639,"best_fitness_score":0.25639,"best_task_score":0.2614},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":62.0,"contact_point_centroid":[0.52501,-0.03054,0.05999],"force_p95":281.94615,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":286.79737,"mean_force":239.26957,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50231,-0.08348,0.09623]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":140.0,"contact_point_centroid":[0.47498,0.11837,0.05997],"force_p95":202.81306,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":235.33245,"mean_force":136.4138,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.49251,0.05175,0.10354]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":29.0,"contact_point_centroid":[0.47499,0.06767,0.05999],"force_p95":140.057,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":153.296,"mean_force":109.72901,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50091,-0.01794,0.09715]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":67.0,"contact_point_centroid":[0.47499,0.09828,0.05999],"force_p95":134.4058,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":147.73971,"mean_force":78.24564,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50186,-0.06545,0.09646]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.52503,-0.03657,0.05997],"force_p95":93.12762,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":107.82162,"mean_force":29.4208,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50298,-0.09002,0.09584]},{"body_a":"peg","body_b":"channel_base_body","contact_count":233.0,"contact_point_centroid":[0.49736,0.00621,0.00842],"force_p95":85.66919,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":100.54797,"mean_force":14.84633,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5015,-0.04455,0.09687]},{"body_a":"peg","body_b":"link7","contact_count":47.0,"contact_point_centroid":[0.49591,0.05426,0.06415],"force_p95":96.84809,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":100.37691,"mean_force":70.62215,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50052,0.01024,0.09796]},{"body_a":"peg","body_b":"channel_base_body","contact_count":208.0,"contact_point_centroid":[0.4963,0.05838,0.00939],"force_p95":81.82311,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.30525,"mean_force":15.85786,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.49355,0.04772,0.10282]},{"body_a":"peg","body_b":"link7","contact_count":51.0,"contact_point_centroid":[0.49488,0.07434,0.05986],"force_p95":85.6051,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":88.03552,"mean_force":62.60133,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.49836,0.02674,0.09909]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.475,0.07446,0.06],"force_p95":70.38844,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.38844,"mean_force":70.38844,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50296,-0.09002,0.09582]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47498,0.11998,0.05997],"force_p95":44.90741,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":44.90741,"mean_force":44.90741,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48675,0.06615,0.10687]},{"body_a":"peg","body_b":"channel_base_body","contact_count":592.0,"contact_point_centroid":[0.49529,0.06388,0.00937],"force_p95":0.57532,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55992,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48658,0.14519,0.24332]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50391,0.21523,0.29291]},{"body_a":"peg","body_b":"channel_base_body","contact_count":573.0,"contact_point_centroid":[0.49536,-0.00112,0.00805],"force_p95":0.6834,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69549,"mean_force":0.60553,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50075,-0.09024,0.13992]},{"body_a":"peg","body_b":"channel_base_body","contact_count":481.0,"contact_point_centroid":[0.49511,0.06397,0.0094],"force_p95":0.55084,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54537,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48282,0.06935,0.15364]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.02314,0.02418],"force_p95":0.39359,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39359,"mean_force":0.39359,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.5007,-0.09024,0.17269]}],"total_contact_groups":16},"final_pose_error":0.01084,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49476,-0.00116,0.02421],"final_tcp_position":[0.50084,-0.09022,0.1852],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":286.79737,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":619.0,"n_steps_budget":1000.0,"object_pos_end":[0.49514,0.06366,0.03395],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14387,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54109,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":620.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_peg","tcp_end":[0.48057,0.07328,0.2022],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16915,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":481.0,"n_steps_budget":930.0,"object_pos_end":[0.49495,0.06363,0.03402],"object_pos_start":[0.49514,0.06366,0.03395],"object_to_goal_dist_end":0.14384,"object_to_goal_dist_start":0.14387,"object_z_max":0.03402,"peak_contact_force":44.90741,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":482.0,"raw_peak_contact_force":44.90741,"subtask_id":"reach_peg","tcp_end":[0.48676,0.06614,0.10674],"tcp_start":[0.48057,0.07328,0.2022],"tcp_to_object_dist_end":0.07322,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":208.0,"n_steps_budget":600.0,"object_pos_end":[0.49617,0.05099,0.03543],"object_pos_start":[0.49495,0.06363,0.03402],"object_to_goal_dist_end":0.13113,"object_to_goal_dist_start":0.14384,"object_z_max":0.0354,"peak_contact_force":80.93698,"phase_name":"center_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":399.0,"raw_peak_contact_force":235.33245,"subtask_id":"center_at_channel","tcp_end":[0.49977,0.01954,0.09792],"tcp_start":[0.48676,0.06614,0.10674],"tcp_to_object_dist_end":0.07004,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":250.0,"n_steps_budget":900.0,"object_pos_end":[0.4969,-0.00105,0.02413],"object_pos_start":[0.49617,0.05099,0.03543],"object_to_goal_dist_end":0.08059,"object_to_goal_dist_start":0.13113,"object_z_max":0.04045,"peak_contact_force":268.87254,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":438.0,"raw_peak_contact_force":286.79737,"subtask_id":"traverse_channel","tcp_end":[0.50303,-0.09002,0.09582],"tcp_start":[0.49977,0.01954,0.09792],"tcp_to_object_dist_end":0.11443,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.49476,-0.00116,0.02421],"object_pos_start":[0.4969,-0.00105,0.02413],"object_to_goal_dist_end":0.08058,"object_to_goal_dist_start":0.08059,"object_z_max":0.02425,"peak_contact_force":0.60242,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":579.0,"raw_peak_contact_force":107.82162,"tcp_end":[0.50084,-0.09022,0.1852],"tcp_start":[0.50303,-0.09002,0.09582],"tcp_to_object_dist_end":0.18408,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93985,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.14979,"center_at_channel.align_height":0.08945,"descend_to_peg.descend_force":13.82437,"push_through_channel.push_distance":0.16913},"optimized_scores":{"best_composite_score":0.11485,"best_fitness_score":0.20485,"best_task_score":0.14597},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":488.0,"contact_point_centroid":[0.52504,-0.0017,0.05995],"force_p95":407.55106,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":465.8386,"mean_force":297.73721,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50612,-0.05659,0.09621]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":132.0,"contact_point_centroid":[0.47498,0.11442,0.05996],"force_p95":356.41262,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":362.24407,"mean_force":164.59533,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.48938,0.04278,0.10662]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.47499,0.06292,0.05999],"force_p95":152.50349,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":216.2033,"mean_force":86.15394,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50171,-0.02342,0.09643]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.475,0.10182,0.06],"force_p95":135.7507,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":135.7507,"mean_force":135.7507,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51,-0.06351,0.09651]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":300.0,"contact_point_centroid":[0.475,0.09942,0.05999],"force_p95":99.4192,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":135.6468,"mean_force":62.35038,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50725,-0.05909,0.09634]},{"body_a":"peg","body_b":"channel_base_body","contact_count":188.0,"contact_point_centroid":[0.49594,0.05425,0.00938],"force_p95":93.58405,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.30197,"mean_force":15.09987,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.48994,0.04169,0.10622]},{"body_a":"peg","body_b":"link7","contact_count":46.0,"contact_point_centroid":[0.49452,0.07136,0.05911],"force_p95":100.65956,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":106.24658,"mean_force":59.63012,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.49814,0.02331,0.09911]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.475,0.12,0.05996],"force_p95":100.70585,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":100.70585,"mean_force":100.70585,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.47908,0.06191,0.11398]},{"body_a":"peg","body_b":"channel_base_body","contact_count":569.0,"contact_point_centroid":[0.49469,-0.00718,0.0082],"force_p95":83.53942,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":99.04744,"mean_force":8.15436,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50549,-0.0495,0.09633]},{"body_a":"peg","body_b":"link7","contact_count":58.0,"contact_point_centroid":[0.49698,0.05076,0.06309],"force_p95":96.98898,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":98.8299,"mean_force":74.03315,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50142,0.00633,0.09731]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.52507,-0.00709,0.0599],"force_p95":41.66123,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.01321,"mean_force":12.2533,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50998,-0.06355,0.09658]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49372,-0.01076,0.00807],"force_p95":0.70148,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.47901,"mean_force":0.65259,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50779,-0.06382,0.1406]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.475,-0.03563,0.02433],"force_p95":8.9506,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.99809,"mean_force":3.18737,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50761,-0.06384,0.14366]},{"body_a":"peg","body_b":"channel_base_body","contact_count":617.0,"contact_point_centroid":[0.49431,0.05903,0.00936],"force_p95":0.56286,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56992,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48056,0.14191,0.23928]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5023,0.22056,0.28754]},{"body_a":"peg","body_b":"channel_base_body","contact_count":434.0,"contact_point_centroid":[0.49431,0.05888,0.00939],"force_p95":0.55009,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54591,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.47236,0.06457,0.15265]}],"total_contact_groups":17},"final_pose_error":0.01111,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49383,-0.01113,0.02414],"final_tcp_position":[0.50785,-0.06379,0.18561],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":465.8386,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":646.0,"n_steps_budget":1000.0,"object_pos_end":[0.49402,0.05887,0.03388],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13913,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54907,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":652.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_peg","tcp_end":[0.46738,0.06801,0.19339],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":434.0,"n_steps_budget":900.0,"object_pos_end":[0.49407,0.05915,0.03394],"object_pos_start":[0.49402,0.05887,0.03388],"object_to_goal_dist_end":0.1394,"object_to_goal_dist_start":0.13913,"object_z_max":0.03394,"peak_contact_force":100.70585,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":435.0,"raw_peak_contact_force":100.70585,"subtask_id":"reach_peg","tcp_end":[0.47913,0.06192,0.11382],"tcp_start":[0.46738,0.06801,0.19339],"tcp_to_object_dist_end":0.08131,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":188.0,"n_steps_budget":600.0,"object_pos_end":[0.49581,0.049,0.03458],"object_pos_start":[0.49407,0.05915,0.03394],"object_to_goal_dist_end":0.12918,"object_to_goal_dist_start":0.1394,"object_z_max":0.03456,"peak_contact_force":119.85441,"phase_name":"center_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":366.0,"raw_peak_contact_force":362.24407,"subtask_id":"center_at_channel","tcp_end":[0.50037,0.01833,0.09715],"tcp_start":[0.47913,0.06192,0.11382],"tcp_to_object_dist_end":0.06984,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":593.0,"n_steps_budget":1000.0,"object_pos_end":[0.49436,-0.01073,0.02412],"object_pos_start":[0.49581,0.049,0.03458],"object_to_goal_dist_end":0.07128,"object_to_goal_dist_start":0.12918,"object_z_max":0.04045,"peak_contact_force":422.73558,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1451.0,"raw_peak_contact_force":465.8386,"subtask_id":"traverse_channel","tcp_end":[0.51,-0.06351,0.09651],"tcp_start":[0.50037,0.01833,0.09715],"tcp_to_object_dist_end":0.09093,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49383,-0.01113,0.02414],"object_pos_start":[0.49436,-0.01073,0.02412],"object_to_goal_dist_end":0.07094,"object_to_goal_dist_start":0.07128,"object_z_max":0.02454,"peak_contact_force":0.61314,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":557.0,"raw_peak_contact_force":135.7507,"tcp_end":[0.50785,-0.06379,0.18561],"tcp_start":[0.51,-0.06351,0.09651],"tcp_to_object_dist_end":0.17042,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94891,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.17594,"center_at_channel.align_height":0.13274,"descend_to_peg.descend_force":19.53115,"push_through_channel.push_distance":0.14484},"optimized_scores":{"best_composite_score":0.13566,"best_fitness_score":0.22566,"best_task_score":0.16746},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":359.0,"contact_point_centroid":[0.47498,0.11996,0.05998],"force_p95":145.08774,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":207.78764,"mean_force":80.732,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.50957,0.07568,0.07057]},{"body_a":"peg","body_b":"link7","contact_count":189.0,"contact_point_centroid":[0.5042,0.05755,0.06098],"force_p95":152.25524,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":155.7205,"mean_force":121.17375,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51209,-0.00579,0.093]},{"body_a":"peg","body_b":"channel_base_body","contact_count":225.0,"contact_point_centroid":[0.50644,0.02952,0.00893],"force_p95":134.90857,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":140.24848,"mean_force":92.82412,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51197,-0.01076,0.09276]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":389.0,"contact_point_centroid":[0.52501,0.11993,0.05963],"force_p95":122.80549,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":131.72564,"mean_force":62.10533,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.51065,0.07365,0.07124]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":174.0,"contact_point_centroid":[0.52518,0.04565,0.04507],"force_p95":47.20439,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.88815,"mean_force":32.70637,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51212,-0.00506,0.09293]},{"body_a":"peg","body_b":"channel_base_body","contact_count":515.0,"contact_point_centroid":[0.51125,0.07632,0.00958],"force_p95":28.08649,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.50907,"mean_force":13.32093,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.5104,0.07306,0.07182]},{"body_a":"attachment","body_b":"peg","contact_count":426.0,"contact_point_centroid":[0.50953,0.07854,0.05897],"force_p95":28.01216,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.09738,"mean_force":15.55056,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.50977,0.0756,0.07045]},{"body_a":"peg","body_b":"channel_base_body","contact_count":635.0,"contact_point_centroid":[0.50598,0.08084,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.09806,"mean_force":0.58543,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51791,0.08473,0.14338]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50627,0.09887,0.05869],"force_p95":24.63406,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.63406,"mean_force":24.63406,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50626,0.08064,0.07079]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":254.0,"contact_point_centroid":[0.52505,0.07991,0.04571],"force_p95":4.93181,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.21744,"mean_force":2.06353,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.51185,0.07321,0.07065]},{"body_a":"peg","body_b":"channel_base_body","contact_count":547.0,"contact_point_centroid":[0.50139,-0.01455,0.00809],"force_p95":0.79066,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.9467,"mean_force":0.7078,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50827,-0.07406,0.13327]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52501,0.00924,0.02432],"force_p95":8.29394,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.52413,"mean_force":3.4496,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50818,-0.07388,0.15302]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":16.0,"contact_point_centroid":[0.47491,-0.03708,0.02724],"force_p95":6.32331,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.66818,"mean_force":2.04692,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50949,-0.07544,0.09104]},{"body_a":"peg","body_b":"channel_base_body","contact_count":558.0,"contact_point_centroid":[0.50569,0.0809,0.00936],"force_p95":0.55751,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57411,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50943,0.15235,0.24953]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50273,0.22133,0.28713]}],"total_contact_groups":15},"final_pose_error":0.01127,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50513,-0.01409,0.02413],"final_tcp_position":[0.50839,-0.07386,0.17859],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":207.78764,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":587.0,"n_steps_budget":930.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.55007,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":594.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.53072,0.08954,0.2173],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.18538,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":635.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.0809,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":25.09806,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":636.0,"raw_peak_contact_force":25.09806,"subtask_id":"reach_peg","tcp_end":[0.50623,0.08063,0.07056],"tcp_start":[0.53072,0.08954,0.2173],"tcp_to_object_dist_end":0.03679,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":515.0,"n_steps_budget":660.0,"object_pos_end":[0.50692,0.07964,0.0338],"object_pos_start":[0.50596,0.0809,0.03378],"object_to_goal_dist_end":0.15991,"object_to_goal_dist_start":0.16113,"object_z_max":0.03496,"peak_contact_force":0.56522,"phase_name":"center_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1943.0,"raw_peak_contact_force":207.78764,"subtask_id":"center_at_channel","tcp_end":[0.51033,0.04176,0.09133],"tcp_start":[0.50623,0.08063,0.07056],"tcp_to_object_dist_end":0.06897,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":236.0,"n_steps_budget":900.0,"object_pos_end":[0.49613,-0.01592,0.02764],"object_pos_start":[0.50692,0.07964,0.0338],"object_to_goal_dist_end":0.06538,"object_to_goal_dist_start":0.15991,"object_z_max":0.03815,"peak_contact_force":0.3859,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":588.0,"raw_peak_contact_force":155.7205,"subtask_id":"traverse_channel","tcp_end":[0.51072,-0.07364,0.08961],"tcp_start":[0.51033,0.04176,0.09133],"tcp_to_object_dist_end":0.08594,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":547.0,"n_steps_budget":630.0,"object_pos_end":[0.50513,-0.01409,0.02413],"object_pos_start":[0.49613,-0.01592,0.02764],"object_to_goal_dist_end":0.06798,"object_to_goal_dist_start":0.06538,"object_z_max":0.0277,"peak_contact_force":0.57444,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":573.0,"raw_peak_contact_force":8.9467,"tcp_end":[0.50839,-0.07386,0.17859],"tcp_start":[0.51072,-0.07364,0.08961],"tcp_to_object_dist_end":0.16565,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```