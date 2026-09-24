## Search State

- **Seed**: 7
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | release → approach → push | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | 6 | 0.4733 | 0.89 | ❌ rejected |
| 3 | release → approach → push | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | 5 | 0.5517 | 0.94 | ✅ accepted |
| 2 | release → approach → push | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | 4 | -0.0730 | 0.00 | ✅ accepted |
| 1 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.3400 | 0.00 | ❌ rejected |
| 0 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.3400 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.89 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.473) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: contact_object
  anchor: object
  weight: 0.3
- id: reach_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    max_time:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: duration.max_time
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: approach_behind
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
    - 0.0
    offset_along_axis:
      distance: 0.02
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.005
    orientation:
      mode: none
  parameters:
    behind_distance:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.02
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: contact_object
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.3
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    distance:
      type: scalar
      range:
      - 0.1
      - 0.45
      default: 0.3
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (replace)
  - retries: max_attempts=0, strategy=repeat
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.02, mode=add_to_offset, sign=negative}, tolerance=0.005
  - orientation: mode=none
  - parameter_bindings:
    - behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.3, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.473
- **task_score** (E): 0.886
- **fitness_score**: 0.803  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| release_1 | 1.00 | 1.00 | 0.0085 |
| approach_behind | 1.00 | 1.00 | 0.2710 |
| push_to_goal | 1.00 | 1.00 | 0.2007 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| release_1 | release | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, -0.000, 0.293) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| approach_behind | approach | 1.00 / step_budget | (0.496, -0.000, 0.293)→(0.517, 0.067, 0.036) | (0.513, 0.027, 0.025)→(0.514, 0.026, 0.025) | 0.180→0.179 | 1.00 / 3.667 | 0.174 | 163.251 |
| push_to_goal | push | 1.00 / time_limit | (0.517, 0.067, 0.036)→(0.497, -0.130, 0.033) | (0.514, 0.026, 0.025)→(0.507, -0.161, 0.029) | 0.179→0.020 | 1.00 / 2.667 | 25.232 | 54.478 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.707
- goal_progress: 0.949
- terminal_score: 0.949
- phase_score: 0.796
- phase_breakdown.contact_object_score: 0.440
- phase_breakdown.reach_goal_score: 0.949

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.857
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.949
- **Median Q (composite search score)**: 0.457
- **K-run variance**: 0.0015
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.166


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `75e2389a1a667086aa2b9c0de482ff37adf5571150b90a83772692baadf8b52e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `154c216c563de6b8ee153943e5b668ca6d0c7dfd9253696b060f91a67dca06ec`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.12644,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.behind_distance":0.04938,"approach_behind.speed":0.11287,"push_to_goal.distance":0.30469,"push_to_goal.max_time":1.45043,"push_to_goal.speed":0.15164,"release_1.max_time":0.33048},"optimized_scores":{"best_composite_score":0.43568,"best_fitness_score":0.76568,"best_task_score":0.84398},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":806.0,"contact_point_centroid":[0.51481,-0.04253,0.04699],"force_p95":63.07673,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":95.21455,"mean_force":18.59965,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50127,-0.0328,0.02792]},{"body_a":"push_box","body_b":"link7","contact_count":453.0,"contact_point_centroid":[0.53237,-0.08935,0.05806],"force_p95":63.83229,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":94.3609,"mean_force":29.96558,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49839,-0.08082,0.02858]},{"body_a":"world","body_b":"push_box","contact_count":1459.0,"contact_point_centroid":[0.5261,-0.06855,-7e-05],"force_p95":47.63058,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.99879,"mean_force":15.83455,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50248,-0.02097,0.02828]},{"body_a":"world","body_b":"push_box","contact_count":800.0,"contact_point_centroid":[0.51501,0.04767,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49754,-3e-05,0.29537]},{"body_a":"world","body_b":"push_box","contact_count":3628.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50421,0.04566,0.16097]}],"total_contact_groups":5},"final_pose_error":0.07263,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52549,-0.16606,0.03199],"final_tcp_position":[0.49684,-0.13962,0.03079],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":95.21455,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49646,-4e-05,0.29284],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.2727,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":907.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3628.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_object","tcp_end":[0.51363,0.09184,0.03173],"tcp_start":[0.49646,-4e-05,0.29284],"tcp_to_object_dist_end":0.04471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52549,-0.16606,0.03199],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.03093,"object_to_goal_dist_start":0.19823,"object_z_max":0.03197,"peak_contact_force":71.46122,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2718.0,"raw_peak_contact_force":95.21455,"subtask_id":"reach_goal","tcp_end":[0.49684,-0.13962,0.03079],"tcp_start":[0.51363,0.09184,0.03173],"tcp_to_object_dist_end":0.03901,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93258,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.behind_distance":0.0421,"approach_behind.speed":0.10961,"push_to_goal.distance":0.3525,"push_to_goal.max_time":1.67841,"push_to_goal.speed":0.14058,"release_1.max_time":0.29963},"optimized_scores":{"best_composite_score":0.52719,"best_fitness_score":0.85719,"best_task_score":0.94901},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":88.0,"contact_point_centroid":[0.48603,0.08639,0.04701],"force_p95":236.68895,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":245.98595,"mean_force":162.28914,"phase_index":1.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.47767,0.09247,0.04965]},{"body_a":"world","body_b":"push_box","contact_count":3527.0,"contact_point_centroid":[0.47937,0.05962,-5e-05],"force_p95":0.8354,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":207.62158,"mean_force":4.3154,"phase_index":1.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.484,0.0471,0.16275]},{"body_a":"push_box","body_b":"link7","contact_count":146.0,"contact_point_centroid":[0.526,-0.08607,0.05776],"force_p95":32.4255,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.69347,"mean_force":13.87228,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48988,-0.07504,0.03104]},{"body_a":"attachment","body_b":"push_box","contact_count":729.0,"contact_point_centroid":[0.49396,-0.02091,0.04488],"force_p95":30.3159,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.46099,"mean_force":8.57636,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48307,-0.01006,0.03064]},{"body_a":"world","body_b":"push_box","contact_count":1271.0,"contact_point_centroid":[0.50144,-0.04789,-9e-05],"force_p95":21.66602,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.30242,"mean_force":6.78185,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48198,0.0038,0.03093]},{"body_a":"world","body_b":"push_box","contact_count":800.0,"contact_point_centroid":[0.47924,0.05847,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49754,-3e-05,0.29537]}],"total_contact_groups":6},"final_pose_error":0.13297,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50805,-0.15494,0.02999],"final_tcp_position":[0.49338,-0.12078,0.03021],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":245.98595,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49646,-4e-05,0.29284],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.27471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":926.0,"n_steps_budget":1000.0,"object_pos_end":[0.48027,0.05687,0.02453],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20781,"object_to_goal_dist_start":0.2095,"object_z_max":0.02624,"peak_contact_force":0.27417,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3615.0,"raw_peak_contact_force":245.98595,"subtask_id":"contact_object","tcp_end":[0.47626,0.09827,0.03465],"tcp_start":[0.49646,-4e-05,0.29284],"tcp_to_object_dist_end":0.04281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50805,-0.15494,0.02999],"object_pos_start":[0.48027,0.05687,0.02453],"object_to_goal_dist_end":0.01068,"object_to_goal_dist_start":0.20781,"object_z_max":0.03155,"peak_contact_force":0.35114,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2146.0,"raw_peak_contact_force":50.69347,"subtask_id":"reach_goal","tcp_end":[0.49338,-0.12078,0.03021],"tcp_start":[0.47626,0.09827,0.03465],"tcp_to_object_dist_end":0.03718,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.39726,"average_solve_count":73.0,"average_success_count":73.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.behind_distance":0.03414,"approach_behind.speed":0.15478,"push_to_goal.distance":0.18181,"push_to_goal.max_time":1.51262,"push_to_goal.speed":0.09182,"release_1.max_time":0.23914},"optimized_scores":{"best_composite_score":0.45717,"best_fitness_score":0.78717,"best_task_score":0.86558},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":85.0,"contact_point_centroid":[0.5607,0.00025,0.04662],"force_p95":243.38497,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":243.52251,"mean_force":175.78798,"phase_index":1.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.55232,0.00763,0.04765]},{"body_a":"world","body_b":"push_box","contact_count":3186.0,"contact_point_centroid":[0.54537,-0.0252,-4e-05],"force_p95":12.93831,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":236.47188,"mean_force":4.98025,"phase_index":1.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52173,0.00308,0.1635]},{"body_a":"attachment","body_b":"push_box","contact_count":598.0,"contact_point_centroid":[0.52582,-0.07105,0.03803],"force_p95":13.9581,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.52481,"mean_force":4.78327,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52889,-0.05954,0.03707]},{"body_a":"world","body_b":"push_box","contact_count":1900.0,"contact_point_centroid":[0.51538,-0.09938,-8e-05],"force_p95":5.57984,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.85688,"mean_force":1.86611,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52907,-0.05936,0.0372]},{"body_a":"world","body_b":"push_box","contact_count":800.0,"contact_point_centroid":[0.54443,-0.02558,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49754,-3e-05,0.29537]}],"total_contact_groups":5},"final_pose_error":0.03236,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48819,-0.16326,0.02504],"final_tcp_position":[0.50218,-0.1292,0.03763],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":243.52251,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49646,-4e-05,0.29284],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.27331,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":825.0,"n_steps_budget":1000.0,"object_pos_end":[0.54694,-0.02766,0.02453],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13103,"object_to_goal_dist_start":0.13211,"object_z_max":0.02501,"peak_contact_force":0.00285,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3271.0,"raw_peak_contact_force":243.52251,"subtask_id":"contact_object","tcp_end":[0.55968,0.00951,0.04208],"tcp_start":[0.49646,-4e-05,0.29284],"tcp_to_object_dist_end":0.04304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48819,-0.16326,0.02504],"object_pos_start":[0.54694,-0.02766,0.02453],"object_to_goal_dist_end":0.01776,"object_to_goal_dist_start":0.13103,"object_z_max":0.02824,"peak_contact_force":3.8842,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2498.0,"raw_peak_contact_force":17.52481,"subtask_id":"reach_goal","tcp_end":[0.50218,-0.1292,0.03763],"tcp_start":[0.55968,0.00951,0.04208],"tcp_to_object_dist_end":0.03892,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```