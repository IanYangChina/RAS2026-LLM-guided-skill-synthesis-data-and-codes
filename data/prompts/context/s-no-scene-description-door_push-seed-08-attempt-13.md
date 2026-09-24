## Search State

- **Seed**: 8
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 1.1200 | 1.00 | ✅ accepted |
| 12 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 9 | -0.1404 | 0.12 | ❌ rejected |
| 11 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | 0.2523 | 0.55 | ❌ rejected |
| 10 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 8 | 0.0749 | 0.17 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.4353 | 0.32 | ❌ rejected |

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

## Current Skill (Q=1.120) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: approach_door
  anchor: object
  offset:
  - 0.0
  - -0.15
  - 0.15
  weight: 0.3
- id: push_hinge
  anchor: fixture
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
    anchor: task_object
    offset:
    - 0.0
    - -0.15
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: approach_door
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - -0.15
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 3.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_door
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
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
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.6
      default: 0.3
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_max_time:
      type: scalar
      range:
      - 3.0
      - 10.0
      default: 6.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_maintained
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_hinge

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, -0.15, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, -0.15, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.3, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_max_time: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_maintained, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 1.120
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.4405 |
| contact_1 | 1.00 | 1.00 | 0.0005 |
| push_1 | 1.00 | 0.67 | 0.2601 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.100, 0.399, 0.350)→(0.034, -0.032, 0.410) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.333 | 232.693 | 1310.721 |
| contact_1 | contact | 1.00 / force_exceeded | (0.034, -0.032, 0.410)→(0.034, -0.032, 0.410) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 4.000 | 203.584 | 95.806 |
| push_1 | push | 1.00 / time_limit | (0.034, -0.032, 0.410)→(0.093, 0.069, 0.641) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 3.000 | 0.000 | 323.201 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.667

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.120
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.233


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `ea6bae111f14debb91f5aac35e1b236c8a3b6c6e55761aa2eab002718511c500`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `4672b672dcc6ffecf2b710096d1b05b46bb79ca3304db4877275d5463822e477`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.83333,"average_solve_count":72.0,"average_success_count":72.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.307,"approach_1.arc_height":0.14857,"contact_1.contact_force_threshold":14.47762,"contact_1.contact_speed":0.05569,"push_1.push_distance":0.41179,"push_1.push_max_time":5.00624,"push_1.push_speed":0.16556},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":36.0,"contact_point_centroid":[0.13612,0.03646,0.52342],"force_p95":1378.12472,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1419.20212,"mean_force":789.12837,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.0362,-0.00575,0.39716]},{"body_a":"link1","body_b":"link7","contact_count":245.0,"contact_point_centroid":[0.03819,0.01658,0.37759],"force_p95":449.68857,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":710.17228,"mean_force":239.70774,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.03305,-0.00316,0.3965]},{"body_a":"door_frame","body_b":"link6","contact_count":113.0,"contact_point_centroid":[0.16198,0.17508,0.75019],"force_p95":458.31048,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":484.39078,"mean_force":333.63378,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.08793,0.07424,0.61357]},{"body_a":"link1","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.07125,-0.01154,0.37698],"force_p95":126.20903,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":126.20903,"mean_force":126.20903,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.03688,-0.01175,0.3979]},{"body_a":"link1","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.07096,-0.01328,0.37704],"force_p95":97.40814,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":118.63003,"mean_force":26.75327,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.03694,-0.01289,0.39817]},{"body_a":"door_panel","body_b":"link6","contact_count":26.0,"contact_point_centroid":[0.15124,0.00415,0.599],"force_p95":80.65203,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":101.35998,"mean_force":48.78467,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.05718,0.02418,0.46893]},{"body_a":"door_panel","body_b":"link7","contact_count":308.0,"contact_point_centroid":[0.12873,0.12672,0.42846],"force_p95":29.30951,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.47887,"mean_force":15.91876,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.05996,0.17667,0.40551]},{"body_a":"door_panel","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.1583,0.00963,0.63122],"force_p95":25.65334,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.86183,"mean_force":21.35833,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.08193,0.05754,0.63078]},{"body_a":"world","body_b":"door_panel","contact_count":924.0,"contact_point_centroid":[0.30949,0.15189,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.05801,0.15778,0.39514]},{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.14523,0.01573,0.52201],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.03688,-0.01175,0.3979]},{"body_a":"world","body_b":"door_panel","contact_count":860.0,"contact_point_centroid":[0.33061,0.09319,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.06595,0.03938,0.50214]}],"total_contact_groups":11},"final_pose_error":0.17542,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.0811,0.05487,0.63385],"hinge_angle":0.51275,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1419.20212,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":341.9878,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1513.0,"raw_peak_contact_force":1419.20212,"subtask_id":"approach_door","tcp_end":[0.03688,-0.01175,0.3979],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.39978,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":126.20903,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":126.20903,"subtask_id":"approach_door","tcp_end":[0.03696,-0.01225,0.39798],"tcp_start":[0.03688,-0.01175,0.3979],"tcp_to_object_dist_end":0.39988,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1010.0,"raw_peak_contact_force":484.39078,"subtask_id":"push_hinge","tcp_end":[0.0811,0.05487,0.63385],"tcp_start":[0.03696,-0.01225,0.39798],"tcp_to_object_dist_end":0.64137,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `6091bac9443f311cc90f1388d6700bb5b9c315c724ba8069ca061d7c4a07c1f1`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.13235,"average_solve_count":68.0,"average_success_count":68.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.28967,"approach_1.arc_height":0.10069,"contact_1.contact_force_threshold":13.6291,"contact_1.contact_speed":0.08213,"push_1.push_distance":0.31133,"push_1.push_max_time":5.75481,"push_1.push_speed":0.21737},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":174.0,"contact_point_centroid":[0.13993,0.03514,0.51959],"force_p95":1117.18102,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1280.06463,"mean_force":551.54778,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.02407,-0.00681,0.39982]},{"body_a":"link1","body_b":"link7","contact_count":267.0,"contact_point_centroid":[0.04571,-0.00017,0.37633],"force_p95":422.38191,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":614.97737,"mean_force":272.38424,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.02219,-0.00418,0.399]},{"body_a":"link2","body_b":"link7","contact_count":42.0,"contact_point_centroid":[0.01179,0.02885,0.37821],"force_p95":219.94955,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":315.14373,"mean_force":28.29668,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.01572,0.00475,0.39599]},{"body_a":"link1","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.08607,-0.06719,0.36633],"force_p95":68.00421,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.74694,"mean_force":40.90714,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.03319,-0.03446,0.41596]},{"body_a":"door_panel","body_b":"link7","contact_count":122.0,"contact_point_centroid":[0.12283,0.1153,0.39998],"force_p95":30.74666,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.03393,"mean_force":17.05368,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.05458,0.16708,0.3764]},{"body_a":"link1","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.08613,-0.06704,0.36604],"force_p95":32.41597,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":32.41597,"mean_force":32.41597,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.03301,-0.03412,0.41493]},{"body_a":"door_panel","body_b":"link6","contact_count":17.0,"contact_point_centroid":[0.19031,-0.05316,0.64052],"force_p95":28.99026,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.07963,"mean_force":22.037,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.07079,0.0329,0.54667]},{"body_a":"world","body_b":"door_panel","contact_count":992.0,"contact_point_centroid":[0.30982,0.14243,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.05145,0.15946,0.38213]},{"body_a":"world","body_b":"door_panel","contact_count":736.0,"contact_point_centroid":[0.35165,0.06549,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.06514,0.02281,0.52692]}],"total_contact_groups":9},"final_pose_error":0.01467,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.1066,0.09706,0.67068],"hinge_angle":0.6784,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1280.06463,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":2.91548,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1597.0,"raw_peak_contact_force":1280.06463,"subtask_id":"approach_door","tcp_end":[0.03301,-0.03412,0.41493],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.41764,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":359.14271,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":32.41597,"subtask_id":"approach_door","tcp_end":[0.03304,-0.03444,0.41512],"tcp_start":[0.03301,-0.03412,0.41493],"tcp_to_object_dist_end":0.41786,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":871.0,"n_steps_budget":900.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":764.0,"raw_peak_contact_force":69.74694,"subtask_id":"push_hinge","tcp_end":[0.1066,0.09706,0.67068],"tcp_start":[0.03304,-0.03444,0.41512],"tcp_to_object_dist_end":0.686,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `3d62b54ff2d8b84e841b6e4711bcf5c00d2771c3332b770c71c3a72dad860645`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.76389,"average_solve_count":72.0,"average_success_count":72.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.3174,"approach_1.arc_height":0.11585,"contact_1.contact_force_threshold":14.54094,"contact_1.contact_speed":0.08941,"push_1.push_distance":0.41157,"push_1.push_max_time":8.78961,"push_1.push_speed":0.14775},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":139.0,"contact_point_centroid":[0.14096,0.03042,0.5186],"force_p95":1133.26828,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1232.89595,"mean_force":573.58939,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.02909,-0.00751,0.39763]},{"body_a":"link1","body_b":"link7","contact_count":282.0,"contact_point_centroid":[0.05,-0.00658,0.37535],"force_p95":420.17237,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":666.80172,"mean_force":258.31984,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.02781,-0.00963,0.39918]},{"body_a":"door_panel","body_b":"link6","contact_count":49.0,"contact_point_centroid":[0.20055,-0.06516,0.52678],"force_p95":119.55284,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":415.46465,"mean_force":66.98909,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.04095,-0.03583,0.44289]},{"body_a":"link1","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.07995,-0.07872,0.36535],"force_p95":165.62907,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":180.61328,"mean_force":106.8016,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.03375,-0.04923,0.41574]},{"body_a":"link1","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.0791,-0.07936,0.36513],"force_p95":128.79245,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":128.79245,"mean_force":128.79245,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.0331,-0.05062,0.41615]},{"body_a":"door_panel","body_b":"link7","contact_count":138.0,"contact_point_centroid":[0.12217,0.10049,0.41058],"force_p95":26.95782,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.133,"mean_force":16.32661,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.05164,0.14847,0.38733]},{"body_a":"link2","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.01689,0.02516,0.37865],"force_p95":1.83834,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":8.16214,"mean_force":0.39251,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.02169,0.00087,0.39597]},{"body_a":"world","body_b":"door_panel","contact_count":1092.0,"contact_point_centroid":[0.31262,0.13527,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.05356,0.14976,0.38609]},{"body_a":"world","body_b":"door_panel","contact_count":756.0,"contact_point_centroid":[0.35698,0.05985,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.06175,0.00136,0.51528]}],"total_contact_groups":9},"final_pose_error":0.17717,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09118,0.05384,0.61782],"hinge_angle":0.71506,"initial_hinge_angle":0.15917,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15917,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1232.89595,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":353.175,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1679.0,"raw_peak_contact_force":1232.89595,"subtask_id":"approach_door","tcp_end":[0.0331,-0.05062,0.41615],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.42052,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":125.40075,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":128.79245,"subtask_id":"approach_door","tcp_end":[0.03323,-0.05008,0.41587],"tcp_start":[0.0331,-0.05062,0.41615],"tcp_to_object_dist_end":0.42019,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":819.0,"raw_peak_contact_force":415.46465,"subtask_id":"push_hinge","tcp_end":[0.09118,0.05384,0.61782],"tcp_start":[0.03323,-0.05008,0.41587],"tcp_to_object_dist_end":0.62683,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```