## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | align → grasp → approach → contact → insert | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | admittance_control | pose_tolerance | time_limit | pose_tolerance | force_exceeded | pose_tolerance | 18 | -0.2438 | 0.91 | ✅ accepted |
| 13 | align → grasp → approach → contact → insert | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | time_limit | pose_tolerance | force_exceeded | pose_tolerance | 18 | -0.2442 | 0.91 | ✅ accepted |
| 12 | align → approach → grasp → contact → insert | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | time_limit | force_exceeded | force_exceeded | 13 | 0.1251 | 0.88 | ❌ rejected |
| 11 | align → approach → grasp → contact → insert | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | time_limit | force_exceeded | pose_tolerance | 14 | -0.1322 | 0.87 | ❌ rejected |
| 10 | align → approach → grasp → contact → insert | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | time_limit | force_exceeded | force_exceeded | 14 | 0.1414 | 0.88 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.91). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=-0.244) — your mutation base

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
- id: contact_descend_1
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
      distance: 0.12
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
      - 0.08
      - 0.15
      default: 0.12
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
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.02
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
      - 0.01
      - 0.06
      default: 0.02
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.008
      binds_to:
      - path: generator.speed
        mode: replace
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
    retry_lateral_x:
      type: scalar
      range:
      - -0.04
      - 0.04
      default: 0.0
      binds_to:
      - path: retry.offset.x
        mode: replace
    retry_lateral_y:
      type: scalar
      range:
      - -0.04
      - 0.04
      default: 0.0
      binds_to:
      - path: retry.offset.y
        mode: replace
  guards:
  - id: insertion_force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: insert_peg

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_1** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.02
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
- **contact_descend_1** (`contact`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.12, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
- **insert_1** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.02, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.02
  - parameter_bindings:
    - insert_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
    - retry_lateral_x: status=consumed; consumers=retry.offset.x (replace)
    - retry_lateral_y: status=consumed; consumers=retry.offset.y (replace)
  - guards:
    - id=insertion_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: -0.244
- **task_score** (E): 0.913
- **fitness_score**: 0.546  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.990

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 0.00 | 0.1133 |
| grasp_1 | 1.00 | 0.00 | 0.0094 |
| approach_1 | 1.00 | 0.00 | 0.0445 |
| contact_descend_1 | 1.00 | 1.00 | 0.0865 |
| insert_1 | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.012, 0.189) | (0.504, -0.000, 0.340)→(0.498, 0.012, 0.229) | 0.260→0.151 | 0.00 / 0.000 | 0.000 | 0.000 |
| grasp_1 | grasp | 1.00 / step_budget | (0.497, 0.012, 0.189)→(0.492, 0.012, 0.181) | (0.498, 0.012, 0.229)→(0.493, 0.012, 0.221) | 0.151→0.143 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_1 | approach | 1.00 / step_budget | (0.492, 0.012, 0.181)→(0.498, 0.015, 0.137) | (0.493, 0.012, 0.221)→(0.500, 0.015, 0.177) | 0.143→0.099 | 0.00 / 0.000 | 0.000 | 0.000 |
| contact_descend_1 | contact | 1.00 / force_exceeded | (0.498, 0.015, 0.137)→(0.497, 0.016, 0.051) | (0.500, 0.015, 0.177)→(0.499, 0.016, 0.091) | 0.099→0.023 | 1.00 / 1.000 | 64.861 | 0.000 |
| insert_1 | insert | 0.00 / guard_failure | (0.497, 0.016, 0.051)→(0.497, 0.016, 0.051) | (0.499, 0.016, 0.091)→(0.499, 0.016, 0.091) | 0.023→0.023 | 1.00 / 1.000 | 68.991 | 76.626 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.982
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.982
- phase_score: 0.304
- phase_breakdown.reach_socket_score: 1.000
- phase_breakdown.insert_peg_score: 0.006

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.575
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.982
- **Median Q (composite search score)**: -0.248
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: insert_1.retry_lateral_x
- **Final σ (mean)**: 0.350


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.50829,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00144,"align_1.lateral_offset_y":0.00271,"approach_1.approach_height":0.03589,"approach_1.approach_speed":0.01398,"approach_1.lateral_offset_x":0.00503,"approach_1.lateral_offset_y":0.00971,"contact_descend_1.contact_force_threshold":22.78511,"contact_descend_1.descend_distance":0.13057,"contact_descend_1.descend_speed":0.01432,"contact_descend_1.lateral_offset_x":0.00447,"contact_descend_1.lateral_offset_y":0.00894,"grasp_1.grasp_duration":1.1114,"insert_1.insert_distance":0.03631,"insert_1.insert_speed":0.01543,"insert_1.lateral_offset_x":-0.00458,"insert_1.lateral_offset_y":0.00221,"insert_1.retry_lateral_x":-0.00237,"insert_1.retry_lateral_y":-0.00837},"optimized_scores":{"best_composite_score":-0.21476,"best_fitness_score":0.57524,"best_task_score":0.98225},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.51515,-0.00371,0.04995],"force_p95":79.63126,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":80.32569,"mean_force":75.65247,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50018,-0.00385,0.05068]}],"total_contact_groups":1},"final_pose_error":0.0096,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.50009,-0.00386,0.05059],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":80.32569,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":344.0,"n_steps_budget":780.0,"object_pos_end":[0.49905,-0.00865,0.22937],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.14962,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.49859,-0.00864,0.18937],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49464,-0.00864,0.22146],"object_pos_start":[0.49905,-0.00865,0.22937],"object_to_goal_dist_end":0.14183,"object_to_goal_dist_start":0.14962,"object_z_max":0.22937,"peak_contact_force":0.0,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49341,-0.00863,0.18148],"tcp_start":[0.49859,-0.00864,0.18937],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":239.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,-0.00394,0.16351],"object_pos_start":[0.49464,-0.00864,0.22146],"object_to_goal_dist_end":0.08369,"object_to_goal_dist_start":0.14183,"object_z_max":0.22146,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.50204,-0.00394,0.12355],"tcp_start":[0.49341,-0.00863,0.18148],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":458.0,"n_steps_budget":1000.0,"object_pos_end":[0.5024,-0.00384,0.09069],"object_pos_start":[0.50372,-0.00394,0.16351],"object_to_goal_dist_end":0.01161,"object_to_goal_dist_start":0.08369,"object_z_max":0.16351,"peak_contact_force":64.14258,"phase_name":"contact_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50026,-0.00384,0.05075],"tcp_start":[0.50204,-0.00394,0.12355],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":600.0,"object_pos_end":[0.5023,-0.00385,0.09064],"object_pos_start":[0.5024,-0.00384,0.09069],"object_to_goal_dist_end":0.01154,"object_to_goal_dist_start":0.01161,"object_z_max":0.09069,"peak_contact_force":75.17602,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":80.32569,"subtask_id":"insert_peg","tcp_end":[0.50009,-0.00386,0.05059],"tcp_start":[0.50011,-0.00385,0.05062],"tcp_to_object_dist_end":0.04011,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `b372e597e9ea71ad79503f48aaa87b3bb2c0c3a8e8252ca19ea88229597605ec`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.07563,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00313,"align_1.lateral_offset_y":-0.00975,"approach_1.approach_height":0.05985,"approach_1.approach_speed":0.0461,"approach_1.lateral_offset_x":-0.00105,"approach_1.lateral_offset_y":-0.0096,"contact_descend_1.contact_force_threshold":24.48321,"contact_descend_1.descend_distance":0.10859,"contact_descend_1.descend_speed":0.01807,"contact_descend_1.lateral_offset_x":-0.00045,"contact_descend_1.lateral_offset_y":-0.00982,"grasp_1.grasp_duration":1.32819,"insert_1.insert_distance":0.03646,"insert_1.insert_speed":0.01286,"insert_1.lateral_offset_x":-0.00434,"insert_1.lateral_offset_y":0.00073,"insert_1.retry_lateral_x":-0.04,"insert_1.retry_lateral_y":0.01017},"optimized_scores":{"best_composite_score":-0.24778,"best_fitness_score":0.54222,"best_task_score":0.90334},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.51732,0.02199,0.04996],"force_p95":73.31089,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":73.79025,"mean_force":69.17127,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50236,0.02135,0.05069]}],"total_contact_groups":1},"final_pose_error":0.01364,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.50228,0.02133,0.0506],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":73.79025,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":355.0,"n_steps_budget":780.0,"object_pos_end":[0.50371,0.01942,0.22881],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15011,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.50324,0.0194,0.18881],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49928,0.01928,0.22077],"object_pos_start":[0.50371,0.01942,0.22881],"object_to_goal_dist_end":0.14209,"object_to_goal_dist_start":0.15011,"object_z_max":0.22881,"peak_contact_force":0.0,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49804,0.01922,0.18079],"tcp_start":[0.50324,0.0194,0.18881],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":128.0,"n_steps_budget":600.0,"object_pos_end":[0.50452,0.02124,0.18742],"object_pos_start":[0.49928,0.01928,0.22077],"object_to_goal_dist_end":0.10959,"object_to_goal_dist_start":0.14209,"object_z_max":0.22077,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.50287,0.02117,0.14745],"tcp_start":[0.49804,0.01922,0.18079],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":605.0,"n_steps_budget":1000.0,"object_pos_end":[0.50455,0.02145,0.09071],"object_pos_start":[0.50452,0.02124,0.18742],"object_to_goal_dist_end":0.02441,"object_to_goal_dist_start":0.10959,"object_z_max":0.18742,"peak_contact_force":66.9638,"phase_name":"contact_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50243,0.02136,0.05076],"tcp_start":[0.50287,0.02117,0.14745],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":690.0,"object_pos_end":[0.50445,0.02144,0.09066],"object_pos_start":[0.50455,0.02145,0.09071],"object_to_goal_dist_end":0.02435,"object_to_goal_dist_start":0.02441,"object_z_max":0.09071,"peak_contact_force":65.64585,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":73.79025,"subtask_id":"insert_peg","tcp_end":[0.50228,0.02133,0.0506],"tcp_start":[0.5023,0.02134,0.05063],"tcp_to_object_dist_end":0.04011,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ae45bae888bf338225755528d96cf0281f13a4171bef9e43a6d9a98635b19bee`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.99231,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00591,"align_1.lateral_offset_y":-0.00882,"approach_1.approach_height":0.05262,"approach_1.approach_speed":0.02916,"approach_1.lateral_offset_x":0.0089,"approach_1.lateral_offset_y":-0.0095,"contact_descend_1.contact_force_threshold":17.75713,"contact_descend_1.descend_distance":0.11572,"contact_descend_1.descend_speed":0.02982,"contact_descend_1.lateral_offset_x":0.00869,"contact_descend_1.lateral_offset_y":-0.00508,"grasp_1.grasp_duration":1.16655,"insert_1.insert_distance":0.0463,"insert_1.insert_speed":0.01153,"insert_1.lateral_offset_x":0.00252,"insert_1.lateral_offset_y":-0.00095,"insert_1.retry_lateral_x":0.03782,"insert_1.retry_lateral_y":-0.03776},"optimized_scores":{"best_composite_score":-0.26883,"best_fitness_score":0.52117,"best_task_score":0.85286},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.50317,0.03167,0.04993],"force_p95":74.70833,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.76206,"mean_force":69.5083,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48821,0.03083,0.05061]}],"total_contact_groups":1},"final_pose_error":0.01831,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.48813,0.03081,0.05052],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":75.76206,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":354.0,"n_steps_budget":780.0,"object_pos_end":[0.49073,0.02659,0.22914],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15178,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.4903,0.02656,0.18914],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48634,0.02641,0.22145],"object_pos_start":[0.49073,0.02659,0.22914],"object_to_goal_dist_end":0.14455,"object_to_goal_dist_start":0.15178,"object_z_max":0.22914,"peak_contact_force":0.0,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.48516,0.02634,0.18147],"tcp_start":[0.4903,0.02656,0.18914],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":160.0,"n_steps_budget":1000.0,"object_pos_end":[0.49114,0.02858,0.18068],"object_pos_start":[0.48634,0.02641,0.22145],"object_to_goal_dist_end":0.10503,"object_to_goal_dist_start":0.14455,"object_z_max":0.22145,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.48954,0.0285,0.14071],"tcp_start":[0.48516,0.02634,0.18147],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":1000.0,"object_pos_end":[0.49034,0.03096,0.09064],"object_pos_start":[0.49114,0.02858,0.18068],"object_to_goal_dist_end":0.03413,"object_to_goal_dist_start":0.10503,"object_z_max":0.18068,"peak_contact_force":63.47637,"phase_name":"contact_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.48829,0.03084,0.05069],"tcp_start":[0.48954,0.0285,0.14071],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":990.0,"object_pos_end":[0.49025,0.03095,0.09058],"object_pos_start":[0.49034,0.03096,0.09064],"object_to_goal_dist_end":0.03413,"object_to_goal_dist_start":0.03413,"object_z_max":0.09064,"peak_contact_force":66.15249,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":75.76206,"subtask_id":"insert_peg","tcp_end":[0.48813,0.03081,0.05052],"tcp_start":[0.48815,0.03082,0.05055],"tcp_to_object_dist_end":0.04012,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```