## Search State

- **Seed**: 7
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | descend → push | linear_cartesian | linear_cartesian | position_control | impedance_control | contact_detected | pose_tolerance | 4 | 0.3304 | 0.20 | ❌ rejected |
| 4 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 4 | -0.1966 | 0.00 | ❌ rejected |
| 3 | descend → push | linear_cartesian | linear_cartesian | position_control | impedance_control | contact_detected | pose_tolerance | 5 | 0.2425 | 0.33 | ✅ accepted |
| 2 | descend → push | linear_cartesian | linear_cartesian | position_control | impedance_control | contact_detected | pose_tolerance | 5 | 0.2422 | 0.33 | ✅ accepted |
| 1 | descend → insert → grasp → approach | linear_cartesian | impedance_motion | — | linear_cartesian | position_control | admittance_control | position_control | position_control | contact_detected | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2647 | 0.31 | ❌ rejected |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.330) — your mutation base

```yaml
skill: door_push
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_door
  anchor: object
  offset:
  - 0.0
  - -0.15
  - 0.0
  weight: 0.3
- id: push_open
  metric: goal_progress
  weight: 0.7
phases:
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    entity: door_panel
    offset:
    - 0.0
    - -0.15
    - 0.0
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    desc_y:
      type: scalar
      range:
      - -0.3
      - 0.0
      default: -0.15
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: reach_door
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: door_panel
    offset:
    - 0.0
    - -0.15
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_x
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    force_limit:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 30.0
      binds_to:
      - path: guards.safe_force.threshold
        mode: replace
    push_dist:
      type: scalar
      range:
      - 0.02
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    retry_x:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: retry.offset.x
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: ensure_contact
    when: before_phase
    predicate: contact_detected
    threshold: 0.5
    on_failure: retry
  - id: safe_force
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_open

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=door_panel, offset=[0.0, -0.15, 0.0], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - desc_y: status=consumed; consumers=target.offset.y (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, entity=door_panel, offset=[0.0, -0.15, 0.0], offset_along_axis={axis=world_x, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_limit: status=consumed; consumers=guards.safe_force.threshold (replace)
    - push_dist: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - retry_x: status=consumed; consumers=retry.offset.x (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=ensure_contact, when=before_phase, predicate=contact_detected, on_failure=retry, threshold=0.5
    - id=safe_force, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.330
- **task_score** (E): 0.197
- **fitness_score**: 0.197  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.200

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_1 | 0.67 | 0.67 | 0.1370 |
| push_1 | 0.00 | 0.67 | 0.0003 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_1 | descend | 0.67 / condition_met | (0.100, 0.399, 0.350)→(0.190, 0.336, 0.286) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 3.333 | 10.949 | 222.584 |
| push_1 | push | 0.00 / guard_failure | (0.190, 0.335, 0.284)→(0.190, 0.335, 0.284) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.000 | 0.642 | 108.841 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.589
- arc_quality: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.589
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.589
- **Median Q (composite search score)**: 0.303
- **K-run variance**: 0.0017
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.7
- **Parameters at upper bound**: descend_1.speed
- **Final σ (mean)**: 0.788


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2fa9c04e562df03eff32cc7f63abe386d265bbd85d42dcee2df7f90a42e2de0a`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `fb31b2d7951f101afe3533d0babe40d387e4396f53837e61e543f2cfc46b7e19`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31818,"average_solve_count":22.0,"average_success_count":22.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.speed":0.11873,"push_1.force_limit":15.94982,"push_1.push_dist":0.16235,"push_1.speed":0.02944},"optimized_scores":{"best_composite_score":0.3,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":5.0,"contact_point_centroid":[0.10043,0.18288,0.58454],"force_p95":62.04656,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.643,"mean_force":18.85509,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.13303,0.36052,0.28001]},{"body_a":"world","body_b":"door_panel","contact_count":396.0,"contact_point_centroid":[0.30062,0.18137,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.11561,0.38017,0.31542]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30061,0.18146,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.13295,0.36068,0.28018]}],"total_contact_groups":3},"final_pose_error":0.16223,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.13308,0.36034,0.2798],"hinge_angle":0.04271,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":74.643,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":442.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":4.8188,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":396.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_door","tcp_end":[0.13295,0.36068,0.28018],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.47568,"terminated_normally":true,"termination_reason":"condition_met"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":1.92712,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":74.643,"subtask_id":"push_open","tcp_end":[0.13308,0.36034,0.2798],"tcp_start":[0.13308,0.36038,0.27986],"tcp_to_object_dist_end":0.47523,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2fe1c8aab50c64fd16f940100e2036790f2ea8f75271c649e6989441e8f9191e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5,"average_solve_count":26.0,"average_success_count":26.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.speed":0.07583,"push_1.force_limit":28.79583,"push_1.push_dist":0.16022,"push_1.speed":0.04075},"optimized_scores":{"best_composite_score":0.30254,"best_fitness_score":0.00254,"best_task_score":0.00254},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.09954,0.20365,0.58524],"force_p95":55.18641,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.18641,"mean_force":55.18641,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.13152,0.36221,0.28302]},{"body_a":"door_panel","body_b":"link5","contact_count":4.0,"contact_point_centroid":[0.09962,0.20366,0.58512],"force_p95":24.61267,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.95609,"mean_force":7.23902,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.1316,0.36206,0.2828]},{"body_a":"world","body_b":"door_panel","contact_count":536.0,"contact_point_centroid":[0.29976,0.20195,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.11635,0.37928,0.31385]},{"body_a":"world","body_b":"door_panel","contact_count":12.0,"contact_point_centroid":[0.29976,0.20182,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.1316,0.36205,0.28279]}],"total_contact_groups":4},"final_pose_error":0.16016,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.13162,0.36193,0.28263],"hinge_angle":-0.05907,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":55.18641,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":485.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":28.02931,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":537.0,"raw_peak_contact_force":55.18641,"subtask_id":"reach_door","tcp_end":[0.13157,0.36215,0.28292],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.47802,"terminated_normally":true,"termination_reason":"condition_met"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":16.0,"raw_peak_contact_force":28.95609,"subtask_id":"push_open","tcp_end":[0.13162,0.36193,0.28263],"tcp_start":[0.13162,0.36198,0.28269],"tcp_to_object_dist_end":0.4777,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `356d1c9659b48b76a1cff255b134bf18d0729848f67621b991467785bdaaef44`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.46341,"average_solve_count":41.0,"average_success_count":41.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.speed":0.19999,"push_1.force_limit":27.64933,"push_1.push_dist":0.28997,"push_1.speed":0.03643},"optimized_scores":{"best_composite_score":0.38855,"best_fitness_score":0.58855,"best_task_score":0.58855},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link4","contact_count":646.0,"contact_point_centroid":[0.11193,0.10853,0.63278],"force_p95":508.77578,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":612.56458,"mean_force":423.61569,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.20722,0.32242,0.28546]},{"body_a":"door_panel","body_b":"link4","contact_count":2.0,"contact_point_centroid":[0.13693,0.03221,0.64625],"force_p95":218.08274,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":222.92276,"mean_force":174.52261,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.30568,0.28397,0.29211]},{"body_a":"world","body_b":"door_panel","contact_count":1044.0,"contact_point_centroid":[0.30642,0.15128,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.17617,0.34229,0.29618]}],"total_contact_groups":3},"final_pose_error":0.29022,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.30551,0.28359,0.28998],"hinge_angle":0.43764,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":612.56458,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1690.0,"raw_peak_contact_force":612.56458,"subtask_id":"reach_door","tcp_end":[0.3057,0.28447,0.29615],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.51194,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":222.92276,"subtask_id":"push_open","tcp_end":[0.30551,0.28359,0.28998],"tcp_start":[0.30559,0.28374,0.29077],"tcp_to_object_dist_end":0.50779,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```