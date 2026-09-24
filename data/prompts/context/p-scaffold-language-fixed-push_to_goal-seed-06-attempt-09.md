## Search State

- **Seed**: 6
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | 0.0894 | 0.17 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | 0.1487 | 0.30 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | 0.0577 | 0.34 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3078 | 0.88 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.5115 | 0.95 | ✅ accepted |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: push_to_goal
- Frozen realised-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`
- Frozen object start: [0.5045797221766332, -0.01880749562239939, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5045797221766332, -0.01880749562239939, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: push_box
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.05, 0.05, 0.05]
    mass_kg: 0.1
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5046, -0.0188, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5045797221766332, -0.01880749562239939, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0046, -0.1312, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.08, 0.00) | distance | — |
| contact | object | (0.00, 0.03, 0.00) | distance | — |
| push | goal | (0.00, 0.03, 0.00) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.089) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach
  anchor: object
  offset:
  - 0.0
  - 0.08
  - 0.0
- id: contact
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.0
- id: push
  offset:
  - 0.0
  - 0.03
  - 0.0
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.08
    - 0.05
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset.z
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
  subtask_id: approach
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.03
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.08, 0.05], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.03, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.089
- **task_score** (E): 0.168
- **fitness_score**: 0.099  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2009 |
| contact_1 | 1.00 | 1.00 | 0.0001 |
| push_1 | 1.00 | 1.00 | 0.0001 |
| retract_1 | 1.00 | 1.00 | 0.0537 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.107, 0.132) | (0.500, 0.029, 0.025)→(0.500, 0.036, 0.027) | 0.180→0.186 | 1.00 / 4.667 | 189.431 | 264.756 |
| contact_1 | contact | 1.00 / force_exceeded | (0.496, 0.107, 0.132)→(0.496, 0.107, 0.132) | (0.500, 0.036, 0.027)→(0.500, 0.036, 0.027) | 0.186→0.186 | 1.00 / 4.667 | 64.638 | 64.638 |
| push_1 | push | 1.00 / force_exceeded | (0.496, 0.107, 0.132)→(0.496, 0.107, 0.132) | (0.500, 0.036, 0.027)→(0.500, 0.036, 0.027) | 0.186→0.186 | 1.00 / 4.667 | 118.772 | 118.772 |
| retract_1 | retract | 1.00 / step_budget | (0.496, 0.107, 0.132)→(0.499, 0.055, 0.144) | (0.500, 0.036, 0.027)→(0.502, 0.002, 0.032) | 0.186→0.153 | 1.00 / 2.333 | 11.540 | 108.985 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.327
- lateral_force_integral: None
- approach_alignment: 0.444
- goal_progress: 0.309
- terminal_score: 0.309
- phase_score: 0.052
- phase_breakdown.push_score: 0.010
- phase_breakdown.approach_score: 0.120
- phase_breakdown.contact_score: 0.078

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.155
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.309
- **Median Q (composite search score)**: 0.063
- **K-run variance**: 0.0015
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.262


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `acf3715aaa310bcc73047d49f01e71bc863ef036ae437b7dc851a0f6d3fe40ae`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec1d0331416d42e6883eeb3b72499fac99c0735b785eb70ece69dc94e8044fc3`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08108,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06424,"approach_1.speed":0.01054,"contact_1.contact_force":7.1344,"contact_1.speed":0.03458,"push_1.push_depth":0.1646,"push_1.push_force_threshold":13.36077,"push_1.speed":0.03066,"retract_1.retract_height":0.11773,"retract_1.speed":0.06938},"optimized_scores":{"best_composite_score":0.14481,"best_fitness_score":0.15481,"best_task_score":0.30854},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":446.0,"contact_point_centroid":[0.49652,0.01149,0.04681],"force_p95":258.59712,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":280.81799,"mean_force":147.07649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49818,0.06849,0.13713]},{"body_a":"world","body_b":"push_box","contact_count":2826.0,"contact_point_centroid":[0.50435,-0.01284,-0.00022],"force_p95":117.54605,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":183.43417,"mean_force":24.24299,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49244,0.03332,0.1879]},{"body_a":"push_box","body_b":"link7","contact_count":207.0,"contact_point_centroid":[0.49936,-0.00481,0.04415],"force_p95":83.75323,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":112.39211,"mean_force":46.50436,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49735,0.04987,0.13682]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50643,-0.00093,0.06684],"force_p95":110.87896,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":110.87896,"mean_force":110.87896,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49419,0.08,0.12882]},{"body_a":"push_box","body_b":"link6","contact_count":81.0,"contact_point_centroid":[0.49988,-0.00371,0.06586],"force_p95":101.56987,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":102.93563,"mean_force":78.56453,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49312,0.08039,0.12931]},{"body_a":"push_box","body_b":"link6","contact_count":45.0,"contact_point_centroid":[0.50095,-0.00836,0.06693],"force_p95":75.31307,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":86.33664,"mean_force":24.65998,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49456,0.07553,0.13067]},{"body_a":"push_box","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.50097,-0.00413,0.06538],"force_p95":84.53092,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.53092,"mean_force":84.53092,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49419,0.08,0.12882]},{"body_a":"world","body_b":"push_box","contact_count":328.0,"contact_point_centroid":[0.50778,-0.02918,-0.00025],"force_p95":52.59611,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.38863,"mean_force":29.63759,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49788,0.04589,0.13792]},{"body_a":"world","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.50503,-0.00272,-0.00068],"force_p95":52.7061,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.46569,"mean_force":36.86979,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49418,0.07998,0.12881]},{"body_a":"world","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.50504,-0.00274,-0.00068],"force_p95":53.17453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.2315,"mean_force":52.66182,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49419,0.08,0.12882]},{"body_a":"push_box","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.50096,-0.00417,0.06539],"force_p95":52.87671,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.87671,"mean_force":52.87671,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49418,0.07998,0.12881]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.49468,0.03118,0.03155],"force_p95":47.31933,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.31933,"mean_force":47.31933,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49418,0.07998,0.12881]}],"total_contact_groups":12},"final_pose_error":0.01968,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51483,-0.06047,0.027],"final_tcp_position":[0.5022,0.0171,0.14638],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":280.81799,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":879.0,"n_steps_budget":1000.0,"object_pos_end":[0.50512,-0.00165,0.03398],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.14871,"object_to_goal_dist_start":0.13127,"object_z_max":0.03516,"peak_contact_force":86.11721,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3353.0,"raw_peak_contact_force":280.81799,"subtask_id":"approach","tcp_end":[0.49418,0.07998,0.12881],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50512,-0.00163,0.03399],"object_pos_start":[0.50512,-0.00165,0.03398],"object_to_goal_dist_end":0.14873,"object_to_goal_dist_start":0.14871,"object_z_max":0.03398,"peak_contact_force":54.46569,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":54.46569,"subtask_id":"contact","tcp_end":[0.49419,0.08,0.12882],"tcp_start":[0.49418,0.07998,0.12881],"tcp_to_object_dist_end":0.1256,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50511,-0.00162,0.03399],"object_pos_start":[0.50512,-0.00163,0.03399],"object_to_goal_dist_end":0.14874,"object_to_goal_dist_start":0.14873,"object_z_max":0.03399,"peak_contact_force":110.87896,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":110.87896,"subtask_id":"push","tcp_end":[0.4942,0.08002,0.12884],"tcp_start":[0.49419,0.08,0.12882],"tcp_to_object_dist_end":0.12562,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":207.0,"n_steps_budget":780.0,"object_pos_end":[0.51483,-0.06047,0.027],"object_pos_start":[0.50511,-0.00162,0.03399],"object_to_goal_dist_end":0.09077,"object_to_goal_dist_start":0.14874,"object_z_max":0.03606,"peak_contact_force":21.85996,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":580.0,"raw_peak_contact_force":112.39211,"tcp_end":[0.5022,0.0171,0.14638],"tcp_start":[0.4942,0.08002,0.12884],"tcp_to_object_dist_end":0.14293,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `589e611c6c27578474525e3fd29be4fb5907d8bbd5d1ca44922bfd811e342c78`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.99329,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09286,"approach_1.speed":0.04422,"contact_1.contact_force":11.21198,"contact_1.speed":0.02122,"push_1.push_depth":0.12174,"push_1.push_force_threshold":13.11139,"push_1.speed":0.04266,"retract_1.retract_height":0.12368,"retract_1.speed":0.03171},"optimized_scores":{"best_composite_score":0.06343,"best_fitness_score":0.07343,"best_task_score":0.10179},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":26.0,"contact_point_centroid":[0.50696,0.0488,0.04826],"force_p95":262.02573,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":271.21985,"mean_force":209.78479,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51198,0.11266,0.13535]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.51278,0.05068,0.04694],"force_p95":157.25878,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":157.25878,"mean_force":157.25878,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51381,0.11514,0.13319]},{"body_a":"world","body_b":"push_box","contact_count":2140.0,"contact_point_centroid":[0.51503,0.04768,-2e-05],"force_p95":0.24534,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":135.52316,"mean_force":2.81059,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49441,0.04426,0.2165]},{"body_a":"push_box","body_b":"link7","contact_count":161.0,"contact_point_centroid":[0.50171,0.03796,0.05204],"force_p95":88.95915,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":124.88128,"mean_force":60.44635,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51416,0.09535,0.13909]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.51591,0.04854,-0.00044],"force_p95":74.23992,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.4597,"mean_force":39.82045,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51381,0.11514,0.13319]},{"body_a":"world","body_b":"push_box","contact_count":325.0,"contact_point_centroid":[0.51244,0.0275,-0.00034],"force_p95":59.90321,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.13683,"mean_force":30.43094,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51409,0.09919,0.13829]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.49393,0.05391,0.04695],"force_p95":47.02681,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.02681,"mean_force":47.02681,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51393,0.115,0.13322]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.51588,0.04851,-0.00051],"force_p95":38.56174,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.03512,"mean_force":12.89526,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51393,0.115,0.13322]}],"total_contact_groups":8},"final_pose_error":0.01964,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51346,0.02725,0.03532],"final_tcp_position":[0.51429,0.06782,0.14254],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":271.21985,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":535.0,"n_steps_budget":1000.0,"object_pos_end":[0.51601,0.04892,0.02398],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19956,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":244.78217,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2166.0,"raw_peak_contact_force":271.21985,"subtask_id":"approach","tcp_end":[0.51393,0.115,0.13322],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12769,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51588,0.04896,0.02412],"object_pos_start":[0.51601,0.04892,0.02398],"object_to_goal_dist_end":0.19959,"object_to_goal_dist_start":0.19956,"object_z_max":0.02398,"peak_contact_force":47.02681,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":47.02681,"subtask_id":"contact","tcp_end":[0.51381,0.11514,0.13319],"tcp_start":[0.51393,0.115,0.13322],"tcp_to_object_dist_end":0.1276,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51581,0.04898,0.02423],"object_pos_start":[0.51588,0.04896,0.02412],"object_to_goal_dist_end":0.19961,"object_to_goal_dist_start":0.19959,"object_z_max":0.02412,"peak_contact_force":157.25878,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":157.25878,"subtask_id":"push","tcp_end":[0.51372,0.11525,0.13317],"tcp_start":[0.51381,0.11514,0.13319],"tcp_to_object_dist_end":0.12753,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":161.0,"n_steps_budget":1000.0,"object_pos_end":[0.51346,0.02725,0.03532],"object_pos_start":[0.51581,0.04898,0.02423],"object_to_goal_dist_end":0.17806,"object_to_goal_dist_start":0.19961,"object_z_max":0.03524,"peak_contact_force":1.62422,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":486.0,"raw_peak_contact_force":124.88128,"tcp_end":[0.51429,0.06782,0.14254],"tcp_start":[0.51372,0.11525,0.13317],"tcp_to_object_dist_end":0.11465,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f2c9c63f0d9eca1b3ff8bf951759f6a3adee73f9f65e1cd3613c5e9d1203ebcc`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.99387,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09429,"approach_1.speed":0.03252,"contact_1.contact_force":18.91693,"contact_1.speed":0.02099,"push_1.push_depth":0.12904,"push_1.push_force_threshold":17.3751,"push_1.speed":0.03297,"retract_1.retract_height":0.12108,"retract_1.speed":0.03337},"optimized_scores":{"best_composite_score":0.05988,"best_fitness_score":0.06988,"best_task_score":0.09446},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.47483,0.05924,0.0485],"force_p95":237.63545,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":242.23003,"mean_force":191.87545,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48002,0.12307,0.13572]},{"body_a":"world","body_b":"push_box","contact_count":2160.0,"contact_point_centroid":[0.47924,0.05848,-1e-05],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":129.45284,"mean_force":2.03359,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48097,0.04833,0.21736]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47977,0.06058,0.04733],"force_p95":92.42167,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":92.42167,"mean_force":92.42167,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48089,0.12508,0.1339]},{"body_a":"push_box","body_b":"link7","contact_count":153.0,"contact_point_centroid":[0.46849,0.04844,0.05194],"force_p95":89.27661,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":89.68167,"mean_force":66.55807,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48055,0.10573,0.13906]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47979,0.06075,0.04734],"force_p95":88.17765,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":88.17765,"mean_force":88.17765,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48089,0.12522,0.1339]},{"body_a":"world","body_b":"push_box","contact_count":317.0,"contact_point_centroid":[0.47654,0.0379,-0.00035],"force_p95":62.15606,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":79.32826,"mean_force":32.62071,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48063,0.10972,0.1383]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.47966,0.05916,-0.00042],"force_p95":62.04738,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.50532,"mean_force":23.48942,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48089,0.12508,0.1339]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.47967,0.05919,-0.0004],"force_p95":42.36581,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.84012,"mean_force":22.33601,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48089,0.12522,0.1339]}],"total_contact_groups":8},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47622,0.03795,0.03507],"final_tcp_position":[0.47973,0.07901,0.1419],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":242.23003,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":540.0,"n_steps_budget":1000.0,"object_pos_end":[0.4798,0.05953,0.02415],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2105,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":237.39363,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2180.0,"raw_peak_contact_force":242.23003,"subtask_id":"approach","tcp_end":[0.48089,0.12508,0.1339],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12784,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.47973,0.05958,0.02419],"object_pos_start":[0.4798,0.05953,0.02415],"object_to_goal_dist_end":0.21055,"object_to_goal_dist_start":0.2105,"object_z_max":0.02415,"peak_contact_force":92.42167,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":92.42167,"subtask_id":"contact","tcp_end":[0.48089,0.12522,0.1339],"tcp_start":[0.48089,0.12508,0.1339],"tcp_to_object_dist_end":0.12785,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.47965,0.0596,0.02423],"object_pos_start":[0.47973,0.05958,0.02419],"object_to_goal_dist_end":0.21059,"object_to_goal_dist_start":0.21055,"object_z_max":0.02419,"peak_contact_force":88.17765,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":88.17765,"subtask_id":"push","tcp_end":[0.48091,0.12532,0.1339],"tcp_start":[0.48089,0.12522,0.1339],"tcp_to_object_dist_end":0.12787,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":153.0,"n_steps_budget":1000.0,"object_pos_end":[0.47622,0.03795,0.03507],"object_pos_start":[0.47965,0.0596,0.02423],"object_to_goal_dist_end":0.18971,"object_to_goal_dist_start":0.21059,"object_z_max":0.03497,"peak_contact_force":11.13603,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":470.0,"raw_peak_contact_force":89.68167,"tcp_end":[0.47973,0.07901,0.1419],"tcp_start":[0.48091,0.12532,0.1339],"tcp_to_object_dist_end":0.1145,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```