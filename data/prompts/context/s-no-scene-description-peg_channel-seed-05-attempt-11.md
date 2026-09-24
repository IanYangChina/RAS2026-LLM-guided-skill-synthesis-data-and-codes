## Search State

- **Seed**: 5
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | grasp → lift → rotate → approach → descend → push → retract | — | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.1583 | 0.04 | ❌ rejected |
| 10 | approach → grasp → lift → rotate → approach → descend → push → retract | linear_cartesian | — | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2305 | 0.00 | ❌ rejected |
| 9 | grasp → lift → approach → descend → push → retract | — | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | admittance_control | admittance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1643 | 0.12 | ❌ rejected |
| 8 | grasp → approach → descend → push → retract | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.0869 | 0.14 | ✅ accepted |
| 7 | grasp → approach → push → retract | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.0715 | 0.12 | ✅ accepted |

**Proposal policy**: task_score is 0.04 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.158) — your mutation base

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

- **Composite score**: -0.158
- **task_score** (E): 0.041
- **fitness_score**: 0.196  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.095
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| grasp_0 | 1.00 | 1.00 | 0.0095 |
| lift_1 | 1.00 | 1.00 | 0.1253 |
| rotate_2 | 0.67 | 1.00 | 0.0229 |
| approach_3 | 1.00 | 1.00 | 0.1385 |
| descend_4 | 0.67 | 1.00 | 0.0440 |
| push_5 | 0.33 | 1.00 | 0.0355 |
| retract_6 | 1.00 | 1.00 | 0.1032 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| grasp_0 | grasp | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.198, 0.291) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.534 | 2.488 |
| lift_1 | lift | 1.00 / step_budget | (0.497, 0.198, 0.291)→(0.497, 0.089, 0.239) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.540 | 0.592 |
| rotate_2 | rotate | 0.67 / step_budget | (0.497, 0.089, 0.239)→(0.490, 0.110, 0.234) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.533 | 0.585 |
| approach_3 | approach | 1.00 / step_budget | (0.490, 0.110, 0.234)→(0.496, 0.082, 0.099) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.553 | 0.586 |
| descend_4 | descend | 0.67 / force_exceeded | (0.496, 0.082, 0.099)→(0.495, 0.080, 0.055) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.667 | 19.919 | 19.938 |
| push_5 | push | 0.33 / guard_failure | (0.495, 0.024, 0.048)→(0.495, -0.012, 0.045) | (0.504, 0.095, 0.034)→(0.503, 0.080, 0.031) | 0.175→0.161 | 1.00 / 1.667 | 15.365 | 49.806 |
| retract_6 | retract | 1.00 / step_budget | (0.495, -0.012, 0.045)→(0.492, -0.012, 0.149) | (0.503, 0.080, 0.030)→(0.503, 0.080, 0.031) | 0.161→0.161 | 1.00 / 1.000 | 0.547 | 43.144 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.267
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.121
- phase_score: 0.405
- phase_breakdown.approach_channel_entry_score: 0.820
- phase_breakdown.push_through_channel_score: 0.228

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.292
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.121
- **Median Q (composite search score)**: -0.158
- **K-run variance**: 0.0136
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: push_5.push_force_limit
- **Final σ (mean)**: 0.336


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51429,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_3.approach_speed":0.04758,"descend_4.descend_force_threshold":19.07295,"lift_1.lift_height":0.17766,"push_5.push_distance":0.22435,"push_5.push_force_limit":39.99905,"retract_6.retraction_height":0.16053},"optimized_scores":{"best_composite_score":-0.01536,"best_fitness_score":0.29178,"best_task_score":0.12145},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49516,-0.10022,0.04042],"force_p95":104.62915,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":106.80178,"mean_force":74.29146,"phase_index":5.0,"phase_name":"push_5","phase_type":"push","tcp_position_centroid":[0.49515,-0.08845,0.04032]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":10.0,"contact_point_centroid":[0.49466,-0.10031,0.04252],"force_p95":101.13258,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":101.68947,"mean_force":80.18756,"phase_index":6.0,"phase_name":"retract_6","phase_type":"retract","tcp_position_centroid":[0.49465,-0.08862,0.04243]},{"body_a":"peg","body_b":"channel_base_body","contact_count":397.0,"contact_point_centroid":[0.50358,0.07019,0.00855],"force_p95":33.09588,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.94987,"mean_force":3.96947,"phase_index":5.0,"phase_name":"push_5","phase_type":"push","tcp_position_centroid":[0.49377,-0.00538,0.04884]},{"body_a":"attachment","body_b":"peg","contact_count":63.0,"contact_point_centroid":[0.50132,0.07781,0.05723],"force_p95":38.63129,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.4475,"mean_force":21.32002,"phase_index":5.0,"phase_name":"push_5","phase_type":"push","tcp_position_centroid":[0.49405,0.06899,0.05829]},{"body_a":"peg","body_b":"channel_base_body","contact_count":215.0,"contact_point_centroid":[0.50556,0.10473,0.00939],"force_p95":0.57566,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.73472,"mean_force":0.72753,"phase_index":4.0,"phase_name":"descend_4","phase_type":"descend","tcp_position_centroid":[0.49402,0.08144,0.07867]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50442,0.08686,0.05884],"force_p95":21.12404,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.29249,"mean_force":19.60798,"phase_index":4.0,"phase_name":"descend_4","phase_type":"descend","tcp_position_centroid":[0.49442,0.08055,0.06076]},{"body_a":"peg","body_b":"channel_base_body","contact_count":423.0,"contact_point_centroid":[0.50547,0.1046,0.00937],"force_p95":0.57957,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57306,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.497,0.19847,0.29242]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.49937,0.19945,0.29908]},{"body_a":"peg","body_b":"channel_base_body","contact_count":428.0,"contact_point_centroid":[0.50325,0.06173,0.00798],"force_p95":0.77008,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77008,"mean_force":0.6062,"phase_index":6.0,"phase_name":"retract_6","phase_type":"retract","tcp_position_centroid":[0.49234,-0.08825,0.10958]},{"body_a":"peg","body_b":"channel_base_body","contact_count":473.0,"contact_point_centroid":[0.50599,0.10476,0.00939],"force_p95":0.57566,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57724,"mean_force":0.54633,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4962,0.14431,0.25355]},{"body_a":"peg","body_b":"channel_base_body","contact_count":271.0,"contact_point_centroid":[0.50577,0.10461,0.00939],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57576,"mean_force":0.54639,"phase_index":2.0,"phase_name":"rotate_2","phase_type":"rotate","tcp_position_centroid":[0.49277,0.10048,0.21496]},{"body_a":"peg","body_b":"channel_base_body","contact_count":421.0,"contact_point_centroid":[0.50603,0.10456,0.00939],"force_p95":0.57569,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57571,"mean_force":0.54629,"phase_index":3.0,"phase_name":"approach_3","phase_type":"approach","tcp_position_centroid":[0.49184,0.09702,0.1564]}],"total_contact_groups":12},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50363,0.06189,0.02406],"final_tcp_position":[0.49251,-0.08845,0.18097],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":106.80178,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50589,0.10472,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.53144,"phase_name":"grasp_0","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":455.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.49666,0.19833,0.29147],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.27427,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":473.0,"n_steps_budget":870.0,"object_pos_end":[0.50598,0.1046,0.03384],"object_pos_start":[0.50589,0.10472,0.03384],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18492,"object_z_max":0.03384,"peak_contact_force":0.53555,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":473.0,"raw_peak_contact_force":0.57724,"tcp_end":[0.49722,0.08949,0.21896],"tcp_start":[0.49666,0.19833,0.29147],"tcp_to_object_dist_end":0.18595,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":271.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.10467,0.03384],"object_pos_start":[0.50598,0.1046,0.03384],"object_to_goal_dist_end":0.18487,"object_to_goal_dist_start":0.1848,"object_z_max":0.03384,"peak_contact_force":0.54956,"phase_name":"rotate_2","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":271.0,"raw_peak_contact_force":0.57576,"tcp_end":[0.49014,0.11077,0.21415],"tcp_start":[0.49722,0.08949,0.21896],"tcp_to_object_dist_end":0.18112,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":421.0,"n_steps_budget":1000.0,"object_pos_end":[0.50586,0.10456,0.03384],"object_pos_start":[0.50599,0.10467,0.03384],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18487,"object_z_max":0.03384,"peak_contact_force":0.55164,"phase_name":"approach_3","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":421.0,"raw_peak_contact_force":0.57571,"subtask_id":"approach_channel_entry","tcp_end":[0.49563,0.0827,0.09847],"tcp_start":[0.49014,0.11077,0.21415],"tcp_to_object_dist_end":0.069,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":215.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.10472,0.03381],"object_pos_start":[0.50586,0.10456,0.03384],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18476,"object_z_max":0.03384,"peak_contact_force":21.73472,"phase_name":"descend_4","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":217.0,"raw_peak_contact_force":21.73472,"tcp_end":[0.49447,0.08052,0.06053],"tcp_start":[0.49563,0.0827,0.09847],"tcp_to_object_dist_end":0.03783,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.50306,0.06192,0.02406],"object_pos_start":[0.50596,0.10472,0.03381],"object_to_goal_dist_end":0.14285,"object_to_goal_dist_start":0.18492,"object_z_max":0.04081,"peak_contact_force":30.99707,"phase_name":"push_5","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":463.0,"raw_peak_contact_force":106.80178,"subtask_id":"push_through_channel","tcp_end":[0.49516,-0.08884,0.04026],"tcp_start":[0.49517,-0.08871,0.0403],"tcp_to_object_dist_end":0.15184,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":428.0,"n_steps_budget":1000.0,"object_pos_end":[0.50363,0.06189,0.02406],"object_pos_start":[0.50305,0.0618,0.02405],"object_to_goal_dist_end":0.14283,"object_to_goal_dist_start":0.14273,"object_z_max":0.02406,"peak_contact_force":0.59293,"phase_name":"retract_6","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":438.0,"raw_peak_contact_force":101.68947,"tcp_end":[0.49251,-0.08845,0.18097],"tcp_start":[0.49516,-0.08884,0.04026],"tcp_to_object_dist_end":0.2176,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33607,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_3.approach_speed":0.05059,"descend_4.descend_force_threshold":22.34753,"lift_1.lift_height":0.17008,"push_5.push_distance":0.20221,"push_5.push_force_limit":26.99042,"retract_6.retraction_height":0.06974},"optimized_scores":{"best_composite_score":-0.15807,"best_fitness_score":0.14907,"best_task_score":0.00191},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.50007,0.06942,0.00933],"force_p95":41.83156,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.98474,"mean_force":22.48627,"phase_index":5.0,"phase_name":"push_5","phase_type":"push","tcp_position_centroid":[0.49422,0.0804,0.0605]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.506,0.08083,0.05849],"force_p95":41.40286,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.56359,"mean_force":22.08472,"phase_index":5.0,"phase_name":"push_5","phase_type":"push","tcp_position_centroid":[0.49422,0.0804,0.0605]},{"body_a":"peg","body_b":"channel_base_body","contact_count":213.0,"contact_point_centroid":[0.50285,0.06749,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.43618,"mean_force":0.71985,"phase_index":4.0,"phase_name":"descend_4","phase_type":"descend","tcp_position_centroid":[0.49397,0.08153,0.07869]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50613,0.08088,0.05871],"force_p95":36.80942,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.80942,"mean_force":36.80942,"phase_index":4.0,"phase_name":"descend_4","phase_type":"descend","tcp_position_centroid":[0.49435,0.08061,0.0609]},{"body_a":"peg","body_b":"channel_base_body","contact_count":159.0,"contact_point_centroid":[0.50108,0.06678,0.00941],"force_p95":0.69252,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.09032,"mean_force":0.95403,"phase_index":6.0,"phase_name":"retract_6","phase_type":"retract","tcp_position_centroid":[0.49164,0.07948,0.08423]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.50542,0.08038,0.05849],"force_p95":22.22393,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.57395,"mean_force":6.57085,"phase_index":6.0,"phase_name":"retract_6","phase_type":"retract","tcp_position_centroid":[0.49366,0.07976,0.06044]},{"body_a":"peg","body_b":"channel_base_body","contact_count":434.0,"contact_point_centroid":[0.50304,0.06752,0.00933],"force_p95":0.56983,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56647,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.49705,0.1985,0.29258]},{"body_a":"peg","body_b":"channel_base_body","contact_count":481.0,"contact_point_centroid":[0.50309,0.06735,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55115,"mean_force":0.54665,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49617,0.14431,0.25012]},{"body_a":"peg","body_b":"channel_base_body","contact_count":257.0,"contact_point_centroid":[0.50299,0.06764,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55074,"mean_force":0.54664,"phase_index":2.0,"phase_name":"rotate_2","phase_type":"rotate","tcp_position_centroid":[0.49272,0.10023,0.208]},{"body_a":"peg","body_b":"channel_base_body","contact_count":398.0,"contact_point_centroid":[0.50313,0.06741,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55066,"mean_force":0.54665,"phase_index":3.0,"phase_name":"approach_3","phase_type":"approach","tcp_position_centroid":[0.49177,0.09698,0.1528]}],"total_contact_groups":10},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5028,0.06716,0.03388],"final_tcp_position":[0.49101,0.07943,0.11038],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":41.98474,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54626,"phase_name":"grasp_0","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":434.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49666,0.19833,0.29147],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.28908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":481.0,"n_steps_budget":900.0,"object_pos_end":[0.50301,0.06745,0.0338],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14762,"object_z_max":0.0338,"peak_contact_force":0.54705,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":481.0,"raw_peak_contact_force":0.55115,"tcp_end":[0.49716,0.08937,0.21195],"tcp_start":[0.49666,0.19833,0.29147],"tcp_to_object_dist_end":0.17959,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":257.0,"n_steps_budget":600.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50301,0.06745,0.0338],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14761,"object_z_max":0.0338,"peak_contact_force":0.54372,"phase_name":"rotate_2","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":257.0,"raw_peak_contact_force":0.55074,"tcp_end":[0.49006,0.11053,0.20716],"tcp_start":[0.49716,0.08937,0.21195],"tcp_to_object_dist_end":0.17911,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":398.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14762,"object_z_max":0.0338,"peak_contact_force":0.54778,"phase_name":"approach_3","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":398.0,"raw_peak_contact_force":0.55066,"subtask_id":"approach_channel_entry","tcp_end":[0.49557,0.08281,0.09826],"tcp_start":[0.49006,0.11053,0.20716],"tcp_to_object_dist_end":0.0667,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":213.0,"n_steps_budget":600.0,"object_pos_end":[0.50313,0.0675,0.03381],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14767,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":37.43618,"phase_name":"descend_4","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":214.0,"raw_peak_contact_force":37.43618,"tcp_end":[0.49439,0.0806,0.06076],"tcp_start":[0.49557,0.08281,0.09826],"tcp_to_object_dist_end":0.03121,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.50294,0.06739,0.03367],"object_pos_start":[0.50313,0.0675,0.03381],"object_to_goal_dist_end":0.14756,"object_to_goal_dist_start":0.14767,"object_z_max":0.03381,"peak_contact_force":14.55157,"phase_name":"push_5","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":14.0,"raw_peak_contact_force":41.98474,"subtask_id":"push_through_channel","tcp_end":[0.49409,0.07996,0.06022],"tcp_start":[0.49409,0.08005,0.06028],"tcp_to_object_dist_end":0.03068,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":159.0,"n_steps_budget":600.0,"object_pos_end":[0.5028,0.06716,0.03388],"object_pos_start":[0.50292,0.06725,0.03363],"object_to_goal_dist_end":0.14731,"object_to_goal_dist_start":0.14741,"object_z_max":0.03439,"peak_contact_force":0.53897,"phase_name":"retract_6","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":169.0,"raw_peak_contact_force":27.09032,"tcp_end":[0.49101,0.07943,0.11038],"tcp_start":[0.49409,0.07996,0.06022],"tcp_to_object_dist_end":0.07837,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83007,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_3.approach_speed":0.07664,"descend_4.descend_force_threshold":24.96681,"lift_1.lift_height":0.25025,"push_5.push_distance":0.12555,"push_5.push_force_limit":21.01242,"retract_6.retraction_height":0.13811},"optimized_scores":{"best_composite_score":-0.30154,"best_fitness_score":0.14846,"best_task_score":0.00067},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":428.0,"contact_point_centroid":[0.50352,0.11166,0.00936],"force_p95":0.61517,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56336,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.49702,0.19848,0.29249]},{"body_a":"peg","body_b":"channel_base_body","contact_count":358.0,"contact_point_centroid":[0.50358,0.11158,0.00941],"force_p95":0.59898,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65254,"mean_force":0.54323,"phase_index":6.0,"phase_name":"retract_6","phase_type":"retract","tcp_position_centroid":[0.49289,-0.02671,0.09401]},{"body_a":"peg","body_b":"channel_base_body","contact_count":513.0,"contact_point_centroid":[0.50365,0.11172,0.00939],"force_p95":0.60771,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64773,"mean_force":0.54489,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49643,0.14253,0.28626]},{"body_a":"peg","body_b":"channel_base_body","contact_count":326.0,"contact_point_centroid":[0.50379,0.11171,0.0094],"force_p95":0.6009,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6431,"mean_force":0.54508,"phase_index":4.0,"phase_name":"descend_4","phase_type":"descend","tcp_position_centroid":[0.49459,0.08032,0.06931]},{"body_a":"peg","body_b":"channel_base_body","contact_count":257.0,"contact_point_centroid":[0.50365,0.1116,0.0094],"force_p95":0.59822,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63253,"mean_force":0.54448,"phase_index":5.0,"phase_name":"push_5","phase_type":"push","tcp_position_centroid":[0.49454,0.02717,0.03753]},{"body_a":"peg","body_b":"channel_base_body","contact_count":595.0,"contact_point_centroid":[0.50375,0.1116,0.00942],"force_p95":0.59586,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63064,"mean_force":0.54317,"phase_index":3.0,"phase_name":"approach_3","phase_type":"approach","tcp_position_centroid":[0.49282,0.09575,0.18956]},{"body_a":"peg","body_b":"channel_base_body","contact_count":265.0,"contact_point_centroid":[0.50359,0.11172,0.00942],"force_p95":0.60064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6281,"mean_force":0.54319,"phase_index":2.0,"phase_name":"rotate_2","phase_type":"rotate","tcp_position_centroid":[0.49375,0.09947,0.28134]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.49961,0.19955,0.29976]}],"total_contact_groups":8},"final_pose_error":0.01974,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50373,0.11166,0.03381],"final_tcp_position":[0.49297,-0.02654,0.1543],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":2.06328,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,0.11179,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.5238,"phase_name":"grasp_0","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":444.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.49666,0.19833,0.29147],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.27191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":513.0,"n_steps_budget":750.0,"object_pos_end":[0.50372,0.11178,0.03386],"object_pos_start":[0.5037,0.11179,0.0338],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.19192,"object_z_max":0.03391,"peak_contact_force":0.53809,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":513.0,"raw_peak_contact_force":0.64773,"tcp_end":[0.49774,0.08825,0.28535],"tcp_start":[0.49666,0.19833,0.29147],"tcp_to_object_dist_end":0.25266,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":265.0,"n_steps_budget":630.0,"object_pos_end":[0.50376,0.11177,0.0338],"object_pos_start":[0.50372,0.11178,0.03386],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19192,"object_z_max":0.03398,"peak_contact_force":0.50449,"phase_name":"rotate_2","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":265.0,"raw_peak_contact_force":0.6281,"tcp_end":[0.49121,0.10967,0.28043],"tcp_start":[0.49774,0.08825,0.28535],"tcp_to_object_dist_end":0.24695,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":595.0,"n_steps_budget":1000.0,"object_pos_end":[0.50369,0.11173,0.03384],"object_pos_start":[0.50376,0.11177,0.0338],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.1919,"object_z_max":0.03404,"peak_contact_force":0.55949,"phase_name":"approach_3","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":595.0,"raw_peak_contact_force":0.63064,"subtask_id":"approach_channel_entry","tcp_end":[0.496,0.08153,0.09878],"tcp_start":[0.49121,0.10967,0.28043],"tcp_to_object_dist_end":0.07203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":326.0,"n_steps_budget":600.0,"object_pos_end":[0.50368,0.11171,0.03381],"object_pos_start":[0.50369,0.11173,0.03384],"object_to_goal_dist_end":0.19184,"object_to_goal_dist_start":0.19187,"object_z_max":0.03385,"peak_contact_force":0.58688,"phase_name":"descend_4","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":326.0,"raw_peak_contact_force":0.6431,"tcp_end":[0.49565,0.07953,0.04229],"tcp_start":[0.496,0.08153,0.09878],"tcp_to_object_dist_end":0.03423,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":257.0,"n_steps_budget":810.0,"object_pos_end":[0.50373,0.11165,0.03381],"object_pos_start":[0.50368,0.11171,0.03381],"object_to_goal_dist_end":0.19179,"object_to_goal_dist_start":0.19184,"object_z_max":0.0339,"peak_contact_force":0.54762,"phase_name":"push_5","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":257.0,"raw_peak_contact_force":0.63253,"subtask_id":"push_through_channel","tcp_end":[0.4958,-0.02662,0.03572],"tcp_start":[0.49565,0.07953,0.04229],"tcp_to_object_dist_end":0.13851,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":358.0,"n_steps_budget":870.0,"object_pos_end":[0.50373,0.11166,0.03381],"object_pos_start":[0.50373,0.11165,0.03381],"object_to_goal_dist_end":0.1918,"object_to_goal_dist_start":0.19179,"object_z_max":0.03395,"peak_contact_force":0.50811,"phase_name":"retract_6","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":358.0,"raw_peak_contact_force":0.65254,"tcp_end":[0.49297,-0.02654,0.1543],"tcp_start":[0.4958,-0.02662,0.03572],"tcp_to_object_dist_end":0.18366,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```