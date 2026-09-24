## Search State

- **Seed**: 6
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | 3 | 1.0160 | 0.85 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.7950 | 0.88 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.8841 | 0.88 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.7954 | 0.88 | ✅ accepted |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.7908 | 0.87 | ❌ rejected |

**Proposal policy**: task_score is 0.85 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=1.016) — your mutation base

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

- **Composite score**: 1.016
- **task_score** (E): 0.845
- **fitness_score**: 0.726  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2901 |
| contact_1 | 1.00 | 1.00 | 0.0391 |
| push_1 | 1.00 | 1.00 | 0.1542 |
| retract_1 | 1.00 | 1.00 | 0.1552 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.104, 0.032) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.496, 0.104, 0.032)→(0.495, 0.066, 0.021) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 5.000 | 20.302 | 0.245 |
| push_1 | push | 1.00 / time_limit | (0.495, 0.066, 0.021)→(0.494, -0.088, 0.019) | (0.500, 0.029, 0.025)→(0.492, -0.124, 0.025) | 0.180→0.031 | 1.00 / 2.667 | 1.591 | 68.695 |
| retract_1 | retract | 1.00 / time_limit | (0.494, -0.088, 0.019)→(0.491, -0.087, 0.174) | (0.492, -0.124, 0.025)→(0.492, -0.125, 0.025) | 0.031→0.031 | 1.00 / 4.000 | 0.245 | 16.947 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.842
- goal_progress: 0.955
- terminal_score: 0.955
- phase_score: 0.808
- phase_breakdown.push_score: 0.828
- phase_breakdown.approach_score: 0.822
- phase_breakdown.contact_score: 0.764

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.867
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.955
- **Median Q (composite search score)**: 0.976
- **K-run variance**: 0.0105
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Parameters at upper bound**: push_1.push_speed
- **Final σ (mean)**: 0.410


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79167,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":12.60816,"push_1.push_depth":0.00561,"push_1.push_speed":0.09464},"optimized_scores":{"best_composite_score":1.15681,"best_fitness_score":0.86681,"best_task_score":0.95533},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1352.0,"contact_point_centroid":[0.50646,-0.0996,-0.0001],"force_p95":48.80871,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":66.35737,"mean_force":15.54506,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49696,-0.0495,0.01965]},{"body_a":"attachment","body_b":"push_box","contact_count":846.0,"contact_point_centroid":[0.50934,-0.05681,0.04181],"force_p95":41.15882,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.2054,"mean_force":16.33799,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49706,-0.04531,0.01965]},{"body_a":"push_box","body_b":"link7","contact_count":479.0,"contact_point_centroid":[0.52428,-0.03929,0.05211],"force_p95":39.47915,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.18355,"mean_force":26.55901,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49789,-0.01715,0.01986]},{"body_a":"push_box","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.52391,-0.13372,0.05001],"force_p95":7.94866,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.33705,"mean_force":4.70677,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49379,-0.11836,0.01971]},{"body_a":"world","body_b":"push_box","contact_count":3954.0,"contact_point_centroid":[0.49889,-0.15583,-1e-05],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.13072,"mean_force":0.27093,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49224,-0.11782,0.09296]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.49561,-0.13054,0.01983],"force_p95":2.9048,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.99166,"mean_force":2.12308,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49558,-0.11855,0.01982]},{"body_a":"world","body_b":"push_box","contact_count":3492.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49925,0.02864,0.16605]},{"body_a":"world","body_b":"push_box","contact_count":1880.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49822,0.03751,0.02514]}],"total_contact_groups":8},"final_pose_error":0.04507,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49899,-0.15578,0.02499],"final_tcp_position":[0.49268,-0.11785,0.17488],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":66.35737,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":873.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3492.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.50028,0.0578,0.03311],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":470.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":18.48507,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1880.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49958,0.01814,0.0213],"tcp_start":[0.50028,0.0578,0.03311],"tcp_to_object_dist_end":0.03747,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":902.0,"n_steps_budget":960.0,"object_pos_end":[0.49966,-0.15546,0.02493],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00547,"object_to_goal_dist_start":0.13127,"object_z_max":0.02771,"peak_contact_force":1.59203,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2677.0,"raw_peak_contact_force":66.35737,"subtask_id":"push","tcp_end":[0.49565,-0.11842,0.01985],"tcp_start":[0.49958,0.01814,0.0213],"tcp_to_object_dist_end":0.0376,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49899,-0.15578,0.02499],"object_pos_start":[0.49966,-0.15546,0.02493],"object_to_goal_dist_end":0.00586,"object_to_goal_dist_start":0.00547,"object_z_max":0.02514,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3975.0,"raw_peak_contact_force":24.33705,"tcp_end":[0.49268,-0.11785,0.17488],"tcp_start":[0.49565,-0.11842,0.01985],"tcp_to_object_dist_end":0.15475,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80263,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":8.23705,"push_1.push_depth":0.05979,"push_1.push_speed":0.1},"optimized_scores":{"best_composite_score":0.976,"best_fitness_score":0.686,"best_task_score":0.83129},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1486.0,"contact_point_centroid":[0.51748,-0.04558,-0.00014],"force_p95":58.51783,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.08456,"mean_force":27.68321,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50415,0.0098,0.02009]},{"body_a":"push_box","body_b":"link7","contact_count":779.0,"contact_point_centroid":[0.53084,0.00229,0.05325],"force_p95":54.75923,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.29841,"mean_force":35.64091,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50515,0.02273,0.02026]},{"body_a":"attachment","body_b":"push_box","contact_count":951.0,"contact_point_centroid":[0.5193,-0.00158,0.04598],"force_p95":58.30329,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.93914,"mean_force":29.44855,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50399,0.00924,0.01997]},{"body_a":"push_box","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.52256,-0.09271,0.04988],"force_p95":7.26042,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.1755,"mean_force":5.40046,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49502,-0.07917,0.01846]},{"body_a":"world","body_b":"push_box","contact_count":3977.0,"contact_point_centroid":[0.49737,-0.11666,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.63466,"mean_force":0.27808,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49333,-0.07856,0.09131]},{"body_a":"world","body_b":"push_box","contact_count":3960.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50423,0.06072,0.1639]},{"body_a":"world","body_b":"push_box","contact_count":1832.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50835,0.10239,0.02374]}],"total_contact_groups":7},"final_pose_error":0.04498,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49748,-0.11665,0.02499],"final_tcp_position":[0.49375,-0.07855,0.17366],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":83.08456,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":990.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3960.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51027,0.12151,0.03099],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":458.0,"n_steps_budget":600.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":21.47595,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1832.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.50982,0.08463,0.02081],"tcp_start":[0.51027,0.12151,0.03099],"tcp_to_object_dist_end":0.03756,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4978,-0.11597,0.02494],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.0341,"object_to_goal_dist_start":0.19823,"object_z_max":0.02865,"peak_contact_force":2.14331,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3216.0,"raw_peak_contact_force":83.08456,"subtask_id":"push","tcp_end":[0.49676,-0.07891,0.01854],"tcp_start":[0.50982,0.08463,0.02081],"tcp_to_object_dist_end":0.03762,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49748,-0.11665,0.02499],"object_pos_start":[0.4978,-0.11597,0.02494],"object_to_goal_dist_end":0.03344,"object_to_goal_dist_start":0.0341,"object_z_max":0.02513,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":23.1755,"tcp_end":[0.49375,-0.07855,0.17366],"tcp_start":[0.49676,-0.07891,0.01854],"tcp_to_object_dist_end":0.15352,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80392,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":5.09715,"push_1.push_depth":0.03514,"push_1.push_speed":0.09969},"optimized_scores":{"best_composite_score":0.91511,"best_fitness_score":0.62511,"best_task_score":0.74862},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1587.0,"contact_point_centroid":[0.48289,-0.0303,-6e-05],"force_p95":40.73392,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.64355,"mean_force":7.78358,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48043,0.01495,0.01882]},{"body_a":"attachment","body_b":"push_box","contact_count":902.0,"contact_point_centroid":[0.48534,0.00799,0.02852],"force_p95":32.13451,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.98516,"mean_force":9.57725,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47998,0.01959,0.01885]},{"body_a":"push_box","body_b":"link7","contact_count":276.0,"contact_point_centroid":[0.50306,0.05012,0.05086],"force_p95":31.57644,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.10654,"mean_force":20.55063,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47513,0.07263,0.0195]},{"body_a":"attachment","body_b":"push_box","contact_count":11.0,"contact_point_centroid":[0.48405,-0.07743,0.02113],"force_p95":2.34107,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.32992,"mean_force":0.99163,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48669,-0.06581,0.01975]},{"body_a":"world","body_b":"push_box","contact_count":3968.0,"contact_point_centroid":[0.47839,-0.10212,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.50616,"mean_force":0.24803,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48573,-0.06542,0.09211]},{"body_a":"world","body_b":"push_box","contact_count":3972.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48715,0.06586,0.16416]},{"body_a":"world","body_b":"push_box","contact_count":1816.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47369,0.11284,0.02458]}],"total_contact_groups":7},"final_pose_error":0.04483,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47837,-0.10198,0.02499],"final_tcp_position":[0.48614,-0.0654,0.17431],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":56.64355,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3972.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.47614,0.13178,0.03157],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":454.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":20.94631,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1816.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.4745,0.09544,0.02151],"tcp_start":[0.47614,0.13178,0.03157],"tcp_to_object_dist_end":0.03743,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.479,-0.10124,0.025],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.05309,"object_to_goal_dist_start":0.2095,"object_z_max":0.0267,"peak_contact_force":1.03726,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2765.0,"raw_peak_contact_force":56.64355,"subtask_id":"push","tcp_end":[0.48914,-0.0657,0.01904],"tcp_start":[0.4745,0.09544,0.02151],"tcp_to_object_dist_end":0.03743,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47837,-0.10198,0.02499],"object_pos_start":[0.479,-0.10124,0.025],"object_to_goal_dist_end":0.05267,"object_to_goal_dist_start":0.05309,"object_z_max":0.02504,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3979.0,"raw_peak_contact_force":3.32992,"tcp_end":[0.48614,-0.0654,0.17431],"tcp_start":[0.48914,-0.0657,0.01904],"tcp_to_object_dist_end":0.15394,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```