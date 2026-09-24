## Search State

- **Seed**: 2
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.6971 | 0.86 | ✅ accepted |
| 8 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.3778 | 0.62 | ❌ rejected |
| 7 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.3809 | 0.62 | ✅ accepted |
| 6 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.2367 | 0.53 | ❌ rejected |
| 5 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.2450 | 0.57 | ✅ accepted |

**Proposal policy**: task_score is 0.86 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.697) — your mutation base

```yaml
skill: door_push
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_door
  anchor: object
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
    anchor: body
    entity: door_panel
    offset:
    - -0.35
    - -0.02
    - 0.45
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
    anchor: body
    entity: door_panel
    offset:
    - -0.38
    - -0.02
    - 0.35
    tolerance: 0.005
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
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
    anchor: body
    entity: door_panel
    offset:
    - -0.4
    - -0.02
    - 0.35
    offset_along_axis:
      distance: 0.06
      axis: world_x
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 25.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_push_dist:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.06
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
    anchor: body
    entity: door_panel
    offset:
    - -0.4
    - -0.02
    - 0.35
    offset_along_axis:
      distance: 0.25
      axis: world_y
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.25
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
  - target: source=yaml, anchor=body, entity=door_panel, offset=[-0.35, -0.02, 0.45], tolerance=0.02
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **align_1** (`align`)
  - target: source=yaml, anchor=body, entity=door_panel, offset=[-0.38, -0.02, 0.35], tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=body, entity=door_panel, offset=[-0.4, -0.02, 0.35], offset_along_axis={axis=world_x, distance=0.06, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_push_dist: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=body, entity=door_panel, offset=[-0.4, -0.02, 0.35], offset_along_axis={axis=world_y, distance=0.25, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.697
- **task_score** (E): 0.857
- **fitness_score**: 0.857  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2268 |
| align_1 | 0.00 | 1.00 | 0.1180 |
| contact_1 | 1.00 | 1.00 | 0.0003 |
| push_1 | 0.00 | 0.67 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.146, 0.199, 0.446) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 11.254 | 31.399 |
| align_1 | align | 0.00 / step_budget | (0.146, 0.199, 0.446)→(0.111, 0.114, 0.373) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.333 | 309.892 | 692.174 |
| contact_1 | contact | 1.00 / force_exceeded | (0.111, 0.114, 0.373)→(0.111, 0.114, 0.373) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.333 | 408.739 | 408.739 |
| push_1 | push | 0.00 / guard_failure | (0.111, 0.114, 0.373)→(0.111, 0.113, 0.372) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 1.000 | 0.304 | 422.056 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.500

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.840
- **K-run variance**: 0.0408
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.327


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93636,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00516,"align_1.lateral_offset_y":0.00907,"approach_1.speed":0.05894,"contact_1.contact_force_threshold":5.50805,"contact_1.contact_push_dist":0.05021,"push_1.push_distance":0.30121,"push_1.push_speed":0.03513},"optimized_scores":{"best_composite_score":0.84,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link2","body_b":"link5","contact_count":464.0,"contact_point_centroid":[-0.01006,0.12175,0.34305],"force_p95":463.73912,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":718.03158,"mean_force":302.87108,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.11974,0.11406,0.38424]},{"body_a":"door_panel","body_b":"link4","contact_count":89.0,"contact_point_centroid":[0.132,0.04414,0.64841],"force_p95":480.26637,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":544.77442,"mean_force":335.64875,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.11443,0.11795,0.37946]},{"body_a":"link2","body_b":"link5","contact_count":1.0,"contact_point_centroid":[-0.00871,0.11711,0.33409],"force_p95":392.15233,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":392.15233,"mean_force":392.15233,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.11117,0.10611,0.36987]},{"body_a":"link2","body_b":"link5","contact_count":3.0,"contact_point_centroid":[-0.00863,0.1171,0.33383],"force_p95":259.74702,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":261.93267,"mean_force":235.33437,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.11138,0.10607,0.36933]},{"body_a":"door_panel","body_b":"link7","contact_count":43.0,"contact_point_centroid":[0.19722,0.09416,0.36569],"force_p95":100.23358,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":107.08572,"mean_force":56.62731,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.12471,0.11832,0.35346]},{"body_a":"door_panel","body_b":"link7","contact_count":94.0,"contact_point_centroid":[0.17553,0.14709,0.48022],"force_p95":27.79874,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.4753,"mean_force":18.46341,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.1406,0.22123,0.44277]},{"body_a":"door_panel","body_b":"link6","contact_count":141.0,"contact_point_centroid":[0.10055,0.19816,0.54312],"force_p95":23.71676,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.94032,"mean_force":16.73831,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.12706,0.27993,0.42608]},{"body_a":"world","body_b":"door_panel","contact_count":640.0,"contact_point_centroid":[0.30081,0.19212,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.12097,0.30674,0.40832]},{"body_a":"world","body_b":"door_panel","contact_count":488.0,"contact_point_centroid":[0.31809,0.11656,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.11989,0.11734,0.38206]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.32405,0.10439,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.11144,0.10603,0.36912]}],"total_contact_groups":10},"final_pose_error":0.3759,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.11144,0.10597,0.36899],"hinge_angle":0.44815,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":718.03158,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":576.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":875.0,"raw_peak_contact_force":31.4753,"subtask_id":"reach_door","tcp_end":[0.14576,0.19913,0.44617],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.50987,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":520.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":334.4586,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1084.0,"raw_peak_contact_force":718.03158,"subtask_id":"reach_door","tcp_end":[0.11117,0.10611,0.36987],"tcp_start":[0.14576,0.19913,0.44617],"tcp_to_object_dist_end":0.40053,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":392.15233,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":392.15233,"subtask_id":"push_door","tcp_end":[0.1113,0.1061,0.36956],"tcp_start":[0.11117,0.10611,0.36987],"tcp_to_object_dist_end":0.40028,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.70711,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":7.0,"raw_peak_contact_force":261.93267,"subtask_id":"push_door","tcp_end":[0.11144,0.10597,0.36899],"tcp_start":[0.11144,0.10603,0.36912],"tcp_to_object_dist_end":0.39976,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0106e02cd8847cdbc8cb80732350ffe717d1fc22c509bf8221b103cb157c8e2d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.10909,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00124,"align_1.lateral_offset_y":0.00017,"approach_1.speed":0.05937,"contact_1.contact_force_threshold":9.32041,"contact_1.contact_push_dist":0.06796,"push_1.push_distance":0.17366,"push_1.push_speed":0.04613},"optimized_scores":{"best_composite_score":0.84,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link2","body_b":"link5","contact_count":1.0,"contact_point_centroid":[-0.00945,0.12422,0.34133],"force_p95":782.79309,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":782.79309,"mean_force":782.79309,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10836,0.12733,0.37952]},{"body_a":"link2","body_b":"link5","contact_count":1.0,"contact_point_centroid":[-0.00957,0.12416,0.34125],"force_p95":702.81985,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":702.81985,"mean_force":702.81985,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10825,0.12735,0.3795]},{"body_a":"link2","body_b":"link5","contact_count":467.0,"contact_point_centroid":[-0.01504,0.12243,0.34515],"force_p95":382.71114,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":697.17007,"mean_force":301.29339,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.11431,0.1177,0.38357]},{"body_a":"door_panel","body_b":"link4","contact_count":112.0,"contact_point_centroid":[0.12968,0.04949,0.65107],"force_p95":421.87029,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":539.38445,"mean_force":308.11581,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.10747,0.1308,0.37959]},{"body_a":"door_panel","body_b":"link4","contact_count":3.0,"contact_point_centroid":[0.1319,0.04373,0.65312],"force_p95":270.34836,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":271.53769,"mean_force":257.52329,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10857,0.12737,0.37956]},{"body_a":"door_panel","body_b":"link4","contact_count":1.0,"contact_point_centroid":[0.13178,0.04407,0.65307],"force_p95":270.59231,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":270.59231,"mean_force":270.59231,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10825,0.12735,0.3795]},{"body_a":"door_panel","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.20031,0.11368,0.3712],"force_p95":68.17041,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.86359,"mean_force":48.37454,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.13156,0.1266,0.34086]},{"body_a":"door_panel","body_b":"link6","contact_count":154.0,"contact_point_centroid":[0.10065,0.20079,0.54189],"force_p95":25.33425,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.60908,"mean_force":16.82025,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.1264,0.28275,0.42477]},{"body_a":"door_panel","body_b":"link7","contact_count":93.0,"contact_point_centroid":[0.17552,0.14725,0.4802],"force_p95":27.34093,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.53436,"mean_force":18.66678,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.14057,0.22136,0.44275]},{"body_a":"world","body_b":"door_panel","contact_count":584.0,"contact_point_centroid":[0.30088,0.19276,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.12183,0.30288,0.41041]},{"body_a":"world","body_b":"door_panel","contact_count":496.0,"contact_point_centroid":[0.3162,0.12104,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.11819,0.12437,0.3803]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.31979,0.11268,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.1086,0.12742,0.37958]}],"total_contact_groups":12},"final_pose_error":0.22859,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10886,0.12717,0.37958],"hinge_angle":0.40234,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":782.79309,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":576.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":16.87151,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":831.0,"raw_peak_contact_force":32.60908,"subtask_id":"reach_door","tcp_end":[0.14577,0.19907,0.44619],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.50986,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":522.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":298.2163,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1100.0,"raw_peak_contact_force":697.17007,"subtask_id":"reach_door","tcp_end":[0.10825,0.12735,0.3795],"tcp_start":[0.14577,0.19907,0.44619],"tcp_to_object_dist_end":0.41467,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":702.81985,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":702.81985,"subtask_id":"push_door","tcp_end":[0.10836,0.12733,0.37952],"tcp_start":[0.10825,0.12735,0.3795],"tcp_to_object_dist_end":0.41472,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.2049,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":782.79309,"subtask_id":"push_door","tcp_end":[0.10886,0.12717,0.37958],"tcp_start":[0.10875,0.12737,0.3796],"tcp_to_object_dist_end":0.41485,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7bc2b9dece282a8a9fabbafdd09525b72694e2e86202e4d7347d50b4ed50bf95`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.1028,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00516,"align_1.lateral_offset_y":0.00846,"approach_1.speed":0.06116,"contact_1.contact_force_threshold":13.58468,"contact_1.contact_push_dist":0.05998,"push_1.push_distance":0.32875,"push_1.push_speed":0.04559},"optimized_scores":{"best_composite_score":0.41126,"best_fitness_score":0.57126,"best_task_score":0.57126},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link2","body_b":"link5","contact_count":456.0,"contact_point_centroid":[-0.01043,0.12188,0.34375],"force_p95":461.67125,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":661.31887,"mean_force":310.53152,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.11956,0.11393,0.38406]},{"body_a":"door_panel","body_b":"link4","contact_count":87.0,"contact_point_centroid":[0.13301,0.04169,0.64926],"force_p95":409.27641,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":547.81495,"mean_force":317.59249,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.11494,0.11862,0.37853]},{"body_a":"link2","body_b":"link5","contact_count":1.0,"contact_point_centroid":[-0.00784,0.11774,0.33405],"force_p95":221.44262,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":221.44262,"mean_force":221.44262,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.11228,0.10733,0.36922]},{"body_a":"link2","body_b":"link5","contact_count":1.0,"contact_point_centroid":[-0.00782,0.11774,0.33418],"force_p95":131.24581,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":131.24581,"mean_force":131.24581,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.11224,0.10739,0.36954]},{"body_a":"door_panel","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.20289,0.1111,0.36723],"force_p95":70.34419,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":71.85559,"mean_force":49.3175,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.13211,0.122,0.33873]},{"body_a":"door_panel","body_b":"link7","contact_count":57.0,"contact_point_centroid":[0.17602,0.13761,0.48192],"force_p95":28.2213,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.11358,"mean_force":18.34411,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.14275,0.2124,0.44457]},{"body_a":"world","body_b":"door_panel","contact_count":592.0,"contact_point_centroid":[0.30402,0.15892,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.12022,0.31043,0.4048]},{"body_a":"world","body_b":"door_panel","contact_count":472.0,"contact_point_centroid":[0.31797,0.11693,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.12012,0.12101,0.38092]}],"total_contact_groups":8},"final_pose_error":0.40233,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.11237,0.10705,0.36866],"hinge_angle":0.454,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":661.31887,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":569.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":16.8893,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":649.0,"raw_peak_contact_force":30.11358,"subtask_id":"reach_door","tcp_end":[0.14589,0.19885,0.44632],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.50992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":520.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":297.00081,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1042.0,"raw_peak_contact_force":661.31887,"subtask_id":"reach_door","tcp_end":[0.11224,0.10739,0.36954],"tcp_start":[0.14589,0.19885,0.44632],"tcp_to_object_dist_end":0.40086,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":131.24581,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":131.24581,"subtask_id":"push_door","tcp_end":[0.11228,0.10733,0.36922],"tcp_start":[0.11224,0.10739,0.36954],"tcp_to_object_dist_end":0.40057,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":221.44262,"subtask_id":"push_door","tcp_end":[0.11237,0.10705,0.36866],"tcp_start":[0.11233,0.10716,0.36879],"tcp_to_object_dist_end":0.39999,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```