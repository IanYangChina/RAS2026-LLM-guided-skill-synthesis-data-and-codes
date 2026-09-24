## Search State

- **Seed**: 6
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | align → approach → descend → insert → grasp | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 12 | -0.0983 | 0.87 | ❌ rejected |
| 5 | align → approach → descend → insert → grasp | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 12 | -0.0312 | 0.87 | ✅ accepted |
| 4 | align → approach → descend → insert → grasp | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 12 | -0.0313 | 0.87 | ✅ accepted |
| 3 | align → approach → descend → insert → grasp | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | time_limit | 9 | 0.0817 | 0.87 | ❌ rejected |
| 2 | align → approach → insert → grasp | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | 0.0846 | 0.79 | ❌ rejected |

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

## Current Skill (Q=-0.098) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_socket
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: insert_peg
  target_entity: object
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
- id: descend_1
  type: descend
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
      distance: 0.06
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    descend_distance:
      type: scalar
      range:
      - 0.04
      - 0.08
      default: 0.06
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.015
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: insert_peg
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
      distance: 0.05
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
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_max_force:
      type: scalar
      range:
      - 20.0
      - 60.0
      default: 40.0
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
      - -0.003
      - 0.003
      default: 0.0
      binds_to:
      - path: retry.offset.x
        mode: replace
    retry_lateral_y:
      type: scalar
      range:
      - -0.003
      - 0.003
      default: 0.0
      binds_to:
      - path: retry.offset.y
        mode: replace
  guards:
  - id: insertion_force_guard
    when: during_phase
    predicate: force_below
    threshold: 60.0
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
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.06, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **insert_1** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.05, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.02
  - parameter_bindings:
    - insert_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_max_force: status=consumed; consumers=termination.force_threshold (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - retry_lateral_x: status=consumed; consumers=retry.offset.x (replace)
    - retry_lateral_y: status=consumed; consumers=retry.offset.y (replace)
  - guards:
    - id=insertion_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=60.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: -0.098
- **task_score** (E): 0.874
- **fitness_score**: 0.458  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.690

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 0.00 | 0.1130 |
| approach_1 | 1.00 | 0.00 | 0.0584 |
| descend_1 | 1.00 | 1.00 | 0.0829 |
| insert_1 | 0.67 | 1.00 | 0.0000 |
| grasp_1 | 1.00 | 1.00 | 0.0005 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.014, 0.189) | (0.504, -0.000, 0.340)→(0.497, 0.014, 0.229) | 0.260→0.150 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_1 | approach | 1.00 / step_budget | (0.496, 0.014, 0.189)→(0.496, 0.018, 0.132) | (0.497, 0.014, 0.229)→(0.497, 0.018, 0.172) | 0.150→0.096 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.018, 0.132)→(0.510, 0.019, 0.050) | (0.497, 0.018, 0.172)→(0.510, 0.019, 0.090) | 0.096→0.033 | 1.00 / 1.000 | 402.432 | 493.066 |
| insert_1 | insert | 0.67 / force_exceeded | (0.510, 0.019, 0.050)→(0.510, 0.019, 0.050) | (0.510, 0.019, 0.090)→(0.510, 0.019, 0.090) | 0.033→0.033 | 1.00 / 1.000 | 59.224 | 59.224 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, 0.019, 0.050)→(0.510, 0.019, 0.050) | (0.510, 0.019, 0.090)→(0.510, 0.019, 0.090) | 0.033→0.033 | 1.00 / 1.000 | 66.472 | 79.008 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.946
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.946
- phase_score: 0.241
- phase_breakdown.reach_socket_score: 0.803
- phase_breakdown.insert_peg_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.523
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.946
- **Median Q (composite search score)**: -0.045
- **K-run variance**: 0.0180
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.329


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.45055,"average_solve_count":182.0,"average_success_count":182.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00185,"align_1.lateral_offset_y":0.00857,"approach_1.approach_height":0.04363,"approach_1.approach_speed":0.03931,"descend_1.descend_distance":0.05498,"descend_1.descend_speed":0.01587,"grasp_1.grasp_duration":1.26183,"insert_1.insert_distance":0.04242,"insert_1.insert_max_force":27.59977,"insert_1.insert_speed":0.00917,"insert_1.retry_lateral_x":0.00243,"insert_1.retry_lateral_y":-0.00086},"optimized_scores":{"best_composite_score":0.03305,"best_fitness_score":0.52305,"best_task_score":0.94647},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":517.0,"contact_point_centroid":[0.51396,-0.01334,0.04994],"force_p95":445.33336,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":496.35139,"mean_force":428.83082,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50507,-0.0121,0.0501]},{"body_a":"attachment","body_b":"peg_socket","contact_count":450.0,"contact_point_centroid":[0.4966,-0.01134,0.04998],"force_p95":74.79297,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.97004,"mean_force":70.23553,"phase_index":4.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5115,-0.01225,0.05]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.49616,-0.01316,0.04995],"force_p95":52.22479,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":52.22479,"mean_force":52.22479,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51112,-0.01224,0.04992]}],"total_contact_groups":3},"final_pose_error":0.01475,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.51113,-0.01224,0.04992],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":496.35139,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":342.0,"n_steps_budget":780.0,"object_pos_end":[0.49871,-0.0035,0.22953],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.14958,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.49824,-0.0035,0.18953],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":205.0,"n_steps_budget":1000.0,"object_pos_end":[0.49981,-0.01066,0.17247],"object_pos_start":[0.49871,-0.0035,0.22953],"object_to_goal_dist_end":0.09308,"object_to_goal_dist_start":0.14958,"object_z_max":0.22953,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.4989,-0.01066,0.13248],"tcp_start":[0.49824,-0.0035,0.18953],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":830.0,"n_steps_budget":1000.0,"object_pos_end":[0.51108,-0.01224,0.08992],"object_pos_start":[0.49981,-0.01066,0.17247],"object_to_goal_dist_end":0.01926,"object_to_goal_dist_start":0.09308,"object_z_max":0.17247,"peak_contact_force":398.40487,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":517.0,"raw_peak_contact_force":496.35139,"subtask_id":"insert_peg","tcp_end":[0.51112,-0.01224,0.04992],"tcp_start":[0.4989,-0.01066,0.13248],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.5111,-0.01224,0.08992],"object_pos_start":[0.51108,-0.01224,0.08992],"object_to_goal_dist_end":0.01927,"object_to_goal_dist_start":0.01926,"object_z_max":0.08992,"peak_contact_force":52.22479,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":52.22479,"subtask_id":"insert_peg","tcp_end":[0.51113,-0.01224,0.04992],"tcp_start":[0.51112,-0.01224,0.04992],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51156,-0.01225,0.09001],"object_pos_start":[0.5111,-0.01224,0.08992],"object_to_goal_dist_end":0.01959,"object_to_goal_dist_start":0.01927,"object_z_max":0.09001,"peak_contact_force":66.52619,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":450.0,"raw_peak_contact_force":75.97004,"tcp_end":[0.51165,-0.01226,0.05001],"tcp_start":[0.51113,-0.01224,0.04992],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `b372e597e9ea71ad79503f48aaa87b3bb2c0c3a8e8252ca19ea88229597605ec`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.45876,"average_solve_count":194.0,"average_success_count":194.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.0081,"align_1.lateral_offset_y":-0.00985,"approach_1.approach_height":0.043,"approach_1.approach_speed":0.02561,"descend_1.descend_distance":0.06017,"descend_1.descend_speed":0.02013,"grasp_1.grasp_duration":1.38309,"insert_1.insert_distance":0.04962,"insert_1.insert_max_force":35.73492,"insert_1.insert_speed":0.01603,"insert_1.retry_lateral_x":0.00026,"insert_1.retry_lateral_y":-0.00105},"optimized_scores":{"best_composite_score":-0.04521,"best_fitness_score":0.44479,"best_task_score":0.86294},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":633.0,"contact_point_centroid":[0.52034,0.03618,0.04994],"force_p95":436.44457,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":487.30289,"mean_force":420.89732,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51294,0.03107,0.0501]},{"body_a":"attachment","body_b":"peg_socket","contact_count":450.0,"contact_point_centroid":[0.506,0.0351,0.04998],"force_p95":74.6854,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.81376,"mean_force":69.94334,"phase_index":4.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52053,0.03147,0.05005]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.50608,0.0367,0.04995],"force_p95":52.38884,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":52.38884,"mean_force":52.38884,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.52013,0.03145,0.04997]}],"total_contact_groups":3},"final_pose_error":0.02206,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.52015,0.03145,0.04997],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":487.30289,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":351.0,"n_steps_budget":780.0,"object_pos_end":[0.49931,0.01932,0.22895],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.1502,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.49884,0.01929,0.18895],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":227.0,"n_steps_budget":1000.0,"object_pos_end":[0.50558,0.02925,0.17077],"object_pos_start":[0.49931,0.01932,0.22895],"object_to_goal_dist_end":0.09553,"object_to_goal_dist_start":0.1502,"object_z_max":0.22895,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.50466,0.0292,0.13078],"tcp_start":[0.49884,0.01929,0.18895],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":937.0,"n_steps_budget":1000.0,"object_pos_end":[0.51997,0.03151,0.08997],"object_pos_start":[0.50558,0.02925,0.17077],"object_to_goal_dist_end":0.03861,"object_to_goal_dist_start":0.09553,"object_z_max":0.17077,"peak_contact_force":394.33079,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":633.0,"raw_peak_contact_force":487.30289,"subtask_id":"insert_peg","tcp_end":[0.52013,0.03145,0.04997],"tcp_start":[0.50466,0.0292,0.13078],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":870.0,"object_pos_end":[0.51999,0.03151,0.08997],"object_pos_start":[0.51997,0.03151,0.08997],"object_to_goal_dist_end":0.03862,"object_to_goal_dist_start":0.03861,"object_z_max":0.08997,"peak_contact_force":52.38884,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":52.38884,"subtask_id":"insert_peg","tcp_end":[0.52015,0.03145,0.04997],"tcp_start":[0.52013,0.03145,0.04997],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52047,0.03153,0.09006],"object_pos_start":[0.51999,0.03151,0.08997],"object_to_goal_dist_end":0.03891,"object_to_goal_dist_start":0.03862,"object_z_max":0.09006,"peak_contact_force":66.27734,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":450.0,"raw_peak_contact_force":75.81376,"tcp_end":[0.52069,0.03147,0.05006],"tcp_start":[0.52015,0.03145,0.04997],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ae45bae888bf338225755528d96cf0281f13a4171bef9e43a6d9a98635b19bee`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.19291,"average_solve_count":254.0,"average_success_count":254.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00768,"align_1.lateral_offset_y":-0.00996,"approach_1.approach_height":0.04271,"approach_1.approach_speed":0.01292,"descend_1.descend_distance":0.06362,"descend_1.descend_speed":0.00797,"grasp_1.grasp_duration":1.6236,"insert_1.insert_distance":0.06102,"insert_1.insert_max_force":28.3338,"insert_1.insert_speed":0.01388,"insert_1.retry_lateral_x":-0.00206,"insert_1.retry_lateral_y":-0.00244},"optimized_scores":{"best_composite_score":-0.28276,"best_fitness_score":0.40724,"best_task_score":0.81279},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":685.0,"contact_point_centroid":[0.49109,0.04319,0.04994],"force_p95":458.77046,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":495.54469,"mean_force":434.19631,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49078,0.0382,0.05004]},{"body_a":"attachment","body_b":"peg_socket","contact_count":450.0,"contact_point_centroid":[0.48323,0.0402,0.04998],"force_p95":83.63827,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":85.24023,"mean_force":72.04055,"phase_index":4.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49814,0.03868,0.05016]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.48311,0.04033,0.04995],"force_p95":72.85495,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":73.05949,"mean_force":69.82253,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49801,0.03867,0.05009]}],"total_contact_groups":3},"final_pose_error":0.03328,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.49801,0.03864,0.05008],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":495.54469,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":354.0,"n_steps_budget":780.0,"object_pos_end":[0.49228,0.02561,0.22902],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.1514,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.49185,0.02558,0.18902],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":218.0,"n_steps_budget":1000.0,"object_pos_end":[0.48507,0.03604,0.17192],"object_pos_start":[0.49228,0.02561,0.22902],"object_to_goal_dist_end":0.09985,"object_to_goal_dist_start":0.1514,"object_z_max":0.22902,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.4842,0.03598,0.13193],"tcp_start":[0.49185,0.02558,0.18902],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49749,0.03874,0.09009],"object_pos_start":[0.48507,0.03604,0.17192],"object_to_goal_dist_end":0.04011,"object_to_goal_dist_start":0.09985,"object_z_max":0.17192,"peak_contact_force":414.56076,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":685.0,"raw_peak_contact_force":495.54469,"subtask_id":"insert_peg","tcp_end":[0.49801,0.03869,0.0501],"tcp_start":[0.4842,0.03598,0.13193],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.4975,0.03872,0.09009],"object_pos_start":[0.49749,0.03874,0.09009],"object_to_goal_dist_end":0.04009,"object_to_goal_dist_start":0.04011,"object_z_max":0.09009,"peak_contact_force":73.05949,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":73.05949,"subtask_id":"insert_peg","tcp_end":[0.49801,0.03864,0.05008],"tcp_start":[0.49801,0.03865,0.05008],"tcp_to_object_dist_end":0.04001,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49774,0.03873,0.09017],"object_pos_start":[0.4975,0.03869,0.09008],"object_to_goal_dist_end":0.04011,"object_to_goal_dist_start":0.04005,"object_z_max":0.09017,"peak_contact_force":66.61148,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":450.0,"raw_peak_contact_force":85.24023,"tcp_end":[0.49829,0.03869,0.05018],"tcp_start":[0.49801,0.03864,0.05008],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```