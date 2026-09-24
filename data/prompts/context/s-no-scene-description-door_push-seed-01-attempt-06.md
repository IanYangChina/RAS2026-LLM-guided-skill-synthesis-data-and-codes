## Search State

- **Seed**: 1
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → align → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.6200 | 1.00 | ✅ accepted |
| 5 | rotate → align → push | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | position_control | time_limit | pose_tolerance | time_limit | 3 | 0.3605 | 0.54 | ❌ rejected |
| 4 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 4 | 0.4281 | 0.29 | ❌ rejected |
| 3 | rotate → align → push | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | position_control | time_limit | pose_tolerance | time_limit | 3 | 0.3605 | 0.54 | ❌ rejected |
| 2 | rotate → align → push | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | position_control | time_limit | pose_tolerance | time_limit | 3 | 0.3605 | 0.54 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.620) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: reach_door
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: open_door
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_door
- id: align_contact
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
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
  subtask_id: reach_door
- id: push_door
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
      distance: 0.3
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.05
    orientation:
      mode: none
  parameters:
    force_limit:
      type: scalar
      range:
      - 10.0
      - 50.0
      default: 30.0
      binds_to:
      - path: guards.force_guard.threshold
        mode: replace
    hinge_threshold:
      type: scalar
      range:
      - 0.1
      - 0.524
      default: 0.524
      binds_to:
      - path: guards.push_guard.threshold
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: continue
  - id: push_guard
    when: during_phase
    predicate: hinge_delta_reached
    threshold: 0.524
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.02
    - 0.0
  subtask_id: open_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **align_contact** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
- **push_door** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.3, mode=add_to_offset, sign=negative}, tolerance=0.05
  - orientation: mode=none
  - parameter_bindings:
    - force_limit: status=consumed; consumers=guards.force_guard.threshold (replace)
    - hinge_threshold: status=consumed; consumers=guards.push_guard.threshold (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=continue, threshold=30.0
    - id=push_guard, when=during_phase, predicate=hinge_delta_reached, on_failure=retry, threshold=0.524
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.02, 0.0]

## Design Metrics

