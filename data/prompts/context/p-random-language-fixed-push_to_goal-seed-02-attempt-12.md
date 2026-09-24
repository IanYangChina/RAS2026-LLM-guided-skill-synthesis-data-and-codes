## Search State

- **Seed**: 2
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → contact → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | contact_lost | pose_tolerance | 7 | 0.5297 | 0.95 | ✅ accepted |
| 11 | approach → contact → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | contact_lost | pose_tolerance | 7 | 0.3586 | 0.93 | ✅ accepted |
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.4861 | 0.65 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.5646 | 0.69 | ❌ rejected |
| 8 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.5775 | 0.73 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.95). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.530) — your mutation base

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

- **Composite score**: 0.530
- **task_score** (E): 0.948
- **fitness_score**: 0.690  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2742 |
| contact | 1.00 | 1.00 | 0.0417 |
| push | 0.00 | 1.00 | 0.1446 |
| push_final | 1.00 | 1.00 | 0.0728 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.489, 0.058, 0.036) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact | contact | 1.00 / force_exceeded | (0.489, 0.058, 0.036)→(0.487, 0.019, 0.022) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 5.000 | 26.461 | 0.245 |
| push | push | 0.00 / step_budget | (0.487, 0.019, 0.022)→(0.495, -0.118, 0.019) | (0.492, -0.018, 0.025)→(0.516, -0.144, 0.025) | 0.139→0.023 | 1.00 / 2.667 | 9.390 | 37.632 |
| push_final | push | 1.00 / step_budget | (0.495, -0.118, 0.019)→(0.450, -0.125, 0.018) | (0.516, -0.144, 0.025)→(0.503, -0.156, 0.025) | 0.023→0.007 | 1.00 / 4.000 | 0.245 | 22.492 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.621
- goal_progress: 0.935
- terminal_score: 0.935
- phase_score: 0.587
- phase_breakdown.push_score: 0.410
- phase_breakdown.contact_score: 0.777
- phase_breakdown.approach_score: 0.748

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.726
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.981
- **Median Q (composite search score)**: 0.532
- **K-run variance**: 0.0010
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.331


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81053,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.95646,"contact.contact_force_threshold":13.95368,"contact.contact_speed":0.08741,"push.push_depth":0.18313,"push.push_speed":0.02005,"push_final.final_push_depth":0.03277,"push_final.final_push_speed":0.11315},"optimized_scores":{"best_composite_score":0.53169,"best_fitness_score":0.69169,"best_task_score":0.92694},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":908.0,"contact_point_centroid":[0.48311,-0.06527,0.03534],"force_p95":13.88608,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.49662,"mean_force":3.64115,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47921,-0.05334,0.0192]},{"body_a":"world","body_b":"push_box","contact_count":1397.0,"contact_point_centroid":[0.48492,-0.10476,-4e-05],"force_p95":7.39621,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.5978,"mean_force":2.72419,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47875,-0.05097,0.0193]},{"body_a":"world","body_b":"push_box","contact_count":566.0,"contact_point_centroid":[0.50458,-0.15839,-4e-05],"force_p95":0.29703,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.23098,"mean_force":0.2553,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.47721,-0.10134,0.01689]},{"body_a":"attachment","body_b":"push_box","contact_count":5.0,"contact_point_centroid":[0.50253,-0.13248,0.05046],"force_p95":0.66152,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.68606,"mean_force":0.36562,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.49474,-0.12068,0.01881]},{"body_a":"world","body_b":"push_box","contact_count":2232.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48477,0.02489,0.17266]},{"body_a":"world","body_b":"push_box","contact_count":1872.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.46701,0.03182,0.02915]}],"total_contact_groups":6},"final_pose_error":0.01475,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50457,-0.15825,0.02499],"final_tcp_position":[0.46096,-0.08135,0.01712],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":26.05682,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":558.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2232.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.46986,0.05174,0.03893],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":468.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":26.05682,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1872.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.4673,0.01282,0.02304],"tcp_start":[0.46986,0.05174,0.03893],"tcp_to_object_dist_end":0.03727,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50433,-0.15671,0.02528],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.00799,"object_to_goal_dist_start":0.12903,"object_z_max":0.02535,"peak_contact_force":1.62927,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2305.0,"raw_peak_contact_force":25.49662,"subtask_id":"push","tcp_end":[0.49482,-0.12052,0.01887],"tcp_start":[0.4673,0.01282,0.02304],"tcp_to_object_dist_end":0.03796,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":147.0,"n_steps_budget":600.0,"object_pos_end":[0.50457,-0.15825,0.02499],"object_pos_start":[0.50433,-0.15671,0.02528],"object_to_goal_dist_end":0.00943,"object_to_goal_dist_start":0.00799,"object_z_max":0.0253,"peak_contact_force":0.24525,"phase_name":"push_final","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":571.0,"raw_peak_contact_force":1.23098,"subtask_id":"push","tcp_end":[0.46096,-0.08135,0.01712],"tcp_start":[0.49482,-0.12052,0.01887],"tcp_to_object_dist_end":0.08875,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76842,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.41216,"contact.contact_force_threshold":9.74866,"contact.contact_speed":0.22673,"push.push_depth":0.18205,"push.push_speed":0.06995,"push_final.final_push_depth":0.02122,"push_final.final_push_speed":0.11321},"optimized_scores":{"best_composite_score":0.56648,"best_fitness_score":0.72648,"best_task_score":0.93508},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":891.0,"contact_point_centroid":[0.47295,-0.0685,0.03461],"force_p95":13.26615,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.51531,"mean_force":3.68726,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.46945,-0.05655,0.01964]},{"body_a":"world","body_b":"push_box","contact_count":1543.0,"contact_point_centroid":[0.47419,-0.10413,-3e-05],"force_p95":6.83994,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.89336,"mean_force":2.46539,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4684,-0.05395,0.01971]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.49592,-0.13212,0.01898],"force_p95":1.29094,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.29094,"mean_force":1.29094,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.49601,-0.12013,0.01898]},{"body_a":"world","body_b":"push_box","contact_count":495.0,"contact_point_centroid":[0.50146,-0.15798,-1e-05],"force_p95":0.37558,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.79274,"mean_force":0.2566,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.48932,-0.10242,0.01804]},{"body_a":"world","body_b":"push_box","contact_count":2232.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47529,0.02164,0.17252]},{"body_a":"world","body_b":"push_box","contact_count":1880.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.44691,0.02472,0.02954]}],"total_contact_groups":6},"final_pose_error":0.01478,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50172,-0.15816,0.02499],"final_tcp_position":[0.4841,-0.08375,0.01899],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":24.99587,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":558.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2232.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.45028,0.04491,0.0391],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":470.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":24.99587,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1880.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.44659,0.0054,0.02338],"tcp_start":[0.45028,0.04491,0.0391],"tcp_to_object_dist_end":0.0372,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5016,-0.15715,0.025],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.00733,"object_to_goal_dist_start":0.12843,"object_z_max":0.02529,"peak_contact_force":1.00073,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2434.0,"raw_peak_contact_force":23.51531,"subtask_id":"push","tcp_end":[0.49601,-0.12013,0.01898],"tcp_start":[0.44659,0.0054,0.02338],"tcp_to_object_dist_end":0.03792,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":128.0,"n_steps_budget":600.0,"object_pos_end":[0.50172,-0.15816,0.02499],"object_pos_start":[0.5016,-0.15715,0.025],"object_to_goal_dist_end":0.00834,"object_to_goal_dist_start":0.00733,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_final","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":496.0,"raw_peak_contact_force":1.29094,"subtask_id":"push","tcp_end":[0.4841,-0.08375,0.01899],"tcp_start":[0.49601,-0.12013,0.01898],"tcp_to_object_dist_end":0.0767,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.00833,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.19484,"contact.contact_force_threshold":6.22036,"contact.contact_speed":0.07902,"push.push_depth":0.24855,"push.push_speed":0.04578,"push_final.final_push_depth":0.06341,"push_final.final_push_speed":0.09089},"optimized_scores":{"best_composite_score":0.49091,"best_fitness_score":0.65091,"best_task_score":0.98053},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":874.0,"contact_point_centroid":[0.50618,-0.14611,-0.00018],"force_p95":52.69577,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":64.95328,"mean_force":8.93161,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.4402,-0.17099,0.01779]},{"body_a":"push_box","body_b":"link7","contact_count":229.0,"contact_point_centroid":[0.50408,-0.13131,0.05063],"force_p95":60.95135,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.12145,"mean_force":32.2913,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.46743,-0.14099,0.01747]},{"body_a":"push_box","body_b":"link7","contact_count":883.0,"contact_point_centroid":[0.5538,-0.04787,0.05229],"force_p95":59.69958,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.88399,"mean_force":36.70161,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51876,-0.03953,0.01852]},{"body_a":"world","body_b":"push_box","contact_count":1899.0,"contact_point_centroid":[0.55602,-0.08175,-0.00014],"force_p95":45.64541,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.42593,"mean_force":21.16575,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51893,-0.0392,0.01853]},{"body_a":"attachment","body_b":"push_box","contact_count":777.0,"contact_point_centroid":[0.54014,-0.02922,0.05344],"force_p95":30.27047,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.83263,"mean_force":18.33962,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52517,-0.02114,0.01865]},{"body_a":"attachment","body_b":"push_box","contact_count":19.0,"contact_point_centroid":[0.46466,-0.14162,0.0493],"force_p95":3.64845,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.81372,"mean_force":1.05957,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.45592,-0.15314,0.01713]},{"body_a":"world","body_b":"push_box","contact_count":3336.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.52255,0.03855,0.16424]},{"body_a":"world","body_b":"push_box","contact_count":1864.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.54547,0.05722,0.0234]}],"total_contact_groups":8},"final_pose_error":0.01498,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50309,-0.15049,0.02499],"final_tcp_position":[0.40588,-0.20894,0.01874],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":64.95328,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":834.0,"n_steps_budget":960.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3336.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.5467,0.07723,0.03117],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":466.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":28.33042,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1864.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.54769,0.03831,0.02029],"tcp_start":[0.5467,0.07723,0.03117],"tcp_to_object_dist_end":0.03765,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54123,-0.11665,0.02573],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.05303,"object_to_goal_dist_start":0.16043,"object_z_max":0.02856,"peak_contact_force":25.53878,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3559.0,"raw_peak_contact_force":63.88399,"subtask_id":"push","tcp_end":[0.49296,-0.11466,0.01805],"tcp_start":[0.54769,0.03831,0.02029],"tcp_to_object_dist_end":0.04892,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":401.0,"n_steps_budget":990.0,"object_pos_end":[0.50309,-0.15049,0.02499],"object_pos_start":[0.54123,-0.11665,0.02573],"object_to_goal_dist_end":0.00312,"object_to_goal_dist_start":0.05303,"object_z_max":0.02772,"peak_contact_force":0.24525,"phase_name":"push_final","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1122.0,"raw_peak_contact_force":64.95328,"subtask_id":"push","tcp_end":[0.40588,-0.20894,0.01874],"tcp_start":[0.49296,-0.11466,0.01805],"tcp_to_object_dist_end":0.1136,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```