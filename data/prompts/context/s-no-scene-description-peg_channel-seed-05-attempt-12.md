## Search State

- **Seed**: 5
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | grasp → approach → descend → push → retract | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | time_limit | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.1062 | 0.00 | ❌ rejected |
| 11 | grasp → lift → rotate → approach → descend → push → retract | — | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.1583 | 0.04 | ❌ rejected |
| 10 | approach → grasp → lift → rotate → approach → descend → push → retract | linear_cartesian | — | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2305 | 0.00 | ❌ rejected |
| 9 | grasp → lift → approach → descend → push → retract | — | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | admittance_control | admittance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1643 | 0.12 | ❌ rejected |
| 8 | grasp → approach → descend → push → retract | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.0869 | 0.14 | ✅ accepted |

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

## Current Skill (Q=-0.106) — your mutation base

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

- **Composite score**: -0.106
- **task_score** (E): 0.002
- **fitness_score**: 0.151  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| grasp_0 | 1.00 | 1.00 | 0.0095 |
| approach_1 | 1.00 | 1.00 | 0.2247 |
| descend_1 | 0.67 | 1.00 | 0.0426 |
| push_1 | 0.33 | 1.00 | 0.0260 |
| retract_1 | 1.00 | 1.00 | 0.1814 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| grasp_0 | grasp | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.198, 0.291) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.534 | 2.488 |
| approach_1 | approach | 1.00 / step_budget | (0.497, 0.198, 0.291)→(0.496, 0.086, 0.097) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.535 | 0.589 |
| descend_1 | descend | 0.67 / force_exceeded | (0.496, 0.086, 0.097)→(0.495, 0.081, 0.054) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.667 | 12.607 | 12.615 |
| push_1 | push | 0.33 / guard_failure | (0.495, 0.080, 0.054)→(0.495, 0.054, 0.052) | (0.504, 0.095, 0.034)→(0.504, 0.094, 0.034) | 0.175→0.174 | 1.00 / 1.667 | 25.190 | 33.274 |
| retract_1 | retract | 1.00 / step_budget | (0.495, 0.054, 0.052)→(0.493, 0.053, 0.233) | (0.504, 0.094, 0.034)→(0.504, 0.095, 0.034) | 0.174→0.175 | 1.00 / 1.000 | 0.532 | 20.837 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.254
- phase_breakdown.approach_channel_entry_score: 0.820
- phase_breakdown.push_through_channel_score: 0.011

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.152
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.006
- **Median Q (composite search score)**: -0.039
- **K-run variance**: 0.0092
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.376


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84615,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.14907,"descend_1.descend_force_threshold":10.01001,"push_1.push_distance":0.2464,"push_1.push_force_limit":38.95947,"push_1.push_speed":0.07367,"retract_1.retraction_height":0.21591},"optimized_scores":{"best_composite_score":-0.03768,"best_fitness_score":0.15232,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":19.0,"contact_point_centroid":[0.50193,0.09121,0.00934],"force_p95":50.25661,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.90841,"mean_force":31.39119,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49451,0.08031,0.05971]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.5053,0.08517,0.05828],"force_p95":50.14412,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.64855,"mean_force":30.85208,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49451,0.08031,0.05971]},{"body_a":"peg","body_b":"channel_base_body","contact_count":591.0,"contact_point_centroid":[0.50527,0.10511,0.00943],"force_p95":0.6411,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.20096,"mean_force":0.62979,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49187,0.07669,0.15639]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.50395,0.08303,0.05829],"force_p95":24.64701,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.99385,"mean_force":4.69271,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49395,0.07671,0.05953]},{"body_a":"peg","body_b":"channel_base_body","contact_count":204.0,"contact_point_centroid":[0.50559,0.10457,0.00939],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.27603,"mean_force":0.65279,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49473,0.08401,0.07801]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50574,0.08681,0.05884],"force_p95":21.84884,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.84884,"mean_force":21.84884,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49483,0.08216,0.06059]},{"body_a":"peg","body_b":"channel_base_body","contact_count":423.0,"contact_point_centroid":[0.50547,0.1046,0.00937],"force_p95":0.57957,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57306,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.497,0.19847,0.29242]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.49937,0.19945,0.29908]},{"body_a":"peg","body_b":"channel_base_body","contact_count":669.0,"contact_point_centroid":[0.50599,0.10471,0.00939],"force_p95":0.57569,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57724,"mean_force":0.54633,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49591,0.1427,0.19319]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.52525,0.10804,0.05964],"force_p95":0.39397,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49475,"mean_force":0.1448,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49191,0.07656,0.07829]}],"total_contact_groups":10},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50564,0.10538,0.03391],"final_tcp_position":[0.49238,0.0768,0.25531],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":51.90841,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50589,0.10472,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.53144,"phase_name":"grasp_0","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":455.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.49666,0.19833,0.29147],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.27427,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":669.0,"n_steps_budget":990.0,"object_pos_end":[0.50595,0.10457,0.03384],"object_pos_start":[0.50589,0.10472,0.03384],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18492,"object_z_max":0.03384,"peak_contact_force":0.54213,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":669.0,"raw_peak_contact_force":0.57724,"subtask_id":"approach_channel_entry","tcp_end":[0.49654,0.08625,0.09691],"tcp_start":[0.49666,0.19833,0.29147],"tcp_to_object_dist_end":0.06636,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":204.0,"n_steps_budget":600.0,"object_pos_end":[0.50597,0.10471,0.03383],"object_pos_start":[0.50595,0.10457,0.03384],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.18477,"object_z_max":0.03384,"peak_contact_force":22.27603,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":205.0,"raw_peak_contact_force":22.27603,"tcp_end":[0.49486,0.08213,0.06043],"tcp_start":[0.49654,0.08625,0.09691],"tcp_to_object_dist_end":0.03662,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":19.0,"n_steps_budget":1000.0,"object_pos_end":[0.50563,0.10266,0.03526],"object_pos_start":[0.50597,0.10471,0.03383],"object_to_goal_dist_end":0.18281,"object_to_goal_dist_start":0.18491,"object_z_max":0.03551,"peak_contact_force":50.07307,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":38.0,"raw_peak_contact_force":51.90841,"subtask_id":"push_through_channel","tcp_end":[0.49444,0.07717,0.05913],"tcp_start":[0.49445,0.07737,0.05917],"tcp_to_object_dist_end":0.03667,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":591.0,"n_steps_budget":1000.0,"object_pos_end":[0.50564,0.10538,0.03391],"object_pos_start":[0.5057,0.10222,0.03558],"object_to_goal_dist_end":0.18557,"object_to_goal_dist_start":0.18236,"object_z_max":0.03612,"peak_contact_force":0.53544,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":622.0,"raw_peak_contact_force":35.20096,"tcp_end":[0.49238,0.0768,0.25531],"tcp_start":[0.49444,0.07717,0.05913],"tcp_to_object_dist_end":0.22363,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65289,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.08515,"descend_1.descend_force_threshold":5.54331,"push_1.push_distance":0.19686,"push_1.push_force_limit":36.4935,"push_1.push_speed":0.01169,"retract_1.retraction_height":0.17943},"optimized_scores":{"best_composite_score":-0.03926,"best_fitness_score":0.15074,"best_task_score":0.00554},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":13.0,"contact_point_centroid":[0.49179,0.0623,0.00933],"force_p95":41.7138,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.27746,"mean_force":25.76348,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49451,0.08178,0.06007]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.50634,0.08174,0.05843],"force_p95":41.34752,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.93225,"mean_force":25.31855,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49451,0.08178,0.06007]},{"body_a":"peg","body_b":"channel_base_body","contact_count":483.0,"contact_point_centroid":[0.50199,0.06666,0.0094],"force_p95":0.59032,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.6871,"mean_force":0.65927,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49171,0.08063,0.13883]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.50557,0.08069,0.05839],"force_p95":23.55281,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.20089,"mean_force":5.04645,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49375,0.08092,0.06004]},{"body_a":"peg","body_b":"channel_base_body","contact_count":204.0,"contact_point_centroid":[0.50328,0.0675,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.93052,"mean_force":0.61716,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49465,0.08398,0.07799]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50658,0.08212,0.05876],"force_p95":14.46566,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.46566,"mean_force":14.46566,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49474,0.08214,0.06067]},{"body_a":"peg","body_b":"channel_base_body","contact_count":434.0,"contact_point_centroid":[0.50304,0.06752,0.00933],"force_p95":0.56983,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56647,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.49705,0.1985,0.29258]},{"body_a":"peg","body_b":"channel_base_body","contact_count":726.0,"contact_point_centroid":[0.50303,0.06739,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55115,"mean_force":0.54664,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49584,0.1426,0.19303]}],"total_contact_groups":8},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50255,0.06657,0.03385],"final_tcp_position":[0.49203,0.08068,0.21955],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":47.27746,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54626,"phase_name":"grasp_0","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":434.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49666,0.19833,0.29147],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.28908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":726.0,"n_steps_budget":1000.0,"object_pos_end":[0.50303,0.0675,0.0338],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14762,"object_z_max":0.0338,"peak_contact_force":0.54553,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":726.0,"raw_peak_contact_force":0.55115,"subtask_id":"approach_channel_entry","tcp_end":[0.49643,0.08619,0.09679],"tcp_start":[0.49666,0.19833,0.29147],"tcp_to_object_dist_end":0.06604,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":204.0,"n_steps_budget":600.0,"object_pos_end":[0.50307,0.06743,0.03379],"object_pos_start":[0.50303,0.0675,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":14.93052,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":205.0,"raw_peak_contact_force":14.93052,"tcp_end":[0.49477,0.08213,0.06052],"tcp_start":[0.49643,0.08619,0.09679],"tcp_to_object_dist_end":0.03162,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.50273,0.06717,0.03373],"object_pos_start":[0.50307,0.06743,0.03379],"object_to_goal_dist_end":0.14733,"object_to_goal_dist_start":0.14759,"object_z_max":0.03379,"peak_contact_force":24.94142,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":26.0,"raw_peak_contact_force":47.27746,"subtask_id":"push_through_channel","tcp_end":[0.49435,0.0811,0.05969],"tcp_start":[0.49437,0.08116,0.05974],"tcp_to_object_dist_end":0.03063,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.50255,0.06657,0.03385],"object_pos_start":[0.5027,0.06698,0.03369],"object_to_goal_dist_end":0.14673,"object_to_goal_dist_start":0.14714,"object_z_max":0.03447,"peak_contact_force":0.54,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":494.0,"raw_peak_contact_force":26.6871,"tcp_end":[0.49203,0.08068,0.21955],"tcp_start":[0.49435,0.0811,0.05969],"tcp_to_object_dist_end":0.18653,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72956,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07418,"descend_1.descend_force_threshold":22.26173,"push_1.push_distance":0.09646,"push_1.push_force_limit":25.35424,"push_1.push_speed":0.06654,"retract_1.retraction_height":0.20781},"optimized_scores":{"best_composite_score":-0.24156,"best_fitness_score":0.14844,"best_task_score":0.00045},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":428.0,"contact_point_centroid":[0.50352,0.11166,0.00936],"force_p95":0.61517,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56336,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.49702,0.19848,0.29249]},{"body_a":"peg","body_b":"channel_base_body","contact_count":318.0,"contact_point_centroid":[0.5038,0.1115,0.00943],"force_p95":0.59753,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63991,"mean_force":0.54169,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49488,0.08293,0.06843]},{"body_a":"peg","body_b":"channel_base_body","contact_count":735.0,"contact_point_centroid":[0.50365,0.11166,0.00941],"force_p95":0.60397,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63764,"mean_force":0.54371,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49573,0.14255,0.19294]},{"body_a":"peg","body_b":"channel_base_body","contact_count":197.0,"contact_point_centroid":[0.5035,0.11172,0.00942],"force_p95":0.59986,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63554,"mean_force":0.54294,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49462,0.04248,0.03797]},{"body_a":"peg","body_b":"channel_base_body","contact_count":564.0,"contact_point_centroid":[0.50367,0.11158,0.00941],"force_p95":0.60161,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6237,"mean_force":0.54374,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49287,0.00241,0.12907]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.49961,0.19955,0.29976]}],"total_contact_groups":6},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50372,0.1117,0.0339],"final_tcp_position":[0.49333,0.00252,0.22404],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":2.06328,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,0.11179,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.5238,"phase_name":"grasp_0","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":444.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.49666,0.19833,0.29147],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.27191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":735.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11175,0.03388],"object_pos_start":[0.5037,0.11179,0.0338],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19192,"object_z_max":0.03402,"peak_contact_force":0.51819,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":735.0,"raw_peak_contact_force":0.63764,"subtask_id":"approach_channel_entry","tcp_end":[0.49645,0.08614,0.09671],"tcp_start":[0.49666,0.19833,0.29147],"tcp_to_object_dist_end":0.06824,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":318.0,"n_steps_budget":600.0,"object_pos_end":[0.50369,0.1118,0.03389],"object_pos_start":[0.50373,0.11175,0.03388],"object_to_goal_dist_end":0.19193,"object_to_goal_dist_start":0.19189,"object_z_max":0.03399,"peak_contact_force":0.61464,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":318.0,"raw_peak_contact_force":0.63991,"tcp_end":[0.4957,0.08014,0.04245],"tcp_start":[0.49645,0.08614,0.09671],"tcp_to_object_dist_end":0.03376,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":197.0,"n_steps_budget":930.0,"object_pos_end":[0.50376,0.11172,0.03385],"object_pos_start":[0.50369,0.1118,0.03389],"object_to_goal_dist_end":0.19186,"object_to_goal_dist_start":0.19193,"object_z_max":0.03394,"peak_contact_force":0.55683,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":197.0,"raw_peak_contact_force":0.63554,"subtask_id":"push_through_channel","tcp_end":[0.49565,0.00259,0.03595],"tcp_start":[0.4957,0.08014,0.04245],"tcp_to_object_dist_end":0.10946,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":564.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.1117,0.0339],"object_pos_start":[0.50376,0.11172,0.03385],"object_to_goal_dist_end":0.19183,"object_to_goal_dist_start":0.19186,"object_z_max":0.03405,"peak_contact_force":0.52085,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":564.0,"raw_peak_contact_force":0.6237,"tcp_end":[0.49333,0.00252,0.22404],"tcp_start":[0.49565,0.00259,0.03595],"tcp_to_object_dist_end":0.21951,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```