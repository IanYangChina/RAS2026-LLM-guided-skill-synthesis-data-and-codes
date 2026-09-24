## Search State

- **Seed**: 6
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | align → approach → grasp → contact → insert | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | time_limit | force_exceeded | pose_tolerance | 14 | -0.1322 | 0.87 | ❌ rejected |
| 10 | align → approach → grasp → contact → insert | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | time_limit | force_exceeded | force_exceeded | 14 | 0.1414 | 0.88 | ❌ rejected |
| 9 | align → approach → contact → insert → grasp | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | time_limit | 13 | 0.0592 | 0.88 | ✅ accepted |
| 8 | align → approach → descend → insert → grasp | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | time_limit | 13 | 0.2767 | 0.87 | ❌ rejected |
| 7 | align → approach → descend → insert → grasp | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 12 | -0.0734 | 0.87 | ✅ accepted |

**Proposal policy**: task_score is 0.87 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.132) — your mutation base

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

- **Composite score**: -0.132
- **task_score** (E): 0.871
- **fitness_score**: 0.458  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.790

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 0.00 | 0.1133 |
| approach_1 | 1.00 | 0.00 | 0.0573 |
| grasp_peg | 1.00 | 0.00 | 0.0096 |
| contact_1 | 1.00 | 1.00 | 0.0742 |
| insert_1 | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.500, 0.014, 0.189) | (0.504, -0.000, 0.340)→(0.501, 0.014, 0.229) | 0.260→0.150 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.014, 0.189)→(0.497, 0.018, 0.133) | (0.501, 0.014, 0.229)→(0.498, 0.018, 0.173) | 0.150→0.097 | 0.00 / 0.000 | 0.000 | 0.000 |
| grasp_peg | grasp | 1.00 / step_budget | (0.497, 0.018, 0.133)→(0.491, 0.018, 0.125) | (0.498, 0.018, 0.173)→(0.493, 0.018, 0.165) | 0.097→0.090 | 0.00 / 0.000 | 0.000 | 0.000 |
| contact_1 | contact | 1.00 / force_exceeded | (0.491, 0.018, 0.125)→(0.492, 0.019, 0.051) | (0.493, 0.018, 0.165)→(0.494, 0.019, 0.091) | 0.090→0.030 | 1.00 / 1.000 | 72.210 | 0.000 |
| insert_1 | insert | 0.00 / guard_failure | (0.492, 0.019, 0.051)→(0.492, 0.019, 0.051) | (0.494, 0.019, 0.091)→(0.494, 0.019, 0.091) | 0.030→0.030 | 1.00 / 1.000 | 88.593 | 91.636 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.941
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.941
- phase_score: 0.243
- phase_breakdown.reach_socket_score: 0.810
- phase_breakdown.insert_peg_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.522
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.941
- **Median Q (composite search score)**: -0.143
- **K-run variance**: 0.0024
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.98361,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00445,"align_1.lateral_offset_y":0.00955,"approach_1.approach_height":0.04224,"approach_1.approach_speed":0.03725,"contact_1.contact_force_threshold":20.96124,"contact_1.descend_distance":0.09151,"contact_1.descend_speed":0.02812,"grasp_peg.grasp_duration":1.6403,"insert_1.insert_distance":0.06282,"insert_1.insert_speed":0.0113,"insert_1.insert_tolerance":0.01215,"insert_1.insertion_guard_force":51.22039,"insert_1.retry_lateral_x":0.01415,"insert_1.retry_lateral_y":0.00518},"optimized_scores":{"best_composite_score":-0.06776,"best_fitness_score":0.52224,"best_task_score":0.94089},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.50969,-0.01166,0.04998],"force_p95":90.04385,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.16913,"mean_force":82.91609,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49471,-0.0115,0.05075]}],"total_contact_groups":1},"final_pose_error":0.03456,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.49462,-0.0115,0.05068],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":91.02989,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":347.0,"n_steps_budget":780.0,"object_pos_end":[0.50425,-0.00265,0.22904],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.14913,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.50378,-0.00265,0.18905],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":202.0,"n_steps_budget":1000.0,"object_pos_end":[0.50095,-0.01046,0.17145],"object_pos_start":[0.50425,-0.00265,0.22904],"object_to_goal_dist_end":0.09205,"object_to_goal_dist_start":0.14913,"object_z_max":0.22904,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.50003,-0.01045,0.13146],"tcp_start":[0.50378,-0.00265,0.18905],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49586,-0.01047,0.16364],"object_pos_start":[0.50095,-0.01046,0.17145],"object_to_goal_dist_end":0.08439,"object_to_goal_dist_start":0.09205,"object_z_max":0.17145,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49418,-0.01046,0.12367],"tcp_start":[0.50003,-0.01045,0.13146],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":493.0,"n_steps_budget":1000.0,"object_pos_end":[0.49691,-0.01151,0.09073],"object_pos_start":[0.49586,-0.01047,0.16364],"object_to_goal_dist_end":0.01603,"object_to_goal_dist_start":0.08439,"object_z_max":0.16364,"peak_contact_force":91.02989,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49477,-0.01149,0.05079],"tcp_start":[0.49418,-0.01046,0.12367],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49681,-0.01151,0.09069],"object_pos_start":[0.49691,-0.01151,0.09073],"object_to_goal_dist_end":0.01603,"object_to_goal_dist_start":0.01603,"object_z_max":0.09073,"peak_contact_force":88.91632,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":90.16913,"subtask_id":"insert_peg","tcp_end":[0.49462,-0.0115,0.05068],"tcp_start":[0.49466,-0.0115,0.05071],"tcp_to_object_dist_end":0.04007,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `b372e597e9ea71ad79503f48aaa87b3bb2c0c3a8e8252ca19ea88229597605ec`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.54491,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00265,"align_1.lateral_offset_y":-0.00969,"approach_1.approach_height":0.04337,"approach_1.approach_speed":0.02059,"contact_1.contact_force_threshold":17.01634,"contact_1.descend_distance":0.08556,"contact_1.descend_speed":0.00501,"grasp_peg.grasp_duration":1.64492,"insert_1.insert_distance":0.05763,"insert_1.insert_speed":0.00586,"insert_1.insert_tolerance":0.01408,"insert_1.insertion_guard_force":73.13575,"insert_1.retry_lateral_x":0.00614,"insert_1.retry_lateral_y":0.01338},"optimized_scores":{"best_composite_score":-0.14321,"best_fitness_score":0.44679,"best_task_score":0.86642},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.5161,0.03099,0.04994],"force_p95":83.40681,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.84838,"mean_force":78.40163,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50115,0.03007,0.05068]}],"total_contact_groups":1},"final_pose_error":0.02967,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.50107,0.03005,0.05061],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":83.84838,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":356.0,"n_steps_budget":780.0,"object_pos_end":[0.50414,0.01949,0.22871],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15004,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.50367,0.01947,0.18871],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.50644,0.02916,0.17167],"object_pos_start":[0.50414,0.01949,0.22871],"object_to_goal_dist_end":0.09641,"object_to_goal_dist_start":0.15004,"object_z_max":0.22871,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.50551,0.02911,0.13168],"tcp_start":[0.50367,0.01947,0.18871],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50138,0.02887,0.16373],"object_pos_start":[0.50644,0.02916,0.17167],"object_to_goal_dist_end":0.08858,"object_to_goal_dist_start":0.09641,"object_z_max":0.17167,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.4997,0.02878,0.12376],"tcp_start":[0.50551,0.02911,0.13168],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":506.0,"n_steps_budget":1000.0,"object_pos_end":[0.50336,0.0302,0.09067],"object_pos_start":[0.50138,0.02887,0.16373],"object_to_goal_dist_end":0.03221,"object_to_goal_dist_start":0.08858,"object_z_max":0.16373,"peak_contact_force":63.56125,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50122,0.03008,0.05073],"tcp_start":[0.4997,0.02878,0.12376],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50321,0.03018,0.0906],"object_pos_start":[0.50336,0.0302,0.09067],"object_to_goal_dist_end":0.03215,"object_to_goal_dist_start":0.03221,"object_z_max":0.09067,"peak_contact_force":80.55412,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":83.84838,"subtask_id":"insert_peg","tcp_end":[0.50107,0.03005,0.05061],"tcp_start":[0.50109,0.03006,0.05063],"tcp_to_object_dist_end":0.04005,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ae45bae888bf338225755528d96cf0281f13a4171bef9e43a6d9a98635b19bee`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.5906,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00906,"align_1.lateral_offset_y":-0.00952,"approach_1.approach_height":0.04523,"approach_1.approach_speed":0.0417,"contact_1.contact_force_threshold":26.11734,"contact_1.descend_distance":0.06301,"contact_1.descend_speed":0.01805,"grasp_peg.grasp_duration":1.65541,"insert_1.insert_distance":0.06535,"insert_1.insert_speed":0.00611,"insert_1.insert_tolerance":0.01182,"insert_1.insertion_guard_force":50.15321,"insert_1.retry_lateral_x":0.00438,"insert_1.retry_lateral_y":-0.01966},"optimized_scores":{"best_composite_score":-0.18549,"best_fitness_score":0.40451,"best_task_score":0.80654},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.49476,0.03849,0.04992],"force_p95":100.43364,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":100.8919,"mean_force":87.40088,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.47982,0.03747,0.05061]}],"total_contact_groups":1},"final_pose_error":0.0365,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.47973,0.03745,0.05055],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":100.8919,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":355.0,"n_steps_budget":780.0,"object_pos_end":[0.49349,0.02604,0.22884],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15124,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.49305,0.02601,0.18884],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":192.0,"n_steps_budget":990.0,"object_pos_end":[0.48544,0.036,0.17456],"object_pos_start":[0.49349,0.02604,0.22884],"object_to_goal_dist_end":0.10222,"object_to_goal_dist_start":0.15124,"object_z_max":0.22884,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.48458,0.03594,0.13457],"tcp_start":[0.49305,0.02601,0.18884],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4805,0.03567,0.16719],"object_pos_start":[0.48544,0.036,0.17456],"object_to_goal_dist_end":0.0962,"object_to_goal_dist_start":0.10222,"object_z_max":0.17456,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.47889,0.03557,0.12722],"tcp_start":[0.48458,0.03594,0.13457],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":558.0,"n_steps_budget":1000.0,"object_pos_end":[0.48193,0.03762,0.09059],"object_pos_start":[0.4805,0.03567,0.16719],"object_to_goal_dist_end":0.04306,"object_to_goal_dist_start":0.0962,"object_z_max":0.16719,"peak_contact_force":62.03847,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.47988,0.03748,0.05064],"tcp_start":[0.47889,0.03557,0.12722],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.48183,0.03761,0.09055],"object_pos_start":[0.48193,0.03762,0.09059],"object_to_goal_dist_end":0.04308,"object_to_goal_dist_start":0.04306,"object_z_max":0.09059,"peak_contact_force":96.30932,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":100.8919,"subtask_id":"insert_peg","tcp_end":[0.47973,0.03745,0.05055],"tcp_start":[0.47977,0.03746,0.05057],"tcp_to_object_dist_end":0.04006,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```