## Search State

- **Seed**: 5
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | grasp → lift → approach → descend → push → retract | — | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | admittance_control | admittance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1643 | 0.12 | ❌ rejected |
| 8 | grasp → approach → descend → push → retract | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.0869 | 0.14 | ✅ accepted |
| 7 | grasp → approach → push → retract | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.0715 | 0.12 | ✅ accepted |
| 6 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.2993 | 0.00 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → insert → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | -0.5799 | 0.00 | ❌ rejected |

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

## Current Skill (Q=-0.164) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_channel_entry
  offset:
  - 0.0
  - 0.16
  - 0.05
  weight: 0.3
- id: push_through_channel
  metric: goal_progress
  weight: 0.7
phases:
- id: grasp_0
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.16
    - 0.05
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_channel_entry
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.16
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.16
    - 0.0
    offset_along_axis:
      distance: 0.18
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_force_limit:
      type: scalar
      range:
      - 10.0
      - 40.0
      default: 35.0
      binds_to:
      - path: guards.push_guard.threshold
        mode: replace
  guards:
  - id: push_guard
    when: during_phase
    predicate: force_below
    threshold: 35.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.01
    - 0.0
    - 0.01
  subtask_id: push_through_channel
- id: retract_1
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retraction_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **grasp_0** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.16, 0.05], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.16, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.16, 0.0], offset_along_axis={axis=channel_axis, distance=0.18, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_force_limit: status=consumed; consumers=guards.push_guard.threshold (replace)
  - guards:
    - id=push_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=35.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.01, 0.0, 0.01]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retraction_height: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: -0.164
