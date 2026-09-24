## Search State

- **Seed**: 9
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.9782 | 0.82 | ❌ rejected |
| 5 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.9888 | 0.85 | ✅ accepted |
| 4 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.3700 | 0.00 | ❌ rejected |
| 3 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.3700 | 0.00 | ❌ rejected |
| 2 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.3700 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.82 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`
- Frozen object start: [0.5444299044764102, -0.025581934909493356, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5444299044764102, -0.025581934909493356, 0.025)
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
  frozen_object_start: [0.5444, -0.0256, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5444299044764102, -0.025581934909493356, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0444, -0.1244, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b

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

## Current Skill (Q=0.978) — your mutation base

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
    tolerance: 0.01
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
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 2.0
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
      distance: 0.1
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.0
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.08, 0.0], tolerance=0.01
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.03, 0.0]
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.03, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.02
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.978
- **task_score** (E): 0.816
- **fitness_score**: 0.808  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2770 |
| contact_1 | 1.00 | 1.00 | 0.0383 |
| push_1 | 1.00 | 1.00 | 0.1455 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.513, 0.053, 0.033) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.513, 0.053, 0.033)→(0.513, 0.017, 0.023) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 5.000 | 16.550 | 0.245 |
| push_1 | push | 1.00 / time_limit | (0.513, 0.017, 0.023)→(0.499, -0.122, 0.026) | (0.518, -0.020, 0.025)→(0.520, -0.150, 0.029) | 0.139→0.024 | 1.00 / 3.667 | 99.234 | 123.018 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.683
- goal_progress: 0.962
- terminal_score: 0.962
- phase_score: 0.740
- phase_breakdown.push_score: 0.817
- phase_breakdown.approach_score: 0.505
- phase_breakdown.contact_score: 0.767

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.828
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.962
- **Median Q (composite search score)**: 0.971
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.296


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `327b95871eb659cd41b4cf66bc0b4dfb3b240662e8501854b46ee2b8b86a04c5`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5ffd2bb280d1d50ec9ffd23c1ed75abf73d645c1d10372a9b5bb6e9fac6e0bf8`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83929,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_y":0.08445,"contact_1.contact_force_threshold":4.03781,"contact_1.contact_offset_y":0.02124,"push_1.push_depth":0.08347,"push_1.push_duration":1.61397,"push_1.push_speed":0.09204},"optimized_scores":{"best_composite_score":0.97067,"best_fitness_score":0.80067,"best_task_score":0.74087},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":975.0,"contact_point_centroid":[0.55245,-0.06902,0.05439],"force_p95":136.58869,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":152.59753,"mean_force":84.79761,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51857,-0.05427,0.02409]},{"body_a":"world","body_b":"push_box","contact_count":1973.0,"contact_point_centroid":[0.54582,-0.10031,-0.00035],"force_p95":93.2794,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":112.18642,"mean_force":53.65001,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51894,-0.05319,0.02407]},{"body_a":"attachment","body_b":"push_box","contact_count":992.0,"contact_point_centroid":[0.53775,-0.06165,0.05325],"force_p95":98.40099,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":104.57611,"mean_force":57.36859,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5189,-0.05316,0.02403]},{"body_a":"world","body_b":"push_box","contact_count":3644.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51807,0.02765,0.16527]},{"body_a":"world","body_b":"push_box","contact_count":1728.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53639,0.03401,0.0244]}],"total_contact_groups":5},"final_pose_error":0.0817,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53352,-0.14664,0.03111],"final_tcp_position":[0.50187,-0.12273,0.02964],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":152.59753,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":911.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3644.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.53818,0.05572,0.03191],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08183,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":432.0,"n_steps_budget":600.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":25.19199,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1728.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.53827,0.01136,0.0212],"tcp_start":[0.53818,0.05572,0.03191],"tcp_to_object_dist_end":0.03765,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53352,-0.14664,0.03111],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.03424,"object_to_goal_dist_start":0.13211,"object_z_max":0.03113,"peak_contact_force":141.45057,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3940.0,"raw_peak_contact_force":152.59753,"subtask_id":"push","tcp_end":[0.50187,-0.12273,0.02964],"tcp_start":[0.53827,0.01136,0.0212],"tcp_to_object_dist_end":0.03968,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e094d2c5a71c8b89ef1fa30d7ce553b9c4ed64cd3fbca90620c3ede94e719cec`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55472,-0.03508,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9115,"average_solve_count":113.0,"average_success_count":113.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_y":0.09561,"contact_1.contact_force_threshold":4.46129,"contact_1.contact_offset_y":0.02528,"push_1.push_depth":0.19167,"push_1.push_duration":1.92488,"push_1.push_speed":0.09187},"optimized_scores":{"best_composite_score":0.96563,"best_fitness_score":0.79563,"best_task_score":0.74695},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":976.0,"contact_point_centroid":[0.55825,-0.07588,0.05339],"force_p95":150.05223,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":160.34226,"mean_force":90.76256,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52245,-0.05982,0.02364]},{"body_a":"world","body_b":"push_box","contact_count":2017.0,"contact_point_centroid":[0.55085,-0.10543,-0.00039],"force_p95":100.39604,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":113.62974,"mean_force":54.59453,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52331,-0.05775,0.0235]},{"body_a":"attachment","body_b":"push_box","contact_count":993.0,"contact_point_centroid":[0.54266,-0.06754,0.05592],"force_p95":84.20016,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.77902,"mean_force":52.06701,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52288,-0.05878,0.02357]},{"body_a":"world","body_b":"push_box","contact_count":3704.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52302,0.02853,0.16471]},{"body_a":"world","body_b":"push_box","contact_count":1924.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5466,0.02998,0.02363]}],"total_contact_groups":5},"final_pose_error":0.18692,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53167,-0.1488,0.03077],"final_tcp_position":[0.4988,-0.12476,0.02953],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":160.34226,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":926.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3704.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.54798,0.05733,0.03153],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09289,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":481.0,"n_steps_budget":600.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":14.61081,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1924.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.54896,0.00188,0.02032],"tcp_start":[0.54798,0.05733,0.03153],"tcp_to_object_dist_end":0.0377,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53167,-0.1488,0.03077],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.03221,"object_to_goal_dist_start":0.12728,"object_z_max":0.03086,"peak_contact_force":156.2518,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3986.0,"raw_peak_contact_force":160.34226,"subtask_id":"push","tcp_end":[0.4988,-0.12476,0.02953],"tcp_start":[0.54896,0.00188,0.02032],"tcp_to_object_dist_end":0.04074,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0fd7d18e656259f06515eb57b82afa0c0febd9395a43c1a5f926ddaec3767c64`; realized-scene SHA-256: `5de0d8cc5a3c16249bcf1097af6edba15dfacc79d06e3eed726605dcb01257b0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45543,-9e-05,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04457,-0.14991,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45543,-9e-05,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.04494,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_y":0.05003,"contact_1.contact_force_threshold":1.27889,"contact_1.contact_offset_y":0.01161,"push_1.push_depth":0.00828,"push_1.push_duration":1.63947,"push_1.push_speed":0.16326},"optimized_scores":{"best_composite_score":0.99839,"best_fitness_score":0.82839,"best_task_score":0.96152},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":558.0,"contact_point_centroid":[0.47446,-0.04963,0.02924],"force_p95":26.01573,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.11479,"mean_force":5.01086,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47053,-0.03775,0.02242]},{"body_a":"world","body_b":"push_box","contact_count":1033.0,"contact_point_centroid":[0.47354,-0.07413,-7e-05],"force_p95":11.05867,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.19034,"mean_force":3.09921,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46897,-0.03252,0.02266]},{"body_a":"push_box","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.49309,-0.02387,0.05056],"force_p95":14.25929,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.84921,"mean_force":2.17315,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46078,-0.00725,0.02298]},{"body_a":"world","body_b":"push_box","contact_count":3404.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47618,0.02333,0.16664]},{"body_a":"world","body_b":"push_box","contact_count":516.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4512,0.0418,0.03005]}],"total_contact_groups":5},"final_pose_error":0.01352,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49585,-0.15436,0.025],"final_tcp_position":[0.49537,-0.1174,0.02021],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":56.11479,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":851.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3404.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.45375,0.0471,0.03426],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":129.0,"n_steps_budget":600.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":9.847,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":516.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.45039,0.03687,0.02777],"tcp_start":[0.45375,0.0471,0.03426],"tcp_to_object_dist_end":0.0374,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":661.0,"n_steps_budget":690.0,"object_pos_end":[0.49585,-0.15436,0.025],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.00602,"object_to_goal_dist_start":0.1564,"object_z_max":0.02563,"peak_contact_force":0.00044,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1627.0,"raw_peak_contact_force":56.11479,"subtask_id":"push","tcp_end":[0.49537,-0.1174,0.02021],"tcp_start":[0.45039,0.03687,0.02777],"tcp_to_object_dist_end":0.03728,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```