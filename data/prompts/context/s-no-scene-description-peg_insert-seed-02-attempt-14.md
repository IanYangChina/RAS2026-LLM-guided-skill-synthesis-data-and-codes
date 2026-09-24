## Search State

- **Seed**: 2
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.0435 | 0.94 | ❌ rejected |
| 13 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.0453 | 0.95 | ❌ rejected |
| 12 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.0454 | 0.95 | ❌ rejected |
| 11 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 9 | -0.0922 | 0.95 | ❌ rejected |
| 10 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.0057 | 0.94 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.94). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

- Task name: peg_insert
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

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

## Current Skill (Q=-0.043) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: insertion
  metric: goal_progress
  weight: 0.7
phases:
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
    - 0.0
    - 0.1
    orientation:
      mode: none
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: pre_contact
- id: align_1
  type: align
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    align_tolerance:
      type: scalar
      range:
      - 0.003
      - 0.015
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
- id: insert_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: negative
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insertion_force_guard_threshold:
      type: scalar
      range:
      - 25.0
      - 45.0
      default: 35.0
      binds_to:
      - path: guards.insertion_force_guard.threshold
        mode: replace
    insertion_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: insertion_force_guard
    when: during_phase
    predicate: force_below
    threshold: 35.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: insertion

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **align_1** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
    - align_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **insert_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=negative}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insertion_force_guard_threshold: status=consumed; consumers=guards.insertion_force_guard.threshold (replace)
    - insertion_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=insertion_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=35.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]

## Design Metrics

