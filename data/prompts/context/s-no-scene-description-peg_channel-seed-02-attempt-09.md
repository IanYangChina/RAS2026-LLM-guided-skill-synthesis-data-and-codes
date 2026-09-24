## Search State

- **Seed**: 2
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.0752 | 0.00 | ❌ rejected |
| 8 | approach → descend → align → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.2044 | 0.12 | ❌ rejected |
| 7 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1107 | 0.04 | ❌ rejected |
| 6 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1482 | 0.18 | ✅ accepted |
| 5 | approach → descend → align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.0612 | 0.00 | ❌ rejected |

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

## Current Skill (Q=0.075) — your mutation base

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

- **Composite score**: 0.075
- **task_score** (E): 0.001
- **fitness_score**: 0.015  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.400
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1794 |
| descend_to_peg | 1.00 | 1.00 | 0.0776 |
| align_and_insert | 1.00 | 1.00 | 0.0001 |
| push_through_channel | 0.00 | 1.00 | 0.0001 |
| retract_up | 1.00 | 1.00 | 0.0891 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.493, 0.076, 0.173) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.545 | 3.659 |
| descend_to_peg | descend | 1.00 / force_exceeded | (0.493, 0.076, 0.173)→(0.489, 0.070, 0.097) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.000 | 38.951 | 38.951 |
| align_and_insert | push | 1.00 / force_exceeded | (0.489, 0.070, 0.097)→(0.489, 0.070, 0.097) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.000 | 79.652 | 79.652 |
| push_through_channel | push | 0.00 / guard_failure | (0.488, 0.070, 0.097)→(0.488, 0.070, 0.097) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.000 | 37.994 | 65.239 |
| retract_up | retract | 1.00 / step_budget | (0.488, 0.070, 0.097)→(0.486, 0.069, 0.186) | (0.498, 0.068, 0.034)→(0.498, 0.067, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.543 | 93.649 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.002
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.001
- phase_score: 0.033
- phase_breakdown.center_at_channel_score: 0.000
- phase_breakdown.reach_peg_score: 0.216
- phase_breakdown.traverse_channel_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.020
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: 0.078
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.380


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8375,"average_solve_count":80.0,"average_success_count":80.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_and_insert.insert_distance":0.05101,"align_and_insert.insert_force":17.27778,"approach_peg.approach_height":0.13819,"descend_to_peg.descend_force":10.903,"push_through_channel.push_distance":0.1684},"optimized_scores":{"best_composite_score":0.07759,"best_fitness_score":0.01759,"best_task_score":0.00118},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.47498,0.11998,0.05997],"force_p95":130.6284,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":133.88098,"mean_force":95.70014,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48586,0.06668,0.10696]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47498,0.11997,0.05996],"force_p95":117.76154,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":117.76154,"mean_force":117.76154,"phase_index":2.0,"phase_name":"align_and_insert","phase_type":"push","tcp_position_centroid":[0.48574,0.06652,0.10713]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.47497,0.11997,0.05996],"force_p95":67.29416,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":67.80765,"mean_force":61.54385,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4858,0.06657,0.10703]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.475,0.12,0.06],"force_p95":45.98723,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.98723,"mean_force":45.98723,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48572,0.06652,0.10727]},{"body_a":"peg","body_b":"channel_base_body","contact_count":612.0,"contact_point_centroid":[0.49529,0.06391,0.00937],"force_p95":0.57002,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55946,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48658,0.1445,0.23437]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50399,0.21529,0.29296]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49504,0.06382,0.00941],"force_p95":0.5507,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55403,"mean_force":0.54513,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48375,0.06572,0.15088]},{"body_a":"peg","body_b":"channel_base_body","contact_count":383.0,"contact_point_centroid":[0.49533,0.06399,0.0094],"force_p95":0.55081,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54535,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48218,0.06929,0.14417]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.47779,0.06109,0.0094],"force_p95":0.55162,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5519,"mean_force":0.5492,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4858,0.06657,0.10703]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.47845,0.07069,0.0094],"force_p95":0.54601,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54601,"mean_force":0.54601,"phase_index":2.0,"phase_name":"align_and_insert","phase_type":"push","tcp_position_centroid":[0.48574,0.06652,0.10713]}],"total_contact_groups":10},"final_pose_error":0.0113,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49499,0.06358,0.03404],"final_tcp_position":[0.48384,0.06572,0.19589],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":133.88098,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":639.0,"n_steps_budget":1000.0,"object_pos_end":[0.49506,0.06365,0.03396],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14386,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.5442,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":640.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_peg","tcp_end":[0.48036,0.0728,0.18261],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14965,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":383.0,"n_steps_budget":810.0,"object_pos_end":[0.49484,0.06398,0.03401],"object_pos_start":[0.49506,0.06365,0.03396],"object_to_goal_dist_end":0.14419,"object_to_goal_dist_start":0.14386,"object_z_max":0.03401,"peak_contact_force":45.98723,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":384.0,"raw_peak_contact_force":45.98723,"subtask_id":"reach_peg","tcp_end":[0.48574,0.06652,0.10713],"tcp_start":[0.48036,0.0728,0.18261],"tcp_to_object_dist_end":0.07372,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49482,0.06391,0.03401],"object_pos_start":[0.49484,0.06398,0.03401],"object_to_goal_dist_end":0.14412,"object_to_goal_dist_start":0.14419,"object_z_max":0.03401,"peak_contact_force":117.76154,"phase_name":"align_and_insert","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":117.76154,"subtask_id":"center_at_channel","tcp_end":[0.48577,0.06654,0.10707],"tcp_start":[0.48574,0.06652,0.10713],"tcp_to_object_dist_end":0.07366,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06383,0.03401],"object_pos_start":[0.49482,0.06391,0.03401],"object_to_goal_dist_end":0.14405,"object_to_goal_dist_start":0.14412,"object_z_max":0.03401,"peak_contact_force":54.15116,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":67.80765,"subtask_id":"traverse_channel","tcp_end":[0.48584,0.06664,0.10697],"tcp_start":[0.48582,0.06661,0.107],"tcp_to_object_dist_end":0.07356,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49499,0.06358,0.03404],"object_pos_start":[0.49487,0.0637,0.03401],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14391,"object_z_max":0.03404,"peak_contact_force":0.54444,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":546.0,"raw_peak_contact_force":133.88098,"tcp_end":[0.48384,0.06572,0.19589],"tcp_start":[0.48584,0.06664,0.10697],"tcp_to_object_dist_end":0.16225,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83544,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_and_insert.insert_distance":0.0387,"align_and_insert.insert_force":21.10999,"approach_peg.approach_height":0.10289,"descend_to_peg.descend_force":15.25787,"push_through_channel.push_distance":0.15829},"optimized_scores":{"best_composite_score":0.07971,"best_fitness_score":0.01971,"best_task_score":0.00051},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47048,0.11993,0.05995],"force_p95":107.59861,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":107.59861,"mean_force":107.59861,"phase_index":2.0,"phase_name":"align_and_insert","phase_type":"push","tcp_position_centroid":[0.473,0.06311,0.11385]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.47058,0.11996,0.05997],"force_p95":104.59568,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":106.53088,"mean_force":81.70207,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.47314,0.0633,0.11367]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.47053,0.11992,0.05994],"force_p95":80.7191,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":82.28686,"mean_force":68.68423,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.47307,0.06317,0.11374]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47045,0.11996,0.05997],"force_p95":48.37362,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":48.37362,"mean_force":48.37362,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.47296,0.06311,0.11398]},{"body_a":"peg","body_b":"channel_base_body","contact_count":683.0,"contact_point_centroid":[0.49433,0.05903,0.00936],"force_p95":0.5601,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.5676,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48052,0.14032,0.21872]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50257,0.22072,0.28766]},{"body_a":"peg","body_b":"channel_base_body","contact_count":198.0,"contact_point_centroid":[0.49397,0.05894,0.00939],"force_p95":0.5502,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.546,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.46917,0.06462,0.13059]},{"body_a":"peg","body_b":"channel_base_body","contact_count":573.0,"contact_point_centroid":[0.4941,0.05895,0.0094],"force_p95":0.5505,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55347,"mean_force":0.54558,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.47109,0.06235,0.15786]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49002,0.04203,0.00939],"force_p95":0.54762,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54809,"mean_force":0.54475,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.47307,0.06317,0.11374]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.48015,0.04764,0.00939],"force_p95":0.54747,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54747,"mean_force":0.54747,"phase_index":2.0,"phase_name":"align_and_insert","phase_type":"push","tcp_position_centroid":[0.473,0.06311,0.11385]}],"total_contact_groups":10},"final_pose_error":0.01075,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49422,0.0587,0.03401],"final_tcp_position":[0.4712,0.06236,0.20314],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":107.59861,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":712.0,"n_steps_budget":1000.0,"object_pos_end":[0.49398,0.05894,0.03389],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13921,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54487,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":718.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_peg","tcp_end":[0.4668,0.06685,0.14867],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11822,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":198.0,"n_steps_budget":630.0,"object_pos_end":[0.49399,0.05885,0.03391],"object_pos_start":[0.49398,0.05894,0.03389],"object_to_goal_dist_end":0.13911,"object_to_goal_dist_start":0.13921,"object_z_max":0.03391,"peak_contact_force":48.37362,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":199.0,"raw_peak_contact_force":48.37362,"subtask_id":"reach_peg","tcp_end":[0.473,0.06311,0.11385],"tcp_start":[0.4668,0.06685,0.14867],"tcp_to_object_dist_end":0.08275,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49403,0.05881,0.03391],"object_pos_start":[0.49399,0.05885,0.03391],"object_to_goal_dist_end":0.13907,"object_to_goal_dist_start":0.13911,"object_z_max":0.03391,"peak_contact_force":107.59861,"phase_name":"align_and_insert","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":107.59861,"subtask_id":"center_at_channel","tcp_end":[0.47304,0.06313,0.11378],"tcp_start":[0.473,0.06311,0.11385],"tcp_to_object_dist_end":0.08269,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":990.0,"object_pos_end":[0.49408,0.05879,0.03391],"object_pos_start":[0.49403,0.05881,0.03391],"object_to_goal_dist_end":0.13905,"object_to_goal_dist_start":0.13907,"object_z_max":0.03391,"peak_contact_force":57.15661,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":82.28686,"subtask_id":"traverse_channel","tcp_end":[0.47312,0.06325,0.11368],"tcp_start":[0.4731,0.06321,0.11371],"tcp_to_object_dist_end":0.0826,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.49422,0.0587,0.03401],"object_pos_start":[0.4942,0.0588,0.03391],"object_to_goal_dist_end":0.13895,"object_to_goal_dist_start":0.13905,"object_z_max":0.03401,"peak_contact_force":0.54406,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":576.0,"raw_peak_contact_force":106.53088,"tcp_end":[0.4712,0.06236,0.20314],"tcp_start":[0.47312,0.06325,0.11368],"tcp_to_object_dist_end":0.17073,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85556,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_and_insert.insert_distance":0.02867,"align_and_insert.insert_force":12.18306,"approach_peg.approach_height":0.14584,"descend_to_peg.descend_force":15.90585,"push_through_channel.push_distance":0.19921},"optimized_scores":{"best_composite_score":0.06831,"best_fitness_score":0.00831,"best_task_score":0.00145},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.48863,0.07601,0.00936],"force_p95":43.78502,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.62392,"mean_force":23.39411,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50666,0.08064,0.07013]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50672,0.09858,0.05842],"force_p95":43.47891,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.33605,"mean_force":22.93809,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50666,0.08064,0.07013]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":30.0,"contact_point_centroid":[0.525,0.12,0.05328],"force_p95":36.91571,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":40.53448,"mean_force":22.37821,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.5045,0.08002,0.07579]},{"body_a":"peg","body_b":"channel_base_body","contact_count":573.0,"contact_point_centroid":[0.50522,0.0803,0.00942],"force_p95":0.56185,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.74473,"mean_force":0.68068,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50397,0.07946,0.11331]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.506,0.09809,0.05896],"force_p95":18.86009,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.29786,"mean_force":3.96066,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50583,0.08017,0.0706]},{"body_a":"peg","body_b":"channel_base_body","contact_count":510.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.49255,"mean_force":0.5898,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51824,0.08445,0.12954]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50691,0.09881,0.0587],"force_p95":22.06984,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.06984,"mean_force":22.06984,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50693,0.08076,0.07078]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50713,0.06311,0.00938],"force_p95":13.59697,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.59697,"mean_force":13.59697,"phase_index":2.0,"phase_name":"align_and_insert","phase_type":"push","tcp_position_centroid":[0.50688,0.08075,0.07055]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50687,0.09879,0.05858],"force_p95":13.17223,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.17223,"mean_force":13.17223,"phase_index":2.0,"phase_name":"align_and_insert","phase_type":"push","tcp_position_centroid":[0.50688,0.08075,0.07055]},{"body_a":"peg","body_b":"channel_base_body","contact_count":590.0,"contact_point_centroid":[0.50575,0.0809,0.00936],"force_p95":0.55707,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57263,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50963,0.15192,0.23718]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50278,0.22142,0.28711]}],"total_contact_groups":11},"final_pose_error":0.0115,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50575,0.08011,0.03396],"final_tcp_position":[0.50415,0.0794,0.15862],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":45.62392,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":619.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54611,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":626.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.53066,0.0889,0.18908],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15746,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":510.0,"n_steps_budget":870.0,"object_pos_end":[0.50598,0.08085,0.03377],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.16108,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":22.49255,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":511.0,"raw_peak_contact_force":22.49255,"subtask_id":"reach_peg","tcp_end":[0.50688,0.08075,0.07055],"tcp_start":[0.53066,0.0889,0.18908],"tcp_to_object_dist_end":0.03679,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50591,0.08081,0.03379],"object_pos_start":[0.50598,0.08085,0.03377],"object_to_goal_dist_end":0.16104,"object_to_goal_dist_start":0.16108,"object_z_max":0.03377,"peak_contact_force":13.59697,"phase_name":"align_and_insert","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":13.59697,"subtask_id":"center_at_channel","tcp_end":[0.5068,0.08072,0.07038],"tcp_start":[0.50688,0.08075,0.07055],"tcp_to_object_dist_end":0.0366,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.50573,0.08066,0.03387],"object_pos_start":[0.50591,0.08081,0.03379],"object_to_goal_dist_end":0.16088,"object_to_goal_dist_start":0.16104,"object_z_max":0.03388,"peak_contact_force":2.67311,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":10.0,"raw_peak_contact_force":45.62392,"subtask_id":"traverse_channel","tcp_end":[0.5065,0.08049,0.06982],"tcp_start":[0.50652,0.08054,0.0699],"tcp_to_object_dist_end":0.03597,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.50575,0.08011,0.03396],"object_pos_start":[0.50569,0.08057,0.03389],"object_to_goal_dist_end":0.16032,"object_to_goal_dist_start":0.16079,"object_z_max":0.03472,"peak_contact_force":0.5409,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":623.0,"raw_peak_contact_force":40.53448,"tcp_end":[0.50415,0.0794,0.15862],"tcp_start":[0.5065,0.08049,0.06982],"tcp_to_object_dist_end":0.12467,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```