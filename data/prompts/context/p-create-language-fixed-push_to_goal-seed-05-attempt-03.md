## Search State

- **Seed**: 5
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7807 | 0.79 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7687 | 0.80 | ✅ accepted |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7690 | 0.77 | ✅ accepted |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.7823 | 0.77 | ✅ accepted |

**Proposal policy**: task_score is 0.79 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`
- Frozen object start: [0.5366003508494456, 0.03695289476837925, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5366003508494456, 0.03695289476837925, 0.025)
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
  frozen_object_start: [0.5366, 0.037, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5366003508494456, 0.03695289476837925, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0366, -0.187, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266

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

## Current Skill (Q=0.781) — your mutation base

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
    entity: push_box
    offset:
    - 0.0
    - 0.08
    - 0.0
    tolerance: 0.03
    orientation:
      mode: keep_current
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
    orientation:
      mode: keep_current
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
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.03
    - 0.0
    offset_along_axis:
      distance: 0.08
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: push
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.03
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.08, 0.0], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.03, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.03, 0.0], offset_along_axis={axis=world_y, distance=0.08, mode=add_to_offset, sign=negative}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.781
- **task_score** (E): 0.792
- **fitness_score**: 0.791  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2667 |
| contact_1 | 1.00 | 1.00 | 0.0407 |
| push_1 | 1.00 | 1.00 | 0.1839 |
| retract_1 | 1.00 | 1.00 | 0.0704 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.090, 0.051) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.514, 0.090, 0.051)→(0.514, 0.059, 0.025) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 5.000 | 24.267 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.514, 0.059, 0.025)→(0.498, -0.124, 0.020) | (0.519, 0.022, 0.025)→(0.532, -0.143, 0.025) | 0.173→0.036 | 1.00 / 2.000 | 0.426 | 50.852 |
| retract_1 | retract | 1.00 / step_budget | (0.498, -0.124, 0.020)→(0.496, -0.124, 0.091) | (0.532, -0.143, 0.025)→(0.532, -0.145, 0.025) | 0.036→0.038 | 1.00 / 4.000 | 0.245 | 1.674 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.755
- goal_progress: 0.874
- terminal_score: 0.874
- phase_score: 0.788
- phase_breakdown.push_score: 0.890
- phase_breakdown.approach_score: 0.556
- phase_breakdown.contact_score: 0.774

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.822
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.874
- **Median Q (composite search score)**: 0.784
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.306


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `7ff7a4e3a1b03e3d7ba3d0b298d1ee8847b5344eb55f2aa0aaf582e7a98ab8ac`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `028a6956ebe09ab7c7952341570355f52da12e46fb22d3462091c70c024324ff`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35437,"average_solve_count":206.0,"average_success_count":206.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":1.00323,"push_1.push_depth":0.03263,"push_1.push_speed":0.04431,"push_1.push_tolerance":0.02048},"optimized_scores":{"best_composite_score":0.74526,"best_fitness_score":0.75526,"best_task_score":0.70231},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":187.0,"contact_point_centroid":[0.52518,-0.01091,0.03739],"force_p95":31.298,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.55662,"mean_force":5.04166,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51805,-2e-05,0.02101]},{"body_a":"world","body_b":"push_box","contact_count":370.0,"contact_point_centroid":[0.54251,-0.07636,-0.00014],"force_p95":14.10566,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.77906,"mean_force":3.24028,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51216,-0.04192,0.02073]},{"body_a":"push_box","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.54776,-0.05188,0.053],"force_p95":11.63609,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.87073,"mean_force":4.26676,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51097,-0.04758,0.02007]},{"body_a":"world","body_b":"push_box","contact_count":560.0,"contact_point_centroid":[0.55113,-0.12548,-7e-05],"force_p95":0.28523,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64917,"mean_force":0.24805,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4978,-0.12357,0.05299]},{"body_a":"world","body_b":"push_box","contact_count":1564.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51416,0.05016,0.17737]},{"body_a":"world","body_b":"push_box","contact_count":1752.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52857,0.08807,0.03514]}],"total_contact_groups":6},"final_pose_error":0.02974,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55114,-0.12549,0.02499],"final_tcp_position":[0.49771,-0.12292,0.09045],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":46.55662,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":391.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1564.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.5298,0.10327,0.05062],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":438.0,"n_steps_budget":600.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":21.85421,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1752.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.5309,0.07389,0.02493],"tcp_start":[0.5298,0.10327,0.05062],"tcp_to_object_dist_end":0.03737,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":345.0,"n_steps_budget":1000.0,"object_pos_end":[0.55115,-0.12546,0.02431],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.05674,"object_to_goal_dist_start":0.1905,"object_z_max":0.02725,"peak_contact_force":0.79018,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":569.0,"raw_peak_contact_force":46.55662,"subtask_id":"push","tcp_end":[0.50059,-0.12338,0.02004],"tcp_start":[0.5309,0.07389,0.02493],"tcp_to_object_dist_end":0.05078,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":140.0,"n_steps_budget":630.0,"object_pos_end":[0.55114,-0.12549,0.02499],"object_pos_start":[0.55115,-0.12546,0.02431],"object_to_goal_dist_end":0.05671,"object_to_goal_dist_start":0.05674,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":560.0,"raw_peak_contact_force":0.64917,"tcp_end":[0.49771,-0.12292,0.09045],"tcp_start":[0.50059,-0.12338,0.02004],"tcp_to_object_dist_end":0.08453,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1c6409cc6d884b90ecc3937d36e5ea87cc4ef513b6f301a9da66b4e84390f805`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62914,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":8.96298,"push_1.push_depth":0.0342,"push_1.push_speed":0.06726,"push_1.push_tolerance":0.03925},"optimized_scores":{"best_composite_score":0.81245,"best_fitness_score":0.82245,"best_task_score":0.87401},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":196.0,"contact_point_centroid":[0.50006,-0.05997,0.03225],"force_p95":9.43859,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.80438,"mean_force":2.98779,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49745,-0.04807,0.02131]},{"body_a":"world","body_b":"push_box","contact_count":197.0,"contact_point_centroid":[0.50322,-0.09028,-5e-05],"force_p95":14.4514,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.26631,"mean_force":3.5368,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49763,-0.04036,0.0216]},{"body_a":"world","body_b":"push_box","contact_count":516.0,"contact_point_centroid":[0.50481,-0.16641,-6e-05],"force_p95":0.45711,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.74002,"mean_force":0.27126,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49399,-0.12501,0.05538]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.5,-0.1374,0.03505],"force_p95":0.73795,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.80862,"mean_force":0.29874,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49666,-0.12549,0.0201]},{"body_a":"world","body_b":"push_box","contact_count":1432.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50042,0.02603,0.17855]},{"body_a":"world","body_b":"push_box","contact_count":1844.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49889,0.03541,0.03667]}],"total_contact_groups":6},"final_pose_error":0.02995,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5049,-0.1658,0.02499],"final_tcp_position":[0.49395,-0.12443,0.09029],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":49.80438,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":358.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1432.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.50136,0.05356,0.05315],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":461.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":27.10137,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1844.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49997,0.01817,0.02505],"tcp_start":[0.50136,0.05356,0.05315],"tcp_to_object_dist_end":0.03726,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":250.0,"n_steps_budget":1000.0,"object_pos_end":[0.50478,-0.1617,0.02519],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.01264,"object_to_goal_dist_start":0.13127,"object_z_max":0.02616,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":393.0,"raw_peak_contact_force":49.80438,"subtask_id":"push","tcp_end":[0.49679,-0.1249,0.02011],"tcp_start":[0.49997,0.01817,0.02505],"tcp_to_object_dist_end":0.03799,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":139.0,"n_steps_budget":630.0,"object_pos_end":[0.5049,-0.1658,0.02499],"object_pos_start":[0.50478,-0.1617,0.02519],"object_to_goal_dist_end":0.01654,"object_to_goal_dist_start":0.01264,"object_z_max":0.02521,"peak_contact_force":0.24524,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":520.0,"raw_peak_contact_force":1.74002,"tcp_end":[0.49395,-0.12443,0.09029],"tcp_start":[0.49679,-0.1249,0.02011],"tcp_to_object_dist_end":0.07807,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f52ec1899e2888770a8b6b3ae605718303ef4b10e72cfd7d20ce53303721b2b0`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4011,"average_solve_count":182.0,"average_success_count":182.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":3.65382,"push_1.push_depth":0.03298,"push_1.push_speed":0.05947,"push_1.push_tolerance":0.04979},"optimized_scores":{"best_composite_score":0.78444,"best_fitness_score":0.79444,"best_task_score":0.79894},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":218.0,"contact_point_centroid":[0.50901,-0.00294,0.03497],"force_p95":24.84011,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.19646,"mean_force":4.52423,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50414,0.00858,0.02164]},{"body_a":"push_box","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.53738,-0.07377,0.05351],"force_p95":52.06453,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.99094,"mean_force":21.79726,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50025,-0.07284,0.02056]},{"body_a":"world","body_b":"push_box","contact_count":314.0,"contact_point_centroid":[0.52563,-0.05719,-0.0001],"force_p95":25.54982,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.63905,"mean_force":5.32341,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50316,-0.01475,0.0215]},{"body_a":"world","body_b":"push_box","contact_count":528.0,"contact_point_centroid":[0.53762,-0.1435,-0.00013],"force_p95":0.48753,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.63262,"mean_force":0.28088,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4953,-0.12389,0.05511]},{"body_a":"world","body_b":"push_box","contact_count":1568.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50488,0.05494,0.17711]},{"body_a":"world","body_b":"push_box","contact_count":1732.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50856,0.09821,0.03561]}],"total_contact_groups":6},"final_pose_error":0.02959,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5393,-0.14337,0.02499],"final_tcp_position":[0.49525,-0.12331,0.09082],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":56.19646,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":392.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1568.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51069,0.11285,0.05066],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":433.0,"n_steps_budget":600.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":23.84401,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1732.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.50994,0.08463,0.02556],"tcp_start":[0.51069,0.11285,0.05066],"tcp_to_object_dist_end":0.03732,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.5389,-0.14211,0.02541],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.03969,"object_to_goal_dist_start":0.19823,"object_z_max":0.02824,"peak_contact_force":0.48736,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":554.0,"raw_peak_contact_force":56.19646,"subtask_id":"push","tcp_end":[0.49809,-0.12377,0.02028],"tcp_start":[0.50994,0.08463,0.02556],"tcp_to_object_dist_end":0.04503,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":140.0,"n_steps_budget":630.0,"object_pos_end":[0.5393,-0.14337,0.02499],"object_pos_start":[0.5389,-0.14211,0.02541],"object_to_goal_dist_end":0.03986,"object_to_goal_dist_start":0.03969,"object_z_max":0.02541,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":528.0,"raw_peak_contact_force":2.63262,"tcp_end":[0.49525,-0.12331,0.09082],"tcp_start":[0.49809,-0.12377,0.02028],"tcp_to_object_dist_end":0.08171,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```