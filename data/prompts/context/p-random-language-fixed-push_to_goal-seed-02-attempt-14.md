## Search State

- **Seed**: 2
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.0740 | 0.15 | ❌ rejected |
| 13 | approach → contact → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | contact_lost | pose_tolerance | 7 | 0.4842 | 0.87 | ❌ rejected |
| 12 | approach → contact → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | contact_lost | pose_tolerance | 7 | 0.5297 | 0.95 | ✅ accepted |
| 11 | approach → contact → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | contact_lost | pose_tolerance | 7 | 0.3586 | 0.93 | ✅ accepted |
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.4861 | 0.65 | ❌ rejected |

**Proposal policy**: task_score is 0.15 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.074) — your mutation base

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
  termination: contact_lost
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
      - 0.25
      default: 0.12
      binds_to:
      - path: target.offset_along_axis.distance
        mode: add
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: add
  guards:
  - id: maintain_contact
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.02
    - 0.0
  subtask_id: push
- id: push_final
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
    - 0.01
    - 0.0
    offset_along_axis:
      distance: 0.06
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    final_push_depth:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.06
      binds_to:
      - path: target.offset_along_axis.distance
        mode: add
    final_push_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
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
  - guards:
    - id=maintain_contact, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.02, 0.0]
- **push_final** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.01, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.06, mode=replace_offset_projection, sign=positive}, tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - final_push_depth: status=consumed; consumers=target.offset_along_axis.distance (add)
    - final_push_speed: status=consumed; consumers=generator.speed (add)

## Design Metrics

