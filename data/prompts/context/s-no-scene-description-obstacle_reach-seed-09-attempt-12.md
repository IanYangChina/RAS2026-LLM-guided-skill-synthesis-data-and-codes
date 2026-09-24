## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | time_limit | pose_tolerance | 5 | 0.6723 | 0.92 | ❌ rejected |
| 11 | approach → descend | linear_cartesian | linear_cartesian | position_control | position_control | time_limit | pose_tolerance | 4 | 0.7204 | 0.92 | ❌ rejected |
| 10 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | time_limit | pose_tolerance | 4 | 0.6719 | 0.87 | ❌ rejected |
| 9 | approach → descend → approach | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | 7 | 0.5662 | 0.95 | ❌ rejected |
| 8 | approach → descend → approach | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | 7 | 0.5629 | 0.94 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.92). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

- Task name: obstacle_reach
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.5
- Force limit: 5.0 N
- Obstacle body: obstacle_block (contact = collision penalty)
- Primary evaluation target: **TCP distance to goal position (Gaussian proximity kernel)**

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
| `object` | offset from object initial position | approach/contact targets near object |
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

## Current Skill (Q=0.672) — your mutation base

```yaml
skill: obstacle_reach
dsl_version: 2
subtasks:
- id: reach_above_goal
  offset:
  - 0.0
  - 0.0
  - 0.3
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: approach_arc
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.3
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    arc_duration:
      type: scalar
      range:
      - 0.5
      - 5.0
      default: 2.0
      binds_to:
      - path: duration.max_time
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: reach_above_goal
- id: descend_to_goal
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_guard_tol:
      type: scalar
      range:
      - 0.01
      - 0.03
      default: 0.02
      binds_to:
      - path: guards.descend_pose_check.threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: descend_pose_check
    when: after_phase
    predicate: pose_within_tolerance
    args:
      tolerance: 0.02
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.01
  subtask_id: reach_goal
- id: final_precise_approach
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
    - 0.0
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    final_guard_tol:
      type: scalar
      range:
      - 0.01
      - 0.03
      default: 0.02
      binds_to:
      - path: guards.final_pose_check.threshold
        mode: replace
    final_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.025
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: final_pose_check
    when: after_phase
    predicate: pose_within_tolerance
    args:
      tolerance: 0.02
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.3], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_duration: status=consumed; consumers=duration.max_time (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_guard_tol: status=consumed; consumers=guards.descend_pose_check.threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=descend_pose_check, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.02, args={'tolerance': 0.02}
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, -0.01]
- **final_precise_approach** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - final_guard_tol: status=consumed; consumers=guards.final_pose_check.threshold (replace)
    - final_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=final_pose_check, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.02, args={'tolerance': 0.02}
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]

## Design Metrics

- **Composite score**: 0.672
- **task_score** (E): 0.922
- **fitness_score**: 0.922  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.250

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_arc | 1.00 | 0.00 | 0.3333 |
| descend_to_goal | 1.00 | 0.00 | 0.0096 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_arc | approach | 1.00 / time_limit | (0.350, -0.000, 0.321)→(0.642, -0.012, 0.475) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.731→0.731 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_goal | descend | 1.00 / step_budget | (0.708, -0.017, 0.169)→(0.708, -0.017, 0.160) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.731→0.731 | 0.00 / 0.000 | 0.000 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.799
- path_efficiency: 0.460
- arc_smoothness: 0.995
- collision_factor: 1.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 0.000 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.010
- min_tcp_distance: 0.010
- tcp_proximity_score: 0.936
- goal_reached_rate: 1.000
- peak_obstacle_counterbody: None
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: None
- peak_obstacle_obstacle_geom: None

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.936
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.936
- **Median Q (composite search score)**: 0.682
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.371


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `4a44882555f0d0b14e6aa599db443a998da24652eb9b9e2830cc337dec76aa35`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `47104ba1d83b6713840746a9744b8461d7698be90a7b9bbdb4a5ee2c9b597658`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":3.0,"average_failure_rate":0.03093,"average_mean_iterations":10.31959,"average_solve_count":97.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_arc.approach_speed":0.25178,"approach_arc.arc_duration":2.68594,"approach_arc.arc_height":0.05616,"descend_to_goal.descend_guard_tol":0.01588,"descend_to_goal.descend_speed":0.14875},"optimized_scores":{"best_composite_score":0.68239,"best_fitness_score":0.93239,"best_task_score":0.93239},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.0105,"key_states":{"actual_goal_position":[0.73702,-0.02132,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.73108,-0.02122,0.15865],"realised_goal_position":[0.73702,-0.02132,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":901.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_goal","tcp_end":[0.68826,-0.01862,0.45115],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.82315,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":473.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_goal","tcp_end":[0.73108,-0.02122,0.15865],"tcp_start":[0.73119,-0.02116,0.16876],"tcp_to_object_dist_end":0.7484,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `dd76534a039a46a09f9e3c15723c51c6f1027acc2aa2ab4b06e8dae86dbdcd96`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":7.0,"average_failure_rate":0.04,"average_mean_iterations":11.58857,"average_solve_count":175.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_arc.approach_speed":0.17211,"approach_arc.arc_duration":1.37869,"approach_arc.arc_height":0.13153,"descend_to_goal.descend_guard_tol":0.02284,"descend_to_goal.descend_speed":0.02024},"optimized_scores":{"best_composite_score":0.64861,"best_fitness_score":0.89861,"best_task_score":0.89861},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.01604,"key_states":{"actual_goal_position":[0.7456,-0.02923,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.7345,-0.02857,0.16155],"realised_goal_position":[0.7456,-0.02923,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.7611,"object_to_goal_dist_start":0.7611,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_goal","tcp_end":[0.58786,-0.01753,0.51532],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.78195,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":695.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.7611,"object_to_goal_dist_start":0.7611,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_goal","tcp_end":[0.7345,-0.02857,0.16155],"tcp_start":[0.73431,-0.02845,0.16997],"tcp_to_object_dist_end":0.75259,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b9c2919c979234936a5d994fa5db826639b75dec9196808e9cc353d4e638017c`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70861,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_arc.approach_speed":0.25854,"approach_arc.arc_duration":3.24589,"approach_arc.arc_height":0.19862,"descend_to_goal.descend_guard_tol":0.0122,"descend_to_goal.descend_speed":0.06062},"optimized_scores":{"best_composite_score":0.68577,"best_fitness_score":0.93577,"best_task_score":0.93577},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.66286,-7e-05,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.65871,-0.00022,0.15905],"realised_goal_position":[0.66286,-7e-05,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":811.0,"n_steps_budget":840.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.67962,"object_to_goal_dist_start":0.67962,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_goal","tcp_end":[0.64982,-0.00019,0.45886],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.7955,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":531.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.67962,"object_to_goal_dist_start":0.67962,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_goal","tcp_end":[0.65871,-0.00022,0.15905],"tcp_start":[0.6591,-0.00021,0.1693],"tcp_to_object_dist_end":0.67765,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```