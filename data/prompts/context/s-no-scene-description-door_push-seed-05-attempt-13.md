## Search State

- **Seed**: 5
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.9533 | 1.00 | ❌ rejected |
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.0708 | 0.12 | ❌ rejected |
| 11 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.3403 | 0.44 | ❌ rejected |
| 10 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.0368 | 0.06 | ❌ rejected |
| 9 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.0967 | 0.00 | ❌ rejected |

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
| approach_1 | 0.00 | 0.67 | 0.3109 |
| contact_1 | 1.00 | 1.00 | 0.0166 |
| push_1 | 0.00 | 0.67 | 0.3484 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (-0.105, 0.264, 0.305)→(0.104, 0.124, 0.234) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.333 | 246.369 | 1482.503 |
| contact_1 | descend | 1.00 / force_exceeded | (0.104, 0.124, 0.234)→(0.091, 0.125, 0.234) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 107.610 | 174.859 |
| push_1 | push | 0.00 / step_budget | (0.091, 0.125, 0.234)→(0.108, 0.074, 0.271) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.333 | 130.507 | 2096.835 |

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
- **Final σ (mean)**: 0.252


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":47.0,"average_failure_rate":0.34307,"average_mean_iterations":74.55474,"average_solve_count":137.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15091,"approach_1.approach_speed":0.65819,"contact_1.contact_force_threshold":13.7257,"contact_1.contact_speed":0.07013,"push_1.push_distance":0.45922,"push_1.push_pose_tol":0.03653,"push_1.push_speed":0.07666},"optimized_scores":{"best_composite_score":0.95333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":49.0,"contact_point_centroid":[0.23182,0.11819,0.19505],"force_p95":1786.50765,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2746.26218,"mean_force":403.85225,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.18718,0.17338,0.18009]},{"body_a":"door_panel","body_b":"link4","contact_count":209.0,"contact_point_centroid":[0.11898,0.09867,0.59561],"force_p95":1090.10173,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1996.77678,"mean_force":687.37664,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.17688,0.17542,0.17163]},{"body_a":"door_panel","body_b":"link6","contact_count":230.0,"contact_point_centroid":[0.16758,0.13091,0.32275],"force_p95":837.79352,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1152.21736,"mean_force":407.22095,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.14393,0.19527,0.21508]},{"body_a":"door_panel","body_b":"link5","contact_count":13.0,"contact_point_centroid":[0.10849,0.12432,0.54387],"force_p95":379.17656,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":646.18205,"mean_force":65.18115,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.15955,0.21526,0.19147]},{"body_a":"link2","body_b":"link5","contact_count":275.0,"contact_point_centroid":[0.08495,0.04331,0.38073],"force_p95":454.89716,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":500.75584,"mean_force":379.01384,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.20758,0.16615,0.43965]},{"body_a":"link0","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.05353,-0.01599,0.12119],"force_p95":453.63992,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":460.95331,"mean_force":180.17164,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09203,-0.02029,0.08138]},{"body_a":"link1","body_b":"link5","contact_count":97.0,"contact_point_centroid":[-0.02472,0.04877,0.23626],"force_p95":426.12753,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":440.62298,"mean_force":216.32236,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.06113,0.12542,0.12552]},{"body_a":"link0","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.05443,-0.01739,0.11916],"force_p95":198.53589,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":198.53589,"mean_force":198.53589,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.09394,-0.02221,0.07941]},{"body_a":"world","body_b":"door_panel","contact_count":1052.0,"contact_point_centroid":[0.30565,0.15932,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.05373,0.2492,0.29481]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.41466,0.01885,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.11387,-0.02826,0.07777]},{"body_a":"world","body_b":"door_panel","contact_count":628.0,"contact_point_centroid":[0.40994,0.02117,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.13702,0.1642,0.28601]}],"total_contact_groups":11},"final_pose_error":0.09745,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.20711,0.17812,0.39894],"hinge_angle":1.03194,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":2746.26218,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":992.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1553.0,"raw_peak_contact_force":2746.26218,"subtask_id":"tcp_contact","tcp_end":[0.13476,-0.03095,0.07923],"tcp_start":[-0.10949,0.25905,0.35563],"tcp_to_object_dist_end":0.15937,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":18.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":198.53589,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":198.53589,"tcp_end":[0.09273,-0.02182,0.07966],"tcp_start":[0.13476,-0.03095,0.07923],"tcp_to_object_dist_end":0.12418,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":391.51961,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1011.0,"raw_peak_contact_force":500.75584,"subtask_id":"hinge_progress","tcp_end":[0.20711,0.17812,0.39894],"tcp_start":[0.09273,-0.02182,0.07966],"tcp_to_object_dist_end":0.48351,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fbf559b1c4ad02fb5807d56e72eb3a3daf90ab4647e10f958130a5b70ea34720`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":33.0,"average_failure_rate":0.43421,"average_mean_iterations":91.63158,"average_solve_count":76.0,"average_success_count":43.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13699,"approach_1.approach_speed":0.61857,"contact_1.contact_force_threshold":11.50658,"contact_1.contact_speed":0.03053,"push_1.push_distance":0.3091,"push_1.push_pose_tol":0.05676,"push_1.push_speed":0.08712},"optimized_scores":{"best_composite_score":0.95333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":57.0,"contact_point_centroid":[0.10236,0.15527,0.54243],"force_p95":888.67941,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":915.84391,"mean_force":507.66026,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.0296,0.2791,0.29567]},{"body_a":"door_panel","body_b":"link6","contact_count":110.0,"contact_point_centroid":[0.11016,0.15672,0.37682],"force_p95":523.81708,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":554.46779,"mean_force":309.98348,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.00516,0.26597,0.30626]},{"body_a":"door_panel","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.22958,0.04414,0.51312],"force_p95":87.04906,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.31911,"mean_force":84.61862,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.15383,0.14883,0.38271]},{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.23595,0.04431,0.51165],"force_p95":52.27646,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.27646,"mean_force":52.27646,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.15529,0.14462,0.38281]},{"body_a":"door_panel","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.1182,0.19307,0.29608],"force_p95":16.79199,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.6403,"mean_force":14.01173,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.05548,0.2503,0.27392]},{"body_a":"world","body_b":"door_panel","contact_count":808.0,"contact_point_centroid":[0.30138,0.18,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.00766,0.27797,0.29733]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.33138,0.09199,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.15334,0.15026,0.38267]},{"body_a":"world","body_b":"door_panel","contact_count":128.0,"contact_point_centroid":[0.33779,0.08257,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[-0.03008,0.1165,0.2967]}],"total_contact_groups":8},"final_pose_error":0.22545,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[-0.11926,0.02453,0.26556],"hinge_angle":0.57548,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":915.84391,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":812.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":461.70828,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":991.0,"raw_peak_contact_force":915.84391,"subtask_id":"tcp_contact","tcp_end":[0.15334,0.15026,0.38267],"tcp_start":[-0.07602,0.26113,0.2425],"tcp_to_object_dist_end":0.43878,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":87.31911,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6.0,"raw_peak_contact_force":87.31911,"tcp_end":[0.15529,0.14462,0.38281],"tcp_start":[0.15334,0.15026,0.38267],"tcp_to_object_dist_end":0.43769,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":128.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":129.0,"raw_peak_contact_force":52.27646,"subtask_id":"hinge_progress","tcp_end":[-0.11926,0.02453,0.26556],"tcp_start":[0.15529,0.14462,0.38281],"tcp_to_object_dist_end":0.29214,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `99847c10f6e36b39751f22a6e7e446b09a6cc2d5cdc4857751225dedfedfe952`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":5.0,"average_failure_rate":0.07353,"average_mean_iterations":23.27941,"average_solve_count":68.0,"average_success_count":63.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12902,"approach_1.approach_speed":0.80201,"contact_1.contact_force_threshold":17.61087,"contact_1.contact_speed":0.06837,"push_1.push_distance":0.23025,"push_1.push_pose_tol":0.0648,"push_1.push_speed":0.12861},"optimized_scores":{"best_composite_score":0.95333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.10171,0.49998,-0.01242],"force_p95":4555.75477,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5737.47386,"mean_force":1020.63431,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.07819,0.52958,0.00259]},{"body_a":"world","body_b":"link6","contact_count":264.0,"contact_point_centroid":[0.17715,0.06174,-0.00049],"force_p95":1163.46286,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2118.22435,"mean_force":493.05549,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.23399,0.10272,0.13844]},{"body_a":"link0","body_b":"link6","contact_count":182.0,"contact_point_centroid":[0.05516,-0.01488,0.11937],"force_p95":1291.91732,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1604.71795,"mean_force":544.64157,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.23597,0.01905,0.14827]},{"body_a":"door_panel","body_b":"link6","contact_count":118.0,"contact_point_centroid":[0.10136,0.23591,0.342],"force_p95":677.1348,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":785.40162,"mean_force":469.5695,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.01859,0.26857,0.26814]},{"body_a":"door_panel","body_b":"link5","contact_count":87.0,"contact_point_centroid":[0.10098,0.21747,0.49206],"force_p95":683.40076,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":770.69539,"mean_force":359.86222,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.00662,0.26549,0.29299]},{"body_a":"door_panel","body_b":"link5","contact_count":30.0,"contact_point_centroid":[0.35,0.14525,0.141],"force_p95":438.69463,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":488.65767,"mean_force":341.56005,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.26597,0.32841,0.17812]},{"body_a":"door_panel","body_b":"link7","contact_count":70.0,"contact_point_centroid":[0.10377,0.2538,0.24865],"force_p95":332.56398,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":375.91775,"mean_force":245.77556,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.02016,0.26353,0.2593]},{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.1008,0.23208,0.32749],"force_p95":238.72256,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":238.72256,"mean_force":238.72256,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.02347,0.25313,0.23967]},{"body_a":"door_panel","body_b":"link6","contact_count":13.0,"contact_point_centroid":[0.17842,0.22368,0.19404],"force_p95":176.59935,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":177.64259,"mean_force":86.19365,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.14387,0.3398,0.19139]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.10342,0.25187,0.2457],"force_p95":51.3959,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.15496,"mean_force":44.56437,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.02346,0.25304,0.23947]},{"body_a":"world","body_b":"door_panel","contact_count":944.0,"contact_point_centroid":[0.30056,0.18789,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.02053,0.28224,0.31894]},{"body_a":"link1","body_b":"link6","contact_count":10.0,"contact_point_centroid":[0.05258,-0.01603,0.14102],"force_p95":0.0,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.23289,0.02152,0.14935]},{"body_a":"world","body_b":"door_panel","contact_count":404.0,"contact_point_centroid":[0.34208,0.13706,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.14776,0.27125,0.17292]}],"total_contact_groups":13},"final_pose_error":0.20473,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.23648,0.0179,0.14833],"hinge_angle":1.06315,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":5737.47386,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":992.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":277.39776,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1219.0,"raw_peak_contact_force":785.40162,"subtask_id":"tcp_contact","tcp_end":[0.02347,0.25313,0.23967],"tcp_start":[-0.12971,0.27205,0.31733],"tcp_to_object_dist_end":0.34938,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":36.97379,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3.0,"raw_peak_contact_force":238.72256,"tcp_end":[0.02349,0.25278,0.23883],"tcp_start":[0.02347,0.25313,0.23967],"tcp_to_object_dist_end":0.34856,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":548.0,"n_steps_budget":780.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":936.0,"raw_peak_contact_force":5737.47386,"subtask_id":"hinge_progress","tcp_end":[0.23648,0.0179,0.14833],"tcp_start":[0.02349,0.25278,0.23883],"tcp_to_object_dist_end":0.27972,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```