## Search State

- **Seed**: 7
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 5 | 0.4066 | 0.33 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.8021 | 0.82 | ✅ accepted |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7991 | 0.82 | ✅ accepted |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`
- Frozen object start: [0.51501145599256, 0.047665656116349056, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.51501145599256, 0.047665656116349056, 0.025)
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
  frozen_object_start: [0.515, 0.0477, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.51501145599256, 0.047665656116349056, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.015, -0.1977, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752

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

## Current Skill (Q=0.407) — your mutation base

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
    tolerance: 0.02
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
    contact_speed:
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
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.03
    - 0.0
    offset_along_axis:
      distance: 0.02
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.0
      - 0.06
      default: 0.02
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
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.08, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.03, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.03, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.02, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.407
- **task_score** (E): 0.334
- **fitness_score**: 0.383  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2820 |
| contact_1 | 1.00 | 1.00 | 0.0377 |
| push_1 | 0.67 | 1.00 | 0.0785 |
| retract_1 | 1.00 | 1.00 | 0.0806 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, 0.096, 0.041) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.516, 0.096, 0.041)→(0.512, 0.064, 0.023) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 5.000 | 25313.447 | 0.245 |
| push_1 | push | 0.67 / step_budget | (0.512, 0.064, 0.023)→(0.512, -0.014, 0.021) | (0.513, 0.027, 0.025)→(0.532, -0.043, 0.025) | 0.180→0.113 | 1.00 / 4.333 | 8.186 | 20.735 |
| retract_1 | retract | 1.00 / step_budget | (0.512, -0.014, 0.021)→(0.509, -0.014, 0.102) | (0.532, -0.043, 0.025)→(0.532, -0.044, 0.025) | 0.113→0.112 | 1.00 / 4.000 | 0.245 | 10.848 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.607
- lateral_force_integral: None
- approach_alignment: 0.614
- goal_progress: 0.541
- terminal_score: 0.541
- phase_score: 0.476
- phase_breakdown.push_score: 0.211
- phase_breakdown.approach_score: 0.681
- phase_breakdown.contact_score: 0.781

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.502
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.541
- **Median Q (composite search score)**: 0.417
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at upper bound**: contact_1.contact_speed
- **Final σ (mean)**: 0.356


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `75e2389a1a667086aa2b9c0de482ff37adf5571150b90a83772692baadf8b52e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `154c216c563de6b8ee153943e5b668ca6d0c7dfd9253696b060f91a67dca06ec`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78832,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":16.32528,"contact_1.contact_speed":0.05,"push_1.push_depth":0.09409,"push_1.push_force_threshold":22.32579,"push_1.push_speed":0.08288},"optimized_scores":{"best_composite_score":0.44222,"best_fitness_score":0.50222,"best_task_score":0.54145},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":823.0,"contact_point_centroid":[0.51443,0.01341,0.04194],"force_p95":13.87493,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.29846,"mean_force":4.64757,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50664,0.02469,0.01946]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.51817,-0.05641,0.04995],"force_p95":20.10407,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.10407,"mean_force":20.10407,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50341,-0.04742,0.02013]},{"body_a":"world","body_b":"push_box","contact_count":1496.0,"contact_point_centroid":[0.52891,-0.03083,-5e-05],"force_p95":8.64805,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.25319,"mean_force":3.22121,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50638,0.01712,0.01963]},{"body_a":"push_box","body_b":"link7","contact_count":56.0,"contact_point_centroid":[0.54291,-0.00919,0.05249],"force_p95":14.59777,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.96835,"mean_force":6.96734,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50527,-0.00542,0.01974]},{"body_a":"world","body_b":"push_box","contact_count":984.0,"contact_point_centroid":[0.54218,-0.0696,-1e-05],"force_p95":0.24556,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.18557,"mean_force":0.2673,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50037,-0.04733,0.05945]},{"body_a":"world","body_b":"push_box","contact_count":2272.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50726,0.05761,0.17076]},{"body_a":"world","body_b":"push_box","contact_count":1772.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51272,0.1002,0.02966]}],"total_contact_groups":7},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54223,-0.06951,0.02499],"final_tcp_position":[0.50014,-0.04721,0.10054],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":25.29846,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":568.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2272.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51604,0.11692,0.0409],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07107,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":443.0,"n_steps_budget":600.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":17.68684,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1772.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.51285,0.08465,0.02305],"tcp_start":[0.51604,0.11692,0.0409],"tcp_to_object_dist_end":0.0371,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54196,-0.06905,0.02494],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.09117,"object_to_goal_dist_start":0.19823,"object_z_max":0.02687,"peak_contact_force":9.87821,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2375.0,"raw_peak_contact_force":25.29846,"subtask_id":"push","tcp_end":[0.50341,-0.04742,0.02013],"tcp_start":[0.51285,0.08465,0.02305],"tcp_to_object_dist_end":0.04446,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":247.0,"n_steps_budget":630.0,"object_pos_end":[0.54223,-0.06951,0.02499],"object_pos_start":[0.54196,-0.06905,0.02494],"object_to_goal_dist_end":0.0909,"object_to_goal_dist_start":0.09117,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":985.0,"raw_peak_contact_force":20.10407,"tcp_end":[0.50014,-0.04721,0.10054],"tcp_start":[0.50341,-0.04742,0.02013],"tcp_to_object_dist_end":0.08932,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62069,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":1.32834,"contact_1.contact_speed":0.03057,"push_1.push_depth":0.1129,"push_1.push_force_threshold":18.58806,"push_1.push_speed":0.06267},"optimized_scores":{"best_composite_score":0.36004,"best_fitness_score":0.42004,"best_task_score":0.45106},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":837.0,"contact_point_centroid":[0.48235,0.03569,0.0441],"force_p95":13.15197,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.84746,"mean_force":4.81678,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47402,0.04691,0.02043]},{"body_a":"world","body_b":"push_box","contact_count":1431.0,"contact_point_centroid":[0.49935,-0.00777,-5e-05],"force_p95":7.96957,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.46809,"mean_force":3.53728,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47422,0.04596,0.02052]},{"body_a":"push_box","body_b":"link7","contact_count":67.0,"contact_point_centroid":[0.51679,0.01036,0.05316],"force_p95":10.28036,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.08193,"mean_force":6.10673,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47854,0.01172,0.0205]},{"body_a":"world","body_b":"push_box","contact_count":932.0,"contact_point_centroid":[0.51086,-0.03657,-2e-05],"force_p95":0.45336,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.46833,"mean_force":0.25415,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47797,-0.00693,0.06081]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.49524,-0.01608,0.04991],"force_p95":0.73163,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.73163,"mean_force":0.73163,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48086,-0.00693,0.02046]},{"body_a":"world","body_b":"push_box","contact_count":2292.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48467,0.06267,0.17063]},{"body_a":"world","body_b":"push_box","contact_count":2396.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46924,0.10959,0.03013]}],"total_contact_groups":7},"final_pose_error":0.0197,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51098,-0.03552,0.02499],"final_tcp_position":[0.47779,-0.00685,0.10102],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.47025,0.12692,0.04121],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":599.0,"n_steps_budget":870.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2396.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.47116,0.09545,0.02396],"tcp_start":[0.47025,0.12692,0.04121],"tcp_to_object_dist_end":0.03786,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51081,-0.0355,0.02488],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.11501,"object_to_goal_dist_start":0.2095,"object_z_max":0.02714,"peak_contact_force":0.47386,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2335.0,"raw_peak_contact_force":17.84746,"subtask_id":"push","tcp_end":[0.48087,-0.00683,0.02048],"tcp_start":[0.47116,0.09545,0.02396],"tcp_to_object_dist_end":0.04168,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":240.0,"n_steps_budget":630.0,"object_pos_end":[0.51098,-0.03552,0.02499],"object_pos_start":[0.51081,-0.0355,0.02488],"object_to_goal_dist_end":0.115,"object_to_goal_dist_start":0.11501,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":933.0,"raw_peak_contact_force":1.46833,"tcp_end":[0.47779,-0.00685,0.10102],"tcp_start":[0.48087,-0.00683,0.02048],"tcp_to_object_dist_end":0.08778,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68317,"average_solve_count":101.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":5.99089,"contact_1.contact_speed":0.04677,"push_1.push_depth":0.13785,"push_1.push_force_threshold":10.17546,"push_1.push_speed":0.03496},"optimized_scores":{"best_composite_score":0.4174,"best_fitness_score":0.2274,"best_task_score":0.00963},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.55159,-0.0006,0.0227],"force_p95":18.12379,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.05812,"mean_force":9.71487,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55159,0.01139,0.02268]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.55148,-0.0007,0.02255],"force_p95":10.30367,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.97066,"mean_force":5.61534,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55147,0.01128,0.02253]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":6.07324,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.1485,"mean_force":4.91102,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5516,0.01141,0.02271]},{"body_a":"world","body_b":"push_box","contact_count":1045.0,"contact_point_centroid":[0.54355,-0.02657,-1e-05],"force_p95":0.24713,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.57485,"mean_force":0.26093,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54817,0.01113,0.06217]},{"body_a":"world","body_b":"push_box","contact_count":2140.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52977,0.02223,0.17179]},{"body_a":"world","body_b":"push_box","contact_count":1848.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.55483,0.02794,0.0295]}],"total_contact_groups":6},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54351,-0.02661,0.02499],"final_tcp_position":[0.548,0.01115,0.10312],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":29.1174,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":535.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2140.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.56191,0.04535,0.0416],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07492,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":462.0,"n_steps_budget":630.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":29.1174,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1848.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.5516,0.01141,0.02271],"tcp_start":[0.56191,0.04535,0.0416],"tcp_to_object_dist_end":0.03775,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":2.0,"n_steps_budget":600.0,"object_pos_end":[0.54439,-0.02563,0.02498],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13205,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":14.20529,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":19.05812,"subtask_id":"push","tcp_end":[0.55153,0.01131,0.0226],"tcp_start":[0.5516,0.01141,0.02271],"tcp_to_object_dist_end":0.0377,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":264.0,"n_steps_budget":630.0,"object_pos_end":[0.54351,-0.02661,0.02499],"object_pos_start":[0.54439,-0.02563,0.02498],"object_to_goal_dist_end":0.13084,"object_to_goal_dist_start":0.13205,"object_z_max":0.02503,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1048.0,"raw_peak_contact_force":10.97066,"tcp_end":[0.548,0.01115,0.10312],"tcp_start":[0.55153,0.01131,0.0226],"tcp_to_object_dist_end":0.0869,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```