## Search State

- **Seed**: 6
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.7954 | 0.88 | ✅ accepted |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.7908 | 0.87 | ❌ rejected |
| 2 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 4 | 0.5837 | 0.03 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.7829 | 0.87 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.7955 | 0.88 | ✅ accepted |

**Proposal policy**: task_score is 0.88 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.795) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
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
    - 0.08
    - 0.0
  subtask_id: approach
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
    - 0.03
    - 0.0
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: contact
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.03
    - 0.0
    offset_along_axis:
      distance: 0.0
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
  parameters:
    push_depth:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
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
  subtask_id: push
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.2

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.08, 0.0]
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0]
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.03, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.0, mode=add_to_offset, sign=positive}
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.2]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.795
- **task_score** (E): 0.884
- **fitness_score**: 0.755  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2901 |
| contact_1 | 1.00 | 1.00 | 0.0391 |
| push_1 | 0.67 | 1.00 | 0.1603 |
| retract_1 | 0.33 | 1.00 | 0.1623 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.104, 0.032) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.496, 0.104, 0.032)→(0.495, 0.066, 0.021) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 5.000 | 20.302 | 0.245 |
| push_1 | push | 0.67 / step_budget | (0.495, 0.066, 0.021)→(0.494, -0.094, 0.020) | (0.500, 0.029, 0.025)→(0.498, -0.131, 0.025) | 0.180→0.023 | 1.00 / 3.667 | 6.019 | 59.433 |
| retract_1 | retract | 0.33 / step_budget | (0.494, -0.094, 0.020)→(0.496, -0.137, 0.175) | (0.498, -0.131, 0.025)→(0.496, -0.132, 0.025) | 0.023→0.023 | 1.00 / 4.000 | 0.245 | 13.549 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.883
- goal_progress: 0.951
- terminal_score: 0.951
- phase_score: 0.810
- phase_breakdown.push_score: 0.833
- phase_breakdown.approach_score: 0.822
- phase_breakdown.contact_score: 0.764

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.866
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.951
- **Median Q (composite search score)**: 0.768
- **K-run variance**: 0.0067
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.523


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80132,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":17.01392,"push_1.push_depth":0.00623,"push_1.push_speed":0.08227},"optimized_scores":{"best_composite_score":0.90643,"best_fitness_score":0.86643,"best_task_score":0.95106},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1242.0,"contact_point_centroid":[0.50687,-0.1024,-0.00011],"force_p95":53.15793,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":64.94206,"mean_force":15.99629,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49688,-0.05165,0.01963]},{"body_a":"push_box","body_b":"link7","contact_count":462.0,"contact_point_centroid":[0.52424,-0.04275,0.05203],"force_p95":39.26766,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.27691,"mean_force":25.58707,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49777,-0.02155,0.01985]},{"body_a":"attachment","body_b":"push_box","contact_count":817.0,"contact_point_centroid":[0.5088,-0.05871,0.04084],"force_p95":39.2814,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.51199,"mean_force":15.82396,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49698,-0.04718,0.01963]},{"body_a":"push_box","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.52588,-0.13891,0.05019],"force_p95":32.32342,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.11246,"mean_force":12.99734,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49556,-0.1189,0.0199]},{"body_a":"world","body_b":"push_box","contact_count":3487.0,"contact_point_centroid":[0.49914,-0.15956,-2e-05],"force_p95":0.42578,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.69441,"mean_force":0.29041,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49427,-0.13228,0.10823]},{"body_a":"attachment","body_b":"push_box","contact_count":144.0,"contact_point_centroid":[0.49762,-0.13325,0.04407],"force_p95":0.93981,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.85263,"mean_force":0.60555,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.493,-0.1213,0.03615]},{"body_a":"world","body_b":"push_box","contact_count":3492.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49925,0.02864,0.16605]},{"body_a":"world","body_b":"push_box","contact_count":1880.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49822,0.03751,0.02514]}],"total_contact_groups":8},"final_pose_error":0.04523,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49902,-0.15635,0.02499],"final_tcp_position":[0.49626,-0.1433,0.18043],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":64.94206,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":873.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3492.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.50028,0.0578,0.03311],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":470.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":18.48507,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1880.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49958,0.01814,0.0213],"tcp_start":[0.50028,0.0578,0.03311],"tcp_to_object_dist_end":0.03747,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":879.0,"n_steps_budget":1000.0,"object_pos_end":[0.50133,-0.15552,0.0251],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00568,"object_to_goal_dist_start":0.13127,"object_z_max":0.02814,"peak_contact_force":1.64161,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2521.0,"raw_peak_contact_force":64.94206,"subtask_id":"push","tcp_end":[0.49568,-0.11877,0.01988],"tcp_start":[0.49958,0.01814,0.0213],"tcp_to_object_dist_end":0.03755,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49902,-0.15635,0.02499],"object_pos_start":[0.50133,-0.15552,0.0251],"object_to_goal_dist_end":0.00642,"object_to_goal_dist_start":0.00568,"object_z_max":0.02695,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3636.0,"raw_peak_contact_force":33.11246,"tcp_end":[0.49626,-0.1433,0.18043],"tcp_start":[0.49568,-0.11877,0.01988],"tcp_to_object_dist_end":0.15601,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80769,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":7.21438,"push_1.push_depth":0.01999,"push_1.push_speed":0.09998},"optimized_scores":{"best_composite_score":0.76774,"best_fitness_score":0.72774,"best_task_score":0.87986},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1399.0,"contact_point_centroid":[0.51317,-0.05363,-0.00012],"force_p95":56.90141,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.86374,"mean_force":21.11377,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50316,0.00088,0.01957]},{"body_a":"attachment","body_b":"push_box","contact_count":946.0,"contact_point_centroid":[0.51644,-0.00863,0.04261],"force_p95":53.83392,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.83836,"mean_force":21.98628,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50322,0.00245,0.01953]},{"body_a":"push_box","body_b":"link7","contact_count":635.0,"contact_point_centroid":[0.53075,0.00644,0.05282],"force_p95":47.92316,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.10754,"mean_force":28.2214,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50519,0.02842,0.01984]},{"body_a":"world","body_b":"push_box","contact_count":3359.0,"contact_point_centroid":[0.49804,-0.13035,-3e-05],"force_p95":0.44148,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.09933,"mean_force":0.28555,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49489,-0.11451,0.10497]},{"body_a":"attachment","body_b":"push_box","contact_count":175.0,"contact_point_centroid":[0.49605,-0.10628,0.04052],"force_p95":0.9498,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.0412,"mean_force":0.60786,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49388,-0.09437,0.03872]},{"body_a":"world","body_b":"push_box","contact_count":3960.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50423,0.06072,0.1639]},{"body_a":"world","body_b":"push_box","contact_count":1832.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50835,0.10239,0.02374]}],"total_contact_groups":7},"final_pose_error":0.05446,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4977,-0.1263,0.02499],"final_tcp_position":[0.49632,-0.13505,0.17276],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":75.86374,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":990.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3960.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51027,0.12151,0.03099],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":458.0,"n_steps_budget":600.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":21.47595,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1832.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.50982,0.08463,0.02081],"tcp_start":[0.51027,0.12151,0.03099],"tcp_to_object_dist_end":0.03756,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4995,-0.12444,0.02506],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.02557,"object_to_goal_dist_start":0.19823,"object_z_max":0.02809,"peak_contact_force":2.26083,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2980.0,"raw_peak_contact_force":75.86374,"subtask_id":"push","tcp_end":[0.49694,-0.08759,0.01913],"tcp_start":[0.50982,0.08463,0.02081],"tcp_to_object_dist_end":0.03741,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4977,-0.1263,0.02499],"object_pos_start":[0.4995,-0.12444,0.02506],"object_to_goal_dist_end":0.02382,"object_to_goal_dist_start":0.02557,"object_z_max":0.02941,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3534.0,"raw_peak_contact_force":2.09933,"tcp_end":[0.49632,-0.13505,0.17276],"tcp_start":[0.49694,-0.08759,0.01913],"tcp_to_object_dist_end":0.14804,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81132,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":12.32902,"push_1.push_depth":-0.0143,"push_1.push_speed":0.09368},"optimized_scores":{"best_composite_score":0.71215,"best_fitness_score":0.67215,"best_task_score":0.82032},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1566.0,"contact_point_centroid":[0.4856,-0.03782,-7e-05],"force_p95":28.82528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.49206,"mean_force":6.68298,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4816,0.00729,0.01911]},{"body_a":"attachment","body_b":"push_box","contact_count":922.0,"contact_point_centroid":[0.48929,-0.00056,0.03318],"force_p95":26.01218,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.40144,"mean_force":8.53927,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48117,0.01103,0.01907]},{"body_a":"push_box","body_b":"link7","contact_count":310.0,"contact_point_centroid":[0.50338,0.03611,0.05079],"force_p95":21.7141,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.0773,"mean_force":12.12425,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47638,0.05746,0.01913]},{"body_a":"attachment","body_b":"push_box","contact_count":183.0,"contact_point_centroid":[0.49161,-0.09482,0.04143],"force_p95":1.50756,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.43453,"mean_force":0.64011,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48856,-0.08297,0.03887]},{"body_a":"world","body_b":"push_box","contact_count":3306.0,"contact_point_centroid":[0.49126,-0.11784,-3e-05],"force_p95":0.45512,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.25985,"mean_force":0.29446,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49151,-0.1077,0.10608]},{"body_a":"world","body_b":"push_box","contact_count":3972.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48715,0.06586,0.16416]},{"body_a":"world","body_b":"push_box","contact_count":1816.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47369,0.11284,0.02458]}],"total_contact_groups":7},"final_pose_error":0.05528,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49085,-0.11348,0.02499],"final_tcp_position":[0.49492,-0.13215,0.17292],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":37.49206,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3972.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.47614,0.13178,0.03157],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":454.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":20.94631,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1816.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.4745,0.09544,0.02151],"tcp_start":[0.47614,0.13178,0.03157],"tcp_to_object_dist_end":0.03743,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49385,-0.11166,0.02485],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.03883,"object_to_goal_dist_start":0.2095,"object_z_max":0.02656,"peak_contact_force":14.15318,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2798.0,"raw_peak_contact_force":37.49206,"subtask_id":"push","tcp_end":[0.49082,-0.07487,0.01969],"tcp_start":[0.4745,0.09544,0.02151],"tcp_to_object_dist_end":0.03728,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49085,-0.11348,0.02499],"object_pos_start":[0.49385,-0.11166,0.02485],"object_to_goal_dist_end":0.03764,"object_to_goal_dist_start":0.03883,"object_z_max":0.03066,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3489.0,"raw_peak_contact_force":5.43453,"tcp_end":[0.49492,-0.13215,0.17292],"tcp_start":[0.49082,-0.07487,0.01969],"tcp_to_object_dist_end":0.14916,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```