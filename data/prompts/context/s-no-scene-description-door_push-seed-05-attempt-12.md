## Search State

- **Seed**: 5
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.0708 | 0.12 | ❌ rejected |
| 11 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.3403 | 0.44 | ❌ rejected |
| 10 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.0368 | 0.06 | ❌ rejected |
| 9 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.0967 | 0.00 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.9533 | 1.00 | ❌ rejected |

**Proposal policy**: task_score is 0.12 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.071) — your mutation base

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

- **Composite score**: 0.071
- **task_score** (E): 0.117
- **fitness_score**: 0.117  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_door | 0.00 | 1.00 | 0.2210 |
| descend_onto_door | 1.00 | 1.00 | 0.0005 |
| push_door_open | 0.00 | 0.67 | 0.0004 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_door | approach | 0.00 / step_budget | (0.204, 0.410, 0.518)→(0.320, 0.267, 0.625) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.000 | 441.913 | 813.681 |
| descend_onto_door | descend | 1.00 / force_exceeded | (0.320, 0.267, 0.625)→(0.320, 0.267, 0.625) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 152.325 | 152.325 |
| push_door_open | push | 0.00 / guard_failure | (0.320, 0.267, 0.625)→(0.320, 0.266, 0.625) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 1.667 | 121.139 | 386.799 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.219
- arc_quality: 0.333

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.219
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.219
- **Median Q (composite search score)**: 0.087
- **K-run variance**: 0.0081
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 4.0
- **Final σ (mean)**: 0.288


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.15873,"average_solve_count":63.0,"average_success_count":63.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_door.approach_speed":0.23313,"approach_above_door.approach_z":0.56078,"descend_onto_door.contact_force_threshold":29.55989,"descend_onto_door.contact_speed":0.08313,"push_door_open.push_distance":0.30211,"push_door_open.push_pose_tol":0.07636,"push_door_open.push_speed":0.09761},"optimized_scores":{"best_composite_score":0.08669,"best_fitness_score":0.13336,"best_task_score":0.13336},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_frame","body_b":"link5","contact_count":305.0,"contact_point_centroid":[0.10008,0.17503,0.75006],"force_p95":655.61554,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":717.19779,"mean_force":617.79282,"phase_index":0.0,"phase_name":"approach_above_door","phase_type":"approach","tcp_position_centroid":[0.34727,0.28428,0.61289]},{"body_a":"door_panel","body_b":"link5","contact_count":1320.0,"contact_point_centroid":[0.10127,0.17849,0.67941],"force_p95":550.76281,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":626.59583,"mean_force":386.67036,"phase_index":0.0,"phase_name":"approach_above_door","phase_type":"approach","tcp_position_centroid":[0.24905,0.37717,0.50247]},{"body_a":"door_frame","body_b":"link6","contact_count":78.0,"contact_point_centroid":[0.25929,0.22495,0.75003],"force_p95":363.69374,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":383.55538,"mean_force":298.76452,"phase_index":0.0,"phase_name":"approach_above_door","phase_type":"approach","tcp_position_centroid":[0.35316,0.27465,0.61705]},{"body_a":"door_frame","body_b":"link5","contact_count":4.0,"contact_point_centroid":[0.10005,0.17502,0.75004],"force_p95":70.59254,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":73.55365,"mean_force":38.92801,"phase_index":1.0,"phase_name":"descend_onto_door","phase_type":"descend","tcp_position_centroid":[0.35386,0.27323,0.61719]},{"body_a":"door_panel","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.10619,0.12992,0.7],"force_p95":61.56015,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.56015,"mean_force":61.56015,"phase_index":1.0,"phase_name":"descend_onto_door","phase_type":"descend","tcp_position_centroid":[0.35387,0.27318,0.61723]},{"body_a":"door_frame","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.25916,0.22496,0.75003],"force_p95":51.75102,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":52.77488,"mean_force":44.86576,"phase_index":1.0,"phase_name":"descend_onto_door","phase_type":"descend","tcp_position_centroid":[0.35386,0.27321,0.61721]},{"body_a":"world","body_b":"door_panel","contact_count":2080.0,"contact_point_centroid":[0.30158,0.17813,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_above_door","phase_type":"approach","tcp_position_centroid":[0.2432,0.36627,0.49146]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30485,0.15509,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_onto_door","phase_type":"descend","tcp_position_centroid":[0.35386,0.27324,0.61718]},{"body_a":"door_frame","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.10004,0.17502,0.75003],"force_p95":0.0,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.35386,0.27331,0.61704]}],"total_contact_groups":9},"final_pose_error":0.30221,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.35371,0.27321,0.61673],"hinge_angle":0.17635,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":717.19779,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":1910.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":572.856,"phase_name":"approach_above_door","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3783.0,"raw_peak_contact_force":717.19779,"subtask_id":"tcp_approach","tcp_end":[0.35387,0.27318,0.61723],"tcp_start":[0.18335,0.46392,0.49852],"tcp_to_object_dist_end":0.76212,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":73.55365,"phase_name":"descend_onto_door","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12.0,"raw_peak_contact_force":73.55365,"tcp_end":[0.35386,0.27331,0.61704],"tcp_start":[0.35387,0.27318,0.61723],"tcp_to_object_dist_end":0.762,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":0.0,"subtask_id":"hinge_progress","tcp_end":[0.35371,0.27321,0.61673],"tcp_start":[0.35386,0.27331,0.61704],"tcp_to_object_dist_end":0.76165,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fbf559b1c4ad02fb5807d56e72eb3a3daf90ab4647e10f958130a5b70ea34720`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":1.0,"average_failure_rate":0.02222,"average_mean_iterations":10.11111,"average_solve_count":45.0,"average_success_count":44.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_door.approach_speed":0.55257,"approach_above_door.approach_z":0.73924,"descend_onto_door.contact_force_threshold":16.501,"descend_onto_door.contact_speed":0.05379,"push_door_open.push_distance":0.34347,"push_door_open.push_pose_tol":0.06393,"push_door_open.push_speed":0.13958},"optimized_scores":{"best_composite_score":-0.04667,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_frame","body_b":"link5","contact_count":775.0,"contact_point_centroid":[0.10006,0.17503,0.75004],"force_p95":748.4582,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":918.39222,"mean_force":572.01593,"phase_index":0.0,"phase_name":"approach_above_door","phase_type":"approach","tcp_position_centroid":[0.25967,0.27896,0.58139]},{"body_a":"door_panel","body_b":"link5","contact_count":861.0,"contact_point_centroid":[0.09985,0.20934,0.69232],"force_p95":513.16732,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":659.02064,"mean_force":297.55233,"phase_index":0.0,"phase_name":"approach_above_door","phase_type":"approach","tcp_position_centroid":[0.26166,0.28477,0.57522]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.25937,0.22289,0.64293],"force_p95":362.34072,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":362.34072,"mean_force":362.34072,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.2423,0.23668,0.6216]},{"body_a":"door_frame","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.10014,0.17504,0.75007],"force_p95":217.15088,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":217.15088,"mean_force":217.15088,"phase_index":1.0,"phase_name":"descend_onto_door","phase_type":"descend","tcp_position_centroid":[0.24232,0.23663,0.6216]},{"body_a":"door_panel","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.10002,0.21832,0.68911],"force_p95":169.39887,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":169.39887,"mean_force":169.39887,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.2423,0.23668,0.6216]},{"body_a":"door_panel","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.25964,0.22325,0.64257],"force_p95":141.24222,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":143.95571,"mean_force":99.0262,"phase_index":0.0,"phase_name":"approach_above_door","phase_type":"approach","tcp_position_centroid":[0.24298,0.23721,0.62104]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.25937,0.22287,0.64295],"force_p95":71.78108,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":71.78108,"mean_force":71.78108,"phase_index":1.0,"phase_name":"descend_onto_door","phase_type":"descend","tcp_position_centroid":[0.24232,0.23663,0.6216]},{"body_a":"door_panel","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.10004,0.21835,0.68906],"force_p95":45.92582,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.92582,"mean_force":45.92582,"phase_index":1.0,"phase_name":"descend_onto_door","phase_type":"descend","tcp_position_centroid":[0.24232,0.23663,0.6216]},{"body_a":"world","body_b":"door_panel","contact_count":1208.0,"contact_point_centroid":[0.29992,0.20069,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_above_door","phase_type":"approach","tcp_position_centroid":[0.24424,0.30227,0.54277]},{"body_a":"door_frame","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.10012,0.17503,0.75006],"force_p95":0.0,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.2423,0.23668,0.6216]}],"total_contact_groups":10},"final_pose_error":0.34354,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.24229,0.23661,0.62157],"hinge_angle":-0.09516,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":918.39222,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":1229.0,"n_steps_budget":690.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":752.11519,"phase_name":"approach_above_door","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2857.0,"raw_peak_contact_force":918.39222,"subtask_id":"tcp_approach","tcp_end":[0.24232,0.23663,0.6216],"tcp_start":[0.25365,0.28616,0.56288],"tcp_to_object_dist_end":0.70789,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":217.15088,"phase_name":"descend_onto_door","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3.0,"raw_peak_contact_force":217.15088,"tcp_end":[0.2423,0.23668,0.6216],"tcp_start":[0.24232,0.23663,0.6216],"tcp_to_object_dist_end":0.70789,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":362.34072,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":362.34072,"subtask_id":"hinge_progress","tcp_end":[0.24229,0.23661,0.62157],"tcp_start":[0.2423,0.23668,0.6216],"tcp_to_object_dist_end":0.70784,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `99847c10f6e36b39751f22a6e7e446b09a6cc2d5cdc4857751225dedfedfe952`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.71429,"average_solve_count":42.0,"average_success_count":42.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_door.approach_speed":0.70901,"approach_above_door.approach_z":0.51713,"descend_onto_door.contact_force_threshold":13.74851,"descend_onto_door.contact_speed":0.02559,"push_door_open.push_distance":0.40934,"push_door_open.push_pose_tol":0.05257,"push_door_open.push_speed":0.14178},"optimized_scores":{"best_composite_score":0.17243,"best_fitness_score":0.2191,"best_task_score":0.2191},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":856.0,"contact_point_centroid":[0.10044,0.19658,0.67405],"force_p95":647.41215,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":805.4541,"mean_force":451.63363,"phase_index":0.0,"phase_name":"approach_above_door","phase_type":"approach","tcp_position_centroid":[0.24515,0.39453,0.48593]},{"body_a":"door_frame","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.25787,0.2237,0.75067],"force_p95":798.05628,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":798.05628,"mean_force":798.05628,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.36352,0.28997,0.63583]},{"body_a":"door_frame","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.25744,0.2247,0.75016],"force_p95":664.83268,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":664.83268,"mean_force":664.83268,"phase_index":0.0,"phase_name":"approach_above_door","phase_type":"approach","tcp_position_centroid":[0.36241,0.29228,0.63431]},{"body_a":"door_frame","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.10006,0.17501,0.75003],"force_p95":475.85577,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":475.85577,"mean_force":475.85577,"phase_index":0.0,"phase_name":"approach_above_door","phase_type":"approach","tcp_position_centroid":[0.36241,0.29228,0.63431]},{"body_a":"door_panel","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.10486,0.13811,0.69999],"force_p95":166.27172,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":166.27172,"mean_force":166.27172,"phase_index":1.0,"phase_name":"descend_onto_door","phase_type":"descend","tcp_position_centroid":[0.36304,0.291,0.63519]},{"body_a":"door_frame","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.25768,0.22413,0.75045],"force_p95":153.05635,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":153.05635,"mean_force":153.05635,"phase_index":1.0,"phase_name":"descend_onto_door","phase_type":"descend","tcp_position_centroid":[0.36304,0.291,0.63519]},{"body_a":"door_frame","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.10014,0.17503,0.75008],"force_p95":138.03416,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":138.03416,"mean_force":138.03416,"phase_index":1.0,"phase_name":"descend_onto_door","phase_type":"descend","tcp_position_centroid":[0.36304,0.291,0.63519]},{"body_a":"door_panel","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.10492,0.13749,0.7],"force_p95":39.72291,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.72291,"mean_force":39.72291,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.36352,0.28997,0.63583]},{"body_a":"world","body_b":"door_panel","contact_count":1056.0,"contact_point_centroid":[0.30036,0.19311,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_above_door","phase_type":"approach","tcp_position_centroid":[0.22891,0.39093,0.46571]},{"body_a":"door_frame","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.10019,0.17504,0.75011],"force_p95":0.0,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.36352,0.28997,0.63583]}],"total_contact_groups":10},"final_pose_error":0.41008,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.36373,0.28923,0.63617],"hinge_angle":0.15847,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":805.4541,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":1107.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.76795,"phase_name":"approach_above_door","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1914.0,"raw_peak_contact_force":805.4541,"subtask_id":"tcp_approach","tcp_end":[0.36304,0.291,0.63519],"tcp_start":[0.17424,0.48118,0.49283],"tcp_to_object_dist_end":0.78736,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":166.27172,"phase_name":"descend_onto_door","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3.0,"raw_peak_contact_force":166.27172,"tcp_end":[0.36352,0.28997,0.63583],"tcp_start":[0.36304,0.291,0.63519],"tcp_to_object_dist_end":0.78772,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":1.07751,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":798.05628,"subtask_id":"hinge_progress","tcp_end":[0.36373,0.28923,0.63617],"tcp_start":[0.36352,0.28997,0.63583],"tcp_to_object_dist_end":0.78783,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```