## Search State

- **Seed**: 9
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | time_limit | time_limit | 6 | 0.3986 | 0.78 | ❌ rejected |
| 8 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 6 | 0.3855 | 0.75 | ❌ rejected |
| 7 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 7 | -0.2475 | 0.07 | ❌ rejected |
| 6 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 6 | 0.4207 | 0.79 | ✅ accepted |
| 5 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 7 | 0.2972 | 0.63 | ❌ rejected |

**Proposal policy**: task_score is 0.78 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: push_to_goal
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Primary evaluation target: **object displacement ratio toward goal_object_position**

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
| `fixture` | offset from fixture pose | targets near fixture |

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

## Current Skill (Q=0.399) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  weight: 0.2
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.8
phases:
- id: approach_from_behind
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
    - 0.025
    offset_along_axis:
      distance: 0.1
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    approach_behind_distance:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
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
    approach_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.025
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: approach_pose_check
    when: after_phase
    predicate: pose_within_tolerance
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: reach_object
- id: push_to_goal_phase
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: none
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    push_time:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 25.0
    on_failure: abort
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_from_behind** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=replace_offset_projection, sign=negative}, tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - approach_behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - approach_z_offset: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=approach_pose_check, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.02
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **push_to_goal_phase** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_time: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=25.0

## Design Metrics

