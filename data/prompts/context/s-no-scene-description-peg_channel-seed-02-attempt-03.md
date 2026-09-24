## Search State

- **Seed**: 2
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.1936 | 0.13 | ❌ rejected |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.1931 | 0.13 | ❌ rejected |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.1968 | 0.13 | ✅ accepted |
| 0 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.1029 | 0.13 | ✅ accepted |

**Proposal policy**: task_score is 0.13 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.194) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: push_channel
  weight: 0.8
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
  subtask_id: approach_peg
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
      default: 10
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
  subtask_id: approach_peg
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
  subtask_id: push_channel
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

- **Composite score**: 0.194
- **task_score** (E): 0.125
- **fitness_score**: 0.154  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1628 |
| descend_to_peg | 1.00 | 1.00 | 0.1062 |
| push_through_channel | 0.67 | 1.00 | 0.0968 |
| retract_up | 1.00 | 1.00 | 0.0892 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.493, 0.077, 0.201) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.545 | 3.659 |
| descend_to_peg | descend | 1.00 / force_exceeded | (0.493, 0.077, 0.201)→(0.492, 0.069, 0.097) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.000 | 40.463 | 40.463 |
| push_through_channel | push | 0.67 / step_budget | (0.492, 0.069, 0.097)→(0.498, -0.022, 0.095) | (0.498, 0.068, 0.034)→(0.503, 0.029, 0.027) | 0.148→0.110 | 1.00 / 2.667 | 43.035 | 311.635 |
| retract_up | retract | 1.00 / step_budget | (0.498, -0.022, 0.095)→(0.496, -0.023, 0.185) | (0.503, 0.029, 0.027)→(0.498, 0.029, 0.027) | 0.110→0.110 | 1.00 / 1.000 | 0.425 | 118.181 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.376
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.247
- phase_score: 0.245
- phase_breakdown.approach_peg_score: 0.188
- phase_breakdown.push_channel_score: 0.259

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.246
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.247
- **Median Q (composite search score)**: 0.229
- **K-run variance**: 0.0086
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.334


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.96491,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.15917,"descend_to_peg.descend_force":11.08925,"push_through_channel.push_distance":0.16764},"optimized_scores":{"best_composite_score":0.28578,"best_fitness_score":0.24578,"best_task_score":0.2471},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":140.0,"contact_point_centroid":[0.47498,0.07505,0.05997],"force_p95":204.35211,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":221.79504,"mean_force":143.57706,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48937,0.00742,0.10655]},{"body_a":"peg","body_b":"channel_base_body","contact_count":283.0,"contact_point_centroid":[0.49719,0.03531,0.00892],"force_p95":93.83065,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":105.29134,"mean_force":20.57834,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48954,0.00449,0.10668]},{"body_a":"peg","body_b":"link7","contact_count":70.0,"contact_point_centroid":[0.49406,0.06239,0.0631],"force_p95":101.19909,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":104.91605,"mean_force":80.95628,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48957,0.01011,0.1071]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.475,0.00023,0.06],"force_p95":95.21283,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":97.99431,"mean_force":70.17943,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49028,-0.07246,0.10643]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47499,0.11999,0.05999],"force_p95":44.33227,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":44.33227,"mean_force":44.33227,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48675,0.06615,0.10694]},{"body_a":"peg","body_b":"channel_base_body","contact_count":573.0,"contact_point_centroid":[0.4989,0.00345,0.00807],"force_p95":0.72592,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.73418,"mean_force":0.66575,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48813,-0.07257,0.15068]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":13.0,"contact_point_centroid":[0.52509,0.02828,0.02468],"force_p95":9.2654,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.38571,"mean_force":2.39198,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.4894,-0.07341,0.10913]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.47498,-0.02103,0.02428],"force_p95":7.41473,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.15677,"mean_force":2.1321,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48809,-0.07244,0.17955]},{"body_a":"peg","body_b":"channel_base_body","contact_count":592.0,"contact_point_centroid":[0.49529,0.06388,0.00937],"force_p95":0.57532,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55992,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48658,0.14519,0.24339]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47497,0.00052,0.0524],"force_p95":1.48297,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.51176,"mean_force":1.23946,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48949,-0.0174,0.10706]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50391,0.21523,0.29291]},{"body_a":"peg","body_b":"channel_base_body","contact_count":481.0,"contact_point_centroid":[0.49511,0.06397,0.0094],"force_p95":0.55084,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54537,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48283,0.06935,0.15376]}],"total_contact_groups":12},"final_pose_error":0.01063,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4943,0.00378,0.02414],"final_tcp_position":[0.48824,-0.07242,0.19596],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":221.79504,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":619.0,"n_steps_budget":1000.0,"object_pos_end":[0.49514,0.06366,0.03395],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14387,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54109,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":620.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach_peg","tcp_end":[0.48057,0.07328,0.20237],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16932,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":481.0,"n_steps_budget":930.0,"object_pos_end":[0.49495,0.06363,0.03402],"object_pos_start":[0.49514,0.06366,0.03395],"object_to_goal_dist_end":0.14384,"object_to_goal_dist_start":0.14387,"object_z_max":0.03402,"peak_contact_force":44.33227,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":482.0,"raw_peak_contact_force":44.33227,"subtask_id":"approach_peg","tcp_end":[0.48676,0.06614,0.1068],"tcp_start":[0.48057,0.07328,0.20237],"tcp_to_object_dist_end":0.07329,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":297.0,"n_steps_budget":1000.0,"object_pos_end":[0.50534,0.00342,0.02411],"object_pos_start":[0.49495,0.06363,0.03402],"object_to_goal_dist_end":0.08509,"object_to_goal_dist_start":0.14384,"object_z_max":0.03999,"peak_contact_force":128.48042,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":496.0,"raw_peak_contact_force":221.79504,"subtask_id":"push_channel","tcp_end":[0.49032,-0.07214,0.10638],"tcp_start":[0.48676,0.06614,0.1068],"tcp_to_object_dist_end":0.11271,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.4943,0.00378,0.02414],"object_pos_start":[0.50534,0.00342,0.02411],"object_to_goal_dist_end":0.08546,"object_to_goal_dist_start":0.08509,"object_z_max":0.02513,"peak_contact_force":0.72739,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":593.0,"raw_peak_contact_force":97.99431,"tcp_end":[0.48824,-0.07242,0.19596],"tcp_start":[0.49032,-0.07214,0.10638],"tcp_to_object_dist_end":0.18805,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9661,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.19658,"descend_to_peg.descend_force":6.92877,"push_through_channel.push_distance":0.1707},"optimized_scores":{"best_composite_score":0.22851,"best_fitness_score":0.18851,"best_task_score":0.12925},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":90.0,"contact_point_centroid":[0.47499,0.06349,0.05998],"force_p95":159.49293,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":201.40447,"mean_force":122.82805,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48422,-0.0011,0.1116]},{"body_a":"peg","body_b":"channel_base_body","contact_count":253.0,"contact_point_centroid":[0.49608,0.03196,0.00897],"force_p95":105.9363,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.29259,"mean_force":32.31036,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48443,-0.00371,0.11179]},{"body_a":"peg","body_b":"link7","contact_count":93.0,"contact_point_centroid":[0.4883,0.04967,0.06297],"force_p95":111.3824,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":116.92433,"mean_force":86.37275,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48466,-0.00673,0.1121]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.475,-0.01475,0.06],"force_p95":86.77317,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.77317,"mean_force":86.77317,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48498,-0.08076,0.11118]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47497,0.11999,0.05996],"force_p95":57.52393,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":57.52393,"mean_force":57.52393,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48255,0.06117,0.11222]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49337,-0.00315,0.00812],"force_p95":0.80146,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.02442,"mean_force":0.94511,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48309,-0.0803,0.15539]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":45.0,"contact_point_centroid":[0.47498,-0.00043,0.02459],"force_p95":9.42338,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.57855,"mean_force":4.43112,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48314,-0.08045,0.13046]},{"body_a":"peg","body_b":"channel_base_body","contact_count":592.0,"contact_point_centroid":[0.49439,0.05889,0.00936],"force_p95":0.56469,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57092,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48055,0.14236,0.25901]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50213,0.22043,0.28756]},{"body_a":"peg","body_b":"channel_base_body","contact_count":655.0,"contact_point_centroid":[0.49403,0.05909,0.00939],"force_p95":0.55018,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54585,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.47436,0.06456,0.17365]}],"total_contact_groups":10},"final_pose_error":0.01084,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49381,-0.00305,0.02413],"final_tcp_position":[0.48318,-0.08015,0.20043],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":201.40447,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":621.0,"n_steps_budget":990.0,"object_pos_end":[0.49423,0.05904,0.03388],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13929,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54625,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":627.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach_peg","tcp_end":[0.46781,0.06866,0.2371],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.20516,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":655.0,"n_steps_budget":1000.0,"object_pos_end":[0.49397,0.05878,0.03397],"object_pos_start":[0.49423,0.05904,0.03388],"object_to_goal_dist_end":0.13904,"object_to_goal_dist_start":0.13929,"object_z_max":0.03397,"peak_contact_force":57.52393,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":656.0,"raw_peak_contact_force":57.52393,"subtask_id":"approach_peg","tcp_end":[0.48258,0.06117,0.11205],"tcp_start":[0.46781,0.06866,0.2371],"tcp_to_object_dist_end":0.07895,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":269.0,"n_steps_budget":1000.0,"object_pos_end":[0.49533,-0.00271,0.02396],"object_pos_start":[0.49397,0.05878,0.03397],"object_to_goal_dist_end":0.07908,"object_to_goal_dist_start":0.13904,"object_z_max":0.03901,"peak_contact_force":0.62573,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":436.0,"raw_peak_contact_force":201.40447,"subtask_id":"push_channel","tcp_end":[0.4852,-0.07991,0.11108],"tcp_start":[0.48258,0.06117,0.11205],"tcp_to_object_dist_end":0.11684,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49381,-0.00305,0.02413],"object_pos_start":[0.49533,-0.00271,0.02396],"object_to_goal_dist_end":0.07881,"object_to_goal_dist_start":0.07908,"object_z_max":0.02545,"peak_contact_force":0.53262,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":589.0,"raw_peak_contact_force":86.77317,"tcp_end":[0.48318,-0.08015,0.20043],"tcp_start":[0.4852,-0.07991,0.11108],"tcp_to_object_dist_end":0.19272,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.96429,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.11951,"descend_to_peg.descend_force":9.47417,"push_through_channel.push_distance":0.14002},"optimized_scores":{"best_composite_score":0.0666,"best_fitness_score":0.0266,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":645.0,"contact_point_centroid":[0.47495,0.11991,0.05998],"force_p95":325.81906,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":511.70545,"mean_force":232.30548,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51378,0.08183,0.0681]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":97.0,"contact_point_centroid":[0.525,0.08746,0.06],"force_p95":265.69629,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.85972,"mean_force":108.86311,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51688,0.08475,0.06839]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":65.0,"contact_point_centroid":[0.52501,0.11966,0.05724],"force_p95":196.66491,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":201.6277,"mean_force":137.07078,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50801,0.07863,0.0693]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.47496,0.11989,0.05998],"force_p95":168.57331,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":169.77529,"mean_force":112.91959,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51747,0.08595,0.06904]},{"body_a":"peg","body_b":"channel_base_body","contact_count":697.0,"contact_point_centroid":[0.51353,0.08406,0.00901],"force_p95":58.9074,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.74571,"mean_force":48.49147,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51333,0.08161,0.06821]},{"body_a":"attachment","body_b":"peg","contact_count":697.0,"contact_point_centroid":[0.5132,0.08286,0.05714],"force_p95":57.68561,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":73.58613,"mean_force":47.75178,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51333,0.08161,0.06821]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.51706,0.08713,0.05818],"force_p95":42.52451,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.81008,"mean_force":9.39408,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51732,0.08622,0.06969]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.5059,0.08532,0.00941],"force_p95":0.6031,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.99033,"mean_force":0.79087,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51516,0.08492,0.11262]},{"body_a":"peg","body_b":"channel_base_body","contact_count":401.0,"contact_point_centroid":[0.50602,0.0809,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.53205,"mean_force":0.59411,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51873,0.0842,0.11732]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50784,0.09872,0.05879],"force_p95":19.13485,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.13485,"mean_force":19.13485,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50785,0.08095,0.07095]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":513.0,"contact_point_centroid":[0.52517,0.08268,0.04526],"force_p95":9.44279,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.60545,"mean_force":3.1278,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51484,0.08251,0.06799]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":230.0,"contact_point_centroid":[0.52502,0.08507,0.0469],"force_p95":0.25749,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.7442,"mean_force":0.21195,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51538,0.0851,0.10265]},{"body_a":"peg","body_b":"channel_base_body","contact_count":628.0,"contact_point_centroid":[0.50574,0.08085,0.00936],"force_p95":0.55644,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57106,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50991,0.15126,0.2261]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50282,0.22149,0.28711]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.0887,0.06],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.5175,0.08591,0.06895]}],"total_contact_groups":15},"final_pose_error":0.01165,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50698,0.08505,0.03378],"final_tcp_position":[0.5152,0.08487,0.15758],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":511.70545,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":657.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.5464,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":664.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach_peg","tcp_end":[0.53059,0.08822,0.16413],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":401.0,"n_steps_budget":720.0,"object_pos_end":[0.50595,0.08086,0.03377],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":19.53205,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":402.0,"raw_peak_contact_force":19.53205,"subtask_id":"approach_peg","tcp_end":[0.5078,0.08094,0.07071],"tcp_start":[0.53059,0.08822,0.16413],"tcp_to_object_dist_end":0.03699,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":697.0,"n_steps_budget":900.0,"object_pos_end":[0.5073,0.08487,0.03347],"object_pos_start":[0.50595,0.08086,0.03377],"object_to_goal_dist_end":0.16516,"object_to_goal_dist_start":0.16109,"object_z_max":0.03417,"peak_contact_force":0.0,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2714.0,"raw_peak_contact_force":511.70545,"subtask_id":"push_channel","tcp_end":[0.5175,0.08591,0.06895],"tcp_start":[0.5078,0.08094,0.07071],"tcp_to_object_dist_end":0.03693,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.50698,0.08505,0.03378],"object_pos_start":[0.5073,0.08487,0.03347],"object_to_goal_dist_end":0.16532,"object_to_goal_dist_start":0.16516,"object_z_max":0.03422,"peak_contact_force":0.0137,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":793.0,"raw_peak_contact_force":169.77529,"tcp_end":[0.5152,0.08487,0.15758],"tcp_start":[0.5175,0.08591,0.06895],"tcp_to_object_dist_end":0.12407,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```