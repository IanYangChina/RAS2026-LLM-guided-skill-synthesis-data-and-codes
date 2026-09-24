## Search State

- **Seed**: 5
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7477 | 0.83 | ✅ accepted |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 4 | 0.7908 | 0.66 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 4 | 0.7062 | 0.65 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5760 | 0.66 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7533 | 0.78 | ❌ rejected |

**Proposal policy**: task_score is 0.83 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.748) — your mutation base

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
      distance: 0.12
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.04
    orientation:
      mode: keep_current
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.02
      - 0.25
      default: 0.12
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
      - 0.05
      default: 0.04
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
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.03, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.12, mode=add_to_offset, sign=positive}, tolerance=0.04
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

- **Composite score**: 0.748
- **task_score** (E): 0.827
- **fitness_score**: 0.758  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2667 |
| contact_1 | 1.00 | 1.00 | 0.0407 |
| push_1 | 1.00 | 1.00 | 0.1710 |
| retract_1 | 1.00 | 1.00 | 0.0706 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.090, 0.051) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.514, 0.090, 0.051)→(0.514, 0.059, 0.025) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 5.000 | 24.267 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.514, 0.059, 0.025)→(0.497, -0.111, 0.020) | (0.519, 0.022, 0.025)→(0.525, -0.138, 0.025) | 0.173→0.029 | 1.00 / 2.333 | 0.933 | 75.949 |
| retract_1 | retract | 1.00 / step_budget | (0.497, -0.111, 0.020)→(0.495, -0.111, 0.091) | (0.525, -0.138, 0.025)→(0.526, -0.145, 0.025) | 0.029→0.031 | 1.00 / 4.000 | 0.245 | 2.509 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.741
- goal_progress: 0.895
- terminal_score: 0.895
- phase_score: 0.746
- phase_breakdown.push_score: 0.805
- phase_breakdown.approach_score: 0.556
- phase_breakdown.contact_score: 0.774

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.805
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.895
- **Median Q (composite search score)**: 0.749
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.440


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62791,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":12.64662,"push_1.push_depth":0.03156,"push_1.push_speed":0.06573,"push_1.push_tolerance":0.03341},"optimized_scores":{"best_composite_score":0.69835,"best_fitness_score":0.70835,"best_task_score":0.69812},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":78.0,"contact_point_centroid":[0.52681,0.01217,0.0393],"force_p95":47.70501,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.66788,"mean_force":8.99971,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52068,0.02346,0.02175]},{"body_a":"world","body_b":"push_box","contact_count":236.0,"contact_point_centroid":[0.53921,-0.06089,-0.00023],"force_p95":16.26731,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.81205,"mean_force":4.05669,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51268,-0.02351,0.02108]},{"body_a":"push_box","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.54397,-0.05915,0.05333],"force_p95":20.92654,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.4075,"mean_force":4.75732,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50712,-0.05532,0.0203]},{"body_a":"world","body_b":"push_box","contact_count":560.0,"contact_point_centroid":[0.5497,-0.12107,-6e-05],"force_p95":0.25079,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36901,"mean_force":0.24512,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49493,-0.11226,0.05318]},{"body_a":"world","body_b":"push_box","contact_count":1564.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51416,0.05016,0.17737]},{"body_a":"world","body_b":"push_box","contact_count":1752.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52857,0.08807,0.03514]}],"total_contact_groups":6},"final_pose_error":0.02955,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5497,-0.12108,0.02499],"final_tcp_position":[0.49493,-0.11128,0.09075],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":62.66788,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":391.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1564.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.5298,0.10327,0.05062],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":438.0,"n_steps_budget":600.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":21.85421,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1752.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.5309,0.07389,0.02493],"tcp_start":[0.5298,0.10327,0.05062],"tcp_to_object_dist_end":0.03737,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":242.0,"n_steps_budget":1000.0,"object_pos_end":[0.54945,-0.1215,0.02427],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.05708,"object_to_goal_dist_start":0.1905,"object_z_max":0.02839,"peak_contact_force":0.39851,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":334.0,"raw_peak_contact_force":62.66788,"subtask_id":"push","tcp_end":[0.49778,-0.11161,0.02016],"tcp_start":[0.5309,0.07389,0.02493],"tcp_to_object_dist_end":0.05276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":140.0,"n_steps_budget":630.0,"object_pos_end":[0.5497,-0.12108,0.02499],"object_pos_start":[0.54945,-0.1215,0.02427],"object_to_goal_dist_end":0.05751,"object_to_goal_dist_start":0.05708,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":560.0,"raw_peak_contact_force":0.36901,"tcp_end":[0.49493,-0.11128,0.09075],"tcp_start":[0.49778,-0.11161,0.02016],"tcp_to_object_dist_end":0.08614,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13303,"average_solve_count":218.0,"average_success_count":218.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":14.20209,"push_1.push_depth":0.03485,"push_1.push_speed":0.02438,"push_1.push_tolerance":0.03537},"optimized_scores":{"best_composite_score":0.79543,"best_fitness_score":0.80543,"best_task_score":0.89523},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":141.0,"contact_point_centroid":[0.50109,-0.05004,0.03401],"force_p95":16.13797,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.70015,"mean_force":4.00432,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49759,-0.03817,0.0217]},{"body_a":"world","body_b":"push_box","contact_count":128.0,"contact_point_centroid":[0.50739,-0.08126,-5e-05],"force_p95":14.53322,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.0622,"mean_force":5.04822,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49799,-0.02729,0.02227]},{"body_a":"world","body_b":"push_box","contact_count":502.0,"contact_point_centroid":[0.50487,-0.16332,-2e-05],"force_p95":0.48587,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.70821,"mean_force":0.28351,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49349,-0.11625,0.0565]},{"body_a":"world","body_b":"push_box","contact_count":1432.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50042,0.02603,0.17855]},{"body_a":"world","body_b":"push_box","contact_count":1844.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49889,0.03541,0.03667]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.50582,-0.12792,0.05197],"force_p95":0.14646,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15417,"mean_force":0.07708,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49641,-0.11619,0.0202]}],"total_contact_groups":6},"final_pose_error":0.02974,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5051,-0.16277,0.02499],"final_tcp_position":[0.49364,-0.11551,0.09062],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":63.70015,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":358.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1432.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.50136,0.05356,0.05315],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":461.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":27.10137,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1844.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49997,0.01817,0.02505],"tcp_start":[0.50136,0.05356,0.05315],"tcp_to_object_dist_end":0.03726,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":193.0,"n_steps_budget":1000.0,"object_pos_end":[0.50556,-0.15205,0.02614],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00604,"object_to_goal_dist_start":0.13127,"object_z_max":0.02639,"peak_contact_force":0.28453,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":269.0,"raw_peak_contact_force":63.70015,"subtask_id":"push","tcp_end":[0.49649,-0.11588,0.02022],"tcp_start":[0.49997,0.01817,0.02505],"tcp_to_object_dist_end":0.03775,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":140.0,"n_steps_budget":630.0,"object_pos_end":[0.5051,-0.16277,0.02499],"object_pos_start":[0.50556,-0.15205,0.02614],"object_to_goal_dist_end":0.01375,"object_to_goal_dist_start":0.00604,"object_z_max":0.02617,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":504.0,"raw_peak_contact_force":2.70821,"tcp_end":[0.49364,-0.11551,0.09062],"tcp_start":[0.49649,-0.11588,0.02022],"tcp_to_object_dist_end":0.08169,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32579,"average_solve_count":221.0,"average_success_count":221.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":9.42111,"push_1.push_depth":0.02438,"push_1.push_speed":0.03322,"push_1.push_tolerance":0.04592},"optimized_scores":{"best_composite_score":0.74946,"best_fitness_score":0.75946,"best_task_score":0.88803},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.53296,-0.084,0.05428],"force_p95":98.77315,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":101.47907,"mean_force":32.32272,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49901,-0.07884,0.02047]},{"body_a":"world","body_b":"push_box","contact_count":198.0,"contact_point_centroid":[0.51797,-0.03753,-9e-05],"force_p95":28.54192,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.35219,"mean_force":6.04768,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.504,0.00796,0.02198]},{"body_a":"attachment","body_b":"push_box","contact_count":173.0,"contact_point_centroid":[0.5078,-0.01115,0.03455],"force_p95":16.24176,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.18459,"mean_force":3.43582,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50347,0.00043,0.0217]},{"body_a":"world","body_b":"push_box","contact_count":466.0,"contact_point_centroid":[0.52169,-0.15237,-8e-05],"force_p95":0.76553,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44844,"mean_force":0.32623,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49517,-0.10552,0.05949]},{"body_a":"world","body_b":"push_box","contact_count":1568.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50488,0.05494,0.17711]},{"body_a":"world","body_b":"push_box","contact_count":1732.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50856,0.09821,0.03561]}],"total_contact_groups":6},"final_pose_error":0.02952,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52216,-0.1512,0.02499],"final_tcp_position":[0.49524,-0.10487,0.09128],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":101.47907,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":392.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1568.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51069,0.11285,0.05066],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":433.0,"n_steps_budget":600.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":23.84401,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1732.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.50994,0.08463,0.02556],"tcp_start":[0.51069,0.11285,0.05066],"tcp_to_object_dist_end":0.03732,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.5205,-0.14035,0.02574],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.02267,"object_to_goal_dist_start":0.19823,"object_z_max":0.02769,"peak_contact_force":2.11655,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":387.0,"raw_peak_contact_force":101.47907,"subtask_id":"push","tcp_end":[0.49807,-0.10518,0.02066],"tcp_start":[0.50994,0.08463,0.02556],"tcp_to_object_dist_end":0.04203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":140.0,"n_steps_budget":630.0,"object_pos_end":[0.52216,-0.1512,0.02499],"object_pos_start":[0.5205,-0.14035,0.02574],"object_to_goal_dist_end":0.0222,"object_to_goal_dist_start":0.02267,"object_z_max":0.02636,"peak_contact_force":0.24524,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":466.0,"raw_peak_contact_force":4.44844,"tcp_end":[0.49524,-0.10487,0.09128],"tcp_start":[0.49807,-0.10518,0.02066],"tcp_to_object_dist_end":0.08524,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```