## Search State

- **Seed**: 6
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | align → approach → grasp → contact → insert | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | time_limit | force_exceeded | force_exceeded | 13 | 0.1251 | 0.88 | ❌ rejected |
| 11 | align → approach → grasp → contact → insert | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | time_limit | force_exceeded | pose_tolerance | 14 | -0.1322 | 0.87 | ❌ rejected |
| 10 | align → approach → grasp → contact → insert | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | time_limit | force_exceeded | force_exceeded | 14 | 0.1414 | 0.88 | ❌ rejected |
| 9 | align → approach → contact → insert → grasp | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | time_limit | 13 | 0.0592 | 0.88 | ✅ accepted |
| 8 | align → approach → descend → insert → grasp | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | time_limit | 13 | 0.2767 | 0.87 | ❌ rejected |

**Proposal policy**: task_score is 0.88 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.125) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_socket
  anchor: task_goal
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: insert_peg
  anchor: task_goal
  metric: goal_progress
  weight: 0.7
phases:
- id: align_1
  type: align
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
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.02
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  subtask_id: reach_socket
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
    - 0.03
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_socket
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.08
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 10.0
      - 40.0
      default: 20.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_distance:
      type: scalar
      range:
      - 0.06
      - 0.1
      default: 0.08
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.04
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.02
  parameters:
    insert_distance:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_max_force:
      type: scalar
      range:
      - 30.0
      - 80.0
      default: 50.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
    retry_lateral_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: retry.offset.x
        mode: replace
    retry_lateral_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: retry.offset.y
        mode: replace
  guards:
  - id: insertion_force_guard
    when: during_phase
    predicate: force_below
    threshold: 80.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: insert_peg
