## Search State

- **Seed**: 2
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.4861 | 0.65 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.5646 | 0.69 | ❌ rejected |
| 8 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.5775 | 0.73 | ✅ accepted |
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.5398 | 0.62 | ❌ rejected |
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.3504 | 0.70 | ❌ rejected |

**Proposal policy**: task_score is 0.65 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`
- Frozen object start: [0.47139345610991795, -0.0241810627903052, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.47139345610991795, -0.0241810627903052, 0.025)
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
  frozen_object_start: [0.4714, -0.0242, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.47139345610991795, -0.0241810627903052, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0286, -0.1258, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14

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

## Current Skill (Q=0.486) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
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
  metric: goal_progress
  offset:
  - 0.0
  - 0.03
  - 0.0
phases:
- id: approach
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
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 1.0
      default: 0.5
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: approach
- id: contact
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: add
    contact_speed:
      type: scalar
      range:
      - 0.02
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: contact
- id: push
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
      distance: 0.15
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: add
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.08, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (add)
- **contact** (`contact`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.03, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (add)
    - contact_speed: status=consumed; consumers=generator.speed (add)
- **push** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.03, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (add)
    - push_speed: status=consumed; consumers=generator.speed (add)

## Design Metrics

- **Composite score**: 0.486
- **task_score** (E): 0.650
- **fitness_score**: 0.544  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2731 |
| contact | 1.00 | 1.00 | 0.0428 |
| push | 1.00 | 1.00 | 0.2470 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.489, 0.058, 0.038) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact | contact | 1.00 / force_exceeded | (0.489, 0.058, 0.038)→(0.487, 0.018, 0.022) | (0.492, -0.018, 0.025)→(0.492, -0.019, 0.025) | 0.139→0.138 | 1.00 / 5.000 | 20.794 | 4.546 |
| push | push | 1.00 / step_budget | (0.487, 0.018, 0.022)→(0.513, -0.219, 0.024) | (0.492, -0.019, 0.025)→(0.486, -0.148, 0.025) | 0.138→0.049 | 1.00 / 4.000 | 0.245 | 56.754 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.781
- lateral_force_integral: None
- approach_alignment: 0.763
- goal_progress: 0.675
- terminal_score: 0.675
- phase_score: 0.548
- phase_breakdown.push_score: 0.331
- phase_breakdown.contact_score: 0.758
- phase_breakdown.approach_score: 0.777

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.599
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.675
- **Median Q (composite search score)**: 0.559
- **K-run variance**: 0.0301
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.333


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `27920116be2b9a598fe307ae470bb0295293d051bb1ef513a0996a4d851f2459`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1a1e2536715050e6c37d8aed13e4ecd62004f6234f1413b07d7b475a233f55c9`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.26154,"average_solve_count":65.0,"average_success_count":65.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.77009,"contact.contact_force_threshold":13.56033,"contact.contact_speed":0.13106,"push.push_depth":0.1061,"push.push_speed":0.22126},"optimized_scores":{"best_composite_score":0.55927,"best_fitness_score":0.50594,"best_task_score":0.61436},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":241.0,"contact_point_centroid":[0.48003,-0.07142,0.03053],"force_p95":46.17923,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.86381,"mean_force":6.50254,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48017,-0.06015,0.02131]},{"body_a":"world","body_b":"push_box","contact_count":1233.0,"contact_point_centroid":[0.46099,-0.14779,-6e-05],"force_p95":9.90502,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.5414,"mean_force":1.60897,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49879,-0.1504,0.02247]},{"body_a":"world","body_b":"push_box","contact_count":2232.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48477,0.02489,0.17266]},{"body_a":"world","body_b":"push_box","contact_count":1872.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.46701,0.03182,0.02915]}],"total_contact_groups":4},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45533,-0.17192,0.02499],"final_tcp_position":[0.51682,-0.23673,0.02379],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":74.86381,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":558.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2232.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.46986,0.05174,0.03893],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":468.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":26.05682,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1872.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.4673,0.01282,0.02304],"tcp_start":[0.46986,0.05174,0.03893],"tcp_to_object_dist_end":0.03727,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":593.0,"n_steps_budget":780.0,"object_pos_end":[0.45533,-0.17192,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.04976,"object_to_goal_dist_start":0.12903,"object_z_max":0.02705,"peak_contact_force":0.24525,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1474.0,"raw_peak_contact_force":74.86381,"subtask_id":"push","tcp_end":[0.51682,-0.23673,0.02379],"tcp_start":[0.4673,0.01282,0.02304],"tcp_to_object_dist_end":0.08935,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e864853e179d3df1b19d9aaa17e18a5fe8c66fe7533fc0dd3a88a693de7416e7`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.44156,"average_solve_count":77.0,"average_success_count":77.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.60855,"contact.contact_force_threshold":15.9082,"contact.contact_speed":0.06501,"push.push_depth":0.11381,"push.push_speed":0.159},"optimized_scores":{"best_composite_score":0.24684,"best_fitness_score":0.52684,"best_task_score":0.6601},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":233.0,"contact_point_centroid":[0.4649,-0.07123,0.02194],"force_p95":30.27406,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.67556,"mean_force":4.26885,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4681,-0.06031,0.02071]},{"body_a":"world","body_b":"push_box","contact_count":1699.0,"contact_point_centroid":[0.4562,-0.13609,-4e-05],"force_p95":2.67878,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.62532,"mean_force":0.87964,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50312,-0.15331,0.0219]},{"body_a":"attachment","body_b":"push_box","contact_count":40.0,"contact_point_centroid":[0.44786,-0.008,0.02835],"force_p95":11.02386,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.14891,"mean_force":4.66063,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.44663,0.00392,0.02293]},{"body_a":"world","body_b":"push_box","contact_count":1983.0,"contact_point_centroid":[0.45033,-0.03192,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.73882,"mean_force":0.34009,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.4469,0.02363,0.0292]},{"body_a":"world","body_b":"push_box","contact_count":2232.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47529,0.02164,0.17252]}],"total_contact_groups":5},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45635,-0.14973,0.02499],"final_tcp_position":[0.53724,-0.24268,0.02334],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":42.67556,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":558.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2232.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.45028,0.04491,0.0391],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.45066,-0.03458,0.02496],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12553,"object_to_goal_dist_start":0.12843,"object_z_max":0.02504,"peak_contact_force":7.74629,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2023.0,"raw_peak_contact_force":13.14891,"subtask_id":"contact","tcp_end":[0.44667,0.00227,0.02244],"tcp_start":[0.45028,0.04491,0.0391],"tcp_to_object_dist_end":0.03715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":664.0,"n_steps_budget":1000.0,"object_pos_end":[0.45635,-0.14973,0.02499],"object_pos_start":[0.45066,-0.03458,0.02496],"object_to_goal_dist_end":0.04365,"object_to_goal_dist_start":0.12553,"object_z_max":0.02559,"peak_contact_force":0.24525,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1932.0,"raw_peak_contact_force":42.67556,"subtask_id":"push","tcp_end":[0.53724,-0.24268,0.02334],"tcp_start":[0.44667,0.00227,0.02244],"tcp_to_object_dist_end":0.12324,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c820cf29ab3e34ea9695cb40d5aba5de55f3ad951ee91f0df578ae7146ee7727`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2454,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.25847,"contact.contact_force_threshold":9.85618,"contact.contact_speed":0.19772,"push.push_depth":0.08046,"push.push_speed":0.03623},"optimized_scores":{"best_composite_score":0.65232,"best_fitness_score":0.59899,"best_task_score":0.67514},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1196.0,"contact_point_centroid":[0.55215,-0.10559,-6e-05],"force_p95":35.32535,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.72224,"mean_force":7.77234,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50659,-0.09941,0.02198]},{"body_a":"push_box","body_b":"link7","contact_count":258.0,"contact_point_centroid":[0.55679,-0.05067,0.05403],"force_p95":35.85378,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.52226,"mean_force":20.49714,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52246,-0.04276,0.02041]},{"body_a":"attachment","body_b":"push_box","contact_count":352.0,"contact_point_centroid":[0.53781,-0.0445,0.04924],"force_p95":40.68838,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.06307,"mean_force":13.57121,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5243,-0.0365,0.02029]},{"body_a":"world","body_b":"push_box","contact_count":2688.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.52185,0.0372,0.16875]},{"body_a":"world","body_b":"push_box","contact_count":1856.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.5453,0.05678,0.02527]}],"total_contact_groups":5},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54493,-0.12359,0.02499],"final_tcp_position":[0.48461,-0.17813,0.02429],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":52.72224,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":672.0,"n_steps_budget":720.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2688.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.54649,0.07631,0.03448],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07585,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":464.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":28.57994,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1856.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.54764,0.03834,0.02086],"tcp_start":[0.54649,0.07631,0.03448],"tcp_to_object_dist_end":0.03761,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":614.0,"n_steps_budget":1000.0,"object_pos_end":[0.54493,-0.12359,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.05212,"object_to_goal_dist_start":0.16043,"object_z_max":0.02959,"peak_contact_force":0.24525,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1806.0,"raw_peak_contact_force":52.72224,"subtask_id":"push","tcp_end":[0.48461,-0.17813,0.02429],"tcp_start":[0.54764,0.03834,0.02086],"tcp_to_object_dist_end":0.08132,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```