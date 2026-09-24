## Search State

- **Seed**: 2
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → align → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.2044 | 0.12 | ❌ rejected |
| 7 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1107 | 0.04 | ❌ rejected |
| 6 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1482 | 0.18 | ✅ accepted |
| 5 | approach → descend → align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.0612 | 0.00 | ❌ rejected |
| 4 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1447 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.12 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.204) — your mutation base

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

- **Composite score**: 0.204
- **task_score** (E): 0.116
- **fitness_score**: 0.264  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1748 |
| descend_to_grasp | 1.00 | 1.00 | 0.1310 |
| align_at_channel_entrance | 1.00 | 1.00 | 0.0546 |
| push_through_channel | 0.67 | 1.00 | 0.1038 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.492, 0.068, 0.189) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.545 | 3.659 |
| descend_to_grasp | descend | 1.00 / force_exceeded | (0.492, 0.068, 0.189)→(0.494, 0.067, 0.060) | (0.498, 0.068, 0.034)→(0.499, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.000 | 32.950 | 32.950 |
| align_at_channel_entrance | align | 1.00 / step_budget | (0.494, 0.067, 0.060)→(0.504, 0.016, 0.050) | (0.499, 0.068, 0.034)→(0.502, 0.046, 0.037) | 0.148→0.126 | 1.00 / 2.000 | 105.102 | 151.040 |
| push_through_channel | push | 0.67 / step_budget | (0.504, 0.016, 0.050)→(0.505, -0.088, 0.044) | (0.502, 0.046, 0.037)→(0.496, 0.018, 0.024) | 0.126→0.099 | 1.00 / 2.000 | 217.130 | 270.462 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.315
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.198
- phase_score: 0.392
- phase_breakdown.reach_above_peg_score: 0.955
- phase_breakdown.align_at_channel_score: 0.000
- phase_breakdown.descend_to_peg_score: 0.833
- phase_breakdown.push_through_channel_score: 0.234

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.314
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.198
- **Median Q (composite search score)**: 0.214
- **K-run variance**: 0.0020
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.515


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89076,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_channel_entrance.align_height":0.03758,"approach_above.approach_height":0.13136,"approach_above.arc_height":0.16117,"descend_to_grasp.descend_force":14.9422,"push_through_channel.push_distance":0.14951},"optimized_scores":{"best_composite_score":0.25395,"best_fitness_score":0.31395,"best_task_score":0.19762},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":93.0,"contact_point_centroid":[0.50643,-0.10038,0.06499],"force_p95":254.22334,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":279.70951,"mean_force":214.53947,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50347,-0.0883,0.04395]},{"body_a":"peg","body_b":"channel_base_body","contact_count":156.0,"contact_point_centroid":[0.50515,0.04365,0.00842],"force_p95":161.74819,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":165.22204,"mean_force":129.34288,"phase_index":2.0,"phase_name":"align_at_channel_entrance","phase_type":"align","tcp_position_centroid":[0.49724,0.04112,0.05443]},{"body_a":"attachment","body_b":"peg","contact_count":156.0,"contact_point_centroid":[0.50399,0.04928,0.0557],"force_p95":161.22652,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":164.71503,"mean_force":128.85295,"phase_index":2.0,"phase_name":"align_at_channel_entrance","phase_type":"align","tcp_position_centroid":[0.49724,0.04112,0.05443]},{"body_a":"peg","body_b":"channel_base_body","contact_count":256.0,"contact_point_centroid":[0.49627,0.01822,0.00836],"force_p95":35.43366,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":95.52083,"mean_force":4.8024,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50327,-0.05551,0.04543]},{"body_a":"attachment","body_b":"peg","contact_count":35.0,"contact_point_centroid":[0.50512,0.01777,0.0505],"force_p95":89.60333,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":95.40394,"mean_force":29.86426,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50495,0.00664,0.0489]},{"body_a":"peg","body_b":"channel_base_body","contact_count":724.0,"contact_point_centroid":[0.49514,0.06371,0.0094],"force_p95":0.55066,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.38491,"mean_force":0.59497,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48338,0.0632,0.12321]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50179,0.06226,0.0589],"force_p95":35.81336,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.81336,"mean_force":35.81336,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48996,0.06331,0.06058]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":12.0,"contact_point_centroid":[0.47495,0.03671,0.02409],"force_p95":8.40368,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.63261,"mean_force":2.96519,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50223,-0.06355,0.04498]},{"body_a":"peg","body_b":"channel_base_body","contact_count":384.0,"contact_point_centroid":[0.49555,0.06405,0.00936],"force_p95":0.61192,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56761,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48636,0.11269,0.26614]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49864,0.19549,0.30001]}],"total_contact_groups":10},"final_pose_error":0.04713,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49524,0.01351,0.02413],"final_tcp_position":[0.50496,-0.08751,0.04336],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":279.70951,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":411.0,"n_steps_budget":1000.0,"object_pos_end":[0.49491,0.06384,0.03393],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14405,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54501,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":412.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_above_peg","tcp_end":[0.47901,0.06338,0.19118],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":724.0,"n_steps_budget":870.0,"object_pos_end":[0.49537,0.06404,0.03403],"object_pos_start":[0.49491,0.06384,0.03393],"object_to_goal_dist_end":0.14424,"object_to_goal_dist_start":0.14405,"object_z_max":0.03402,"peak_contact_force":36.38491,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":725.0,"raw_peak_contact_force":36.38491,"subtask_id":"descend_to_peg","tcp_end":[0.49004,0.06332,0.06041],"tcp_start":[0.47901,0.06338,0.19118],"tcp_to_object_dist_end":0.02693,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":156.0,"n_steps_budget":600.0,"object_pos_end":[0.50047,0.04399,0.03611],"object_pos_start":[0.49537,0.06404,0.03403],"object_to_goal_dist_end":0.12405,"object_to_goal_dist_start":0.14424,"object_z_max":0.03602,"peak_contact_force":139.00664,"phase_name":"align_at_channel_entrance","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":312.0,"raw_peak_contact_force":165.22204,"subtask_id":"align_at_channel","tcp_end":[0.50486,0.01524,0.04929],"tcp_start":[0.49004,0.06332,0.06041],"tcp_to_object_dist_end":0.03192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":265.0,"n_steps_budget":930.0,"object_pos_end":[0.49524,0.01351,0.02413],"object_pos_start":[0.50047,0.04399,0.03611],"object_to_goal_dist_end":0.09497,"object_to_goal_dist_start":0.12405,"object_z_max":0.03962,"peak_contact_force":215.45702,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":396.0,"raw_peak_contact_force":279.70951,"subtask_id":"push_through_channel","tcp_end":[0.50496,-0.08751,0.04336],"tcp_start":[0.50486,0.01524,0.04929],"tcp_to_object_dist_end":0.10329,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81513,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_channel_entrance.align_height":0.03426,"approach_above.approach_height":0.13075,"approach_above.arc_height":0.16732,"descend_to_grasp.descend_force":8.97322,"push_through_channel.push_distance":0.14246},"optimized_scores":{"best_composite_score":0.21434,"best_fitness_score":0.27434,"best_task_score":0.09873},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":84.0,"contact_point_centroid":[0.50787,-0.1004,0.06499],"force_p95":242.93829,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":248.11595,"mean_force":211.92543,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50489,-0.08837,0.04268]},{"body_a":"peg","body_b":"channel_base_body","contact_count":165.0,"contact_point_centroid":[0.5069,0.03852,0.00822],"force_p95":188.18178,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":193.0855,"mean_force":147.65946,"phase_index":2.0,"phase_name":"align_at_channel_entrance","phase_type":"align","tcp_position_centroid":[0.49719,0.03686,0.05325]},{"body_a":"attachment","body_b":"peg","contact_count":165.0,"contact_point_centroid":[0.5048,0.04434,0.05475],"force_p95":187.67581,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":192.56635,"mean_force":147.17054,"phase_index":2.0,"phase_name":"align_at_channel_entrance","phase_type":"align","tcp_position_centroid":[0.49719,0.03686,0.05325]},{"body_a":"peg","body_b":"channel_base_body","contact_count":242.0,"contact_point_centroid":[0.49701,0.01299,0.00833],"force_p95":78.16735,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":113.18384,"mean_force":8.3279,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5052,-0.05526,0.04438]},{"body_a":"attachment","body_b":"peg","contact_count":42.0,"contact_point_centroid":[0.50711,0.01339,0.05002],"force_p95":109.82558,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":112.72006,"mean_force":44.16846,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50729,0.00229,0.04798]},{"body_a":"peg","body_b":"channel_base_body","contact_count":774.0,"contact_point_centroid":[0.49412,0.05882,0.00939],"force_p95":0.55033,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.53784,"mean_force":0.59505,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47538,0.05859,0.12365]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49993,0.05824,0.05883],"force_p95":37.97796,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.97796,"mean_force":37.97796,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48806,0.05847,0.06049]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47496,0.02988,0.02383],"force_p95":8.32399,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.61532,"mean_force":2.13283,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50416,-0.06403,0.04369]},{"body_a":"peg","body_b":"channel_base_body","contact_count":395.0,"contact_point_centroid":[0.49445,0.05907,0.00934],"force_p95":0.59617,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.58324,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.47756,0.11018,0.26679]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49783,0.19402,0.30016]}],"total_contact_groups":10},"final_pose_error":0.04209,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49578,0.00668,0.02413],"final_tcp_position":[0.50603,-0.08784,0.04213],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":248.11595,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":424.0,"n_steps_budget":1000.0,"object_pos_end":[0.49403,0.05891,0.03386],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13918,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54489,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":430.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_above_peg","tcp_end":[0.46508,0.05898,0.19056],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15935,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":774.0,"n_steps_budget":870.0,"object_pos_end":[0.49438,0.05896,0.03396],"object_pos_start":[0.49403,0.05891,0.03386],"object_to_goal_dist_end":0.1392,"object_to_goal_dist_start":0.13918,"object_z_max":0.03395,"peak_contact_force":38.53784,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":775.0,"raw_peak_contact_force":38.53784,"subtask_id":"descend_to_peg","tcp_end":[0.48815,0.05848,0.06032],"tcp_start":[0.46508,0.05898,0.19056],"tcp_to_object_dist_end":0.02709,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":165.0,"n_steps_budget":600.0,"object_pos_end":[0.50099,0.0402,0.03448],"object_pos_start":[0.49438,0.05896,0.03396],"object_to_goal_dist_end":0.12033,"object_to_goal_dist_start":0.1392,"object_z_max":0.03439,"peak_contact_force":175.81132,"phase_name":"align_at_channel_entrance","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":330.0,"raw_peak_contact_force":193.0855,"subtask_id":"align_at_channel","tcp_end":[0.50666,0.01293,0.04786],"tcp_start":[0.48815,0.05848,0.06032],"tcp_to_object_dist_end":0.0309,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":252.0,"n_steps_budget":900.0,"object_pos_end":[0.49578,0.00668,0.02413],"object_pos_start":[0.50099,0.0402,0.03448],"object_to_goal_dist_end":0.08822,"object_to_goal_dist_start":0.12033,"object_z_max":0.03964,"peak_contact_force":218.2161,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":377.0,"raw_peak_contact_force":248.11595,"subtask_id":"push_through_channel","tcp_end":[0.50603,-0.08784,0.04213],"tcp_start":[0.50666,0.01293,0.04786],"tcp_to_object_dist_end":0.09676,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_channel_entrance.align_height":0.04992,"approach_above.approach_height":0.12711,"approach_above.arc_height":0.18714,"descend_to_grasp.descend_force":13.51471,"push_through_channel.push_distance":0.15758},"optimized_scores":{"best_composite_score":0.14479,"best_fitness_score":0.20479,"best_task_score":0.05265},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":119.0,"contact_point_centroid":[0.50394,-0.10037,0.06499],"force_p95":253.78403,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":283.55918,"mean_force":213.23095,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50098,-0.08833,0.04683]},{"body_a":"peg","body_b":"channel_base_body","contact_count":162.0,"contact_point_centroid":[0.50709,0.05942,0.00906],"force_p95":93.38238,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":94.81351,"mean_force":70.45211,"phase_index":2.0,"phase_name":"align_at_channel_entrance","phase_type":"align","tcp_position_centroid":[0.50448,0.05286,0.05748]},{"body_a":"attachment","body_b":"peg","contact_count":162.0,"contact_point_centroid":[0.50991,0.062,0.05798],"force_p95":92.8893,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":94.31068,"mean_force":70.00923,"phase_index":2.0,"phase_name":"align_at_channel_entrance","phase_type":"align","tcp_position_centroid":[0.50448,0.05286,0.05748]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50329,0.02995,0.05192],"force_p95":21.92564,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.04222,"mean_force":6.03984,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50164,0.01834,0.05185]},{"body_a":"peg","body_b":"channel_base_body","contact_count":294.0,"contact_point_centroid":[0.49704,0.03689,0.00834],"force_p95":0.96503,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.9401,"mean_force":0.78595,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50025,-0.05654,0.04795]},{"body_a":"peg","body_b":"channel_base_body","contact_count":544.0,"contact_point_centroid":[0.50604,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.92787,"mean_force":0.58975,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.51762,0.08099,0.12224]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5165,0.07996,0.05873],"force_p95":23.46147,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.46147,"mean_force":23.46147,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50464,0.0804,0.06043]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.525,0.06786,0.05936],"force_p95":7.64405,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.65014,"mean_force":7.492,"phase_index":2.0,"phase_name":"align_at_channel_entrance","phase_type":"align","tcp_position_centroid":[0.50483,0.06109,0.05845]},{"body_a":"peg","body_b":"channel_base_body","contact_count":347.0,"contact_point_centroid":[0.5055,0.08086,0.00934],"force_p95":0.56732,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59073,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.52047,0.12496,0.25774]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50093,0.19421,0.2988]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47499,0.00931,0.02422],"force_p95":0.44043,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44576,"mean_force":0.3943,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49911,-0.08647,0.04761]}],"total_contact_groups":11},"final_pose_error":0.05063,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49573,0.03312,0.02413],"final_tcp_position":[0.50312,-0.08781,0.04635],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":283.55918,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":376.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54539,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":383.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_above_peg","tcp_end":[0.53268,0.08198,0.18675],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15529,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":544.0,"n_steps_budget":870.0,"object_pos_end":[0.50596,0.08086,0.03377],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":23.92787,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":545.0,"raw_peak_contact_force":23.92787,"subtask_id":"descend_to_peg","tcp_end":[0.5046,0.0804,0.06022],"tcp_start":[0.53268,0.08198,0.18675],"tcp_to_object_dist_end":0.02649,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":162.0,"n_steps_budget":600.0,"object_pos_end":[0.50324,0.05259,0.03962],"object_pos_start":[0.50596,0.08086,0.03377],"object_to_goal_dist_end":0.13263,"object_to_goal_dist_start":0.16109,"object_z_max":0.03962,"peak_contact_force":0.48918,"phase_name":"align_at_channel_entrance","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":327.0,"raw_peak_contact_force":94.81351,"subtask_id":"align_at_channel","tcp_end":[0.50197,0.01951,0.05227],"tcp_start":[0.5046,0.0804,0.06022],"tcp_to_object_dist_end":0.03545,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":301.0,"n_steps_budget":990.0,"object_pos_end":[0.49573,0.03312,0.02413],"object_pos_start":[0.50324,0.05259,0.03962],"object_to_goal_dist_end":0.11431,"object_to_goal_dist_start":0.13263,"object_z_max":0.03962,"peak_contact_force":217.71562,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":425.0,"raw_peak_contact_force":283.55918,"subtask_id":"push_through_channel","tcp_end":[0.50312,-0.08781,0.04635],"tcp_start":[0.50197,0.01951,0.05227],"tcp_to_object_dist_end":0.12317,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```