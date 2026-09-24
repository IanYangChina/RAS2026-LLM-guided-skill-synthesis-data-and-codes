## Search State

- **Seed**: 2
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.2450 | 0.57 | ✅ accepted |
| 4 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.1753 | 0.54 | ✅ accepted |
| 3 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1958 | 0.52 | ❌ rejected |
| 2 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.1679 | 0.53 | ✅ accepted |
| 1 | approach → align → align → pull → descend → release → grasp → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | — | impedance_motion | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | contact_detected | time_limit | grasp_success | pose_tolerance | 7 | -0.0589 | 0.47 | ✅ accepted |

**Proposal policy**: task_score is 0.57 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: door_push
- target_hinge_angle: 0.524 rad (task success = realised hinge-angle delta ratio; not TCP proximity)
- Goal tolerance: 0.05 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 30.0 N
- Primary evaluation target: **hinge angle delta ratio (realised hinge motion / target_hinge_angle)**

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

## Current Skill (Q=0.245) — your mutation base

```yaml
skill: door_push
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_door
  offset:
  - 0.05
  - 0.0
  - 0.1
  weight: 0.3
- id: push_door
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.05
    - 0.0
    - 0.1
    tolerance: 0.02
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_door
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.02
    - 0.0
    - 0.0
    tolerance: 0.005
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
  subtask_id: reach_door
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
      distance: 0.03
      axis: world_x
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 3.0
      - 20.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_push_dist:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: push_door
- id: push_1
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
      distance: 0.2
      axis: world_y
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.35
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: push_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.05, 0.0, 0.1], tolerance=0.02
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **align_1** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.02, 0.0, 0.0], tolerance=0.005
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_x, distance=0.03, mode=add_to_offset, sign=negative}, tolerance=0.01
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_push_dist: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.245
- **task_score** (E): 0.572
- **fitness_score**: 0.572  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2268 |
| align_1 | 1.00 | 0.33 | 0.0975 |
| contact_1 | 0.33 | 0.33 | 0.0348 |
| push_1 | 1.00 | 0.00 | 0.1090 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.146, 0.199, 0.446) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 15.960 | 28.953 |
| align_1 | align | 1.00 / step_budget | (0.146, 0.199, 0.446)→(0.127, 0.171, 0.355) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 0.000 | 20.426 |
| contact_1 | contact | 0.33 / step_budget | (0.127, 0.171, 0.355)→(0.093, 0.176, 0.351) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 4.372 | 6.305 |
| push_1 | push | 1.00 / step_budget | (0.093, 0.176, 0.351)→(0.098, 0.282, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.00 / 0.000 | 0.000 | 4.380 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.808
- arc_quality: 0.750

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.808
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.808
- **Median Q (composite search score)**: 0.266
- **K-run variance**: 0.0180
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.399


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `7dec7b9d265217827596e50fcdf4f13e307fabe21fe4cab198e2a5d141ff1ba8`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2703841599a88ffb6fe3c9276875d1c87ae4a75b7467b1c48183ebe23e97d755`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34764,"average_solve_count":233.0,"average_success_count":233.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00485,"align_1.lateral_offset_y":-0.00998,"approach_1.speed":0.0709,"contact_1.contact_force_threshold":12.80036,"contact_1.contact_push_dist":0.01606,"push_1.push_distance":0.22028,"push_1.push_speed":0.02482},"optimized_scores":{"best_composite_score":0.26618,"best_fitness_score":0.67618,"best_task_score":0.67618},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":93.0,"contact_point_centroid":[0.17556,0.14706,0.4802],"force_p95":28.87225,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.43034,"mean_force":18.51951,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.14064,0.22121,0.44276]},{"body_a":"door_panel","body_b":"link6","contact_count":141.0,"contact_point_centroid":[0.10055,0.19833,0.54307],"force_p95":24.84841,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.62145,"mean_force":16.58931,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.12705,0.28012,0.42599]},{"body_a":"door_panel","body_b":"link7","contact_count":160.0,"contact_point_centroid":[0.16967,0.11203,0.4391],"force_p95":17.0209,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.68981,"mean_force":13.68775,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.13518,0.18414,0.39749]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.164,0.10264,0.39954],"force_p95":18.9151,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.9151,"mean_force":18.9151,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.1258,0.17094,0.3547]},{"body_a":"world","body_b":"door_panel","contact_count":572.0,"contact_point_centroid":[0.30085,0.19247,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.12046,0.3091,0.40678]},{"body_a":"world","body_b":"door_panel","contact_count":576.0,"contact_point_centroid":[0.3093,0.13897,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.13539,0.18444,0.39846]},{"body_a":"world","body_b":"door_panel","contact_count":392.0,"contact_point_centroid":[0.3106,0.13498,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10728,0.17381,0.35109]},{"body_a":"world","body_b":"door_panel","contact_count":472.0,"contact_point_centroid":[0.31019,0.13618,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09354,0.28409,0.34775]}],"total_contact_groups":8},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09831,0.38064,0.34752],"hinge_angle":0.27111,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":31.43034,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":560.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":16.21264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":806.0,"raw_peak_contact_force":31.43034,"subtask_id":"reach_door","tcp_end":[0.14579,0.19916,0.44616],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.50988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":566.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":736.0,"raw_peak_contact_force":20.68981,"subtask_id":"reach_door","tcp_end":[0.1258,0.17094,0.3547],"tcp_start":[0.14579,0.19916,0.44616],"tcp_to_object_dist_end":0.41335,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":378.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":393.0,"raw_peak_contact_force":18.9151,"subtask_id":"push_door","tcp_end":[0.08819,0.17776,0.34876],"tcp_start":[0.1258,0.17094,0.3547],"tcp_to_object_dist_end":0.40126,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":550.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":472.0,"raw_peak_contact_force":0.0,"subtask_id":"push_door","tcp_end":[0.09831,0.38064,0.34752],"tcp_start":[0.08819,0.17776,0.34876],"tcp_to_object_dist_end":0.52471,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0106e02cd8847cdbc8cb80732350ffe717d1fc22c509bf8221b103cb157c8e2d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26923,"average_solve_count":182.0,"average_success_count":182.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.0099,"align_1.lateral_offset_y":-0.00995,"approach_1.speed":0.01163,"contact_1.contact_force_threshold":18.64903,"contact_1.contact_push_dist":0.03937,"push_1.push_distance":0.05491,"push_1.push_speed":0.07805},"optimized_scores":{"best_composite_score":0.39779,"best_fitness_score":0.80779,"best_task_score":0.80779},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":162.0,"contact_point_centroid":[0.10065,0.20078,0.54188],"force_p95":22.33484,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.02931,"mean_force":16.36529,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.12638,0.28273,0.42478]},{"body_a":"door_panel","body_b":"link7","contact_count":99.0,"contact_point_centroid":[0.1755,0.14714,0.48021],"force_p95":24.51096,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.18583,"mean_force":18.10264,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.14056,0.22126,0.44276]},{"body_a":"door_panel","body_b":"link7","contact_count":166.0,"contact_point_centroid":[0.17189,0.11188,0.44033],"force_p95":17.58997,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.28971,"mean_force":13.89721,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.1379,0.18445,0.39907]},{"body_a":"world","body_b":"door_panel","contact_count":556.0,"contact_point_centroid":[0.3009,0.19284,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.12153,0.30415,0.40941]},{"body_a":"world","body_b":"door_panel","contact_count":592.0,"contact_point_centroid":[0.30935,0.13882,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.13845,0.18543,0.40234]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.1679,0.10191,0.39908],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.13042,0.17089,0.35467]},{"body_a":"world","body_b":"door_panel","contact_count":500.0,"contact_point_centroid":[0.31079,0.13443,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09631,0.17419,0.35082]},{"body_a":"world","body_b":"door_panel","contact_count":140.0,"contact_point_centroid":[0.31052,0.13522,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.07749,0.1977,0.34849]}],"total_contact_groups":8},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.08981,0.21795,0.34862],"hinge_angle":0.27865,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":27.02931,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":589.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":15.22925,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":817.0,"raw_peak_contact_force":27.02931,"subtask_id":"reach_door","tcp_end":[0.14582,0.19879,0.44621],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.50979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":562.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":758.0,"raw_peak_contact_force":19.28971,"subtask_id":"reach_door","tcp_end":[0.13051,0.17099,0.35483],"tcp_start":[0.14582,0.19879,0.44621],"tcp_to_object_dist_end":0.41494,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":533.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":501.0,"raw_peak_contact_force":0.0,"subtask_id":"push_door","tcp_end":[0.06547,0.17811,0.34867],"tcp_start":[0.13051,0.17099,0.35483],"tcp_to_object_dist_end":0.39696,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":124.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":140.0,"raw_peak_contact_force":0.0,"subtask_id":"push_door","tcp_end":[0.08981,0.21795,0.34862],"tcp_start":[0.06547,0.17811,0.34867],"tcp_to_object_dist_end":0.42084,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7bc2b9dece282a8a9fabbafdd09525b72694e2e86202e4d7347d50b4ed50bf95`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.70335,"average_solve_count":209.0,"average_success_count":209.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00346,"align_1.lateral_offset_y":-0.00894,"approach_1.speed":0.05999,"contact_1.contact_force_threshold":6.0743,"contact_1.contact_push_dist":0.03414,"push_1.push_distance":0.08539,"push_1.push_speed":0.01924},"optimized_scores":{"best_composite_score":0.07092,"best_fitness_score":0.23092,"best_task_score":0.23092},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":57.0,"contact_point_centroid":[0.176,0.13783,0.48189],"force_p95":26.84113,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.39867,"mean_force":18.1556,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.14269,0.21261,0.44454]},{"body_a":"door_panel","body_b":"link7","contact_count":152.0,"contact_point_centroid":[0.16917,0.11261,0.43927],"force_p95":17.05781,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.29975,"mean_force":13.65012,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.13453,0.18462,0.39762]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.16302,0.10378,0.39948],"force_p95":12.93127,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.1398,"mean_force":8.06475,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.12447,0.17181,0.35453]},{"body_a":"world","body_b":"door_panel","contact_count":572.0,"contact_point_centroid":[0.304,0.15904,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.11935,0.3142,0.40332]},{"body_a":"world","body_b":"door_panel","contact_count":572.0,"contact_point_centroid":[0.30912,0.13952,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.13521,0.18548,0.40054]},{"body_a":"world","body_b":"door_panel","contact_count":256.0,"contact_point_centroid":[0.31037,0.13565,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.11542,0.20543,0.35163]}],"total_contact_groups":6},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.1047,0.24611,0.34924],"hinge_angle":0.27566,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":28.39867,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":572.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":16.43943,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":629.0,"raw_peak_contact_force":28.39867,"subtask_id":"reach_door","tcp_end":[0.14582,0.19907,0.44629],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.50997,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":566.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":724.0,"raw_peak_contact_force":21.29975,"subtask_id":"reach_door","tcp_end":[0.12451,0.17189,0.35469],"tcp_start":[0.14582,0.19907,0.44629],"tcp_to_object_dist_end":0.41334,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.11514,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"push_door","tcp_end":[0.12449,0.17185,0.3546],"tcp_start":[0.12451,0.17189,0.35469],"tcp_to_object_dist_end":0.41324,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":228.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":259.0,"raw_peak_contact_force":13.1398,"subtask_id":"push_door","tcp_end":[0.1047,0.24611,0.34924],"tcp_start":[0.12449,0.17185,0.3546],"tcp_to_object_dist_end":0.43989,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```