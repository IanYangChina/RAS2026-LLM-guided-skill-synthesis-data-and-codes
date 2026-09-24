## Search State

- **Seed**: 5
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.9533 | 1.00 | ✅ accepted |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.6200 | 1.00 | ❌ rejected |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.6200 | 1.00 | ❌ rejected |
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.6700 | 1.00 | ❌ rejected |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | -0.0520 | 0.33 | ❌ rejected |

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

## Current Skill (Q=0.953) — your mutation base

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

- **Composite score**: 0.953
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.3400 |
| contact_1 | 1.00 | 1.00 | 0.0001 |
| push_1 | 0.00 | 1.00 | 0.0836 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (-0.121, 0.258, 0.311)→(0.075, 0.054, 0.125) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 355.339 | 886.066 |
| contact_1 | descend | 1.00 / force_exceeded | (0.075, 0.054, 0.125)→(0.075, 0.054, 0.125) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.667 | 289.268 | 95.534 |
| push_1 | push | 0.00 / step_budget | (0.075, 0.054, 0.125)→(0.105, 0.017, 0.076) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.000 | 306.460 | 1448.893 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.333

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.953
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.371


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":6.0,"average_failure_rate":0.09836,"average_mean_iterations":26.98361,"average_solve_count":61.0,"average_success_count":55.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15184,"approach_1.approach_speed":0.5697,"contact_1.contact_force_threshold":20.59796,"contact_1.contact_speed":0.04006,"push_1.push_distance":0.23282,"push_1.push_pose_tol":0.06915,"push_1.push_speed":0.12631},"optimized_scores":{"best_composite_score":0.95333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link5","contact_count":238.0,"contact_point_centroid":[0.20053,0.06823,-0.00049],"force_p95":433.11435,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1215.58708,"mean_force":305.29168,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.04914,0.07441,0.10058]},{"body_a":"link0","body_b":"link7","contact_count":261.0,"contact_point_centroid":[0.04776,0.03138,0.11694],"force_p95":540.69792,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":906.80452,"mean_force":241.96884,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.05075,0.07389,0.10255]},{"body_a":"door_panel","body_b":"link6","contact_count":12.0,"contact_point_centroid":[0.10499,0.14811,0.43891],"force_p95":803.02071,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":868.57929,"mean_force":399.88818,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.12822,0.24762,0.34158]},{"body_a":"link1","body_b":"link7","contact_count":69.0,"contact_point_centroid":[0.04196,0.03476,0.14516],"force_p95":631.22739,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":695.3931,"mean_force":330.84201,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.06179,0.06886,0.12446]},{"body_a":"link0","body_b":"link7","contact_count":76.0,"contact_point_centroid":[0.04552,0.03157,0.13345],"force_p95":618.11924,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":655.48563,"mean_force":517.18506,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.06239,0.07177,0.12248]},{"body_a":"door_panel","body_b":"link4","contact_count":5.0,"contact_point_centroid":[0.34225,-0.16077,0.32683],"force_p95":331.21465,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":335.42371,"mean_force":256.71579,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.06498,0.07148,0.11848]},{"body_a":"door_panel","body_b":"link4","contact_count":17.0,"contact_point_centroid":[0.26597,-0.09308,0.52496],"force_p95":235.19914,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":239.58666,"mean_force":132.75409,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.12531,0.05176,0.14666]},{"body_a":"door_panel","body_b":"link7","contact_count":26.0,"contact_point_centroid":[0.21903,0.09507,0.34587],"force_p95":157.62733,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":178.86452,"mean_force":116.26605,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.19139,0.17635,0.31671]},{"body_a":"link0","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.05262,0.02248,0.11984],"force_p95":59.17649,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":59.17649,"mean_force":59.17649,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.06751,0.06933,0.12155]},{"body_a":"world","body_b":"door_panel","contact_count":1036.0,"contact_point_centroid":[0.31674,0.14768,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.01193,0.23903,0.2959]},{"body_a":"world","body_b":"door_panel","contact_count":192.0,"contact_point_centroid":[0.43678,0.01002,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.05216,0.07397,0.10404]}],"total_contact_groups":11},"final_pose_error":0.10339,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.04439,0.07699,0.1015],"hinge_angle":1.19838,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1215.58708,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":962.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":369.18464,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1236.0,"raw_peak_contact_force":868.57929,"subtask_id":"tcp_contact","tcp_end":[0.06751,0.06933,0.12155],"tcp_start":[-0.14993,0.23582,0.29351],"tcp_to_object_dist_end":0.15537,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":482.40131,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":59.17649,"tcp_end":[0.06762,0.06931,0.12156],"tcp_start":[0.06751,0.06933,0.12155],"tcp_to_object_dist_end":0.15541,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":281.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":328.76918,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":696.0,"raw_peak_contact_force":1215.58708,"subtask_id":"hinge_progress","tcp_end":[0.04439,0.07699,0.1015],"tcp_start":[0.06762,0.06931,0.12156],"tcp_to_object_dist_end":0.13491,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fbf559b1c4ad02fb5807d56e72eb3a3daf90ab4647e10f958130a5b70ea34720`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":6.0,"average_failure_rate":0.09836,"average_mean_iterations":26.91803,"average_solve_count":61.0,"average_success_count":55.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1493,"approach_1.approach_speed":0.7784,"contact_1.contact_force_threshold":14.27958,"contact_1.contact_speed":0.04242,"push_1.push_distance":0.20908,"push_1.push_pose_tol":0.06622,"push_1.push_speed":0.10527},"optimized_scores":{"best_composite_score":0.95333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link0","body_b":"link7","contact_count":238.0,"contact_point_centroid":[0.05626,-0.01592,0.0995],"force_p95":852.44191,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1218.59504,"mean_force":594.83357,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10095,-0.00249,0.10107]},{"body_a":"door_panel","body_b":"link6","contact_count":46.0,"contact_point_centroid":[0.10234,0.18124,0.437],"force_p95":1050.03512,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1199.13267,"mean_force":550.77844,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.00714,0.27178,0.37385]},{"body_a":"link1","body_b":"link7","contact_count":80.0,"contact_point_centroid":[0.04929,0.02376,0.14641],"force_p95":649.48649,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":694.70427,"mean_force":346.38222,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.07645,0.05271,0.12592]},{"body_a":"link0","body_b":"link7","contact_count":45.0,"contact_point_centroid":[0.0522,0.01729,0.1371],"force_p95":573.21429,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":607.43992,"mean_force":462.17906,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.07901,0.0494,0.1209]},{"body_a":"door_panel","body_b":"link4","contact_count":15.0,"contact_point_centroid":[0.26193,-0.11638,0.53204],"force_p95":218.86519,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":236.17561,"mean_force":121.96507,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.13,0.03765,0.15271]},{"body_a":"door_panel","body_b":"link7","contact_count":55.0,"contact_point_centroid":[0.18943,0.13042,0.32927],"force_p95":133.08156,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":143.5007,"mean_force":78.27045,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.14858,0.19761,0.29211]},{"body_a":"link0","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.05334,0.01465,0.13435],"force_p95":74.46491,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.46491,"mean_force":74.46491,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.08149,0.0456,0.11826]},{"body_a":"world","body_b":"door_panel","contact_count":908.0,"contact_point_centroid":[0.30951,0.16947,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.01497,0.25883,0.31638]},{"body_a":"world","body_b":"door_panel","contact_count":140.0,"contact_point_centroid":[0.41751,0.01753,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10112,-0.00604,0.0989]}],"total_contact_groups":9},"final_pose_error":0.15086,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10322,-0.01981,0.09401],"hinge_angle":1.09019,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1218.59504,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":962.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":386.29895,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1149.0,"raw_peak_contact_force":1199.13267,"subtask_id":"tcp_contact","tcp_end":[0.08149,0.0456,0.11826],"tcp_start":[-0.0962,0.27451,0.32021],"tcp_to_object_dist_end":0.15068,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":74.46491,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":74.46491,"tcp_end":[0.08154,0.04561,0.1183],"tcp_start":[0.08149,0.0456,0.11826],"tcp_to_object_dist_end":0.15075,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":252.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":2.91548,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":378.0,"raw_peak_contact_force":1218.59504,"subtask_id":"hinge_progress","tcp_end":[0.10322,-0.01981,0.09401],"tcp_start":[0.08154,0.04561,0.1183],"tcp_to_object_dist_end":0.14101,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `99847c10f6e36b39751f22a6e7e446b09a6cc2d5cdc4857751225dedfedfe952`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":6.0,"average_failure_rate":0.08,"average_mean_iterations":23.94667,"average_solve_count":75.0,"average_success_count":69.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14217,"approach_1.approach_speed":0.55564,"contact_1.contact_force_threshold":11.68116,"contact_1.contact_speed":0.06925,"push_1.push_distance":0.25554,"push_1.push_pose_tol":0.03908,"push_1.push_speed":0.06682},"optimized_scores":{"best_composite_score":0.95333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":170.0,"contact_point_centroid":[0.14247,-0.02572,-0.00058],"force_p95":1247.42592,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1912.49834,"mean_force":607.62107,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.16675,-0.00757,0.03205]},{"body_a":"link0","body_b":"link6","contact_count":175.0,"contact_point_centroid":[0.03638,-0.04806,0.09845],"force_p95":1362.09112,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1845.76518,"mean_force":720.72404,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.1674,-0.00724,0.03297]},{"body_a":"link2","body_b":"link6","contact_count":12.0,"contact_point_centroid":[0.12258,-0.00996,0.31263],"force_p95":1407.20276,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1488.86064,"mean_force":712.3346,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.15265,0.07134,0.20412]},{"body_a":"link1","body_b":"link7","contact_count":127.0,"contact_point_centroid":[0.046,0.02859,0.16296],"force_p95":481.77759,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":590.48525,"mean_force":380.99477,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.06854,0.06124,0.14232]},{"body_a":"link2","body_b":"link6","contact_count":34.0,"contact_point_centroid":[0.08466,0.07691,0.31089],"force_p95":394.82493,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":405.25752,"mean_force":329.62039,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09233,0.06077,0.15776]},{"body_a":"link1","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.05179,0.01793,0.15592],"force_p95":256.14099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":256.23518,"mean_force":200.68875,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.07671,0.04826,0.13424]},{"body_a":"door_panel","body_b":"link7","contact_count":29.0,"contact_point_centroid":[0.16747,0.10931,0.33054],"force_p95":171.92386,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":208.10178,"mean_force":106.43525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.14744,0.19357,0.33037]},{"body_a":"door_panel","body_b":"link4","contact_count":45.0,"contact_point_centroid":[0.27359,-0.10982,0.52455],"force_p95":130.40117,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":156.63839,"mean_force":69.38625,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.07933,0.06156,0.15002]},{"body_a":"link1","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.05156,0.01816,0.15603],"force_p95":152.9593,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":152.9593,"mean_force":152.9593,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.07629,0.04833,0.13411]},{"body_a":"world","body_b":"door_panel","contact_count":888.0,"contact_point_centroid":[0.3172,0.15319,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.01592,0.23895,0.29907]},{"body_a":"link1","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.03903,-0.03834,0.14259],"force_p95":0.0,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.1792,-0.00083,0.0461]},{"body_a":"world","body_b":"door_panel","contact_count":148.0,"contact_point_centroid":[0.42411,0.01469,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.17763,0.00928,0.09292]}],"total_contact_groups":12},"final_pose_error":0.24539,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.16684,-0.00751,0.03362],"hinge_angle":1.12261,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1912.49834,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":962.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":310.53446,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1123.0,"raw_peak_contact_force":590.48525,"subtask_id":"tcp_contact","tcp_end":[0.07629,0.04833,0.13411],"tcp_start":[-0.11668,0.26492,0.318],"tcp_to_object_dist_end":0.16168,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":310.93794,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":152.9593,"tcp_end":[0.07637,0.04817,0.13404],"tcp_start":[0.07629,0.04833,0.13411],"tcp_to_object_dist_end":0.16162,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":324.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":587.69431,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":515.0,"raw_peak_contact_force":1912.49834,"subtask_id":"hinge_progress","tcp_end":[0.16684,-0.00751,0.03362],"tcp_start":[0.07637,0.04817,0.13404],"tcp_to_object_dist_end":0.17036,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```