- **Composite score**: 0.620
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2222 |
| align_contact | 1.00 | 0.33 | 0.0891 |
| push_door | 0.33 | 0.67 | 0.1953 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.199, 0.446) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 7.679 | 54.813 |
| align_contact | align | 1.00 / step_budget | (0.100, 0.199, 0.446)→(0.104, 0.181, 0.360) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 0.000 | 24.073 |
| push_door | push | 0.33 / guard_failure | (0.104, 0.181, 0.360)→(0.110, -0.014, 0.361) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 1.667 | 22.211 | 49.937 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.620
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.418


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `083132501f1ba139cf05fa7994a1ee954b157d46058e9396ba8b78c93b367725`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a0caaf91521131af8da2ca1e0ce4fb631dc10b8d496fc3757eb1acd97f543da3`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.38095,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_contact.lateral_offset_x":0.0059,"approach.approach_speed":0.18732,"push_door.force_limit":40.41511,"push_door.hinge_threshold":0.17749,"push_door.push_distance":0.23754,"push_door.push_speed":0.03445,"push_door.push_tolerance":0.03013},"optimized_scores":{"best_composite_score":0.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":154.0,"contact_point_centroid":[0.10121,0.17269,0.5441],"force_p95":22.22914,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.58295,"mean_force":14.58848,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09977,0.2437,0.43784]},{"body_a":"door_panel","body_b":"link7","contact_count":124.0,"contact_point_centroid":[0.16891,0.03968,0.38547],"force_p95":37.59095,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.33228,"mean_force":31.39245,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10758,0.10066,0.35983]},{"body_a":"door_panel","body_b":"link7","contact_count":70.0,"contact_point_centroid":[0.16513,0.14542,0.4698],"force_p95":23.03088,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.67182,"mean_force":14.60597,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09985,0.20273,0.44593]},{"body_a":"door_panel","body_b":"link7","contact_count":61.0,"contact_point_centroid":[0.16771,0.12817,0.42577],"force_p95":19.79678,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.68096,"mean_force":15.49206,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.10239,0.18556,0.4018]},{"body_a":"world","body_b":"door_panel","contact_count":816.0,"contact_point_centroid":[0.30071,0.18342,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09987,0.30476,0.40845]},{"body_a":"world","body_b":"door_panel","contact_count":340.0,"contact_point_centroid":[0.30661,0.14807,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.10228,0.1858,0.4037]},{"body_a":"world","body_b":"door_panel","contact_count":168.0,"contact_point_centroid":[0.32773,0.10196,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.1079,0.09055,0.35971]}],"total_contact_groups":7},"final_pose_error":0.04942,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.11008,-0.00978,0.3577],"hinge_angle":0.69228,"initial_hinge_angle":0.00413,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.00413,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":49.58295,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":752.0,"n_steps_budget":810.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.45052,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1040.0,"raw_peak_contact_force":49.58295,"subtask_id":"reach_door","tcp_end":[0.09991,0.19128,0.44728],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49662,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":327.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":401.0,"raw_peak_contact_force":23.68096,"subtask_id":"reach_door","tcp_end":[0.10495,0.1805,0.35983],"tcp_start":[0.09991,0.19128,0.44728],"tcp_to_object_dist_end":0.41602,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":292.0,"raw_peak_contact_force":40.33228,"subtask_id":"open_door","tcp_end":[0.11008,-0.00978,0.3577],"tcp_start":[0.10495,0.1805,0.35983],"tcp_to_object_dist_end":0.37438,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5bc49f053da41ee2995fb91d1adc375d35d8209a2f6f497df40da3fd7dd59d69`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.1747,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_contact.lateral_offset_x":-3e-05,"approach.approach_speed":0.07299,"push_door.force_limit":42.20591,"push_door.hinge_threshold":0.10675,"push_door.push_distance":0.31459,"push_door.push_speed":0.03838,"push_door.push_tolerance":0.05057},"optimized_scores":{"best_composite_score":0.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":119.0,"contact_point_centroid":[0.16386,0.04696,0.38936],"force_p95":39.23167,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.84344,"mean_force":30.15408,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10395,0.10847,0.36153]},{"body_a":"door_panel","body_b":"link6","contact_count":352.0,"contact_point_centroid":[0.10086,0.1904,0.53795],"force_p95":24.99345,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.57634,"mean_force":15.9243,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09953,0.26463,0.43064]},{"body_a":"door_panel","body_b":"link7","contact_count":119.0,"contact_point_centroid":[0.16485,0.14178,0.42582],"force_p95":23.43411,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.71119,"mean_force":16.71065,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.09956,0.19917,0.40182]},{"body_a":"door_panel","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.10325,0.14935,0.54868],"force_p95":15.94726,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.78659,"mean_force":8.3933,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.09966,0.21488,0.44417]},{"body_a":"world","body_b":"door_panel","contact_count":996.0,"contact_point_centroid":[0.30016,0.19821,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09963,0.32117,0.40122]},{"body_a":"world","body_b":"door_panel","contact_count":336.0,"contact_point_centroid":[0.30475,0.15581,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.09956,0.19897,0.40128]},{"body_a":"world","body_b":"door_panel","contact_count":180.0,"contact_point_centroid":[0.32342,0.10854,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10411,0.10593,0.36167]}],"total_contact_groups":7},"final_pose_error":0.15181,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10896,0.0164,0.36296],"hinge_angle":0.64163,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":42.84344,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":9.58616,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1348.0,"raw_peak_contact_force":35.57634,"subtask_id":"reach_door","tcp_end":[0.09966,0.21491,0.44416],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.50339,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":339.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":457.0,"raw_peak_contact_force":26.71119,"subtask_id":"reach_door","tcp_end":[0.09971,0.18322,0.35922],"tcp_start":[0.09966,0.21491,0.44416],"tcp_to_object_dist_end":0.4154,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":183.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":299.0,"raw_peak_contact_force":42.84344,"subtask_id":"open_door","tcp_end":[0.10896,0.0164,0.36296],"tcp_start":[0.09971,0.18322,0.35922],"tcp_to_object_dist_end":0.37931,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `36664242b94803fac749fdbd125449f5f6a464dcd4b70b6714af07046570273f`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.53175,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_contact.lateral_offset_x":0.00759,"approach.approach_speed":0.18063,"push_door.force_limit":46.94893,"push_door.hinge_threshold":0.31802,"push_door.push_distance":0.43603,"push_door.push_speed":0.03757,"push_door.push_tolerance":0.0634},"optimized_scores":{"best_composite_score":0.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":274.0,"contact_point_centroid":[0.10097,0.19249,0.53694],"force_p95":26.14356,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.2807,"mean_force":17.87129,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09964,0.26702,0.42956]},{"body_a":"door_panel","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.23899,-0.02298,0.45395],"force_p95":64.53746,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.63378,"mean_force":52.64066,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.11232,-0.04587,0.36182]},{"body_a":"door_panel","body_b":"link7","contact_count":122.0,"contact_point_centroid":[0.1707,0.03443,0.39017],"force_p95":44.25044,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.78615,"mean_force":32.08458,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.11009,0.09587,0.36404]},{"body_a":"door_panel","body_b":"link7","contact_count":73.0,"contact_point_centroid":[0.1651,0.14476,0.46976],"force_p95":20.82386,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.49221,"mean_force":14.79105,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.0998,0.20213,0.44594]},{"body_a":"door_panel","body_b":"link7","contact_count":61.0,"contact_point_centroid":[0.16837,0.12812,0.42712],"force_p95":19.22779,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.82683,"mean_force":15.66189,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.10303,0.1855,0.40318]},{"body_a":"world","body_b":"door_panel","contact_count":764.0,"contact_point_centroid":[0.30087,0.19169,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09974,0.29423,0.41286]},{"body_a":"world","body_b":"door_panel","contact_count":316.0,"contact_point_centroid":[0.30664,0.14795,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.10292,0.18571,0.40495]},{"body_a":"world","body_b":"door_panel","contact_count":228.0,"contact_point_centroid":[0.33216,0.09566,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.11067,0.07198,0.36401]}],"total_contact_groups":8},"final_pose_error":0.20887,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.11222,-0.04784,0.36154],"hinge_angle":0.70875,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":79.2807,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":782.0,"n_steps_budget":840.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1111.0,"raw_peak_contact_force":79.2807,"subtask_id":"reach_door","tcp_end":[0.09987,0.19084,0.44726],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49642,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":327.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":377.0,"raw_peak_contact_force":21.82683,"subtask_id":"reach_door","tcp_end":[0.10644,0.18046,0.35983],"tcp_start":[0.09987,0.19084,0.44726],"tcp_to_object_dist_end":0.41638,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":66.63378,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":353.0,"raw_peak_contact_force":66.63378,"subtask_id":"open_door","tcp_end":[0.11222,-0.04784,0.36154],"tcp_start":[0.10644,0.18046,0.35983],"tcp_to_object_dist_end":0.38157,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```