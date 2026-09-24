## Search State

- **Seed**: 5
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.0967 | 0.00 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.9533 | 1.00 | ❌ rejected |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.9533 | 1.00 | ✅ accepted |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.6200 | 1.00 | ❌ rejected |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.6200 | 1.00 | ❌ rejected |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.097) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: tcp_contact
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: hinge_progress
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach_1
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.5
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: approach_pose_guard
    when: after_phase
    predicate: pose_within_tolerance
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: tcp_contact
- id: contact_1
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.05
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_x
      tolerance: 0.1
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_pose_tol:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: hinge_progress

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=approach_pose_guard, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=reduce_speed
- **contact_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.05
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_x, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_pose_tol: status=consumed; consumers=termination.pose_tolerance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.097
- **task_score** (E): 0.000
- **fitness_score**: 0.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

**⚠ Warning**: CMA-ES stagnated + low fitness_score → structure may be fundamentally incompatible with task

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1238 |
| contact_1 | 1.00 | 1.00 | 0.0007 |
| push_1 | 0.00 | 1.00 | 0.1370 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (-0.110, -0.105, 0.392)→(-0.071, -0.143, 0.374) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.667 | 229.555 | 868.614 |
| contact_1 | descend | 1.00 / force_exceeded | (-0.071, -0.143, 0.374)→(-0.070, -0.143, 0.373) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.000 | 265.184 | 265.184 |
| push_1 | push | 0.00 / step_budget | (-0.070, -0.143, 0.373)→(-0.025, -0.207, 0.262) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.333 | 96.707 | 726.680 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.000
- arc_quality: 0.333

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.097
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.267


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `e036e59174e9f4dc4d090dc26b64c24f51b2862ad33098baa3e34b1ab5217b2c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `121441f93055d9c3a0317d86ccf3c4d50a1368e9262fdd196bc29f47a537ab6f`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.59524,"average_solve_count":84.0,"average_success_count":84.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.32875,"approach_1.approach_speed":0.54943,"approach_1.arc_height":0.09076,"contact_1.contact_force_threshold":18.039,"contact_1.contact_speed":0.02909,"push_1.push_distance":0.31042,"push_1.push_pose_tol":0.03686,"push_1.push_speed":0.1192},"optimized_scores":{"best_composite_score":-0.09667,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link2","body_b":"link5","contact_count":759.0,"contact_point_centroid":[-0.07299,-0.05314,0.3447],"force_p95":641.64521,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1296.39298,"mean_force":292.63557,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.05222,0.00281,0.48074]},{"body_a":"link2","body_b":"link7","contact_count":116.0,"contact_point_centroid":[-0.04107,-0.10422,0.37323],"force_p95":946.54545,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1109.03498,"mean_force":462.38536,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.04072,-0.09456,0.43104]},{"body_a":"link2","body_b":"link5","contact_count":581.0,"contact_point_centroid":[-0.02664,-0.09355,0.2849],"force_p95":216.22061,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":540.75538,"mean_force":151.28188,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[-0.03861,-0.18114,0.3862]},{"body_a":"link2","body_b":"link7","contact_count":936.0,"contact_point_centroid":[-0.03334,-0.12168,0.33296],"force_p95":388.79371,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":484.59653,"mean_force":304.12209,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[-0.04308,-0.16517,0.39947]},{"body_a":"link2","body_b":"link5","contact_count":1.0,"contact_point_centroid":[-0.05244,-0.09559,0.29104],"force_p95":350.192,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":350.192,"mean_force":350.192,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[-0.05853,-0.13035,0.4211]},{"body_a":"link2","body_b":"link7","contact_count":1.0,"contact_point_centroid":[-0.04124,-0.11956,0.35071],"force_p95":120.07552,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":120.07552,"mean_force":120.07552,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[-0.05853,-0.13035,0.4211]},{"body_a":"world","body_b":"door_panel","contact_count":1200.0,"contact_point_centroid":[0.30211,0.16933,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.02462,0.01883,0.45869]},{"body_a":"world","body_b":"door_panel","contact_count":948.0,"contact_point_centroid":[0.30196,0.17035,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[-0.04296,-0.1656,0.40028]}],"total_contact_groups":8},"final_pose_error":0.35597,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[-0.03397,-0.19085,0.34909],"hinge_angle":0.09628,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1296.39298,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1142.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":263.71546,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2075.0,"raw_peak_contact_force":1296.39298,"subtask_id":"tcp_contact","tcp_end":[-0.05853,-0.13035,0.4211],"tcp_start":[-0.07421,-0.24471,0.45058],"tcp_to_object_dist_end":0.44468,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":350.192,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":350.192,"tcp_end":[-0.05868,-0.13075,0.42095],"tcp_start":[-0.05853,-0.13035,0.4211],"tcp_to_object_dist_end":0.44467,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":242.28597,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2465.0,"raw_peak_contact_force":540.75538,"subtask_id":"hinge_progress","tcp_end":[-0.03397,-0.19085,0.34909],"tcp_start":[-0.05868,-0.13075,0.42095],"tcp_to_object_dist_end":0.3993,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fbf559b1c4ad02fb5807d56e72eb3a3daf90ab4647e10f958130a5b70ea34720`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.51685,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24115,"approach_1.approach_speed":0.62138,"approach_1.arc_height":0.08014,"contact_1.contact_force_threshold":14.59414,"contact_1.contact_speed":0.05876,"push_1.push_distance":0.18145,"push_1.push_pose_tol":0.04198,"push_1.push_speed":0.07812},"optimized_scores":{"best_composite_score":-0.09667,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link1","body_b":"link5","contact_count":232.0,"contact_point_centroid":[-0.0157,-0.05248,0.19198],"force_p95":712.22728,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":726.3418,"mean_force":556.75576,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[-0.03699,-0.18187,0.29823]},{"body_a":"link2","body_b":"link7","contact_count":561.0,"contact_point_centroid":[-0.08242,-0.07954,0.35096],"force_p95":407.30319,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":668.45562,"mean_force":274.61649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.10286,-0.05283,0.38319]},{"body_a":"link1","body_b":"link5","contact_count":59.0,"contact_point_centroid":[-0.02588,-0.04753,0.20719],"force_p95":568.84603,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":644.80318,"mean_force":458.15059,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.08213,-0.14732,0.35508]},{"body_a":"link2","body_b":"link5","contact_count":150.0,"contact_point_centroid":[-0.08705,0.07982,0.36105],"force_p95":557.06659,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":630.50507,"mean_force":312.1876,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.0248,0.26956,0.41466]},{"body_a":"link2","body_b":"link7","contact_count":740.0,"contact_point_centroid":[-0.05867,-0.11368,0.32917],"force_p95":293.38506,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":456.80484,"mean_force":273.67415,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[-0.05366,-0.1578,0.33648]},{"body_a":"link1","body_b":"link5","contact_count":1.0,"contact_point_centroid":[-0.0244,-0.04897,0.20674],"force_p95":82.98776,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":82.98776,"mean_force":82.98776,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[-0.06871,-0.16486,0.33928]},{"body_a":"world","body_b":"door_panel","contact_count":1100.0,"contact_point_centroid":[0.30015,0.18741,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.06338,0.05681,0.38868]},{"body_a":"world","body_b":"door_panel","contact_count":1048.0,"contact_point_centroid":[0.30014,0.18753,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[-0.0504,-0.1635,0.32818]}],"total_contact_groups":8},"final_pose_error":0.31243,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[-0.03227,-0.2001,0.2704],"hinge_angle":0.01205,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":726.3418,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1138.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":424.42096,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1870.0,"raw_peak_contact_force":668.45562,"subtask_id":"tcp_contact","tcp_end":[-0.06871,-0.16486,0.33928],"tcp_start":[-0.12766,-0.03595,0.36588],"tcp_to_object_dist_end":0.38342,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":82.98776,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":82.98776,"tcp_end":[-0.06835,-0.16509,0.33909],"tcp_start":[-0.06871,-0.16486,0.33928],"tcp_to_object_dist_end":0.38329,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":46.42031,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2020.0,"raw_peak_contact_force":726.3418,"subtask_id":"hinge_progress","tcp_end":[-0.03227,-0.2001,0.2704],"tcp_start":[-0.06835,-0.16509,0.33909],"tcp_to_object_dist_end":0.33793,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `99847c10f6e36b39751f22a6e7e446b09a6cc2d5cdc4857751225dedfedfe952`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.36667,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.25756,"approach_1.approach_speed":0.33805,"approach_1.arc_height":0.06866,"contact_1.contact_force_threshold":17.40692,"contact_1.contact_speed":0.0393,"push_1.push_distance":0.2455,"push_1.push_pose_tol":0.04603,"push_1.push_speed":0.12921},"optimized_scores":{"best_composite_score":-0.09667,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link1","body_b":"link5","contact_count":429.0,"contact_point_centroid":[-0.01971,-0.05061,0.2066],"force_p95":805.01935,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":912.94411,"mean_force":471.00432,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[-0.04552,-0.2136,0.26525]},{"body_a":"link2","body_b":"link5","contact_count":216.0,"contact_point_centroid":[-0.08697,0.07726,0.36103],"force_p95":537.02156,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":640.99307,"mean_force":320.0029,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.01764,0.26913,0.41597]},{"body_a":"link1","body_b":"link5","contact_count":37.0,"contact_point_centroid":[-0.02397,-0.04871,0.20682],"force_p95":563.1819,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":566.94771,"mean_force":457.48214,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.09513,-0.12385,0.36569]},{"body_a":"link2","body_b":"link7","contact_count":791.0,"contact_point_centroid":[-0.08251,-0.08043,0.3509],"force_p95":364.50105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":564.34154,"mean_force":265.07078,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.10612,-0.0491,0.38063]},{"body_a":"link2","body_b":"link7","contact_count":584.0,"contact_point_centroid":[-0.07031,-0.10459,0.3337],"force_p95":323.9106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":403.87022,"mean_force":283.8539,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[-0.07914,-0.13803,0.37338]},{"body_a":"link1","body_b":"link5","contact_count":2.0,"contact_point_centroid":[-0.02475,-0.04862,0.20687],"force_p95":344.25415,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":362.37279,"mean_force":181.18639,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[-0.08498,-0.13403,0.36022]},{"body_a":"link2","body_b":"link7","contact_count":2.0,"contact_point_centroid":[-0.06497,-0.10597,0.32574],"force_p95":344.1511,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":358.16099,"mean_force":218.06205,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[-0.08498,-0.13403,0.36022]},{"body_a":"world","body_b":"door_panel","contact_count":1376.0,"contact_point_centroid":[0.3006,0.18157,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.06374,0.06582,0.38772]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30057,0.18186,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[-0.08477,-0.13424,0.36014]},{"body_a":"world","body_b":"door_panel","contact_count":976.0,"contact_point_centroid":[0.30056,0.18204,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[-0.06654,-0.16577,0.3329]}],"total_contact_groups":10},"final_pose_error":0.34925,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[-0.00989,-0.23017,0.16561],"hinge_angle":0.03889,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":912.94411,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1464.0,"n_steps_budget":780.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.52729,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2420.0,"raw_peak_contact_force":640.99307,"subtask_id":"tcp_contact","tcp_end":[-0.08518,-0.13382,0.36031],"tcp_start":[-0.12722,-0.03431,0.36099],"tcp_to_object_dist_end":0.39369,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":362.37279,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8.0,"raw_peak_contact_force":362.37279,"tcp_end":[-0.08444,-0.1346,0.35999],"tcp_start":[-0.08518,-0.13382,0.36031],"tcp_to_object_dist_end":0.3935,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":1.41421,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1989.0,"raw_peak_contact_force":912.94411,"subtask_id":"hinge_progress","tcp_end":[-0.00989,-0.23017,0.16561],"tcp_start":[-0.08444,-0.1346,0.35999],"tcp_to_object_dist_end":0.28373,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```