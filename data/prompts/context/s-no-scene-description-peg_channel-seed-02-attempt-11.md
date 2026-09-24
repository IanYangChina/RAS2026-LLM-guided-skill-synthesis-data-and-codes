## Search State

- **Seed**: 2
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | force_threshold_switch | position_control | pose_tolerance | force_exceeded | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.0941 | 0.02 | ❌ rejected |
| 10 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1441 | 0.17 | ❌ rejected |
| 9 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.0752 | 0.00 | ❌ rejected |
| 8 | approach → descend → align → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.2044 | 0.12 | ❌ rejected |
| 7 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1107 | 0.04 | ❌ rejected |

**Proposal policy**: task_score is 0.02 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.094) — your mutation base

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

- **Composite score**: 0.094
- **task_score** (E): 0.024
- **fitness_score**: 0.034  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.400
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1613 |
| descend_to_peg | 1.00 | 1.00 | 0.1040 |
| center_at_channel | 1.00 | 1.00 | 0.0574 |
| push_through_channel | 1.00 | 1.00 | 0.0001 |
| retract_up | 1.00 | 1.00 | 0.0891 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.493, 0.077, 0.200) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.545 | 3.659 |
| descend_to_peg | descend | 1.00 / force_exceeded | (0.493, 0.077, 0.200)→(0.491, 0.070, 0.097) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.000 | 52.512 | 52.512 |
| center_at_channel | align | 1.00 / step_budget | (0.491, 0.070, 0.097)→(0.499, 0.018, 0.109) | (0.498, 0.068, 0.034)→(0.499, 0.061, 0.036) | 0.148→0.141 | 1.00 / 1.667 | 29.855 | 187.423 |
| push_through_channel | push | 1.00 / force_exceeded | (0.498, 0.008, 0.108)→(0.498, 0.007, 0.108) | (0.499, 0.061, 0.036)→(0.499, 0.058, 0.036) | 0.141→0.138 | 1.00 / 2.667 | 26.399 | 40.861 |
| retract_up | retract | 1.00 / step_budget | (0.498, 0.007, 0.108)→(0.496, 0.007, 0.197) | (0.499, 0.057, 0.036)→(0.499, 0.060, 0.034) | 0.137→0.140 | 1.00 / 1.000 | 0.546 | 46.028 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.035
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.011
- phase_score: 0.065
- phase_breakdown.center_at_channel_score: 0.000
- phase_breakdown.reach_peg_score: 0.213
- phase_breakdown.traverse_channel_score: 0.047

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.044
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.051
- **Median Q (composite search score)**: 0.099
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.191


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87379,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.15706,"center_at_channel.align_height":0.09284,"descend_to_peg.descend_force":12.26551,"push_through_channel.push_distance":0.16071,"push_through_channel.push_force_threshold":28.54713},"optimized_scores":{"best_composite_score":0.09869,"best_fitness_score":0.03869,"best_task_score":0.05107},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":162.0,"contact_point_centroid":[0.47498,0.11826,0.05997],"force_p95":215.20936,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":241.7501,"mean_force":142.25735,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.49317,0.05077,0.10291]},{"body_a":"peg","body_b":"channel_base_body","contact_count":225.0,"contact_point_centroid":[0.49562,0.05842,0.00939],"force_p95":84.56349,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":91.69249,"mean_force":15.65279,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.494,0.04781,0.10234]},{"body_a":"peg","body_b":"link7","contact_count":58.0,"contact_point_centroid":[0.49498,0.0742,0.05981],"force_p95":88.80816,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.51245,"mean_force":58.74451,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.4991,0.02705,0.09838]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.475,0.10496,0.06],"force_p95":86.16648,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":89.87622,"mean_force":52.7788,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50075,0.01883,0.09697]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.50025,0.03453,0.00954],"force_p95":48.98651,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.11993,"mean_force":32.36166,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50068,0.01922,0.09702]},{"body_a":"peg","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.49629,0.06487,0.06111],"force_p95":48.61923,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.77665,"mean_force":31.83309,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50068,0.01922,0.09702]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47499,0.11998,0.05998],"force_p95":48.35328,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":48.35328,"mean_force":48.35328,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48669,0.0662,0.1069]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.475,0.10532,0.06],"force_p95":43.04674,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":44.24053,"mean_force":34.23591,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50068,0.01929,0.09703]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49563,0.04933,0.00946],"force_p95":0.57211,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.0097,"mean_force":0.59478,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49852,0.01809,0.14085]},{"body_a":"peg","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.49561,0.06422,0.06205],"force_p95":2.51652,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.47117,"mean_force":1.11316,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49997,0.01835,0.09962]},{"body_a":"peg","body_b":"channel_base_body","contact_count":592.0,"contact_point_centroid":[0.49529,0.06388,0.00937],"force_p95":0.57532,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55992,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48657,0.14513,0.24247]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50391,0.21523,0.2929]},{"body_a":"peg","body_b":"channel_base_body","contact_count":472.0,"contact_point_centroid":[0.49537,0.0639,0.0094],"force_p95":0.55083,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54536,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48277,0.06937,0.15288]}],"total_contact_groups":13},"final_pose_error":0.01135,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49553,0.05067,0.03402],"final_tcp_position":[0.49861,0.01815,0.18586],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":241.7501,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":619.0,"n_steps_budget":1000.0,"object_pos_end":[0.49514,0.06366,0.03395],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14387,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54109,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":620.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_peg","tcp_end":[0.48056,0.07328,0.20043],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":472.0,"n_steps_budget":930.0,"object_pos_end":[0.49502,0.06414,0.03402],"object_pos_start":[0.49514,0.06366,0.03395],"object_to_goal_dist_end":0.14435,"object_to_goal_dist_start":0.14387,"object_z_max":0.03402,"peak_contact_force":48.35328,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":473.0,"raw_peak_contact_force":48.35328,"subtask_id":"reach_peg","tcp_end":[0.48671,0.0662,0.10675],"tcp_start":[0.48056,0.07328,0.20043],"tcp_to_object_dist_end":0.07323,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":225.0,"n_steps_budget":600.0,"object_pos_end":[0.49622,0.05028,0.03542],"object_pos_start":[0.49502,0.06414,0.03402],"object_to_goal_dist_end":0.13042,"object_to_goal_dist_start":0.14435,"object_z_max":0.03539,"peak_contact_force":88.56993,"phase_name":"center_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":445.0,"raw_peak_contact_force":241.7501,"subtask_id":"center_at_channel","tcp_end":[0.50066,0.01954,0.09704],"tcp_start":[0.48671,0.0662,0.10675],"tcp_to_object_dist_end":0.06901,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.49626,0.04988,0.03547],"object_pos_start":[0.49622,0.05028,0.03542],"object_to_goal_dist_end":0.13001,"object_to_goal_dist_start":0.13042,"object_z_max":0.03552,"peak_contact_force":28.54669,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":14.0,"raw_peak_contact_force":52.11993,"subtask_id":"traverse_channel","tcp_end":[0.50076,0.01887,0.09698],"tcp_start":[0.50069,0.01906,0.09702],"tcp_to_object_dist_end":0.06902,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49553,0.05067,0.03402],"object_pos_start":[0.49629,0.04941,0.03553],"object_to_goal_dist_end":0.13088,"object_to_goal_dist_start":0.12954,"object_z_max":0.0366,"peak_contact_force":0.55012,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":576.0,"raw_peak_contact_force":89.87622,"tcp_end":[0.49861,0.01815,0.18586],"tcp_start":[0.50076,0.01887,0.09698],"tcp_to_object_dist_end":0.15531,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81481,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.15515,"center_at_channel.align_height":0.12399,"descend_to_peg.descend_force":8.93461,"push_through_channel.push_distance":0.16692,"push_through_channel.push_force_threshold":33.50809},"optimized_scores":{"best_composite_score":0.10358,"best_fitness_score":0.04358,"best_task_score":0.01135},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.47498,0.11999,0.05991],"force_p95":119.20325,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":121.15671,"mean_force":90.63648,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.48035,0.06088,0.11381]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.475,0.12,0.05995],"force_p95":87.56378,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":87.56378,"mean_force":87.56378,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.47961,0.06194,0.11394]},{"body_a":"peg","body_b":"channel_base_body","contact_count":155.0,"contact_point_centroid":[0.4925,0.04863,0.00952],"force_p95":27.76314,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.94057,"mean_force":13.00021,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49065,0.00518,0.11448]},{"body_a":"peg","body_b":"link7","contact_count":82.0,"contact_point_centroid":[0.49064,0.06156,0.05955],"force_p95":28.41395,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.56159,"mean_force":23.64457,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49032,-0.00012,0.11386]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49434,0.05333,0.00943],"force_p95":0.57697,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.38062,"mean_force":0.59582,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48847,-0.00656,0.15814]},{"body_a":"peg","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.49063,0.05555,0.05996],"force_p95":15.57332,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.93289,"mean_force":3.11868,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49037,-0.00612,0.11429]},{"body_a":"peg","body_b":"channel_base_body","contact_count":611.0,"contact_point_centroid":[0.49443,0.05895,0.00936],"force_p95":0.56316,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57015,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48054,0.14199,0.24151]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50227,0.22054,0.28753]},{"body_a":"peg","body_b":"channel_base_body","contact_count":459.0,"contact_point_centroid":[0.49414,0.05895,0.00939],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54592,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.47265,0.06464,0.15512]},{"body_a":"peg","body_b":"channel_base_body","contact_count":126.0,"contact_point_centroid":[0.49416,0.05906,0.0094],"force_p95":0.5506,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55169,"mean_force":0.54566,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.48551,0.04131,0.11483]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47497,0.05221,0.05956],"force_p95":0.18731,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19248,"mean_force":0.14457,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48987,-0.00633,0.11547]}],"total_contact_groups":11},"final_pose_error":0.01107,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49448,0.05331,0.03401],"final_tcp_position":[0.48858,-0.00651,0.2032],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":121.15671,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":640.0,"n_steps_budget":1000.0,"object_pos_end":[0.49412,0.05909,0.03388],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13935,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54689,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":646.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_peg","tcp_end":[0.46744,0.06811,0.19844],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16695,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":459.0,"n_steps_budget":930.0,"object_pos_end":[0.49414,0.05916,0.03394],"object_pos_start":[0.49412,0.05909,0.03388],"object_to_goal_dist_end":0.13942,"object_to_goal_dist_start":0.13935,"object_z_max":0.03394,"peak_contact_force":87.56378,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":460.0,"raw_peak_contact_force":87.56378,"subtask_id":"reach_peg","tcp_end":[0.47967,0.06195,0.11377],"tcp_start":[0.46744,0.06811,0.19844],"tcp_to_object_dist_end":0.08118,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":126.0,"n_steps_budget":600.0,"object_pos_end":[0.49409,0.05918,0.03396],"object_pos_start":[0.49414,0.05916,0.03394],"object_to_goal_dist_end":0.13943,"object_to_goal_dist_start":0.13942,"object_z_max":0.03396,"peak_contact_force":0.55116,"phase_name":"center_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":140.0,"raw_peak_contact_force":121.15671,"subtask_id":"center_at_channel","tcp_end":[0.49216,0.01697,0.11708],"tcp_start":[0.47967,0.06195,0.11377],"tcp_to_object_dist_end":0.09325,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":155.0,"n_steps_budget":1000.0,"object_pos_end":[0.49426,0.05262,0.03522],"object_pos_start":[0.49409,0.05918,0.03396],"object_to_goal_dist_end":0.13283,"object_to_goal_dist_start":0.13943,"object_z_max":0.03522,"peak_contact_force":26.50448,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":237.0,"raw_peak_contact_force":36.94057,"subtask_id":"traverse_channel","tcp_end":[0.49058,-0.00594,0.11407],"tcp_start":[0.49062,-0.00586,0.1141],"tcp_to_object_dist_end":0.09829,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49448,0.05331,0.03401],"object_pos_start":[0.49429,0.05253,0.03519],"object_to_goal_dist_end":0.13356,"object_to_goal_dist_start":0.13274,"object_z_max":0.0352,"peak_contact_force":0.54742,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":555.0,"raw_peak_contact_force":24.38062,"tcp_end":[0.48858,-0.00651,0.2032],"tcp_start":[0.49058,-0.00594,0.11407],"tcp_to_object_dist_end":0.17955,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88596,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_height":0.15778,"center_at_channel.align_height":0.13607,"descend_to_peg.descend_force":12.84314,"push_through_channel.push_distance":0.15932,"push_through_channel.push_force_threshold":30.99123},"optimized_scores":{"best_composite_score":0.07988,"best_fitness_score":0.01988,"best_task_score":0.0098},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":330.0,"contact_point_centroid":[0.47497,0.11995,0.05997],"force_p95":133.2982,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":199.36207,"mean_force":68.76535,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.50927,0.07573,0.07082]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":382.0,"contact_point_centroid":[0.52501,0.11991,0.05962],"force_p95":120.81055,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":132.89242,"mean_force":62.74772,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.50994,0.07424,0.07155]},{"body_a":"peg","body_b":"channel_base_body","contact_count":515.0,"contact_point_centroid":[0.51056,0.07634,0.00962],"force_p95":20.72063,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.88618,"mean_force":11.03012,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.50968,0.06982,0.0748]},{"body_a":"attachment","body_b":"peg","contact_count":383.0,"contact_point_centroid":[0.50911,0.07889,0.05913],"force_p95":18.83649,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.51551,"mean_force":12.75157,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.50931,0.07587,0.07068]},{"body_a":"peg","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.501,0.09192,0.06125],"force_p95":34.91573,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.97002,"mean_force":22.48505,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.50576,0.02702,0.10621]},{"body_a":"peg","body_b":"link7","contact_count":60.0,"contact_point_centroid":[0.50016,0.07957,0.06471],"force_p95":28.02409,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.5222,"mean_force":22.31374,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50265,0.01302,0.11292]},{"body_a":"peg","body_b":"channel_base_body","contact_count":65.0,"contact_point_centroid":[0.50489,0.05923,0.00972],"force_p95":26.09902,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.40215,"mean_force":20.69621,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50272,0.01338,0.11302]},{"body_a":"peg","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.49939,0.07569,0.06384],"force_p95":16.26521,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.827,"mean_force":3.28022,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50212,0.00909,0.11199]},{"body_a":"peg","body_b":"channel_base_body","contact_count":558.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.61804,"mean_force":0.58453,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51809,0.08458,0.13514]},{"body_a":"peg","body_b":"channel_base_body","contact_count":573.0,"contact_point_centroid":[0.50564,0.07538,0.00943],"force_p95":0.68222,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.50993,"mean_force":0.59025,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50009,0.00857,0.15581]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50665,0.09883,0.05877],"force_p95":21.19037,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.19037,"mean_force":21.19037,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50665,0.08071,0.07093]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.525,0.07622,0.01384],"force_p95":4.4413,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.72326,"mean_force":2.94414,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50257,0.01235,0.11269]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":222.0,"contact_point_centroid":[0.52507,0.07995,0.04386],"force_p95":4.00056,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.07565,"mean_force":1.6868,"phase_index":2.0,"phase_name":"center_at_channel","phase_type":"align","tcp_position_centroid":[0.51176,0.07116,0.07237]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":70.0,"contact_point_centroid":[0.52515,0.07642,0.05872],"force_p95":0.56234,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.49198,"mean_force":0.21033,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50008,0.00855,0.1301]},{"body_a":"peg","body_b":"channel_base_body","contact_count":578.0,"contact_point_centroid":[0.50575,0.0809,0.00936],"force_p95":0.55714,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57316,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5095,0.15231,0.24229]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50277,0.2214,0.28713]}],"total_contact_groups":16},"final_pose_error":0.01099,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50689,0.07581,0.03379],"final_tcp_position":[0.50023,0.00863,0.20111],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":199.36207,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":607.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54612,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":614.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.53067,0.0892,0.20035],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1686,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":558.0,"n_steps_budget":930.0,"object_pos_end":[0.50598,0.08085,0.03377],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.16108,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":21.61804,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":559.0,"raw_peak_contact_force":21.61804,"subtask_id":"reach_peg","tcp_end":[0.50661,0.0807,0.0707],"tcp_start":[0.53067,0.0892,0.20035],"tcp_to_object_dist_end":0.03693,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":515.0,"n_steps_budget":660.0,"object_pos_end":[0.50676,0.07301,0.03758],"object_pos_start":[0.50598,0.08085,0.03377],"object_to_goal_dist_end":0.15318,"object_to_goal_dist_start":0.16108,"object_z_max":0.03749,"peak_contact_force":0.44399,"phase_name":"center_at_channel","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1856.0,"raw_peak_contact_force":199.36207,"subtask_id":"center_at_channel","tcp_end":[0.50365,0.01841,0.11395],"tcp_start":[0.50661,0.0807,0.0707],"tcp_to_object_dist_end":0.09393,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":65.0,"n_steps_budget":990.0,"object_pos_end":[0.50601,0.07004,0.03761],"object_pos_start":[0.50676,0.07301,0.03758],"object_to_goal_dist_end":0.15018,"object_to_goal_dist_start":0.15318,"object_z_max":0.03804,"peak_contact_force":24.14662,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":161.0,"raw_peak_contact_force":33.5222,"subtask_id":"traverse_channel","tcp_end":[0.50232,0.00926,0.11188],"tcp_start":[0.50237,0.00934,0.11192],"tcp_to_object_dist_end":0.09604,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.50689,0.07581,0.03379],"object_pos_start":[0.50601,0.07001,0.0376],"object_to_goal_dist_end":0.15609,"object_to_goal_dist_start":0.15015,"object_z_max":0.03764,"peak_contact_force":0.53971,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":651.0,"raw_peak_contact_force":23.827,"tcp_end":[0.50023,0.00863,0.20111],"tcp_start":[0.50232,0.00926,0.11188],"tcp_to_object_dist_end":0.18043,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```