- **Composite score**: -0.043
- **task_score** (E): 0.943
- **fitness_score**: 0.387  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.00 | 0.0575 |
| align_1 | 1.00 | 0.67 | 0.1290 |
| insert_1 | 0.00 | 1.00 | 0.0003 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, -0.008, 0.248) | (0.504, -0.000, 0.340)→(0.502, -0.008, 0.287) | 0.260→0.208 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_1 | align | 1.00 / step_budget | (0.495, -0.008, 0.248)→(0.483, -0.023, 0.121) | (0.502, -0.008, 0.287)→(0.521, -0.020, 0.111) | 0.208→0.048 | 0.67 / 0.667 | 231.658 | 4855.559 |
| insert_1 | push | 0.00 / guard_failure | (0.483, -0.022, 0.120)→(0.483, -0.021, 0.120) | (0.521, -0.020, 0.111)→(0.521, -0.019, 0.110) | 0.048→0.048 | 1.00 / 1.333 | 203.545 | 498.306 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.987
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.987
- phase_score: 0.029
- phase_breakdown.insertion_score: 0.029
- phase_breakdown.pre_contact_score: 0.029

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.412
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.987
- **Median Q (composite search score)**: -0.050
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.305


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6921a9025d4eafab3a26182307d104597a59aa3c28d9e7087cf253b6e9b1c7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `d09be956b809b9acd01354eeb5f0494d5058516cbca42b9f2b0bee8c1b6b25a7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.55556,"average_solve_count":54.0,"average_success_count":54.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.12472,"align_1.align_tolerance":0.00954,"approach_1.approach_height":0.15381,"approach_1.approach_speed":0.27412,"approach_1.approach_tolerance":0.02424,"insert_1.insertion_depth":0.12339,"insert_1.insertion_force_guard_threshold":34.9135,"insert_1.insertion_speed":0.03766},"optimized_scores":{"best_composite_score":-0.04985,"best_fitness_score":0.38015,"best_task_score":0.93026},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.51127,-0.01258,0.07948],"force_p95":1114.82796,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1142.06312,"mean_force":905.51537,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48524,-0.01283,0.08002]},{"body_a":"peg_socket","body_b":"link7","contact_count":643.0,"contact_point_centroid":[0.54057,-0.0113,0.06858],"force_p95":351.93388,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1026.00861,"mean_force":305.28449,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46795,-0.01713,0.11285]},{"body_a":"peg_socket","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.5408,-0.01258,0.06475],"force_p95":443.55554,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":521.83004,"mean_force":130.45751,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.47492,-0.02572,0.11834]},{"body_a":"attachment","body_b":"peg_socket","contact_count":16.0,"contact_point_centroid":[0.44951,7e-05,0.07968],"force_p95":249.42106,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":278.21781,"mean_force":119.19098,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44718,-0.01326,0.08519]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.5409,-0.02078,0.07992],"force_p95":139.01134,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":139.17977,"mean_force":137.49544,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.47492,-0.02564,0.11836]}],"total_contact_groups":5},"final_pose_error":0.16239,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.47514,-0.02537,0.11862],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":1142.06312,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":83.0,"n_steps_budget":600.0,"object_pos_end":[0.49457,-0.00982,0.29542],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.21572,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.48699,-0.00977,0.25615],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":726.0,"n_steps_budget":810.0,"object_pos_end":[0.5127,-0.02316,0.10574],"object_pos_start":[0.49457,-0.00982,0.29542],"object_to_goal_dist_end":0.03689,"object_to_goal_dist_start":0.21572,"object_z_max":0.29542,"peak_contact_force":345.8402,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":665.0,"raw_peak_contact_force":1142.06312,"tcp_end":[0.47484,-0.02585,0.11836],"tcp_start":[0.48699,-0.00977,0.25615],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.51266,-0.02307,0.10539],"object_pos_start":[0.5127,-0.02316,0.10574],"object_to_goal_dist_end":0.03657,"object_to_goal_dist_start":0.03689,"object_z_max":0.10574,"peak_contact_force":135.8111,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":521.83004,"subtask_id":"insertion","tcp_end":[0.47514,-0.02537,0.11862],"tcp_start":[0.47494,-0.02557,0.11842],"tcp_to_object_dist_end":0.03986,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7c892e828ea48eee928c80191ad243a972830b09953cba6358be1d4656816d00`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.74194,"average_solve_count":62.0,"average_success_count":62.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.05629,"align_1.align_tolerance":0.00958,"approach_1.approach_height":0.11783,"approach_1.approach_speed":0.20433,"approach_1.approach_tolerance":0.02779,"insert_1.insertion_depth":0.10607,"insert_1.insertion_force_guard_threshold":39.43111,"insert_1.insertion_speed":0.04455},"optimized_scores":{"best_composite_score":-0.06285,"best_fitness_score":0.36715,"best_task_score":0.91228},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":889.0,"contact_point_centroid":[0.52664,-0.02096,0.06476],"force_p95":340.24584,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":12068.10147,"mean_force":457.31221,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46021,-0.02499,0.11842]},{"body_a":"attachment","body_b":"peg_socket","contact_count":355.0,"contact_point_centroid":[0.52441,-0.02514,0.07959],"force_p95":1362.21901,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":10016.53595,"mean_force":462.67201,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46396,-0.02894,0.11564]},{"body_a":"peg_socket","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.52634,-0.0231,0.04884],"force_p95":3913.4021,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4174.08627,"mean_force":1505.53079,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44165,-0.02072,0.10273]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5268,-0.02037,0.06469],"force_p95":365.29683,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":365.43675,"mean_force":356.98277,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.46246,-0.03631,0.1193]},{"body_a":"world","body_b":"link6","contact_count":303.0,"contact_point_centroid":[0.67912,-0.01888,-2e-05],"force_p95":81.38265,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":269.80012,"mean_force":30.83132,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46195,-0.025,0.1203]}],"total_contact_groups":5},"final_pose_error":0.14625,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46246,-0.03653,0.11929],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":12068.10147,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":123.0,"n_steps_budget":600.0,"object_pos_end":[0.48508,-0.01503,0.26217],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.1834,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.47493,-0.01491,0.22348],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4999,-0.03241,0.10573],"object_pos_start":[0.48508,-0.01503,0.26217],"object_to_goal_dist_end":0.04138,"object_to_goal_dist_start":0.1834,"object_z_max":0.26217,"peak_contact_force":349.13472,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1561.0,"raw_peak_contact_force":12068.10147,"tcp_end":[0.46246,-0.03619,0.1193],"tcp_start":[0.47493,-0.01491,0.22348],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.4999,-0.03251,0.10573],"object_pos_start":[0.4999,-0.03241,0.10573],"object_to_goal_dist_end":0.04146,"object_to_goal_dist_start":0.04138,"object_z_max":0.10573,"peak_contact_force":365.43675,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":365.43675,"subtask_id":"insertion","tcp_end":[0.46246,-0.03653,0.11929],"tcp_start":[0.46246,-0.03642,0.1193],"tcp_to_object_dist_end":0.04002,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `65c1f23a0338c26bf257d85b07ab64c0180da795e8d67e7d51a2ed2fb2a4d0db`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.97059,"average_solve_count":68.0,"average_success_count":68.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.05296,"align_1.align_tolerance":0.01137,"approach_1.approach_height":0.17394,"approach_1.approach_speed":0.35263,"approach_1.approach_tolerance":0.01681,"insert_1.insertion_depth":0.10515,"insert_1.insertion_force_guard_threshold":33.61934,"insert_1.insertion_speed":0.04013},"optimized_scores":{"best_composite_score":-0.01768,"best_fitness_score":0.41232,"best_task_score":0.98705},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":8.0,"contact_point_centroid":[0.56729,0.00068,0.07828],"force_p95":1251.81926,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1356.51257,"mean_force":862.42164,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.54923,0.00062,0.07945]},{"body_a":"peg_socket","body_b":"link7","contact_count":903.0,"contact_point_centroid":[0.59526,-0.00351,0.07981],"force_p95":286.93765,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1252.33029,"mean_force":243.82554,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50483,-0.001,0.11171]},{"body_a":"attachment","body_b":"peg_socket","contact_count":24.0,"contact_point_centroid":[0.50255,0.01113,0.07901],"force_p95":910.87815,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":978.72761,"mean_force":347.95961,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49759,6e-05,0.08538]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.59497,-0.00099,0.07968],"force_p95":557.85934,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":607.65196,"mean_force":275.58829,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.51088,-0.00309,0.12193]}],"total_contact_groups":4},"final_pose_error":0.14891,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.51051,-0.00233,0.12162],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1356.51257,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":113.0,"n_steps_budget":600.0,"object_pos_end":[0.52682,0.0006,0.30386],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.22546,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.52242,0.00059,0.2641],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55098,-0.0037,0.12242],"object_pos_start":[0.52682,0.0006,0.30386],"object_to_goal_dist_end":0.06642,"object_to_goal_dist_start":0.22546,"object_z_max":0.30386,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":935.0,"raw_peak_contact_force":1356.51257,"tcp_end":[0.51105,-0.00546,0.12401],"tcp_start":[0.52242,0.00059,0.2641],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":10.0,"n_steps_budget":1000.0,"object_pos_end":[0.55074,-0.00145,0.11976],"object_pos_start":[0.55098,-0.0037,0.12242],"object_to_goal_dist_end":0.06448,"object_to_goal_dist_start":0.06642,"object_z_max":0.12242,"peak_contact_force":109.3872,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":607.65196,"subtask_id":"insertion","tcp_end":[0.51051,-0.00233,0.12162],"tcp_start":[0.51059,-0.00262,0.12175],"tcp_to_object_dist_end":0.04028,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```