- **Composite score**: 0.074
- **task_score** (E): 0.150
- **fitness_score**: 0.317  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2737 |
| contact | 1.00 | 1.00 | 0.0427 |
| push | 0.00 | 1.00 | 0.0002 |
| push_final | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.489, 0.058, 0.037) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact | contact | 1.00 / force_exceeded | (0.489, 0.058, 0.037)→(0.487, 0.018, 0.022) | (0.492, -0.018, 0.025)→(0.492, -0.019, 0.025) | 0.139→0.138 | 1.00 / 5.000 | 20.904 | 4.546 |
| push | push | 0.00 / guard_failure | (0.483, 0.005, 0.020)→(0.483, 0.005, 0.020) | (0.492, -0.019, 0.025)→(0.491, -0.031, 0.025) | 0.138→0.126 | 1.00 / 1.667 | 0.740 | 43.135 |
| push_final | push | 0.00 / guard_failure | (0.484, -0.003, 0.019)→(0.484, -0.004, 0.019) | (0.491, -0.032, 0.025)→(0.492, -0.040, 0.025) | 0.126→0.118 | 1.00 / 3.333 | 12.636 | 40.240 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.220
- lateral_force_integral: None
- approach_alignment: 0.479
- goal_progress: 0.213
- terminal_score: 0.213
- phase_score: 0.411
- phase_breakdown.push_score: 0.073
- phase_breakdown.contact_score: 0.761
- phase_breakdown.approach_score: 0.732

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.360
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.227
- **Median Q (composite search score)**: 0.100
- **K-run variance**: 0.0085
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.232


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78689,"average_solve_count":61.0,"average_success_count":61.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.19953,"contact.contact_force_threshold":12.73859,"contact.contact_speed":0.18588,"push.push_depth":0.24901,"push.push_speed":0.11764,"push_final.final_push_depth":0.03977,"push_final.final_push_speed":0.1156},"optimized_scores":{"best_composite_score":0.09982,"best_fitness_score":0.25982,"best_task_score":0.01048},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.46717,0.00068,0.02215],"force_p95":34.15879,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.68946,"mean_force":17.53008,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.46717,0.01261,0.02213]},{"body_a":"attachment","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.46832,-1e-05,0.02738],"force_p95":27.14304,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.65922,"mean_force":7.89273,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.46702,0.01194,0.02172]},{"body_a":"world","body_b":"push_box","contact_count":18.0,"contact_point_centroid":[0.46856,-0.02783,-4e-05],"force_p95":14.94011,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.96258,"mean_force":2.88593,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.46698,0.01189,0.02166]},{"body_a":"world","body_b":"push_box","contact_count":16.0,"contact_point_centroid":[0.47137,-0.02424,-1e-05],"force_p95":10.3346,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.73494,"mean_force":6.69634,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.46716,0.01264,0.02214]},{"body_a":"world","body_b":"push_box","contact_count":3012.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48385,0.0262,0.16613]},{"body_a":"world","body_b":"push_box","contact_count":1884.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.46663,0.03233,0.02637]}],"total_contact_groups":6},"final_pose_error":0.25446,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47124,-0.0256,0.02505],"final_tcp_position":[0.46689,0.01132,0.02141],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":34.68946,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":753.0,"n_steps_budget":900.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3012.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.46915,0.05273,0.03399],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07747,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":471.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":26.18055,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1884.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.4672,0.0128,0.02224],"tcp_start":[0.46915,0.05273,0.03399],"tcp_to_object_dist_end":0.03732,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.47138,-0.0243,0.02497],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12892,"object_to_goal_dist_start":0.12903,"object_z_max":0.02503,"peak_contact_force":0.60934,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":22.0,"raw_peak_contact_force":34.68946,"subtask_id":"push","tcp_end":[0.46712,0.01232,0.02196],"tcp_start":[0.46717,0.01239,0.02202],"tcp_to_object_dist_end":0.03699,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.47126,-0.02522,0.02495],"object_pos_start":[0.47134,-0.02452,0.02505],"object_to_goal_dist_end":0.12805,"object_to_goal_dist_start":0.12871,"object_z_max":0.02505,"peak_contact_force":1.50311,"phase_name":"push_final","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":24.0,"raw_peak_contact_force":33.65922,"subtask_id":"push","tcp_end":[0.46689,0.01132,0.02141],"tcp_start":[0.46695,0.01144,0.02148],"tcp_to_object_dist_end":0.03697,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72414,"average_solve_count":58.0,"average_success_count":58.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.58514,"contact.contact_force_threshold":18.86243,"contact.contact_speed":0.21104,"push.push_depth":0.19719,"push.push_speed":0.12201,"push_final.final_push_depth":0.08654,"push_final.final_push_speed":0.10725},"optimized_scores":{"best_composite_score":-0.04965,"best_fitness_score":0.36035,"best_task_score":0.22685},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":17.0,"contact_point_centroid":[0.44905,-0.01198,0.03016],"force_p95":19.5392,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.39208,"mean_force":6.39868,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.44733,-4e-05,0.02184]},{"body_a":"attachment","body_b":"push_box","contact_count":52.0,"contact_point_centroid":[0.4519,-0.02615,0.02525],"force_p95":10.35659,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.18543,"mean_force":2.32222,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.45056,-0.01432,0.01926]},{"body_a":"world","body_b":"push_box","contact_count":90.0,"contact_point_centroid":[0.45401,-0.064,-0.0001],"force_p95":8.65321,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.21074,"mean_force":1.74643,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.4505,-0.01387,0.0194]},{"body_a":"attachment","body_b":"push_box","contact_count":40.0,"contact_point_centroid":[0.44786,-0.008,0.02835],"force_p95":11.02386,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.14891,"mean_force":4.66063,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.44663,0.00392,0.02293]},{"body_a":"world","body_b":"push_box","contact_count":31.0,"contact_point_centroid":[0.45058,-0.04442,-5e-05],"force_p95":11.46691,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.86901,"mean_force":3.7116,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.44739,-0.00024,0.02182]},{"body_a":"world","body_b":"push_box","contact_count":1983.0,"contact_point_centroid":[0.45033,-0.03192,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.73882,"mean_force":0.34009,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.4469,0.02363,0.0292]},{"body_a":"world","body_b":"push_box","contact_count":2232.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47529,0.02164,0.17252]}],"total_contact_groups":7},"final_pose_error":0.27099,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45612,-0.06093,0.02511],"final_tcp_position":[0.45341,-0.02384,0.01838],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":41.39208,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":558.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2232.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.45028,0.04491,0.0391],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.45066,-0.03458,0.02496],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12553,"object_to_goal_dist_start":0.12843,"object_z_max":0.02504,"peak_contact_force":7.74629,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2023.0,"raw_peak_contact_force":13.14891,"subtask_id":"contact","tcp_end":[0.44667,0.00227,0.02244],"tcp_start":[0.45028,0.04491,0.0391],"tcp_to_object_dist_end":0.03715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":21.0,"n_steps_budget":1000.0,"object_pos_end":[0.45213,-0.04007,0.0248],"object_pos_start":[0.45066,-0.03458,0.02496],"object_to_goal_dist_end":0.1199,"object_to_goal_dist_start":0.12553,"object_z_max":0.02518,"peak_contact_force":1.07593,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":48.0,"raw_peak_contact_force":41.39208,"subtask_id":"push","tcp_end":[0.44815,-0.00356,0.02117],"tcp_start":[0.44823,-0.00335,0.02124],"tcp_to_object_dist_end":0.03691,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":74.0,"n_steps_budget":1000.0,"object_pos_end":[0.45602,-0.06046,0.02492],"object_pos_start":[0.45218,-0.0409,0.02494],"object_to_goal_dist_end":0.09976,"object_to_goal_dist_start":0.11912,"object_z_max":0.026,"peak_contact_force":0.46182,"phase_name":"push_final","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":142.0,"raw_peak_contact_force":22.18543,"subtask_id":"push","tcp_end":[0.45341,-0.02384,0.01838],"tcp_start":[0.45343,-0.02372,0.01841],"tcp_to_object_dist_end":0.03729,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76271,"average_solve_count":59.0,"average_success_count":59.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.62981,"contact.contact_force_threshold":17.02967,"contact.contact_speed":0.18653,"push.push_depth":0.13498,"push.push_speed":0.11576,"push_final.final_push_depth":0.08934,"push_final.final_push_speed":0.10557},"optimized_scores":{"best_composite_score":0.17195,"best_fitness_score":0.33195,"best_task_score":0.21304},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":33.0,"contact_point_centroid":[0.5491,-0.02947,-0.00029],"force_p95":38.9076,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":64.87437,"mean_force":6.07676,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.53215,0.00287,0.01654]},{"body_a":"attachment","body_b":"push_box","contact_count":7.0,"contact_point_centroid":[0.54238,-0.00789,0.04998],"force_p95":48.44916,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.06441,"mean_force":15.74006,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.53268,0.00376,0.01681]},{"body_a":"push_box","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.56944,-0.00469,0.04994],"force_p95":47.20968,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.96251,"mean_force":12.35945,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.53288,0.00409,0.0169]},{"body_a":"world","body_b":"push_box","contact_count":87.0,"contact_point_centroid":[0.55181,-0.02911,-6e-05],"force_p95":8.26756,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.32423,"mean_force":3.5964,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5404,0.02284,0.01892]},{"body_a":"push_box","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.56959,-0.00345,0.0509],"force_p95":35.61882,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.86117,"mean_force":12.3917,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.53476,0.00925,0.01743]},{"body_a":"attachment","body_b":"push_box","contact_count":52.0,"contact_point_centroid":[0.54698,0.01225,0.04136],"force_p95":11.3384,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.18295,"mean_force":3.7533,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5408,0.02396,0.01895]},{"body_a":"world","body_b":"push_box","contact_count":2240.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.52148,0.03617,0.1725]},{"body_a":"world","body_b":"push_box","contact_count":1852.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.5451,0.05634,0.02708]}],"total_contact_groups":8},"final_pose_error":0.29316,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54932,-0.03379,0.02438],"final_tcp_position":[0.53149,0.00165,0.01619],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":64.87437,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":560.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2240.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.54616,0.07546,0.03765],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0755,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":463.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":28.78662,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1852.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.54758,0.03828,0.0214],"tcp_start":[0.54616,0.07546,0.03765],"tcp_to_object_dist_end":0.03752,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":84.0,"n_steps_budget":1000.0,"object_pos_end":[0.548,-0.02994,0.02525],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.1293,"object_to_goal_dist_start":0.16043,"object_z_max":0.02598,"peak_contact_force":0.53488,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":145.0,"raw_peak_contact_force":53.32423,"subtask_id":"push","tcp_end":[0.53351,0.00531,0.01726],"tcp_start":[0.53348,0.00555,0.01727],"tcp_to_object_dist_end":0.03895,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":15.0,"n_steps_budget":1000.0,"object_pos_end":[0.54912,-0.03356,0.02426],"object_pos_start":[0.5483,-0.03049,0.02547],"object_to_goal_dist_end":0.12638,"object_to_goal_dist_start":0.1289,"object_z_max":0.0255,"peak_contact_force":35.94182,"phase_name":"push_final","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":47.0,"raw_peak_contact_force":64.87437,"subtask_id":"push","tcp_end":[0.53149,0.00165,0.01619],"tcp_start":[0.53155,0.00179,0.01625],"tcp_to_object_dist_end":0.0402,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```