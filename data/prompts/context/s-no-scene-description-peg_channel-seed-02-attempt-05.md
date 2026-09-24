## Search State

- **Seed**: 2
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.0612 | 0.00 | ❌ rejected |
| 4 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1447 | 0.17 | ✅ accepted |
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.1936 | 0.13 | ❌ rejected |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.1931 | 0.13 | ❌ rejected |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.1968 | 0.13 | ✅ accepted |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.061) — your mutation base

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

- **Composite score**: 0.061
- **task_score** (E): 0.001
- **fitness_score**: 0.048  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.320

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1614 |
| descend_to_peg | 1.00 | 1.00 | 0.1044 |
| center_at_entrance | 1.00 | 1.00 | 0.0288 |
| seat_in_channel | 1.00 | 1.00 | 0.0330 |
| push_through_channel | 0.00 | 1.00 | 0.0001 |
| retract_up | 1.00 | 1.00 | 0.0888 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.493, 0.077, 0.200) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.546 | 3.659 |
| descend_to_peg | descend | 1.00 / force_exceeded | (0.493, 0.077, 0.200)→(0.491, 0.070, 0.097) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.000 | 78.622 | 78.622 |
| center_at_entrance | align | 1.00 / step_budget | (0.491, 0.070, 0.097)→(0.494, 0.075, 0.123) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.543 | 121.295 |
| seat_in_channel | descend | 1.00 / force_exceeded | (0.494, 0.075, 0.123)→(0.495, 0.077, 0.090) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.000 | 38.959 | 38.959 |
| push_through_channel | push | 0.00 / guard_failure | (0.495, 0.077, 0.090)→(0.495, 0.077, 0.090) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.333 | 20.026 | 119.113 |
| retract_up | retract | 1.00 / step_budget | (0.495, 0.077, 0.090)→(0.493, 0.076, 0.178) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.545 | 104.355 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.002
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.001
- phase_score: 0.090
- phase_breakdown.traverse_channel_score: 0.000
- phase_breakdown.reach_peg_score: 0.212
- phase_breakdown.center_at_entrance_score: 0.386

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.054
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: 0.064
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.401


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55372,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.16489,"descend_to_peg.descend_force":15.52246,"push_through_channel.push_distance":0.16401,"seat_in_channel.seat_force":12.02062},"optimized_scores":{"best_composite_score":0.06413,"best_fitness_score":0.0508,"best_task_score":0.00121},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.47498,0.11998,0.05997],"force_p95":141.7245,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":147.1075,"mean_force":105.57468,"phase_index":2.0,"phase_name":"center_at_entrance","phase_type":"align","tcp_position_centroid":[0.4869,0.06619,0.10675]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47499,0.11998,0.05998],"force_p95":138.51024,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":138.51024,"mean_force":138.51024,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48678,0.06613,0.1069]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.475,0.11999,0.05999],"force_p95":132.37335,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":133.55123,"mean_force":121.77247,"phase_index":4.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49456,0.07635,0.09066]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.475,0.11999,0.05999],"force_p95":123.25837,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":125.61098,"mean_force":102.08481,"phase_index":5.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49454,0.07653,0.09039]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.475,0.11999,0.06],"force_p95":52.59538,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":52.59538,"mean_force":52.59538,"phase_index":3.0,"phase_name":"seat_in_channel","phase_type":"descend","tcp_position_centroid":[0.4945,0.07628,0.09081]},{"body_a":"peg","body_b":"channel_base_body","contact_count":586.0,"contact_point_centroid":[0.49541,0.06399,0.00937],"force_p95":0.57732,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56007,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48654,0.14516,0.24567]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50389,0.21522,0.2929]},{"body_a":"peg","body_b":"channel_base_body","contact_count":204.0,"contact_point_centroid":[0.49453,0.06387,0.0094],"force_p95":0.55064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55403,"mean_force":0.54517,"phase_index":3.0,"phase_name":"seat_in_channel","phase_type":"descend","tcp_position_centroid":[0.49298,0.07457,0.10617]},{"body_a":"peg","body_b":"channel_base_body","contact_count":573.0,"contact_point_centroid":[0.49509,0.06391,0.00941],"force_p95":0.55083,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55362,"mean_force":0.54508,"phase_index":5.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49232,0.07547,0.13423]},{"body_a":"peg","body_b":"channel_base_body","contact_count":506.0,"contact_point_centroid":[0.49514,0.06387,0.0094],"force_p95":0.55082,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54534,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48288,0.06933,0.15629]},{"body_a":"peg","body_b":"channel_base_body","contact_count":71.0,"contact_point_centroid":[0.49545,0.06355,0.00941],"force_p95":0.55063,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55119,"mean_force":0.54522,"phase_index":2.0,"phase_name":"center_at_entrance","phase_type":"align","tcp_position_centroid":[0.48932,0.06937,0.11359]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.49321,0.04667,0.00941],"force_p95":0.54463,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54489,"mean_force":0.54294,"phase_index":4.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49459,0.07641,0.09061]}],"total_contact_groups":12},"final_pose_error":0.01122,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49514,0.06357,0.03403],"final_tcp_position":[0.49245,0.0755,0.1795],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":147.1075,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":613.0,"n_steps_budget":1000.0,"object_pos_end":[0.49488,0.06386,0.03395],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14408,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54698,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":614.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_peg","tcp_end":[0.4806,0.07325,0.20763],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17452,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":506.0,"n_steps_budget":960.0,"object_pos_end":[0.49483,0.06396,0.03402],"object_pos_start":[0.49488,0.06386,0.03395],"object_to_goal_dist_end":0.14418,"object_to_goal_dist_start":0.14408,"object_z_max":0.03402,"peak_contact_force":138.51024,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":507.0,"raw_peak_contact_force":138.51024,"subtask_id":"reach_peg","tcp_end":[0.48684,0.06615,0.10677],"tcp_start":[0.4806,0.07325,0.20763],"tcp_to_object_dist_end":0.07322,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":71.0,"n_steps_budget":600.0,"object_pos_end":[0.49491,0.06408,0.03402],"object_pos_start":[0.49483,0.06396,0.03402],"object_to_goal_dist_end":0.1443,"object_to_goal_dist_start":0.14418,"object_z_max":0.03402,"peak_contact_force":0.54153,"phase_name":"center_at_entrance","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":74.0,"raw_peak_contact_force":147.1075,"subtask_id":"center_at_entrance","tcp_end":[0.49272,0.07339,0.12263],"tcp_start":[0.48684,0.06615,0.10677],"tcp_to_object_dist_end":0.08912,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":204.0,"n_steps_budget":600.0,"object_pos_end":[0.49496,0.06361,0.03403],"object_pos_start":[0.49491,0.06408,0.03402],"object_to_goal_dist_end":0.14382,"object_to_goal_dist_start":0.1443,"object_z_max":0.03403,"peak_contact_force":52.59538,"phase_name":"seat_in_channel","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":205.0,"raw_peak_contact_force":52.59538,"subtask_id":"center_at_entrance","tcp_end":[0.49454,0.07632,0.0907],"tcp_start":[0.49272,0.07339,0.12263],"tcp_to_object_dist_end":0.05807,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.49503,0.06358,0.03403],"object_pos_start":[0.49496,0.06361,0.03403],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14382,"object_z_max":0.03403,"peak_contact_force":0.54052,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":133.55123,"subtask_id":"traverse_channel","tcp_end":[0.49459,0.07651,0.09047],"tcp_start":[0.49462,0.07649,0.09053],"tcp_to_object_dist_end":0.0579,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.49514,0.06357,0.03403],"object_pos_start":[0.49525,0.06361,0.03403],"object_to_goal_dist_end":0.14378,"object_to_goal_dist_start":0.14382,"object_z_max":0.03404,"peak_contact_force":0.54136,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":575.0,"raw_peak_contact_force":125.61098,"tcp_end":[0.49245,0.0755,0.1795],"tcp_start":[0.49459,0.07651,0.09047],"tcp_to_object_dist_end":0.14598,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55085,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.16037,"descend_to_peg.descend_force":15.3548,"push_through_channel.push_distance":0.18881,"seat_in_channel.seat_force":8.06165},"optimized_scores":{"best_composite_score":0.06763,"best_fitness_score":0.0543,"best_task_score":0.00057},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.47495,0.11998,0.05994],"force_p95":154.37467,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":165.80002,"mean_force":78.72625,"phase_index":2.0,"phase_name":"center_at_entrance","phase_type":"align","tcp_position_centroid":[0.48033,0.06183,0.11365]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.475,0.11999,0.05999],"force_p95":99.85254,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":101.5452,"mean_force":85.9624,"phase_index":4.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4932,0.07531,0.09312]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.475,0.12,0.06],"force_p95":80.5028,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":80.5028,"mean_force":80.5028,"phase_index":5.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49322,0.07544,0.09294]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47496,0.11999,0.05995],"force_p95":74.87592,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.87592,"mean_force":74.87592,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48011,0.06184,0.11387]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.475,0.12,0.06],"force_p95":25.56342,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":25.56342,"mean_force":25.56342,"phase_index":3.0,"phase_name":"seat_in_channel","phase_type":"descend","tcp_position_centroid":[0.49315,0.07524,0.09328]},{"body_a":"peg","body_b":"channel_base_body","contact_count":609.0,"contact_point_centroid":[0.4944,0.0589,0.00936],"force_p95":0.56326,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57023,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4806,0.14223,0.24387]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50227,0.22054,0.28754]},{"body_a":"peg","body_b":"channel_base_body","contact_count":544.0,"contact_point_centroid":[0.49405,0.05881,0.0094],"force_p95":0.55053,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55392,"mean_force":0.54512,"phase_index":5.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49102,0.07441,0.13665]},{"body_a":"peg","body_b":"channel_base_body","contact_count":483.0,"contact_point_centroid":[0.49418,0.05907,0.00939],"force_p95":0.55014,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.5459,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.47292,0.06464,0.15756]},{"body_a":"peg","body_b":"channel_base_body","contact_count":218.0,"contact_point_centroid":[0.49439,0.05895,0.0094],"force_p95":0.55063,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55295,"mean_force":0.54542,"phase_index":3.0,"phase_name":"seat_in_channel","phase_type":"descend","tcp_position_centroid":[0.49088,0.07302,0.10841]},{"body_a":"peg","body_b":"channel_base_body","contact_count":68.0,"contact_point_centroid":[0.49297,0.05954,0.0094],"force_p95":0.55036,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5513,"mean_force":0.54582,"phase_index":2.0,"phase_name":"center_at_entrance","phase_type":"align","tcp_position_centroid":[0.48449,0.06587,0.11858]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.47702,0.05954,0.0094],"force_p95":0.54998,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55016,"mean_force":0.54877,"phase_index":4.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49322,0.07533,0.0931]}],"total_contact_groups":12},"final_pose_error":0.01149,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49423,0.05867,0.03404],"final_tcp_position":[0.49113,0.07443,0.18174],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":165.80002,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":638.0,"n_steps_budget":1000.0,"object_pos_end":[0.49422,0.05906,0.03388],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13931,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54405,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":644.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_peg","tcp_end":[0.46749,0.06821,0.20334],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1718,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":483.0,"n_steps_budget":960.0,"object_pos_end":[0.49404,0.05914,0.03394],"object_pos_start":[0.49422,0.05906,0.03388],"object_to_goal_dist_end":0.1394,"object_to_goal_dist_start":0.13931,"object_z_max":0.03394,"peak_contact_force":74.87592,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":484.0,"raw_peak_contact_force":74.87592,"subtask_id":"reach_peg","tcp_end":[0.48016,0.06184,0.11369],"tcp_start":[0.46749,0.06821,0.20334],"tcp_to_object_dist_end":0.08099,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":68.0,"n_steps_budget":600.0,"object_pos_end":[0.49393,0.05885,0.03395],"object_pos_start":[0.49404,0.05914,0.03394],"object_to_goal_dist_end":0.13911,"object_to_goal_dist_start":0.1394,"object_z_max":0.03395,"peak_contact_force":0.55128,"phase_name":"center_at_entrance","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":74.0,"raw_peak_contact_force":165.80002,"subtask_id":"center_at_entrance","tcp_end":[0.48989,0.07129,0.12531],"tcp_start":[0.48016,0.06184,0.11369],"tcp_to_object_dist_end":0.09229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":218.0,"n_steps_budget":600.0,"object_pos_end":[0.49389,0.05907,0.03399],"object_pos_start":[0.49393,0.05885,0.03395],"object_to_goal_dist_end":0.13933,"object_to_goal_dist_start":0.13911,"object_z_max":0.03399,"peak_contact_force":25.56342,"phase_name":"seat_in_channel","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":219.0,"raw_peak_contact_force":25.56342,"subtask_id":"center_at_entrance","tcp_end":[0.49318,0.07527,0.09318],"tcp_start":[0.48989,0.07129,0.12531],"tcp_to_object_dist_end":0.06137,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.49387,0.059,0.03399],"object_pos_start":[0.49389,0.05907,0.03399],"object_to_goal_dist_end":0.13927,"object_to_goal_dist_start":0.13933,"object_z_max":0.03399,"peak_contact_force":0.55016,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":7.0,"raw_peak_contact_force":101.5452,"subtask_id":"traverse_channel","tcp_end":[0.49324,0.07543,0.09299],"tcp_start":[0.49325,0.0754,0.09304],"tcp_to_object_dist_end":0.06125,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":544.0,"n_steps_budget":630.0,"object_pos_end":[0.49423,0.05867,0.03404],"object_pos_start":[0.49391,0.0588,0.03399],"object_to_goal_dist_end":0.13891,"object_to_goal_dist_start":0.13906,"object_z_max":0.03404,"peak_contact_force":0.5423,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":545.0,"raw_peak_contact_force":80.5028,"tcp_end":[0.49113,0.07443,0.18174],"tcp_start":[0.49324,0.07543,0.09299],"tcp_to_object_dist_end":0.14858,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69841,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.14586,"descend_to_peg.descend_force":7.50565,"push_through_channel.push_distance":0.1936,"seat_in_channel.seat_force":9.96895},"optimized_scores":{"best_composite_score":0.05177,"best_fitness_score":0.03844,"best_task_score":0.00064},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.47499,0.11997,0.05998],"force_p95":115.10264,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":122.24401,"mean_force":81.88374,"phase_index":4.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49693,0.0785,0.0856]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.475,0.11999,0.06],"force_p95":104.48581,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":106.95176,"mean_force":82.29232,"phase_index":5.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49697,0.07863,0.08548]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.525,0.12,0.05427],"force_p95":50.85785,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":50.9771,"mean_force":43.51644,"phase_index":2.0,"phase_name":"center_at_entrance","phase_type":"align","tcp_position_centroid":[0.50432,0.08004,0.07663]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.475,0.11999,0.06],"force_p95":38.71831,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":38.71831,"mean_force":38.71831,"phase_index":3.0,"phase_name":"seat_in_channel","phase_type":"descend","tcp_position_centroid":[0.4969,0.07843,0.08583]},{"body_a":"peg","body_b":"channel_base_body","contact_count":159.0,"contact_point_centroid":[0.50331,0.07974,0.00948],"force_p95":0.98823,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.03389,"mean_force":1.15714,"phase_index":2.0,"phase_name":"center_at_entrance","phase_type":"align","tcp_position_centroid":[0.50214,0.07966,0.09371]},{"body_a":"peg","body_b":"channel_base_body","contact_count":510.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.47882,"mean_force":0.58977,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51824,0.08445,0.12955]},{"body_a":"attachment","body_b":"peg","contact_count":18.0,"contact_point_centroid":[0.5063,0.09779,0.05955],"force_p95":22.017,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.46485,"mean_force":5.53831,"phase_index":2.0,"phase_name":"center_at_entrance","phase_type":"align","tcp_position_centroid":[0.50589,0.08038,0.0713]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50691,0.0988,0.0587],"force_p95":22.05601,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.05601,"mean_force":22.05601,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50693,0.08076,0.07078]},{"body_a":"peg","body_b":"channel_base_body","contact_count":590.0,"contact_point_centroid":[0.50575,0.0809,0.00936],"force_p95":0.55707,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57263,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50963,0.15192,0.23718]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50278,0.22142,0.28711]},{"body_a":"peg","body_b":"channel_base_body","contact_count":192.0,"contact_point_centroid":[0.50576,0.08058,0.0094],"force_p95":0.55351,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55762,"mean_force":0.5457,"phase_index":3.0,"phase_name":"seat_in_channel","phase_type":"descend","tcp_position_centroid":[0.49748,0.07851,0.10312]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.50599,0.08044,0.00939],"force_p95":0.55245,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55673,"mean_force":0.54631,"phase_index":5.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49469,0.07756,0.12916]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.49006,0.0751,0.0094],"force_p95":0.54604,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54674,"mean_force":0.54182,"phase_index":4.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49693,0.0785,0.0856]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52513,0.08153,0.05899],"force_p95":0.04153,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.05382,"mean_force":0.00755,"phase_index":2.0,"phase_name":"center_at_entrance","phase_type":"align","tcp_position_centroid":[0.50318,0.07999,0.08298]}],"total_contact_groups":14},"final_pose_error":0.01159,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50596,0.08056,0.03381],"final_tcp_position":[0.49478,0.07758,0.17415],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":122.24401,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":619.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54611,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":626.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.53066,0.0889,0.1891],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15747,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":510.0,"n_steps_budget":870.0,"object_pos_end":[0.50598,0.08085,0.03377],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.16108,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":22.47882,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":511.0,"raw_peak_contact_force":22.47882,"subtask_id":"reach_peg","tcp_end":[0.50688,0.08075,0.07055],"tcp_start":[0.53066,0.0889,0.1891],"tcp_to_object_dist_end":0.03679,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":159.0,"n_steps_budget":600.0,"object_pos_end":[0.50573,0.08071,0.034],"object_pos_start":[0.50598,0.08085,0.03377],"object_to_goal_dist_end":0.16093,"object_to_goal_dist_start":0.16108,"object_z_max":0.03585,"peak_contact_force":0.53568,"phase_name":"center_at_entrance","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":193.0,"raw_peak_contact_force":50.9771,"subtask_id":"center_at_entrance","tcp_end":[0.49915,0.0791,0.12008],"tcp_start":[0.50688,0.08075,0.07055],"tcp_to_object_dist_end":0.08635,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":192.0,"n_steps_budget":600.0,"object_pos_end":[0.50573,0.08059,0.03394],"object_pos_start":[0.50573,0.08071,0.034],"object_to_goal_dist_end":0.1608,"object_to_goal_dist_start":0.16093,"object_z_max":0.034,"peak_contact_force":38.71831,"phase_name":"seat_in_channel","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":193.0,"raw_peak_contact_force":38.71831,"subtask_id":"center_at_entrance","tcp_end":[0.49691,0.07843,0.08569],"tcp_start":[0.49915,0.0791,0.12008],"tcp_to_object_dist_end":0.05254,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50574,0.08053,0.03394],"object_pos_start":[0.50573,0.08059,0.03394],"object_to_goal_dist_end":0.16074,"object_to_goal_dist_start":0.1608,"object_z_max":0.03394,"peak_contact_force":58.98663,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":122.24401,"subtask_id":"traverse_channel","tcp_end":[0.49696,0.07861,0.08549],"tcp_start":[0.49695,0.07856,0.08552],"tcp_to_object_dist_end":0.05233,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.50596,0.08056,0.03381],"object_pos_start":[0.50585,0.08039,0.03394],"object_to_goal_dist_end":0.16079,"object_to_goal_dist_start":0.16061,"object_z_max":0.03394,"peak_contact_force":0.55031,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":545.0,"raw_peak_contact_force":106.95176,"tcp_end":[0.49478,0.07758,0.17415],"tcp_start":[0.49696,0.07861,0.08549],"tcp_to_object_dist_end":0.14082,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```