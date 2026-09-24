## Search State

- **Seed**: 5
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | grasp → approach → push → retract | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.0715 | 0.12 | ✅ accepted |
| 6 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.2993 | 0.00 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → insert → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | -0.5799 | 0.00 | ❌ rejected |
| 4 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.2994 | 0.00 | ❌ rejected |
| 3 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.2993 | 0.00 | ✅ accepted |

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

## Current Skill (Q=-0.071) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.0
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
    anchor: task_object
    offset:
    - 0.0
    - 0.0
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
  subtask_id: approach_peg
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
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
      default: 30.0
      binds_to:
      - path: guards.push_guard.threshold
        mode: replace
  guards:
  - id: push_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.18, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_force_limit: status=consumed; consumers=guards.push_guard.threshold (replace)
  - guards:
    - id=push_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.01, 0.0, 0.01]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retraction_height: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: -0.071
- **task_score** (E): 0.118
- **fitness_score**: 0.189  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| grasp_0 | 1.00 | 1.00 | 0.0095 |
| approach_1 | 1.00 | 1.00 | 0.2237 |
| push_1 | 0.00 | 1.00 | 0.0002 |
| retract_1 | 1.00 | 1.00 | 0.1775 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| grasp_0 | grasp | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.198, 0.291) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.534 | 2.488 |
| approach_1 | approach | 1.00 / step_budget | (0.497, 0.198, 0.291)→(0.501, 0.099, 0.092) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.553 | 0.589 |
| push_1 | push | 0.00 / guard_failure | (0.500, 0.080, 0.082)→(0.500, 0.080, 0.082) | (0.504, 0.095, 0.034)→(0.504, 0.094, 0.034) | 0.175→0.174 | 1.00 / 2.000 | 17.225 | 44.637 |
| retract_1 | retract | 1.00 / step_budget | (0.500, 0.080, 0.082)→(0.499, 0.079, 0.260) | (0.504, 0.093, 0.034)→(0.502, 0.065, 0.027) | 0.173→0.146 | 1.00 / 1.000 | 0.560 | 97.709 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.277
- alignment_error: None
- force_efficiency: 0.366
- terminal_score: 0.240
- phase_score: 0.248
- phase_breakdown.push_through_channel_score: 0.007
- phase_breakdown.approach_peg_score: 0.810

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.244
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.240
- **Median Q (composite search score)**: -0.096
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.316


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93396,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.09012,"push_1.push_distance":0.15112,"push_1.push_force_limit":30.58886,"retract_1.retraction_height":0.19112},"optimized_scores":{"best_composite_score":-0.09607,"best_fitness_score":0.16393,"best_task_score":0.11404},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.525,0.11984,0.05836],"force_p95":136.00263,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":137.52282,"mean_force":93.20155,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50091,0.07965,0.07746]},{"body_a":"peg","body_b":"channel_base_body","contact_count":71.0,"contact_point_centroid":[0.50563,0.10353,0.00938],"force_p95":1.37938,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.04111,"mean_force":1.4285,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50157,0.09561,0.08442]},{"body_a":"peg","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.50588,0.12166,0.04748],"force_p95":29.06657,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.76191,"mean_force":12.99998,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50118,0.08145,0.07793]},{"body_a":"peg","body_b":"channel_base_body","contact_count":505.0,"contact_point_centroid":[0.50131,0.06624,0.00852],"force_p95":0.74711,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.37581,"mean_force":0.61915,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49923,0.07913,0.16261]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52502,0.08006,0.02411],"force_p95":4.99983,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.31064,"mean_force":2.14323,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49885,0.07889,0.1414]},{"body_a":"peg","body_b":"channel_base_body","contact_count":423.0,"contact_point_centroid":[0.50547,0.1046,0.00937],"force_p95":0.57957,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57306,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.497,0.19847,0.29242]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.49937,0.19945,0.29908]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47497,0.06074,0.05094],"force_p95":0.83759,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.85968,"mean_force":0.66354,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49887,0.07904,0.10847]},{"body_a":"peg","body_b":"channel_base_body","contact_count":726.0,"contact_point_centroid":[0.50594,0.10462,0.00939],"force_p95":0.5757,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57724,"mean_force":0.54634,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4958,0.16096,0.1909]}],"total_contact_groups":9},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5016,0.0602,0.02412],"final_tcp_position":[0.49965,0.07922,0.24861],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":137.52282,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50589,0.10472,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.53144,"phase_name":"grasp_0","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":455.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.49666,0.19833,0.29147],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.27427,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":726.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.10466,0.03384],"object_pos_start":[0.50589,0.10472,0.03384],"object_to_goal_dist_end":0.18486,"object_to_goal_dist_start":0.18492,"object_z_max":0.03384,"peak_contact_force":0.54518,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":726.0,"raw_peak_contact_force":0.57724,"subtask_id":"approach_peg","tcp_end":[0.50253,0.10909,0.09185],"tcp_start":[0.49666,0.19833,0.29147],"tcp_to_object_dist_end":0.05828,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":71.0,"n_steps_budget":1000.0,"object_pos_end":[0.50588,0.10322,0.03424],"object_pos_start":[0.50583,0.10466,0.03384],"object_to_goal_dist_end":0.1834,"object_to_goal_dist_start":0.18486,"object_z_max":0.03449,"peak_contact_force":1.41749,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":76.0,"raw_peak_contact_force":32.04111,"subtask_id":"push_through_channel","tcp_end":[0.50109,0.07992,0.07739],"tcp_start":[0.50115,0.08022,0.07746],"tcp_to_object_dist_end":0.04927,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":515.0,"n_steps_budget":1000.0,"object_pos_end":[0.5016,0.0602,0.02412],"object_pos_start":[0.50562,0.10215,0.03477],"object_to_goal_dist_end":0.14111,"object_to_goal_dist_start":0.18232,"object_z_max":0.0408,"peak_contact_force":0.55829,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":528.0,"raw_peak_contact_force":137.52282,"tcp_end":[0.49965,0.07922,0.24861],"tcp_start":[0.50109,0.07992,0.07739],"tcp_to_object_dist_end":0.2253,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93458,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.0794,"push_1.push_distance":0.22064,"push_1.push_force_limit":27.41312,"retract_1.retraction_height":0.19434},"optimized_scores":{"best_composite_score":-0.10284,"best_fitness_score":0.15716,"best_task_score":0.00026},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.47492,0.1198,0.05987],"force_p95":148.51057,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":149.77276,"mean_force":106.12186,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4996,0.07315,0.09029]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.47495,0.11989,0.05993],"force_p95":68.10667,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.18064,"mean_force":47.91615,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49978,0.07325,0.09043]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.52504,0.11991,0.05995],"force_p95":37.24848,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":46.56059,"mean_force":9.31212,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49961,0.07308,0.09019]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.52502,0.11996,0.05998],"force_p95":18.28375,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":18.92596,"mean_force":12.50387,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49976,0.0732,0.09036]},{"body_a":"peg","body_b":"channel_base_body","contact_count":434.0,"contact_point_centroid":[0.50304,0.06752,0.00933],"force_p95":0.56983,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56647,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.49705,0.1985,0.29258]},{"body_a":"peg","body_b":"channel_base_body","contact_count":819.0,"contact_point_centroid":[0.50306,0.06745,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55115,"mean_force":0.54665,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49491,0.14453,0.19135]},{"body_a":"peg","body_b":"channel_base_body","contact_count":520.0,"contact_point_centroid":[0.50308,0.06752,0.00938],"force_p95":0.55055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55065,"mean_force":0.54665,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49795,0.07241,0.17647]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.50743,0.05535,0.00938],"force_p95":0.5477,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54776,"mean_force":0.54685,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49981,0.07331,0.0905]}],"total_contact_groups":8},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50305,0.06742,0.0338],"final_tcp_position":[0.49836,0.07247,0.26476],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":162.13481,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54626,"phase_name":"grasp_0","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":434.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49666,0.19833,0.29147],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.28908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":819.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14762,"object_z_max":0.0338,"peak_contact_force":0.54356,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":819.0,"raw_peak_contact_force":0.55115,"subtask_id":"approach_peg","tcp_end":[0.49992,0.07351,0.09072],"tcp_start":[0.49666,0.19833,0.29147],"tcp_to_object_dist_end":0.05734,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14762,"object_z_max":0.0338,"peak_contact_force":49.44095,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":70.18064,"subtask_id":"push_through_channel","tcp_end":[0.49968,0.07309,0.09023],"tcp_start":[0.49973,0.07315,0.09031],"tcp_to_object_dist_end":0.05682,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":520.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50301,0.06745,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14761,"object_z_max":0.0338,"peak_contact_force":0.54782,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":532.0,"raw_peak_contact_force":149.77276,"tcp_end":[0.49836,0.07247,0.26476],"tcp_start":[0.49968,0.07309,0.09023],"tcp_to_object_dist_end":0.23106,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56818,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06158,"push_1.push_distance":0.16676,"push_1.push_force_limit":24.73586,"retract_1.retraction_height":0.20636},"optimized_scores":{"best_composite_score":-0.01556,"best_fitness_score":0.24444,"best_task_score":0.23977},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":69.0,"contact_point_centroid":[0.5036,0.11069,0.00942],"force_p95":1.13713,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.68986,"mean_force":1.39957,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4995,0.10264,0.08522]},{"body_a":"peg","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.50367,0.12892,0.04884],"force_p95":28.66382,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.34806,"mean_force":12.18653,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49908,0.0888,0.0793]},{"body_a":"peg","body_b":"channel_base_body","contact_count":552.0,"contact_point_centroid":[0.50056,0.07769,0.00882],"force_p95":0.76156,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.8313,"mean_force":0.60109,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4973,0.08636,0.17122]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52503,0.08795,0.02428],"force_p95":5.66239,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.67626,"mean_force":2.41025,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49723,0.0864,0.18716]},{"body_a":"peg","body_b":"channel_base_body","contact_count":428.0,"contact_point_centroid":[0.50352,0.11166,0.00936],"force_p95":0.61517,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56336,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.49702,0.19848,0.29249]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":15.0,"contact_point_centroid":[0.47495,0.0802,0.05674],"force_p95":0.56861,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64521,"mean_force":0.18182,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49701,0.08613,0.10933]},{"body_a":"peg","body_b":"channel_base_body","contact_count":769.0,"contact_point_centroid":[0.5037,0.11172,0.00939],"force_p95":0.60191,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63757,"mean_force":0.54522,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49501,0.16458,0.19328]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"grasp_0","phase_type":"grasp","tcp_position_centroid":[0.49961,0.19955,0.29976]}],"total_contact_groups":8},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5021,0.06742,0.02444],"final_tcp_position":[0.49784,0.08669,0.26538],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":31.68986,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,0.11179,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.5238,"phase_name":"grasp_0","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":444.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.49666,0.19833,0.29147],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.27191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":769.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11176,0.03384],"object_pos_start":[0.5037,0.11179,0.0338],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19192,"object_z_max":0.03391,"peak_contact_force":0.56947,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":769.0,"raw_peak_contact_force":0.63757,"subtask_id":"approach_peg","tcp_end":[0.50047,0.11579,0.09209],"tcp_start":[0.49666,0.19833,0.29147],"tcp_to_object_dist_end":0.05848,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":69.0,"n_steps_budget":1000.0,"object_pos_end":[0.50359,0.11049,0.03423],"object_pos_start":[0.50371,0.11176,0.03384],"object_to_goal_dist_end":0.19061,"object_to_goal_dist_start":0.19189,"object_z_max":0.03446,"peak_contact_force":0.81674,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":74.0,"raw_peak_contact_force":31.68986,"subtask_id":"push_through_channel","tcp_end":[0.49915,0.08735,0.07879],"tcp_start":[0.49914,0.08761,0.07887],"tcp_to_object_dist_end":0.0504,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":561.0,"n_steps_budget":1000.0,"object_pos_end":[0.5021,0.06742,0.02444],"object_pos_start":[0.50327,0.10952,0.03472],"object_to_goal_dist_end":0.14825,"object_to_goal_dist_start":0.18962,"object_z_max":0.04078,"peak_contact_force":0.57303,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":577.0,"raw_peak_contact_force":5.8313,"tcp_end":[0.49784,0.08669,0.26538],"tcp_start":[0.49915,0.08735,0.07879],"tcp_to_object_dist_end":0.24175,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```