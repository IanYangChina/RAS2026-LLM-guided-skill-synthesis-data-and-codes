## Search State

- **Seed**: 7
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.8922 | 1.00 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 1.0533 | 1.00 | ✅ accepted |
| 8 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.6200 | 1.00 | ✅ accepted |
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | -0.1124 | 0.11 | ❌ rejected |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | -0.1690 | 0.10 | ❌ rejected |

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

## Current Skill (Q=0.892) — your mutation base

```yaml
skill: door_push
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_door
  anchor: object
  offset:
  - 0.0
  - -0.2
  - 0.15
  weight: 0.3
- id: push_open
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_door
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: door_panel
    offset:
    - 0.0
    - -0.2
    - 0.15
    tolerance: 0.05
    orientation:
      mode: none
  parameters:
    app_y:
      type: scalar
      range:
      - -0.35
      - -0.05
      default: -0.2
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: reach_door
- id: contact_door
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: door_panel
    offset:
    - 0.0
    - -0.08
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 3.0
      - 10.0
      default: 6.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: reach_door
- id: push_door
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
    - -0.08
    - 0.05
    offset_along_axis:
      distance: 0.25
      axis: world_x
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    force_limit:
      type: scalar
      range:
      - 40.0
      - 150.0
      default: 90.0
      binds_to:
      - path: guards.safe_force.threshold
        mode: replace
    push_dist:
      type: scalar
      range:
      - 0.05
      - 0.4
      default: 0.25
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
  guards:
  - id: safe_force
    when: during_phase
    predicate: force_below
    threshold: 90.0
    on_failure: continue
  subtask_id: push_open

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_door** (`approach`)
  - target: source=yaml, anchor=task_object, entity=door_panel, offset=[0.0, -0.2, 0.15], tolerance=0.05
  - orientation: mode=none
  - parameter_bindings:
    - app_y: status=consumed; consumers=target.offset.y (replace)
- **contact_door** (`contact`)
  - target: source=yaml, anchor=task_object, entity=door_panel, offset=[0.0, -0.08, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_door** (`push`)
  - target: source=yaml, anchor=task_object, entity=door_panel, offset=[0.0, -0.08, 0.05], offset_along_axis={axis=world_x, distance=0.25, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_limit: status=consumed; consumers=guards.safe_force.threshold (replace)
    - push_dist: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=safe_force, when=during_phase, predicate=force_below, on_failure=continue, threshold=90.0

## Design Metrics

- **Composite score**: 0.892
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_door | 0.00 | 0.33 | 0.5146 |
| contact_door | 0.67 | 0.67 | 0.0636 |
| push_door | 0.00 | 1.00 | 0.0126 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_door | approach | 0.00 / step_budget | (0.100, 0.399, 0.350)→(0.032, -0.107, 0.392) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.333 | 0.000 | 162.874 |
| contact_door | contact | 0.67 / force_exceeded | (0.032, -0.107, 0.392)→(0.038, -0.128, 0.334) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 3.333 | 41.825 | 0.000 |
| push_door | push | 0.00 / guard_failure | (0.038, -0.128, 0.334)→(0.044, -0.122, 0.343) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.667 | 56.339 | 152.409 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.333

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.003
- **K-run variance**: 0.0247
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.280


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.72388,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_door.app_speed":0.13587,"approach_door.app_y":-0.29261,"contact_door.contact_force":7.19149,"push_door.force_limit":148.98923,"push_door.push_dist":0.35197,"push_door.push_speed":0.07955},"optimized_scores":{"best_composite_score":0.67,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.23971,-0.10418,0.31082],"force_p95":152.16178,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":156.29361,"mean_force":114.83594,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.07635,-0.14649,0.24044]},{"body_a":"door_panel","body_b":"link6","contact_count":215.0,"contact_point_centroid":[0.18579,-0.01827,0.40815],"force_p95":33.83785,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.99332,"mean_force":20.34544,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.07222,-0.03827,0.38473]},{"body_a":"door_panel","body_b":"link7","contact_count":214.0,"contact_point_centroid":[0.12815,0.07889,0.38165],"force_p95":33.19889,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.25741,"mean_force":18.56272,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.06052,0.11585,0.34238]},{"body_a":"world","body_b":"door_panel","contact_count":852.0,"contact_point_centroid":[0.32446,0.11616,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.06732,0.08578,0.35831]},{"body_a":"world","body_b":"door_panel","contact_count":716.0,"contact_point_centroid":[0.37341,0.04486,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_door","phase_type":"contact","tcp_position_centroid":[0.05666,-0.14804,0.29806]},{"body_a":"world","body_b":"door_panel","contact_count":80.0,"contact_point_centroid":[0.37008,0.04762,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.06968,-0.15426,0.22742]}],"total_contact_groups":6},"final_pose_error":0.24906,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.07655,-0.14606,0.24108],"hinge_angle":0.81273,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":156.29361,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_door","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1281.0,"raw_peak_contact_force":83.99332,"subtask_id":"reach_door","tcp_end":[0.04821,-0.12757,0.35079],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.37637,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_door","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":716.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_door","tcp_end":[0.06064,-0.163,0.21191],"tcp_start":[0.04821,-0.12757,0.35079],"tcp_to_object_dist_end":0.27414,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":86.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":26.26652,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":84.0,"raw_peak_contact_force":156.29361,"subtask_id":"push_open","tcp_end":[0.07655,-0.14606,0.24108],"tcp_start":[0.06064,-0.163,0.21191],"tcp_to_object_dist_end":0.29209,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2fe1c8aab50c64fd16f940100e2036790f2ea8f75271c649e6989441e8f9191e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.57658,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_door.app_speed":0.12543,"approach_door.app_y":-0.09557,"contact_door.contact_force":6.22028,"push_door.force_limit":122.97853,"push_door.push_dist":0.34347,"push_door.push_speed":0.06393},"optimized_scores":{"best_composite_score":1.00333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link1","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.02543,0.01962,0.37815],"force_p95":320.73055,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":324.71507,"mean_force":276.63455,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.02566,-0.00026,0.41267]},{"body_a":"link2","body_b":"link7","contact_count":342.0,"contact_point_centroid":[0.0072,0.0664,0.35078],"force_p95":196.07466,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":263.23737,"mean_force":129.93552,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.03036,0.05351,0.36253]},{"body_a":"link1","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.0189,-0.06525,0.38391],"force_p95":136.72449,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":139.18552,"mean_force":93.32304,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.00081,-0.09767,0.41959]},{"body_a":"door_panel","body_b":"link6","contact_count":49.0,"contact_point_centroid":[0.13102,0.04725,0.46741],"force_p95":51.50378,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.12837,"mean_force":35.48076,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.01052,-0.03389,0.42976]},{"body_a":"door_panel","body_b":"link7","contact_count":158.0,"contact_point_centroid":[0.11661,0.13649,0.37389],"force_p95":32.83593,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.57485,"mean_force":19.69332,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.05315,0.17328,0.32958]},{"body_a":"world","body_b":"door_panel","contact_count":1052.0,"contact_point_centroid":[0.31091,0.14067,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.03933,0.10506,0.35715]},{"body_a":"world","body_b":"door_panel","contact_count":624.0,"contact_point_centroid":[0.3311,0.09243,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_door","phase_type":"contact","tcp_position_centroid":[-0.00431,-0.08106,0.43675]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.33013,0.09395,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.00079,-0.09769,0.41958]}],"total_contact_groups":8},"final_pose_error":0.20318,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.00083,-0.09759,0.41968],"hinge_angle":0.50804,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":324.71507,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_door","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1610.0,"raw_peak_contact_force":324.71507,"subtask_id":"reach_door","tcp_end":[-0.00159,-0.07625,0.44659],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.45306,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":713.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.93156,"phase_name":"contact_door","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":624.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_door","tcp_end":[0.00079,-0.09769,0.41958],"tcp_start":[-0.00159,-0.07625,0.44659],"tcp_to_object_dist_end":0.4308,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":139.18552,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":139.18552,"subtask_id":"push_open","tcp_end":[0.00083,-0.09759,0.41968],"tcp_start":[0.00079,-0.09769,0.41958],"tcp_to_object_dist_end":0.43088,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `356d1c9659b48b76a1cff255b134bf18d0729848f67621b991467785bdaaef44`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.16667,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_door.app_speed":0.1289,"approach_door.app_y":-0.20382,"contact_door.contact_force":5.75089,"push_door.force_limit":109.96972,"push_door.push_dist":0.25698,"push_door.push_speed":0.05348},"optimized_scores":{"best_composite_score":1.00333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.22539,-0.09084,0.41924],"force_p95":155.42018,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":161.74696,"mean_force":114.23099,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.05356,-0.12306,0.36971]},{"body_a":"door_panel","body_b":"link6","contact_count":218.0,"contact_point_centroid":[0.16798,-0.00412,0.41406],"force_p95":35.5613,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.91287,"mean_force":20.6252,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.06336,-0.02787,0.39301]},{"body_a":"door_panel","body_b":"link7","contact_count":160.0,"contact_point_centroid":[0.12201,0.07962,0.37613],"force_p95":30.23787,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.03979,"mean_force":16.72825,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.05215,0.11197,0.33733]},{"body_a":"world","body_b":"door_panel","contact_count":976.0,"contact_point_centroid":[0.31918,0.12154,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.06075,0.1019,0.3599]},{"body_a":"world","body_b":"door_panel","contact_count":188.0,"contact_point_centroid":[0.37069,0.0471,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_door","phase_type":"contact","tcp_position_centroid":[0.05166,-0.11912,0.37518]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.36998,0.0477,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.05358,-0.12314,0.36971]}],"total_contact_groups":6},"final_pose_error":0.18525,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.05349,-0.12284,0.36973],"hinge_angle":0.81398,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":161.74696,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_door","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1354.0,"raw_peak_contact_force":79.91287,"subtask_id":"reach_door","tcp_end":[0.05019,-0.11606,0.37932],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.39984,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":231.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":110.54397,"phase_name":"contact_door","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":188.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_door","tcp_end":[0.05358,-0.12314,0.36971],"tcp_start":[0.05019,-0.11606,0.37932],"tcp_to_object_dist_end":0.39335,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":3.5643,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":7.0,"raw_peak_contact_force":161.74696,"subtask_id":"push_open","tcp_end":[0.05349,-0.12284,0.36973],"tcp_start":[0.05358,-0.12314,0.36971],"tcp_to_object_dist_end":0.39325,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```