- id: grasp_1
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
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_1** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.02
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.08, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **insert_1** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.04, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.02
  - parameter_bindings:
    - insert_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_max_force: status=consumed; consumers=termination.force_threshold (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - retry_lateral_x: status=consumed; consumers=retry.offset.x (replace)
    - retry_lateral_y: status=consumed; consumers=retry.offset.y (replace)
  - guards:
    - id=insertion_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=80.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.125
- **task_score** (E): 0.877
- **fitness_score**: 0.532  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.740

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 0.00 | 0.1136 |
| approach_1 | 1.00 | 0.00 | 0.0273 |
| grasp_1 | 1.00 | 0.00 | 0.0095 |
| contact_1 | 1.00 | 1.00 | 0.1045 |
| insert_1 | 0.67 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.503, 0.015, 0.189) | (0.504, -0.000, 0.340)→(0.503, 0.015, 0.229) | 0.260→0.150 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_1 | approach | 1.00 / step_budget | (0.503, 0.015, 0.189)→(0.498, 0.018, 0.163) | (0.503, 0.015, 0.229)→(0.499, 0.018, 0.203) | 0.150→0.126 | 0.00 / 0.000 | 0.000 | 0.000 |
| grasp_1 | grasp | 1.00 / step_budget | (0.498, 0.018, 0.163)→(0.493, 0.018, 0.155) | (0.499, 0.018, 0.203)→(0.495, 0.018, 0.195) | 0.126→0.118 | 0.00 / 0.000 | 0.000 | 0.000 |
| contact_1 | contact | 1.00 / force_exceeded | (0.493, 0.018, 0.155)→(0.493, 0.019, 0.051) | (0.495, 0.018, 0.195)→(0.495, 0.019, 0.091) | 0.118→0.030 | 1.00 / 1.000 | 61.643 | 0.000 |
| insert_1 | insert | 0.67 / force_exceeded | (0.493, 0.019, 0.051)→(0.493, 0.019, 0.051) | (0.495, 0.019, 0.091)→(0.495, 0.019, 0.091) | 0.030→0.030 | 1.00 / 1.000 | 92.371 | 110.641 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.950
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.950
- phase_score: 0.302
- phase_breakdown.reach_socket_score: 1.000
- phase_breakdown.insert_peg_score: 0.003

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.561
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.950
- **Median Q (composite search score)**: 0.189
- **K-run variance**: 0.0130
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.346


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `60385b1f31aca3065ea31945cfeaa028cd4432c7d54684f37d7ce3abfb247b97`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `4bee8669cc79b9d5e3314636941bfd5dcacadb9648a0bfff5f763dbb49e79a76`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.82609,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00971,"align_1.lateral_offset_y":0.0097,"approach_1.approach_height":0.0775,"approach_1.approach_speed":0.02203,"contact_1.contact_force_threshold":37.38918,"contact_1.descend_distance":0.09272,"contact_1.descend_speed":0.01349,"grasp_1.grasp_duration":1.16926,"insert_1.insert_distance":0.08258,"insert_1.insert_max_force":75.67588,"insert_1.insert_speed":0.01978,"insert_1.retry_lateral_x":-0.00609,"insert_1.retry_lateral_y":0.00381},"optimized_scores":{"best_composite_score":0.22149,"best_fitness_score":0.56149,"best_task_score":0.95048},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.51182,-0.01097,0.04995],"force_p95":92.88238,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":94.03616,"mean_force":82.49841,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49684,-0.0109,0.05067]}],"total_contact_groups":1},"final_pose_error":0.05357,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.49677,-0.01091,0.0506],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":94.03616,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":352.0,"n_steps_budget":780.0,"object_pos_end":[0.50891,-0.00252,0.22883],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.14912,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.50844,-0.00253,0.18884],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":86.0,"n_steps_budget":960.0,"object_pos_end":[0.50361,-0.00838,0.20635],"object_pos_start":[0.50891,-0.00252,0.22883],"object_to_goal_dist_end":0.12668,"object_to_goal_dist_start":0.14912,"object_z_max":0.22883,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.50276,-0.00838,0.16636],"tcp_start":[0.50844,-0.00253,0.18884],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49892,-0.00844,0.19839],"object_pos_start":[0.50361,-0.00838,0.20635],"object_to_goal_dist_end":0.11869,"object_to_goal_dist_start":0.12668,"object_z_max":0.20635,"peak_contact_force":0.0,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49731,-0.00844,0.15842],"tcp_start":[0.50276,-0.00838,0.16636],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":683.0,"n_steps_budget":1000.0,"object_pos_end":[0.49894,-0.0109,0.09064],"object_pos_start":[0.49892,-0.00844,0.19839],"object_to_goal_dist_end":0.01527,"object_to_goal_dist_start":0.11869,"object_z_max":0.19839,"peak_contact_force":62.07452,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49688,-0.0109,0.0507],"tcp_start":[0.49731,-0.00844,0.15842],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.49877,-0.01092,0.09054],"object_pos_start":[0.49894,-0.0109,0.09064],"object_to_goal_dist_end":0.01523,"object_to_goal_dist_start":0.01527,"object_z_max":0.09064,"peak_contact_force":94.03616,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":94.03616,"subtask_id":"insert_peg","tcp_end":[0.49677,-0.01091,0.0506],"tcp_start":[0.49688,-0.0109,0.0507],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `b372e597e9ea71ad79503f48aaa87b3bb2c0c3a8e8252ca19ea88229597605ec`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.85185,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00071,"align_1.lateral_offset_y":-0.00991,"approach_1.approach_height":0.06737,"approach_1.approach_speed":0.03556,"contact_1.contact_force_threshold":22.57867,"contact_1.descend_distance":0.08246,"contact_1.descend_speed":0.01732,"grasp_1.grasp_duration":1.86069,"insert_1.insert_distance":0.05801,"insert_1.insert_max_force":80.33138,"insert_1.insert_speed":0.01221,"insert_1.retry_lateral_x":-0.01508,"insert_1.retry_lateral_y":-0.00074},"optimized_scores":{"best_composite_score":0.1886,"best_fitness_score":0.5286,"best_task_score":0.86813},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.51734,0.03067,0.04998],"force_p95":101.04205,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":104.11086,"mean_force":82.44325,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50239,0.02985,0.05074]}],"total_contact_groups":1},"final_pose_error":0.02974,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.5023,0.02984,0.05065],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":104.11086,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":359.0,"n_steps_budget":780.0,"object_pos_end":[0.50712,0.01932,0.22852],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.14994,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.50665,0.0193,0.18852],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":123.0,"n_steps_budget":780.0,"object_pos_end":[0.50703,0.02785,0.1954],"object_pos_start":[0.50712,0.01932,0.22852],"object_to_goal_dist_end":0.11892,"object_to_goal_dist_start":0.14994,"object_z_max":0.22852,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.50614,0.0278,0.15541],"tcp_start":[0.50665,0.0193,0.18852],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50223,0.02763,0.18737],"object_pos_start":[0.50703,0.02785,0.1954],"object_to_goal_dist_end":0.11089,"object_to_goal_dist_start":0.11892,"object_z_max":0.1954,"peak_contact_force":0.0,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50058,0.02754,0.14741],"tcp_start":[0.50614,0.0278,0.15541],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":642.0,"n_steps_budget":1000.0,"object_pos_end":[0.50455,0.02998,0.09073],"object_pos_start":[0.50223,0.02763,0.18737],"object_to_goal_dist_end":0.03216,"object_to_goal_dist_start":0.11089,"object_z_max":0.18737,"peak_contact_force":62.27973,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50244,0.02986,0.05079],"tcp_start":[0.50058,0.02754,0.14741],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50432,0.02995,0.0906],"object_pos_start":[0.50455,0.02998,0.09073],"object_to_goal_dist_end":0.03206,"object_to_goal_dist_start":0.03216,"object_z_max":0.09073,"peak_contact_force":104.11086,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":104.11086,"subtask_id":"insert_peg","tcp_end":[0.5023,0.02984,0.05065],"tcp_start":[0.50244,0.02986,0.05079],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ae45bae888bf338225755528d96cf0281f13a4171bef9e43a6d9a98635b19bee`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.75676,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00892,"align_1.lateral_offset_y":-0.00839,"approach_1.approach_height":0.07873,"approach_1.approach_speed":0.0261,"contact_1.contact_force_threshold":23.71607,"contact_1.descend_distance":0.07046,"contact_1.descend_speed":0.0188,"grasp_1.grasp_duration":1.06403,"insert_1.insert_distance":0.06197,"insert_1.insert_max_force":115.71749,"insert_1.insert_speed":0.01757,"insert_1.retry_lateral_x":-0.00728,"insert_1.retry_lateral_y":0.01113},"optimized_scores":{"best_composite_score":-0.03474,"best_fitness_score":0.50526,"best_task_score":0.81314},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":5.0,"contact_point_centroid":[0.49571,0.03796,0.04992],"force_p95":125.88643,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":133.77584,"mean_force":91.4093,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48076,0.03703,0.05056]}],"total_contact_groups":1},"final_pose_error":0.03296,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.48066,0.03701,0.05047],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":133.77584,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":355.0,"n_steps_budget":780.0,"object_pos_end":[0.49338,0.02697,0.22906],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15163,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.49295,0.02694,0.18906],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":86.0,"n_steps_budget":810.0,"object_pos_end":[0.48724,0.03397,0.2072],"object_pos_start":[0.49338,0.02697,0.22906],"object_to_goal_dist_end":0.13228,"object_to_goal_dist_start":0.15163,"object_z_max":0.22906,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.48645,0.03392,0.16721],"tcp_start":[0.49295,0.02694,0.18906],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48265,0.03374,0.19973],"object_pos_start":[0.48724,0.03397,0.2072],"object_to_goal_dist_end":0.12559,"object_to_goal_dist_start":0.13228,"object_z_max":0.2072,"peak_contact_force":0.0,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.48112,0.03364,0.15976],"tcp_start":[0.48645,0.03392,0.16721],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":721.0,"n_steps_budget":1000.0,"object_pos_end":[0.48284,0.03718,0.0906],"object_pos_start":[0.48265,0.03374,0.19973],"object_to_goal_dist_end":0.0423,"object_to_goal_dist_start":0.12559,"object_z_max":0.19973,"peak_contact_force":60.5734,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.48086,0.03705,0.05065],"tcp_start":[0.48112,0.03364,0.15976],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.48259,0.03715,0.09047],"object_pos_start":[0.48284,0.03718,0.0906],"object_to_goal_dist_end":0.04234,"object_to_goal_dist_start":0.0423,"object_z_max":0.0906,"peak_contact_force":78.96469,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":5.0,"raw_peak_contact_force":133.77584,"subtask_id":"insert_peg","tcp_end":[0.48066,0.03701,0.05047],"tcp_start":[0.48068,0.03702,0.05049],"tcp_to_object_dist_end":0.04005,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```