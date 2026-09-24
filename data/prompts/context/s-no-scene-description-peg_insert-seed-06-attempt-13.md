## Search State

- **Seed**: 6
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | align → grasp → approach → contact → insert | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | time_limit | pose_tolerance | force_exceeded | pose_tolerance | 18 | -0.2442 | 0.91 | ✅ accepted |
| 12 | align → approach → grasp → contact → insert | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | time_limit | force_exceeded | force_exceeded | 13 | 0.1251 | 0.88 | ❌ rejected |
| 11 | align → approach → grasp → contact → insert | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | time_limit | force_exceeded | pose_tolerance | 14 | -0.1322 | 0.87 | ❌ rejected |
| 10 | align → approach → grasp → contact → insert | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | time_limit | force_exceeded | force_exceeded | 14 | 0.1414 | 0.88 | ❌ rejected |
| 9 | align → approach → contact → insert → grasp | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | time_limit | 13 | 0.0592 | 0.88 | ✅ accepted |

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
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.02
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
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.04, mode=add_to_offset, sign=positive}
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
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: -0.244
- **task_score** (E): 0.912
- **fitness_score**: 0.546  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.990

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 0.00 | 0.1136 |
| grasp_1 | 1.00 | 0.00 | 0.0095 |
| approach_1 | 1.00 | 0.00 | 0.0463 |
| contact_descend_1 | 1.00 | 1.00 | 0.0844 |
| insert_1 | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.501, 0.014, 0.189) | (0.504, -0.000, 0.340)→(0.501, 0.014, 0.229) | 0.260→0.150 | 0.00 / 0.000 | 0.000 | 0.000 |
| grasp_1 | grasp | 1.00 / step_budget | (0.501, 0.014, 0.189)→(0.496, 0.014, 0.181) | (0.501, 0.014, 0.229)→(0.497, 0.014, 0.221) | 0.150→0.143 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_1 | approach | 1.00 / step_budget | (0.496, 0.014, 0.181)→(0.497, 0.016, 0.135) | (0.497, 0.014, 0.221)→(0.499, 0.016, 0.175) | 0.143→0.097 | 0.00 / 0.000 | 0.000 | 0.000 |
| contact_descend_1 | contact | 1.00 / force_exceeded | (0.497, 0.016, 0.135)→(0.496, 0.017, 0.051) | (0.499, 0.016, 0.175)→(0.498, 0.017, 0.091) | 0.097→0.024 | 1.00 / 1.000 | 64.786 | 0.000 |
| insert_1 | insert | 0.00 / guard_failure | (0.495, 0.017, 0.051)→(0.495, 0.017, 0.051) | (0.498, 0.017, 0.091)→(0.498, 0.017, 0.091) | 0.024→0.024 | 1.00 / 1.000 | 61.588 | 72.817 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.985
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.985
- phase_score: 0.304
- phase_breakdown.reach_socket_score: 1.000
- phase_breakdown.insert_peg_score: 0.006

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.576
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.985
- **Median Q (composite search score)**: -0.249
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.324


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21053,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00196,"align_1.lateral_offset_y":0.00538,"approach_1.approach_height":0.04058,"approach_1.approach_speed":0.03777,"approach_1.lateral_offset_x":0.00483,"approach_1.lateral_offset_y":0.00999,"contact_descend_1.contact_force_threshold":22.99882,"contact_descend_1.descend_distance":0.14742,"contact_descend_1.descend_speed":0.01562,"contact_descend_1.lateral_offset_x":0.00178,"contact_descend_1.lateral_offset_y":0.00976,"grasp_1.grasp_duration":1.85427,"insert_1.insert_distance":0.04355,"insert_1.insert_speed":0.01255,"insert_1.lateral_offset_x":0.00162,"insert_1.lateral_offset_y":0.00767,"insert_1.retry_lateral_x":-0.00836,"insert_1.retry_lateral_y":0.00652},"optimized_scores":{"best_composite_score":-0.21365,"best_fitness_score":0.57635,"best_task_score":0.9847},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.51422,-0.00298,0.04991],"force_p95":70.72037,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.61701,"mean_force":63.76606,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49924,-0.00319,0.05062]}],"total_contact_groups":1},"final_pose_error":0.0152,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.49918,-0.0032,0.05053],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":71.61701,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":345.0,"n_steps_budget":780.0,"object_pos_end":[0.50205,-0.0063,0.2293],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.14945,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.50159,-0.0063,0.1893],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49763,-0.00631,0.2213],"object_pos_start":[0.50205,-0.0063,0.2293],"object_to_goal_dist_end":0.14146,"object_to_goal_dist_start":0.14945,"object_z_max":0.2293,"peak_contact_force":0.0,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49639,-0.00631,0.18132],"tcp_start":[0.50159,-0.0063,0.1893],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":198.0,"n_steps_budget":1000.0,"object_pos_end":[0.50393,-0.00336,0.16872],"object_pos_start":[0.49763,-0.00631,0.2213],"object_to_goal_dist_end":0.08887,"object_to_goal_dist_start":0.14146,"object_z_max":0.2213,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.50225,-0.00336,0.12876],"tcp_start":[0.49639,-0.00631,0.18132],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":467.0,"n_steps_budget":1000.0,"object_pos_end":[0.50144,-0.00318,0.09061],"object_pos_start":[0.50393,-0.00336,0.16872],"object_to_goal_dist_end":0.01117,"object_to_goal_dist_start":0.08887,"object_z_max":0.16872,"peak_contact_force":66.52121,"phase_name":"contact_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.4993,-0.00318,0.05067],"tcp_start":[0.50225,-0.00336,0.12876],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":780.0,"object_pos_end":[0.50135,-0.00318,0.09056],"object_pos_start":[0.50144,-0.00318,0.09061],"object_to_goal_dist_end":0.01111,"object_to_goal_dist_start":0.01117,"object_z_max":0.09061,"peak_contact_force":57.03054,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":71.61701,"subtask_id":"insert_peg","tcp_end":[0.49918,-0.0032,0.05053],"tcp_start":[0.4992,-0.00319,0.05056],"tcp_to_object_dist_end":0.04009,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `b372e597e9ea71ad79503f48aaa87b3bb2c0c3a8e8252ca19ea88229597605ec`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.76027,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00292,"align_1.lateral_offset_y":-0.0053,"approach_1.approach_height":0.04536,"approach_1.approach_speed":0.02095,"approach_1.lateral_offset_x":-0.00927,"approach_1.lateral_offset_y":-0.0097,"contact_descend_1.contact_force_threshold":32.37926,"contact_descend_1.descend_distance":0.11247,"contact_descend_1.descend_speed":0.02118,"contact_descend_1.lateral_offset_x":0.00204,"contact_descend_1.lateral_offset_y":-0.00988,"grasp_1.grasp_duration":1.04287,"insert_1.insert_distance":0.04189,"insert_1.insert_speed":0.01339,"insert_1.lateral_offset_x":-0.00155,"insert_1.lateral_offset_y":0.00503,"insert_1.retry_lateral_x":-0.01561,"insert_1.retry_lateral_y":0.00174},"optimized_scores":{"best_composite_score":-0.24906,"best_fitness_score":0.54094,"best_task_score":0.90045},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.51586,0.02251,0.04995],"force_p95":69.20728,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.92266,"mean_force":64.18106,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50089,0.02182,0.05068]}],"total_contact_groups":1},"final_pose_error":0.02095,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.50083,0.02181,0.0506],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":69.92266,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":364.0,"n_steps_budget":780.0,"object_pos_end":[0.50909,0.02341,0.22843],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15054,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.50862,0.02338,0.18843],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50467,0.02323,0.22025],"object_pos_start":[0.50909,0.02341,0.22843],"object_to_goal_dist_end":0.14224,"object_to_goal_dist_start":0.15054,"object_z_max":0.22843,"peak_contact_force":0.0,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50343,0.02317,0.18027],"tcp_start":[0.50862,0.02338,0.18843],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":166.0,"n_steps_budget":1000.0,"object_pos_end":[0.50001,0.02228,0.17491],"object_pos_start":[0.50467,0.02323,0.22025],"object_to_goal_dist_end":0.09749,"object_to_goal_dist_start":0.14224,"object_z_max":0.22025,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.49834,0.0222,0.13495],"tcp_start":[0.50343,0.02317,0.18027],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":564.0,"n_steps_budget":1000.0,"object_pos_end":[0.50307,0.02193,0.09068],"object_pos_start":[0.50001,0.02228,0.17491],"object_to_goal_dist_end":0.02459,"object_to_goal_dist_start":0.09749,"object_z_max":0.17491,"peak_contact_force":64.64896,"phase_name":"contact_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50095,0.02183,0.05073],"tcp_start":[0.49834,0.0222,0.13495],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":990.0,"object_pos_end":[0.50299,0.02192,0.09062],"object_pos_start":[0.50307,0.02193,0.09068],"object_to_goal_dist_end":0.02454,"object_to_goal_dist_start":0.02459,"object_z_max":0.09068,"peak_contact_force":59.85163,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":69.92266,"subtask_id":"insert_peg","tcp_end":[0.50083,0.02181,0.0506],"tcp_start":[0.50085,0.02181,0.05064],"tcp_to_object_dist_end":0.04008,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ae45bae888bf338225755528d96cf0281f13a4171bef9e43a6d9a98635b19bee`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00842,"align_1.lateral_offset_y":-0.00995,"approach_1.approach_height":0.05307,"approach_1.approach_speed":0.03163,"approach_1.lateral_offset_x":0.00962,"approach_1.lateral_offset_y":-0.00975,"contact_descend_1.contact_force_threshold":22.73846,"contact_descend_1.descend_distance":0.13582,"contact_descend_1.descend_speed":0.0205,"contact_descend_1.lateral_offset_x":0.00333,"contact_descend_1.lateral_offset_y":-0.00277,"grasp_1.grasp_duration":1.12117,"insert_1.insert_distance":0.06315,"insert_1.insert_speed":0.00544,"insert_1.lateral_offset_x":0.00624,"insert_1.lateral_offset_y":0.00361,"insert_1.retry_lateral_x":-0.00778,"insert_1.retry_lateral_y":0.00862},"optimized_scores":{"best_composite_score":-0.26978,"best_fitness_score":0.52022,"best_task_score":0.85054},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.5012,0.03216,0.0499],"force_p95":76.17891,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.91034,"mean_force":71.46222,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48624,0.03133,0.05056]}],"total_contact_groups":1},"final_pose_error":0.036,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.48615,0.03131,0.05047],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":76.91034,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":354.0,"n_steps_budget":780.0,"object_pos_end":[0.49293,0.02562,0.22901],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15136,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.4925,0.02559,0.18901],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48853,0.02544,0.22126],"object_pos_start":[0.49293,0.02562,0.22901],"object_to_goal_dist_end":0.14399,"object_to_goal_dist_start":0.15136,"object_z_max":0.22901,"peak_contact_force":0.0,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.48735,0.02538,0.18128],"tcp_start":[0.4925,0.02559,0.18901],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":152.0,"n_steps_budget":990.0,"object_pos_end":[0.49221,0.02813,0.18126],"object_pos_start":[0.48853,0.02544,0.22126],"object_to_goal_dist_end":0.10539,"object_to_goal_dist_start":0.14399,"object_z_max":0.22126,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.4906,0.02804,0.1413],"tcp_start":[0.48735,0.02538,0.18128],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":544.0,"n_steps_budget":1000.0,"object_pos_end":[0.48836,0.03145,0.09057],"object_pos_start":[0.49221,0.02813,0.18126],"object_to_goal_dist_end":0.03516,"object_to_goal_dist_start":0.10539,"object_z_max":0.18126,"peak_contact_force":63.18809,"phase_name":"contact_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.4863,0.03134,0.05062],"tcp_start":[0.4906,0.02804,0.1413],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.48826,0.03144,0.0905],"object_pos_start":[0.48836,0.03145,0.09057],"object_to_goal_dist_end":0.03517,"object_to_goal_dist_start":0.03516,"object_z_max":0.09057,"peak_contact_force":67.88036,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":76.91034,"subtask_id":"insert_peg","tcp_end":[0.48615,0.03131,0.05047],"tcp_start":[0.48618,0.03132,0.0505],"tcp_to_object_dist_end":0.04009,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```