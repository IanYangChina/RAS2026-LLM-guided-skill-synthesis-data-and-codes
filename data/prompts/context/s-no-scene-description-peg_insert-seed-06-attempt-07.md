## Search State

- **Seed**: 6
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | align → approach → descend → insert → grasp | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 12 | -0.0734 | 0.87 | ✅ accepted |
| 6 | align → approach → descend → insert → grasp | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 12 | -0.0983 | 0.87 | ❌ rejected |
| 5 | align → approach → descend → insert → grasp | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 12 | -0.0312 | 0.87 | ✅ accepted |
| 4 | align → approach → descend → insert → grasp | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 12 | -0.0313 | 0.87 | ✅ accepted |
| 3 | align → approach → descend → insert → grasp | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | time_limit | 9 | 0.0817 | 0.87 | ❌ rejected |

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

## Current Skill (Q=-0.073) — your mutation base

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
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.06, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
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

- **Composite score**: -0.073
- **task_score** (E): 0.875
- **fitness_score**: 0.550  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.067
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.690

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 0.00 | 0.1138 |
| approach_1 | 1.00 | 0.00 | 0.0441 |
| descend_1 | 1.00 | 1.00 | 0.0965 |
| insert_1 | 0.67 | 0.67 | 0.0051 |
| grasp_1 | 1.00 | 1.00 | 0.0011 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.499, 0.015, 0.189) | (0.504, -0.000, 0.340)→(0.499, 0.015, 0.229) | 0.260→0.150 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_1 | approach | 1.00 / step_budget | (0.499, 0.015, 0.189)→(0.497, 0.018, 0.146) | (0.499, 0.015, 0.229)→(0.498, 0.018, 0.186) | 0.150→0.109 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.018, 0.146)→(0.509, 0.019, 0.050) | (0.498, 0.018, 0.186)→(0.509, 0.019, 0.090) | 0.109→0.032 | 1.00 / 1.000 | 418.270 | 494.030 |
| insert_1 | insert | 0.67 / step_budget | (0.509, 0.019, 0.050)→(0.504, 0.019, 0.051) | (0.509, 0.019, 0.090)→(0.504, 0.019, 0.091) | 0.032→0.031 | 0.67 / 0.667 | 39.740 | 60.589 |
| grasp_1 | grasp | 1.00 / step_budget | (0.504, 0.019, 0.051)→(0.504, 0.019, 0.050) | (0.504, 0.019, 0.091)→(0.504, 0.019, 0.090) | 0.031→0.030 | 1.00 / 1.000 | 66.937 | 83.741 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.814
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.814
- phase_score: 0.300
- phase_breakdown.reach_socket_score: 1.000
- phase_breakdown.insert_peg_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.574
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.947
- **Median Q (composite search score)**: -0.116
- **K-run variance**: 0.0040
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.340


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.50761,"average_solve_count":197.0,"average_success_count":197.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00554,"align_1.lateral_offset_y":0.00792,"approach_1.approach_height":0.05301,"approach_1.approach_speed":0.0307,"descend_1.descend_distance":0.05313,"descend_1.descend_speed":0.02066,"grasp_1.grasp_duration":1.20505,"insert_1.insert_distance":0.03291,"insert_1.insert_max_force":70.92018,"insert_1.insert_speed":0.01188,"insert_1.retry_lateral_x":0.00175,"insert_1.retry_lateral_y":0.00823},"optimized_scores":{"best_composite_score":-0.11971,"best_fitness_score":0.57029,"best_task_score":0.94742},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":396.0,"contact_point_centroid":[0.51898,-0.01248,0.04993],"force_p95":446.12496,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":502.10023,"mean_force":435.89264,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.504,-0.01208,0.05016]},{"body_a":"attachment","body_b":"peg_socket","contact_count":449.0,"contact_point_centroid":[0.49345,-0.01216,0.04998],"force_p95":78.48232,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.56572,"mean_force":71.64821,"phase_index":4.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50843,-0.01221,0.05013]},{"body_a":"attachment","body_b":"peg_socket","contact_count":164.0,"contact_point_centroid":[0.4955,-0.01281,0.04996],"force_p95":67.66413,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":67.8573,"mean_force":63.27579,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50868,-0.01219,0.05002]}],"total_contact_groups":3},"final_pose_error":0.00611,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.50832,-0.0122,0.05016],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":502.10023,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":348.0,"n_steps_budget":780.0,"object_pos_end":[0.50521,-0.00409,0.22895],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.1491,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.50474,-0.00409,0.18895],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":164.0,"n_steps_budget":1000.0,"object_pos_end":[0.50133,-0.01042,0.18226],"object_pos_start":[0.50521,-0.00409,0.22895],"object_to_goal_dist_end":0.1028,"object_to_goal_dist_start":0.1491,"object_z_max":0.22895,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.50042,-0.01041,0.14227],"tcp_start":[0.50474,-0.00409,0.18895],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":739.0,"n_steps_budget":1000.0,"object_pos_end":[0.5092,-0.01218,0.08994],"object_pos_start":[0.50133,-0.01042,0.18226],"object_to_goal_dist_end":0.01822,"object_to_goal_dist_start":0.1028,"object_z_max":0.18226,"peak_contact_force":444.7798,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":396.0,"raw_peak_contact_force":502.10023,"subtask_id":"insert_peg","tcp_end":[0.50919,-0.01218,0.04994],"tcp_start":[0.50042,-0.01041,0.14227],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":165.0,"n_steps_budget":600.0,"object_pos_end":[0.50789,-0.0122,0.09016],"object_pos_start":[0.5092,-0.01218,0.08994],"object_to_goal_dist_end":0.01773,"object_to_goal_dist_start":0.01822,"object_z_max":0.09016,"peak_contact_force":65.32355,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":164.0,"raw_peak_contact_force":67.8573,"subtask_id":"insert_peg","tcp_end":[0.50832,-0.0122,0.05016],"tcp_start":[0.50919,-0.01218,0.04994],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50811,-0.01221,0.09015],"object_pos_start":[0.50789,-0.0122,0.09016],"object_to_goal_dist_end":0.01783,"object_to_goal_dist_start":0.01773,"object_z_max":0.09016,"peak_contact_force":66.94747,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":449.0,"raw_peak_contact_force":79.56572,"tcp_end":[0.50858,-0.01222,0.05015],"tcp_start":[0.50832,-0.0122,0.05016],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `b372e597e9ea71ad79503f48aaa87b3bb2c0c3a8e8252ca19ea88229597605ec`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.47196,"average_solve_count":214.0,"average_success_count":214.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00122,"align_1.lateral_offset_y":-0.00668,"approach_1.approach_height":0.04277,"approach_1.approach_speed":0.02948,"descend_1.descend_distance":0.0723,"descend_1.descend_speed":0.00964,"grasp_1.grasp_duration":0.85395,"insert_1.insert_distance":0.0223,"insert_1.insert_max_force":72.20809,"insert_1.insert_speed":0.01004,"insert_1.retry_lateral_x":-0.01179,"insert_1.retry_lateral_y":-0.01136},"optimized_scores":{"best_composite_score":-0.11618,"best_fitness_score":0.57382,"best_task_score":0.86191},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":699.0,"contact_point_centroid":[0.51844,0.03624,0.04994],"force_p95":436.06797,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":481.83521,"mean_force":417.89796,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51371,0.03109,0.05008]},{"body_a":"attachment","body_b":"peg_socket","contact_count":420.0,"contact_point_centroid":[0.52038,0.03241,0.04998],"force_p95":88.18724,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.97517,"mean_force":73.37221,"phase_index":4.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50543,0.03133,0.05019]},{"body_a":"attachment","body_b":"peg_socket","contact_count":39.0,"contact_point_centroid":[0.51348,0.03741,0.04999],"force_p95":55.22576,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.01297,"mean_force":24.50186,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51884,0.03139,0.05003]}],"total_contact_groups":3},"final_pose_error":0.00615,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.50714,0.03146,0.05227],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":481.83521,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":360.0,"n_steps_budget":780.0,"object_pos_end":[0.50541,0.02219,0.2285],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15024,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.50495,0.02216,0.1885],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.5067,0.02968,0.17129],"object_pos_start":[0.50541,0.02219,0.2285],"object_to_goal_dist_end":0.09623,"object_to_goal_dist_start":0.15024,"object_z_max":0.2285,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.50578,0.02962,0.1313],"tcp_start":[0.50495,0.02216,0.1885],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52104,0.03154,0.09001],"object_pos_start":[0.5067,0.02968,0.17129],"object_to_goal_dist_end":0.03921,"object_to_goal_dist_start":0.09623,"object_z_max":0.17129,"peak_contact_force":393.71438,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":699.0,"raw_peak_contact_force":481.83521,"subtask_id":"insert_peg","tcp_end":[0.52131,0.03148,0.05001],"tcp_start":[0.50578,0.02962,0.1313],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":370.0,"n_steps_budget":870.0,"object_pos_end":[0.50759,0.03149,0.09227],"object_pos_start":[0.52104,0.03154,0.09001],"object_to_goal_dist_end":0.03463,"object_to_goal_dist_start":0.03921,"object_z_max":0.09226,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":39.0,"raw_peak_contact_force":60.01297,"subtask_id":"insert_peg","tcp_end":[0.50714,0.03146,0.05227],"tcp_start":[0.52131,0.03148,0.05001],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50624,0.03137,0.0902],"object_pos_start":[0.50759,0.03149,0.09227],"object_to_goal_dist_end":0.03357,"object_to_goal_dist_start":0.03463,"object_z_max":0.09227,"peak_contact_force":67.57845,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":420.0,"raw_peak_contact_force":92.97517,"tcp_end":[0.50563,0.03134,0.0502],"tcp_start":[0.50714,0.03146,0.05227],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ae45bae888bf338225755528d96cf0281f13a4171bef9e43a6d9a98635b19bee`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.66292,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00211,"align_1.lateral_offset_y":-0.00856,"approach_1.approach_height":0.07467,"approach_1.approach_speed":0.02338,"descend_1.descend_distance":0.06726,"descend_1.descend_speed":0.01794,"grasp_1.grasp_duration":1.79546,"insert_1.insert_distance":0.06957,"insert_1.insert_max_force":32.76295,"insert_1.insert_speed":0.01486,"insert_1.retry_lateral_x":0.01202,"insert_1.retry_lateral_y":0.00338},"optimized_scores":{"best_composite_score":0.01583,"best_fitness_score":0.50583,"best_task_score":0.81447},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":580.0,"contact_point_centroid":[0.49636,0.04495,0.04993],"force_p95":460.52953,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":498.15354,"mean_force":442.56182,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48986,0.03787,0.05004]},{"body_a":"attachment","body_b":"peg_socket","contact_count":450.0,"contact_point_centroid":[0.48406,0.04611,0.04998],"force_p95":77.49558,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.6832,"mean_force":70.9619,"phase_index":4.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49687,0.03833,0.05004]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.48484,0.04762,0.04995],"force_p95":53.89528,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":53.89528,"mean_force":53.89528,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49662,0.03834,0.04996]}],"total_contact_groups":3},"final_pose_error":0.0409,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.49662,0.03833,0.04996],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":498.15354,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":354.0,"n_steps_budget":780.0,"object_pos_end":[0.48734,0.02687,0.22898],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15191,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.48691,0.02684,0.18898],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":103.0,"n_steps_budget":990.0,"object_pos_end":[0.48462,0.03446,0.20307],"object_pos_start":[0.48734,0.02687,0.22898],"object_to_goal_dist_end":0.12873,"object_to_goal_dist_start":0.15191,"object_z_max":0.22898,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket","tcp_end":[0.4838,0.03441,0.16308],"tcp_start":[0.48691,0.02684,0.18898],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49648,0.03844,0.08996],"object_pos_start":[0.48462,0.03446,0.20307],"object_to_goal_dist_end":0.03987,"object_to_goal_dist_start":0.12873,"object_z_max":0.20307,"peak_contact_force":416.31676,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":580.0,"raw_peak_contact_force":498.15354,"subtask_id":"insert_peg","tcp_end":[0.49662,0.03834,0.04996],"tcp_start":[0.4838,0.03441,0.16308],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49649,0.03844,0.08996],"object_pos_start":[0.49648,0.03844,0.08996],"object_to_goal_dist_end":0.03986,"object_to_goal_dist_start":0.03987,"object_z_max":0.08996,"peak_contact_force":53.89528,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":53.89528,"subtask_id":"insert_peg","tcp_end":[0.49662,0.03833,0.04996],"tcp_start":[0.49662,0.03834,0.04996],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49683,0.03845,0.09005],"object_pos_start":[0.49649,0.03844,0.08996],"object_to_goal_dist_end":0.03987,"object_to_goal_dist_start":0.03986,"object_z_max":0.09005,"peak_contact_force":66.28408,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":450.0,"raw_peak_contact_force":78.6832,"tcp_end":[0.49702,0.03835,0.05005],"tcp_start":[0.49662,0.03833,0.04996],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```