- **Composite score**: 0.399
- **task_score** (E): 0.775
- **fitness_score**: 0.699  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_from_behind | 1.00 | 1.00 | 0.1067 |
| push_to_goal_phase | 0.67 | 1.00 | 0.1058 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_from_behind | approach | 1.00 / time_limit | (0.516, 0.047, 0.133)→(0.534, 0.074, 0.035) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_to_goal_phase | push | 0.67 / time_limit | (0.505, 0.015, 0.031)→(0.494, -0.085, 0.026) | (0.518, -0.020, 0.025)→(0.498, -0.121, 0.025) | 0.139→0.034 | 1.00 / 2.333 | 1.655 | 24.312 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.987
- lateral_force_integral: None
- approach_alignment: 0.663
- goal_progress: 0.986
- terminal_score: 0.986
- phase_score: 0.810
- phase_breakdown.reach_object_score: 0.116
- phase_breakdown.push_to_goal_score: 0.984

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.880
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.986
- **Median Q (composite search score)**: 0.435
- **K-run variance**: 0.0273
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.228


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `327b95871eb659cd41b4cf66bc0b4dfb3b240662e8501854b46ee2b8b86a04c5`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5ffd2bb280d1d50ec9ffd23c1ed75abf73d645c1d10372a9b5bb6e9fac6e0bf8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90323,"average_solve_count":93.0,"average_success_count":93.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_from_behind.approach_behind_distance":0.11442,"approach_from_behind.approach_speed":0.08705,"approach_from_behind.approach_z_offset":0.01906,"push_to_goal_phase.push_speed":0.11741,"push_to_goal_phase.push_stroke_distance":0.41029,"push_to_goal_phase.push_time":5.69879},"optimized_scores":{"best_composite_score":0.43454,"best_fitness_score":0.73454,"best_task_score":0.81995},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":473.0,"contact_point_centroid":[0.53324,-0.05461,0.03583],"force_p95":18.39644,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.91301,"mean_force":4.35171,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.5299,-0.04273,0.02852]},{"body_a":"world","body_b":"push_box","contact_count":2465.0,"contact_point_centroid":[0.53875,-0.04784,-2e-05],"force_p95":6.25548,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.59688,"mean_force":1.1293,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.55052,0.01577,0.02998]},{"body_a":"world","body_b":"push_box","contact_count":7608.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_from_behind","phase_type":"approach","tcp_position_centroid":[0.53838,0.04161,0.1617]}],"total_contact_groups":3},"final_pose_error":0.32938,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.519,-0.13571,0.0257],"final_tcp_position":[0.51025,-0.09938,0.02737],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":22.91301,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1902.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_from_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7608.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.57681,0.08011,0.0369],"tcp_start":[0.54179,0.04446,0.15522],"tcp_to_object_dist_end":0.11118,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.519,-0.13571,0.0257],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.02379,"object_to_goal_dist_start":0.13211,"object_z_max":0.02596,"peak_contact_force":2.66374,"phase_name":"push_to_goal_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2938.0,"raw_peak_contact_force":22.91301,"subtask_id":"push_to_goal","tcp_end":[0.51025,-0.09938,0.02737],"tcp_start":[0.57681,0.08011,0.0369],"tcp_to_object_dist_end":0.0374,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e094d2c5a71c8b89ef1fa30d7ce553b9c4ed64cd3fbca90620c3ede94e719cec`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83516,"average_solve_count":91.0,"average_success_count":91.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_from_behind.approach_behind_distance":0.11126,"approach_from_behind.approach_speed":0.10703,"approach_from_behind.approach_z_offset":0.01852,"push_to_goal_phase.push_speed":0.13166,"push_to_goal_phase.push_stroke_distance":0.33239,"push_to_goal_phase.push_time":4.30514},"optimized_scores":{"best_composite_score":0.58044,"best_fitness_score":0.88044,"best_task_score":0.98596},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":416.0,"contact_point_centroid":[0.53612,-0.06492,0.02745],"force_p95":20.10895,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.74426,"mean_force":4.94956,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.53772,-0.05312,0.02676]},{"body_a":"world","body_b":"push_box","contact_count":2339.0,"contact_point_centroid":[0.5409,-0.06139,-3e-05],"force_p95":5.82285,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.67105,"mean_force":1.17089,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.56075,-0.00417,0.0281]},{"body_a":"world","body_b":"push_box","contact_count":7564.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_from_behind","phase_type":"approach","tcp_position_centroid":[0.55114,0.03486,0.15408]}],"total_contact_groups":3},"final_pose_error":0.24327,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5001,-0.14822,0.02495],"final_tcp_position":[0.51013,-0.11267,0.02553],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":25.74426,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1891.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_from_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7564.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.59629,0.06387,0.03539],"tcp_start":[0.55919,0.03965,0.13761],"tcp_to_object_dist_end":0.10783,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":923.0,"n_steps_budget":1000.0,"object_pos_end":[0.50028,-0.14795,0.0248],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.00208,"object_to_goal_dist_start":0.12728,"object_z_max":0.02533,"peak_contact_force":2.0,"phase_name":"push_to_goal_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2755.0,"raw_peak_contact_force":25.74426,"subtask_id":"push_to_goal","tcp_end":[0.51013,-0.11267,0.02553],"tcp_start":[0.5102,-0.11256,0.02557],"tcp_to_object_dist_end":0.03664,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0fd7d18e656259f06515eb57b82afa0c0febd9395a43c1a5f926ddaec3767c64`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90598,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_from_behind.approach_behind_distance":0.08441,"approach_from_behind.approach_speed":0.0711,"approach_from_behind.approach_z_offset":0.00852,"push_to_goal_phase.push_speed":0.06309,"push_to_goal_phase.push_stroke_distance":0.37601,"push_to_goal_phase.push_time":5.73599},"optimized_scores":{"best_composite_score":0.18071,"best_fitness_score":0.48071,"best_task_score":0.52018},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":509.0,"contact_point_centroid":[0.45959,-0.01968,0.03938],"force_p95":15.95637,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.27944,"mean_force":4.59256,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.45136,-0.0078,0.02647]},{"body_a":"push_box","body_b":"link7","contact_count":160.0,"contact_point_centroid":[0.48063,0.01396,0.04998],"force_p95":17.90951,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.15614,"mean_force":10.14266,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.43473,0.04768,0.02782]},{"body_a":"world","body_b":"push_box","contact_count":2270.0,"contact_point_centroid":[0.4565,-0.02477,-6e-05],"force_p95":8.52875,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.18129,"mean_force":2.05727,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.43942,0.03246,0.02759]},{"body_a":"world","body_b":"push_box","contact_count":5664.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_from_behind","phase_type":"approach","tcp_position_centroid":[0.46255,0.03972,0.16289]}],"total_contact_groups":4},"final_pose_error":0.33316,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47379,-0.07968,0.02531],"final_tcp_position":[0.4621,-0.04287,0.02572],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":24.27944,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1416.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_from_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5664.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.42902,0.07798,0.03182],"tcp_start":[0.44785,0.05694,0.10697],"tcp_to_object_dist_end":0.0827,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47379,-0.07968,0.02531],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.07504,"object_to_goal_dist_start":0.1564,"object_z_max":0.02581,"peak_contact_force":0.3011,"phase_name":"push_to_goal_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2939.0,"raw_peak_contact_force":24.27944,"subtask_id":"push_to_goal","tcp_end":[0.4621,-0.04287,0.02572],"tcp_start":[0.42902,0.07798,0.03182],"tcp_to_object_dist_end":0.03863,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```