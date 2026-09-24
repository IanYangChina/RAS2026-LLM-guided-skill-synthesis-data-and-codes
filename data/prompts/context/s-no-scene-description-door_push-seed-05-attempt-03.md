## Search State

- **Seed**: 5
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | -0.0520 | 0.33 | ❌ rejected |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.7311 | 1.00 | ✅ accepted |
| 1 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 2 | -0.1000 | 0.00 | ❌ rejected |
| 0 | push → release → pull → release → release → grasp | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | 2 | 0.0920 | 0.31 | ✅ accepted |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.052) — your mutation base

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
  guards:
  - id: contact_force_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: abort
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
  guards:
  - id: push_force_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
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
  - guards:
    - id=contact_force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=30.0
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.05
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_x, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_pose_tol: status=consumed; consumers=termination.pose_tolerance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=push_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=2, strategy=reduce_speed

## Design Metrics

- **Composite score**: -0.052
- **task_score** (E): 0.328
- **fitness_score**: 0.328  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.67 | 0.0881 |
| contact_1 | 0.00 | 0.33 | 0.1192 |
| push_1 | 0.33 | 0.67 | 0.0569 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.100, 0.269, 0.447)→(0.100, 0.189, 0.484) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.000 | 2.157 | 46.180 |
| contact_1 | descend | 0.00 / step_budget | (0.100, 0.189, 0.484)→(0.100, 0.180, 0.366) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 0.000 | 17.503 |
| push_1 | push | 0.33 / guard_failure | (0.144, 0.261, 0.519)→(0.160, 0.291, 0.565) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 0.667 | 79.962 | 128.891 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.409
- arc_quality: 0.333

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.409
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.409
- **Median Q (composite search score)**: -0.033
- **K-run variance**: 0.0056
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.385


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.49398,"average_solve_count":83.0,"average_success_count":83.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09803,"approach_1.approach_speed":0.72539,"contact_1.contact_force_threshold":28.57855,"contact_1.contact_speed":0.08468,"push_1.push_distance":0.47637,"push_1.push_pose_tol":0.05941,"push_1.push_speed":0.17253},"optimized_scores":{"best_composite_score":-0.15182,"best_fitness_score":0.22818,"best_task_score":0.22818},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_frame","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.12581,0.22478,0.75031],"force_p95":154.60537,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":159.88804,"mean_force":110.65353,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.16648,0.30198,0.58413]},{"body_a":"door_panel","body_b":"link6","contact_count":28.0,"contact_point_centroid":[0.10284,0.15336,0.5328],"force_p95":23.28635,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.9449,"mean_force":18.00011,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10021,0.22018,0.4279]},{"body_a":"door_panel","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.16543,0.14638,0.45905],"force_p95":21.52267,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.07161,"mean_force":16.9858,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10021,0.2038,0.43517]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.16503,0.12255,0.37885],"force_p95":22.24976,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.24976,"mean_force":22.24976,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09976,0.17998,0.35484]},{"body_a":"door_panel","body_b":"link7","contact_count":130.0,"contact_point_centroid":[0.1651,0.12894,0.41852],"force_p95":17.26761,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.70316,"mean_force":13.53908,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.09983,0.18637,0.39453]},{"body_a":"world","body_b":"door_panel","contact_count":604.0,"contact_point_centroid":[0.30234,0.16804,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.1001,0.3018,0.39128]},{"body_a":"world","body_b":"door_panel","contact_count":520.0,"contact_point_centroid":[0.30638,0.14894,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.09984,0.18688,0.39757]},{"body_a":"world","body_b":"door_panel","contact_count":264.0,"contact_point_centroid":[0.3074,0.14518,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.13509,0.24476,0.47511]}],"total_contact_groups":8},"final_pose_error":0.20317,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.16673,0.30248,0.58493],"hinge_angle":0.22603,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":159.88804,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":554.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":6.47003,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":676.0,"raw_peak_contact_force":42.9449,"subtask_id":"tcp_contact","tcp_end":[0.10016,0.19392,0.43961],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.4908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":520.0,"n_steps_budget":690.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":650.0,"raw_peak_contact_force":20.70316,"tcp_end":[0.09978,0.18003,0.35493],"tcp_start":[0.10016,0.19392,0.43961],"tcp_to_object_dist_end":0.4103,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":269.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":133.83767,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":268.0,"raw_peak_contact_force":159.88804,"subtask_id":"hinge_progress","tcp_end":[0.16673,0.30248,0.58493],"tcp_start":[0.16667,0.30232,0.58472],"tcp_to_object_dist_end":0.6793,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fbf559b1c4ad02fb5807d56e72eb3a3daf90ab4647e10f958130a5b70ea34720`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55729,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13873,"approach_1.approach_speed":0.11584,"contact_1.contact_force_threshold":28.14661,"contact_1.contact_speed":0.05677,"push_1.push_distance":0.47911,"push_1.push_pose_tol":0.05656,"push_1.push_speed":0.04674},"optimized_scores":{"best_composite_score":0.02888,"best_fitness_score":0.40888,"best_task_score":0.40888},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_frame","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.12618,0.22479,0.7503],"force_p95":191.08851,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":200.5375,"mean_force":123.80738,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.16641,0.30134,0.58372]},{"body_a":"door_panel","body_b":"link6","contact_count":183.0,"contact_point_centroid":[0.10122,0.17198,0.5522],"force_p95":25.68465,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.70316,"mean_force":16.26891,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09968,0.24284,0.44599]},{"body_a":"door_panel","body_b":"link7","contact_count":117.0,"contact_point_centroid":[0.16499,0.14315,0.49607],"force_p95":21.89855,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.27404,"mean_force":15.16199,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09962,0.20047,0.47218]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.16514,0.12196,0.37882],"force_p95":19.71187,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.89354,"mean_force":18.07684,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09975,0.17921,0.35471]},{"body_a":"door_panel","body_b":"link7","contact_count":126.0,"contact_point_centroid":[0.16501,0.1254,0.44032],"force_p95":15.38572,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.55816,"mean_force":12.03875,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.0996,0.18265,0.41625]},{"body_a":"world","body_b":"door_panel","contact_count":1120.0,"contact_point_centroid":[0.30121,0.17903,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.0997,0.28726,0.41779]},{"body_a":"world","body_b":"door_panel","contact_count":916.0,"contact_point_centroid":[0.30693,0.14688,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.09959,0.18289,0.42049]},{"body_a":"world","body_b":"door_panel","contact_count":212.0,"contact_point_centroid":[0.30749,0.14488,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.13691,0.24737,0.4813]}],"total_contact_groups":8},"final_pose_error":0.20654,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.16667,0.30188,0.58452],"hinge_angle":0.22758,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":200.5375,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1165.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1420.0,"raw_peak_contact_force":38.70316,"subtask_id":"tcp_contact","tcp_end":[0.09965,0.18656,0.48138],"tcp_start":[0.0997,0.21148,0.466],"tcp_to_object_dist_end":0.5258,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":865.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1042.0,"raw_peak_contact_force":16.55816,"tcp_end":[0.09977,0.17927,0.35483],"tcp_start":[0.09965,0.18656,0.48138],"tcp_to_object_dist_end":0.40987,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":285.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":106.04767,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":217.0,"raw_peak_contact_force":200.5375,"subtask_id":"hinge_progress","tcp_end":[0.16667,0.30188,0.58452],"tcp_start":[0.1666,0.3017,0.5843],"tcp_to_object_dist_end":0.67865,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `99847c10f6e36b39751f22a6e7e446b09a6cc2d5cdc4857751225dedfedfe952`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38462,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18968,"approach_1.approach_speed":0.40722,"contact_1.contact_force_threshold":29.82385,"contact_1.contact_speed":0.03861,"push_1.push_distance":0.25069,"push_1.push_pose_tol":0.04236,"push_1.push_speed":0.1263},"optimized_scores":{"best_composite_score":-0.03302,"best_fitness_score":0.34698,"best_task_score":0.34698},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":59.0,"contact_point_centroid":[0.10156,0.16649,0.59479],"force_p95":33.61282,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.89047,"mean_force":22.82963,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10035,0.2364,0.48888]},{"body_a":"door_panel","body_b":"link7","contact_count":75.0,"contact_point_centroid":[0.16534,0.13975,0.54665],"force_p95":22.17828,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.95517,"mean_force":16.97646,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09998,0.1971,0.52283]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.16514,0.12314,0.41084],"force_p95":26.24882,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.24882,"mean_force":26.24882,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.0997,0.18037,0.38682]},{"body_a":"door_panel","body_b":"link7","contact_count":135.0,"contact_point_centroid":[0.16504,0.12584,0.48063],"force_p95":14.10486,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.24739,"mean_force":12.06787,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.09958,0.18306,0.45664]},{"body_a":"world","body_b":"door_panel","contact_count":592.0,"contact_point_centroid":[0.3017,0.17442,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10039,0.28723,0.44447]},{"body_a":"world","body_b":"door_panel","contact_count":928.0,"contact_point_centroid":[0.30687,0.14709,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.09958,0.18325,0.46153]},{"body_a":"world","body_b":"door_panel","contact_count":172.0,"contact_point_centroid":[0.30735,0.14536,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.12202,0.22114,0.45022]}],"total_contact_groups":7},"final_pose_error":0.04946,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.14775,0.26783,0.52474],"hinge_angle":0.22549,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":56.89047,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":639.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":726.0,"raw_peak_contact_force":56.89047,"subtask_id":"tcp_contact","tcp_end":[0.09975,0.18616,0.53183],"tcp_start":[0.10007,0.19485,0.52514],"tcp_to_object_dist_end":0.57224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1063.0,"raw_peak_contact_force":15.24739,"tcp_end":[0.0997,0.18037,0.38682],"tcp_start":[0.09975,0.18616,0.53183],"tcp_to_object_dist_end":0.4383,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":177.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":173.0,"raw_peak_contact_force":26.24882,"subtask_id":"hinge_progress","tcp_end":[0.14775,0.26783,0.52474],"tcp_start":[0.0997,0.18037,0.38682],"tcp_to_object_dist_end":0.60739,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```