- **task_score** (E): 0.118
- **fitness_score**: 0.206  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| grasp_0 | 1.00 | 1.00 | 0.0095 |
| lift_1 | 1.00 | 1.00 | 0.1522 |
| approach_2 | 1.00 | 1.00 | 0.1845 |
| descend_3 | 1.00 | 1.00 | 0.2093 |
| push_4 | 0.00 | 1.00 | 0.0001 |
| retract_5 | 1.00 | 1.00 | 0.1513 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| grasp_0 | grasp | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.198, 0.291) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.534 | 2.488 |
| lift_1 | lift | 1.00 / step_budget | (0.497, 0.198, 0.291)→(0.496, 0.198, 0.444) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.558 | 0.589 |
| approach_2 | approach | 1.00 / step_budget | (0.496, 0.198, 0.444)→(0.499, 0.084, 0.299) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.541 | 0.587 |
| descend_3 | descend | 1.00 / step_budget | (0.499, 0.084, 0.299)→(0.498, 0.080, 0.090) | (0.504, 0.095, 0.034)→(0.505, 0.092, 0.033) | 0.175→0.172 | 1.00 / 1.667 | 31.083 | 32.707 |
| push_4 | push | 0.00 / guard_failure | (0.497, 0.075, 0.088)→(0.497, 0.075, 0.088) | (0.505, 0.092, 0.033)→(0.505, 0.088, 0.035) | 0.172→0.168 | 1.00 / 2.333 | 40.423 | 133.832 |
| retract_5 | retract | 1.00 / step_budget | (0.497, 0.075, 0.088)→(0.496, 0.074, 0.239) | (0.505, 0.087, 0.036)→(0.505, 0.075, 0.031) | 0.167→0.156 | 1.00 / 1.000 | 0.582 | 164.859 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.344
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.344
- phase_score: 0.277
- phase_breakdown.approach_channel_entry_score: 0.823
- phase_breakdown.push_through_channel_score: 0.043

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.304
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.344
- **Median Q (composite search score)**: -0.205
- **K-run variance**: 0.0049
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.409


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9b36d26f861d7a613dfb3d8c86d70470e42095a430c2befa4bd6e530468a8a7e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2af86d8f59685db6584febc0596b9044223ae39cea3120c112c665a54a1c4732`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92121,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_2.approach_speed":0.10003,"lift_1.lift_height":0.19129,"push_4.push_distance":0.11397,"push_4.push_force_limit":136.87307,"retract_5.retraction_height":0.15697},"optimized_scores":{"best_composite_score":-0.20527,"best_fitness_score":0.16473,"best_task_score":0.00943},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.47485,0.11959,0.05977],"force_p95":158.70521,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":159.6697,"mean_force":108.16364,"phase_index":5.0,"phase_name":"retract_5","phase_type":"retract","tcp_position_centroid":[0.49688,0.07504,0.08821]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.4749,0.11973,0.05985],"force_p95":139.87611,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":141.46983,"mean_force":99.24611,"phase_index":4.0,"phase_name":"push_4","phase_type":"push","tcp_position_centroid":[0.49698,0.07551,0.08809]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.50565,0.08569,0.00888],"force_p95":53.19852,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.28109,"mean_force":24.40893,"phase_index":4.0,"phase_name":"push_4","phase_type":"push","tcp_position_centroid":[0.49709,0.07756,0.08864]},{"body_a":"peg","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.50333,0.11921,0.05847],"force_p95":52.6645,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.68994,"mean_force":36.66643,"phase_index":4.0,"phase_name":"push_4","phase_type":"push","tcp_position_centroid":[0.49715,0.07858,0.08891]},{"body_a":"peg","body_b":"channel_base_body","contact_count":650.0,"contact_point_centroid":[0.50575,0.10434,0.00938],"force_p95":0.57561,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.49943,"mean_force":1.1676,"phase_index":3.0,"phase_name":"descend_3","phase_type":"descend","tcp_position_centroid":[0.49751,0.08098,0.19405]},{"body_a":"peg","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.50298,0.12147,0.0585],"force_p95":44.06445,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.08889,"mean_force":33.84814,"phase_index":3.0,"phase_name":"descend_3","phase_type":"descend","tcp_position_centroid":[0.49728,0.07915,0.09141]},{"body_a":"peg","body_b":"channel_base_body","contact_count":423.0,"contact_point_centroid":[0.50547,0.1046,0.00937],"force_p95":0.57957,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57306,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.497,0.19847,0.29242]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.49937,0.19945,0.29908]},{"body_a":"peg","body_b":"channel_base_body","contact_count":411.0,"contact_point_centroid":[0.50491,0.09958,0.00949],"force_p95":0.77942,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.25677,"mean_force":0.53759,"phase_index":5.0,"phase_name":"retract_5","phase_type":"retract","tcp_position_centroid":[0.49514,0.07419,0.15548]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":30.0,"contact_point_centroid":[0.52523,0.10164,0.05979],"force_p95":0.73722,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.01244,"mean_force":0.2343,"phase_index":5.0,"phase_name":"retract_5","phase_type":"retract","tcp_position_centroid":[0.49541,0.07439,0.11144]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52521,0.09358,0.05992],"force_p95":0.85086,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86237,"mean_force":0.7473,"phase_index":4.0,"phase_name":"push_4","phase_type":"push","tcp_position_centroid":[0.49697,0.07506,0.08799]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50591,0.10463,0.00939],"force_p95":0.5757,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57724,"mean_force":0.54634,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49554,0.1978,0.3707]},{"body_a":"peg","body_b":"channel_base_body","contact_count":693.0,"contact_point_centroid":[0.50588,0.10472,0.00939],"force_p95":0.57565,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57569,"mean_force":0.54635,"phase_index":2.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49336,0.14178,0.38003]}],"total_contact_groups":13},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50533,0.10159,0.03399],"final_tcp_position":[0.49533,0.07404,0.22501],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":159.6697,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50589,0.10472,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.53144,"phase_name":"grasp_0","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":455.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.49666,0.19833,0.29147],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.27427,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50584,0.10469,0.03384],"object_pos_start":[0.50589,0.10472,0.03384],"object_to_goal_dist_end":0.18489,"object_to_goal_dist_start":0.18492,"object_z_max":0.03384,"peak_contact_force":0.54308,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.57724,"tcp_end":[0.49622,0.198,0.45237],"tcp_start":[0.49666,0.19833,0.29147],"tcp_to_object_dist_end":0.42892,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":693.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.10467,0.03384],"object_pos_start":[0.50584,0.10469,0.03384],"object_to_goal_dist_end":0.18486,"object_to_goal_dist_start":0.18489,"object_z_max":0.03384,"peak_contact_force":0.54955,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":693.0,"raw_peak_contact_force":0.57569,"subtask_id":"approach_channel_entry","tcp_end":[0.49877,0.08356,0.29921],"tcp_start":[0.49622,0.198,0.45237],"tcp_to_object_dist_end":0.26631,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":650.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.10345,0.03313],"object_pos_start":[0.50598,0.10467,0.03384],"object_to_goal_dist_end":0.18368,"object_to_goal_dist_start":0.18486,"object_z_max":0.03384,"peak_contact_force":43.78541,"phase_name":"descend_3","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":662.0,"raw_peak_contact_force":45.49943,"tcp_end":[0.4974,0.07939,0.08963],"tcp_start":[0.49877,0.08356,0.29921],"tcp_to_object_dist_end":0.06202,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":20.0,"n_steps_budget":720.0,"object_pos_end":[0.50662,0.09763,0.03565],"object_pos_start":[0.50603,0.10345,0.03313],"object_to_goal_dist_end":0.1778,"object_to_goal_dist_start":0.18368,"object_z_max":0.03594,"peak_contact_force":42.77461,"phase_name":"push_4","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":41.0,"raw_peak_contact_force":141.46983,"subtask_id":"push_through_channel","tcp_end":[0.49692,0.0749,0.08791],"tcp_start":[0.49695,0.07498,0.08796],"tcp_to_object_dist_end":0.05782,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":411.0,"n_steps_budget":990.0,"object_pos_end":[0.50533,0.10159,0.03399],"object_pos_start":[0.50677,0.09692,0.03621],"object_to_goal_dist_end":0.18176,"object_to_goal_dist_start":0.17709,"object_z_max":0.03872,"peak_contact_force":0.55541,"phase_name":"retract_5","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":450.0,"raw_peak_contact_force":159.6697,"tcp_end":[0.49533,0.07404,0.22501],"tcp_start":[0.49692,0.0749,0.08791],"tcp_to_object_dist_end":0.19326,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71875,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_2.approach_speed":0.05947,"lift_1.lift_height":0.14771,"push_4.push_distance":0.18995,"push_4.push_force_limit":118.3527,"retract_5.retraction_height":0.22499},"optimized_scores":{"best_composite_score":-0.22154,"best_fitness_score":0.14846,"best_task_score":0.0002},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.47488,0.11965,0.0598],"force_p95":161.24357,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":161.29535,"mean_force":111.13322,"phase_index":5.0,"phase_name":"retract_5","phase_type":"retract","tcp_position_centroid":[0.49643,0.0755,0.08812]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.47491,0.11973,0.05985],"force_p95":111.70637,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":120.18924,"mean_force":61.86664,"phase_index":4.0,"phase_name":"push_4","phase_type":"push","tcp_position_centroid":[0.49637,0.07595,0.08782]},{"body_a":"peg","body_b":"channel_base_body","contact_count":434.0,"contact_point_centroid":[0.50304,0.06752,0.00933],"force_p95":0.56983,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56647,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.49705,0.1985,0.29258]},{"body_a":"peg","body_b":"channel_base_body","contact_count":843.0,"contact_point_centroid":[0.50304,0.0674,0.00938],"force_p95":0.55058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55115,"mean_force":0.54664,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49544,0.19777,0.35817]},{"body_a":"peg","body_b":"channel_base_body","contact_count":715.0,"contact_point_centroid":[0.5031,0.06751,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55065,"mean_force":0.54665,"phase_index":2.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49328,0.14621,0.36825]},{"body_a":"peg","body_b":"channel_base_body","contact_count":646.0,"contact_point_centroid":[0.503,0.06744,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55058,"mean_force":0.54665,"phase_index":3.0,"phase_name":"descend_3","phase_type":"descend","tcp_position_centroid":[0.49746,0.08153,0.19383]},{"body_a":"peg","body_b":"channel_base_body","contact_count":611.0,"contact_point_centroid":[0.50307,0.06748,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55056,"mean_force":0.54665,"phase_index":5.0,"phase_name":"retract_5","phase_type":"retract","tcp_position_centroid":[0.49476,0.07477,0.1894]},{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.50538,0.06469,0.00938],"force_p95":0.54875,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55054,"mean_force":0.54649,"phase_index":4.0,"phase_name":"push_4","phase_type":"push","tcp_position_centroid":[0.49669,0.0777,0.08848]}],"total_contact_groups":8},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50301,0.06743,0.0338],"final_tcp_position":[0.49529,0.07486,0.29278],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":161.29535,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54626,"phase_name":"grasp_0","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":434.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49666,0.19833,0.29147],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.28908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.50303,0.0675,0.0338],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14762,"object_z_max":0.0338,"peak_contact_force":0.54568,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":843.0,"raw_peak_contact_force":0.55115,"tcp_end":[0.496,0.19794,0.42714],"tcp_start":[0.49666,0.19833,0.29147],"tcp_to_object_dist_end":0.41446,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":715.0,"n_steps_budget":1000.0,"object_pos_end":[0.50307,0.06743,0.0338],"object_pos_start":[0.50303,0.0675,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":0.54554,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":715.0,"raw_peak_contact_force":0.55065,"subtask_id":"approach_channel_entry","tcp_end":[0.49869,0.08458,0.29847],"tcp_start":[0.496,0.19794,0.42714],"tcp_to_object_dist_end":0.26527,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":646.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06748,0.0338],"object_pos_start":[0.50307,0.06743,0.0338],"object_to_goal_dist_end":0.14765,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54736,"phase_name":"descend_3","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":646.0,"raw_peak_contact_force":0.55058,"tcp_end":[0.49714,0.079,0.08951],"tcp_start":[0.49869,0.08458,0.29847],"tcp_to_object_dist_end":0.0572,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.50304,0.06742,0.0338],"object_pos_start":[0.50308,0.06748,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14765,"object_z_max":0.0338,"peak_contact_force":30.05014,"phase_name":"push_4","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":17.0,"raw_peak_contact_force":120.18924,"subtask_id":"push_through_channel","tcp_end":[0.49637,0.07552,0.08772],"tcp_start":[0.49636,0.07569,0.08776],"tcp_to_object_dist_end":0.05494,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":611.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06743,0.0338],"object_pos_start":[0.503,0.06745,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14761,"object_z_max":0.0338,"peak_contact_force":0.54737,"phase_name":"retract_5","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":620.0,"raw_peak_contact_force":161.29535,"tcp_end":[0.49529,0.07486,0.29278],"tcp_start":[0.49637,0.07552,0.08772],"tcp_to_object_dist_end":0.2592,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51942,"average_solve_count":206.0,"average_success_count":206.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_2.approach_speed":0.04703,"lift_1.lift_height":0.20504,"push_4.push_distance":0.12486,"push_4.push_force_limit":99.6277,"retract_5.retraction_height":0.1314},"optimized_scores":{"best_composite_score":-0.06617,"best_fitness_score":0.30383,"best_task_score":0.34438},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.47486,0.11972,0.05984],"force_p95":171.69403,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":173.61262,"mean_force":126.1358,"phase_index":5.0,"phase_name":"retract_5","phase_type":"retract","tcp_position_centroid":[0.49807,0.07472,0.08856]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.47491,0.1198,0.05989],"force_p95":130.69778,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":139.83708,"mean_force":67.34543,"phase_index":4.0,"phase_name":"push_4","phase_type":"push","tcp_position_centroid":[0.49787,0.07525,0.0883]},{"body_a":"peg","body_b":"channel_base_body","contact_count":24.0,"contact_point_centroid":[0.49985,0.08758,0.00891],"force_p95":69.33007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.7482,"mean_force":42.95551,"phase_index":4.0,"phase_name":"push_4","phase_type":"push","tcp_position_centroid":[0.49792,0.07857,0.08889]},{"body_a":"peg","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.50222,0.12053,0.05804],"force_p95":69.06678,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.4102,"mean_force":53.73605,"phase_index":4.0,"phase_name":"push_4","phase_type":"push","tcp_position_centroid":[0.49793,0.07935,0.08902]},{"body_a":"peg","body_b":"channel_base_body","contact_count":655.0,"contact_point_centroid":[0.50384,0.11071,0.00936],"force_p95":43.39268,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.07017,"mean_force":3.7215,"phase_index":3.0,"phase_name":"descend_3","phase_type":"descend","tcp_position_centroid":[0.49752,0.08099,0.19313]},{"body_a":"peg","body_b":"link7","contact_count":49.0,"contact_point_centroid":[0.50191,0.12654,0.05745],"force_p95":49.12561,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.60475,"mean_force":42.50356,"phase_index":3.0,"phase_name":"descend_3","phase_type":"descend","tcp_position_centroid":[0.49764,0.08007,0.09656]},{"body_a":"peg","body_b":"channel_base_body","contact_count":317.0,"contact_point_centroid":[0.50596,0.05991,0.00831],"force_p95":0.91251,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.32494,"mean_force":0.68675,"phase_index":5.0,"phase_name":"retract_5","phase_type":"retract","tcp_position_centroid":[0.49614,0.07402,0.146]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52501,0.03245,0.02428],"force_p95":8.70629,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.84221,"mean_force":3.4177,"phase_index":5.0,"phase_name":"retract_5","phase_type":"retract","tcp_position_centroid":[0.49584,0.07381,0.14914]},{"body_a":"peg","body_b":"channel_base_body","contact_count":428.0,"contact_point_centroid":[0.50352,0.11166,0.00936],"force_p95":0.61517,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56336,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.49702,0.19848,0.29249]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50369,0.11168,0.00941],"force_p95":0.59562,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63935,"mean_force":0.54402,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49554,0.1978,0.37031]},{"body_a":"peg","body_b":"channel_base_body","contact_count":792.0,"contact_point_centroid":[0.5037,0.11169,0.0094],"force_p95":0.59406,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63553,"mean_force":0.54458,"phase_index":2.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49387,0.14375,0.38303]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.49961,0.19955,0.29976]}],"total_contact_groups":12},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50613,0.05668,0.02415],"final_tcp_position":[0.49616,0.0739,0.19996],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":173.61262,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,0.11179,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.5238,"phase_name":"grasp_0","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":444.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.49666,0.19833,0.29147],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.27191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.11171,0.03381],"object_pos_start":[0.5037,0.11179,0.0338],"object_to_goal_dist_end":0.19185,"object_to_goal_dist_start":0.19192,"object_z_max":0.03403,"peak_contact_force":0.58421,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.63935,"tcp_end":[0.49621,0.198,0.45159],"tcp_start":[0.49666,0.19833,0.29147],"tcp_to_object_dist_end":0.42666,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":792.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.1117,0.0338],"object_pos_start":[0.50376,0.11171,0.03381],"object_to_goal_dist_end":0.19184,"object_to_goal_dist_start":0.19185,"object_z_max":0.03392,"peak_contact_force":0.5282,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":792.0,"raw_peak_contact_force":0.63553,"subtask_id":"approach_channel_entry","tcp_end":[0.49874,0.08347,0.29903],"tcp_start":[0.49621,0.198,0.45159],"tcp_to_object_dist_end":0.26677,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":655.0,"n_steps_budget":1000.0,"object_pos_end":[0.50497,0.10565,0.03195],"object_pos_start":[0.50371,0.1117,0.0338],"object_to_goal_dist_end":0.18589,"object_to_goal_dist_start":0.19184,"object_z_max":0.034,"peak_contact_force":48.91476,"phase_name":"descend_3","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":704.0,"raw_peak_contact_force":52.07017,"tcp_end":[0.49808,0.08091,0.08972],"tcp_start":[0.49874,0.08347,0.29903],"tcp_to_object_dist_end":0.06322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":24.0,"n_steps_budget":810.0,"object_pos_end":[0.50469,0.09782,0.03618],"object_pos_start":[0.50497,0.10565,0.03195],"object_to_goal_dist_end":0.17793,"object_to_goal_dist_start":0.18589,"object_z_max":0.03661,"peak_contact_force":48.44415,"phase_name":"push_4","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":46.0,"raw_peak_contact_force":139.83708,"subtask_id":"push_through_channel","tcp_end":[0.49793,0.07481,0.08824],"tcp_start":[0.4979,0.07498,0.08826],"tcp_to_object_dist_end":0.05732,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":336.0,"n_steps_budget":840.0,"object_pos_end":[0.50613,0.05668,0.02415],"object_pos_start":[0.50473,0.09655,0.03701],"object_to_goal_dist_end":0.13773,"object_to_goal_dist_start":0.17663,"object_z_max":0.04074,"peak_contact_force":0.64351,"phase_name":"retract_5","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":333.0,"raw_peak_contact_force":173.61262,"tcp_end":[0.49616,0.0739,0.19996],"tcp_start":[0.49793,0.07481,0.08824],"tcp_to_object_dist_end":0.17693,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```