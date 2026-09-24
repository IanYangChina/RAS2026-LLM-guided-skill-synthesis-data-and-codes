## Search State

- **Seed**: 2
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → contact → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | contact_lost | pose_tolerance | 7 | 0.3586 | 0.93 | ✅ accepted |
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.4861 | 0.65 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.5646 | 0.69 | ❌ rejected |
| 8 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.5775 | 0.73 | ✅ accepted |
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.5398 | 0.62 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.93). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.359) — your mutation base

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

- **Composite score**: 0.359
- **task_score** (E): 0.934
- **fitness_score**: 0.685  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2720 |
| contact | 1.00 | 1.00 | 0.0445 |
| push | 0.00 | 1.00 | 0.1455 |
| push_final | 1.00 | 1.00 | 0.0706 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.489, 0.057, 0.039) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact | contact | 1.00 / step_budget | (0.489, 0.057, 0.039)→(0.487, 0.016, 0.022) | (0.492, -0.018, 0.025)→(0.492, -0.021, 0.025) | 0.139→0.137 | 1.00 / 4.667 | 13.219 | 7.064 |
| push | push | 0.00 / step_budget | (0.487, 0.016, 0.022)→(0.495, -0.122, 0.019) | (0.492, -0.021, 0.025)→(0.516, -0.145, 0.026) | 0.137→0.024 | 1.00 / 2.333 | 16.883 | 36.403 |
| push_final | push | 1.00 / step_budget | (0.495, -0.122, 0.019)→(0.453, -0.118, 0.016) | (0.516, -0.145, 0.026)→(0.502, -0.155, 0.026) | 0.024→0.009 | 1.00 / 3.667 | 13.639 | 36.334 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.970
- lateral_force_integral: None
- approach_alignment: 0.599
- goal_progress: 0.961
- terminal_score: 0.961
- phase_score: 0.504
- phase_breakdown.push_score: 0.244
- phase_breakdown.contact_score: 0.774
- phase_breakdown.approach_score: 0.747

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.708
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.979
- **Median Q (composite search score)**: 0.298
- **K-run variance**: 0.0145
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.419


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.93333,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.49808,"contact.contact_force_threshold":8.50849,"contact.contact_speed":0.2366,"push.push_depth":0.16751,"push.push_speed":0.07453,"push_final.final_push_depth":0.04551,"push_final.final_push_speed":0.02007},"optimized_scores":{"best_composite_score":0.52677,"best_fitness_score":0.68677,"best_task_score":0.96139},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":178.0,"contact_point_centroid":[0.50868,-0.1377,0.05169],"force_p95":40.39928,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.88233,"mean_force":32.21073,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.47298,-0.09108,0.01337]},{"body_a":"world","body_b":"push_box","contact_count":454.0,"contact_point_centroid":[0.49866,-0.13415,-0.00015],"force_p95":28.20505,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.11163,"mean_force":13.16466,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.47692,-0.09624,0.01425]},{"body_a":"attachment","body_b":"push_box","contact_count":883.0,"contact_point_centroid":[0.48325,-0.06358,0.03643],"force_p95":13.51036,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.82548,"mean_force":3.89728,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47883,-0.05167,0.01921]},{"body_a":"world","body_b":"push_box","contact_count":1335.0,"contact_point_centroid":[0.48624,-0.10331,-4e-05],"force_p95":7.1247,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.86761,"mean_force":2.96436,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47783,-0.04692,0.01933]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.49837,-0.12848,0.03481],"force_p95":0.41721,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42797,"mean_force":0.32045,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.49381,-0.11652,0.01885]},{"body_a":"world","body_b":"push_box","contact_count":2232.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48477,0.02489,0.17266]},{"body_a":"world","body_b":"push_box","contact_count":1872.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.46701,0.03182,0.02915]}],"total_contact_groups":7},"final_pose_error":0.0148,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49912,-0.14616,0.02805],"final_tcp_position":[0.4572,-0.07091,0.01071],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":43.88233,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":558.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2232.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.46986,0.05174,0.03893],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":468.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":26.05682,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1872.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.4673,0.01282,0.02304],"tcp_start":[0.46986,0.05174,0.03893],"tcp_to_object_dist_end":0.03727,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50189,-0.15301,0.02553],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.00359,"object_to_goal_dist_start":0.12903,"object_z_max":0.02565,"peak_contact_force":0.18633,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2218.0,"raw_peak_contact_force":23.82548,"subtask_id":"push","tcp_end":[0.49379,-0.11646,0.01885],"tcp_start":[0.4673,0.01282,0.02304],"tcp_to_object_dist_end":0.03803,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":208.0,"n_steps_budget":1000.0,"object_pos_end":[0.49912,-0.14616,0.02805],"object_pos_start":[0.50189,-0.15301,0.02553],"object_to_goal_dist_end":0.00498,"object_to_goal_dist_start":0.00359,"object_z_max":0.02821,"peak_contact_force":40.42691,"phase_name":"push_final","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":634.0,"raw_peak_contact_force":43.88233,"subtask_id":"push","tcp_end":[0.4572,-0.07091,0.01071],"tcp_start":[0.49379,-0.11646,0.01885],"tcp_to_object_dist_end":0.08787,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85417,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.95384,"contact.contact_force_threshold":15.37486,"contact.contact_speed":0.06926,"push.push_depth":0.20851,"push.push_speed":0.08746,"push_final.final_push_depth":0.02003,"push_final.final_push_speed":0.07938},"optimized_scores":{"best_composite_score":0.2982,"best_fitness_score":0.7082,"best_task_score":0.86285},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":883.0,"contact_point_centroid":[0.4747,-0.07442,0.03374],"force_p95":15.62689,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.53362,"mean_force":3.90807,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47126,-0.06249,0.0188]},{"body_a":"world","body_b":"push_box","contact_count":1625.0,"contact_point_centroid":[0.47639,-0.11104,-4e-05],"force_p95":7.51041,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.65437,"mean_force":2.44221,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4716,-0.06322,0.01883]},{"body_a":"attachment","body_b":"push_box","contact_count":40.0,"contact_point_centroid":[0.44786,-0.008,0.02835],"force_p95":11.02386,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.14891,"mean_force":4.66063,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.44663,0.00392,0.02293]},{"body_a":"world","body_b":"push_box","contact_count":1983.0,"contact_point_centroid":[0.45033,-0.03192,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.73882,"mean_force":0.34009,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.4469,0.02363,0.0292]},{"body_a":"world","body_b":"push_box","contact_count":559.0,"contact_point_centroid":[0.50381,-0.16733,-4e-05],"force_p95":0.3555,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.96063,"mean_force":0.2609,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.49064,-0.10711,0.01713]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.49989,-0.14057,0.01823],"force_p95":1.89891,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.93728,"mean_force":1.55363,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.49966,-0.12864,0.0183]},{"body_a":"world","body_b":"push_box","contact_count":2232.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47529,0.02164,0.17252]}],"total_contact_groups":7},"final_pose_error":0.01478,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50359,-0.16725,0.02499],"final_tcp_position":[0.4835,-0.08532,0.01819],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":22.53362,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":558.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2232.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.45028,0.04491,0.0391],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.45066,-0.03458,0.02496],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12553,"object_to_goal_dist_start":0.12843,"object_z_max":0.02504,"peak_contact_force":7.74629,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2023.0,"raw_peak_contact_force":13.14891,"subtask_id":"contact","tcp_end":[0.44667,0.00227,0.02244],"tcp_start":[0.45028,0.04491,0.0391],"tcp_to_object_dist_end":0.03715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50384,-0.16543,0.02522],"object_pos_start":[0.45066,-0.03458,0.02496],"object_to_goal_dist_end":0.0159,"object_to_goal_dist_start":0.12553,"object_z_max":0.02528,"peak_contact_force":20.36941,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2508.0,"raw_peak_contact_force":22.53362,"subtask_id":"push","tcp_end":[0.49964,-0.12858,0.0183],"tcp_start":[0.44667,0.00227,0.02244],"tcp_to_object_dist_end":0.03772,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":146.0,"n_steps_budget":600.0,"object_pos_end":[0.50359,-0.16725,0.02499],"object_pos_start":[0.50384,-0.16543,0.02522],"object_to_goal_dist_end":0.01761,"object_to_goal_dist_start":0.0159,"object_z_max":0.02525,"peak_contact_force":0.24525,"phase_name":"push_final","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":561.0,"raw_peak_contact_force":1.96063,"subtask_id":"push","tcp_end":[0.4835,-0.08532,0.01819],"tcp_start":[0.49964,-0.12858,0.0183],"tcp_to_object_dist_end":0.08462,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86486,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.51342,"contact.contact_force_threshold":14.75755,"contact.contact_speed":0.03144,"push.push_depth":0.12076,"push.push_speed":0.10044,"push_final.final_push_depth":0.04619,"push_final.final_push_speed":0.10795},"optimized_scores":{"best_composite_score":0.25093,"best_fitness_score":0.66093,"best_task_score":0.979},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":507.0,"contact_point_centroid":[0.50443,-0.14478,-0.00031],"force_p95":55.07678,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.15832,"mean_force":16.56007,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.44991,-0.16289,0.01769]},{"body_a":"push_box","body_b":"link7","contact_count":881.0,"contact_point_centroid":[0.5541,-0.05043,0.05241],"force_p95":58.51223,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.85104,"mean_force":36.92059,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51921,-0.04229,0.01858]},{"body_a":"push_box","body_b":"link7","contact_count":247.0,"contact_point_centroid":[0.50201,-0.13082,0.05137],"force_p95":56.35797,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.60539,"mean_force":32.63301,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.46688,-0.1447,0.0178]},{"body_a":"world","body_b":"push_box","contact_count":1931.0,"contact_point_centroid":[0.55627,-0.08648,-0.00015],"force_p95":44.78868,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.56934,"mean_force":20.74402,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51832,-0.04484,0.01855]},{"body_a":"attachment","body_b":"push_box","contact_count":746.0,"contact_point_centroid":[0.54137,-0.03146,0.05449],"force_p95":29.81553,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.38229,"mean_force":18.7144,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52602,-0.02342,0.01869]},{"body_a":"attachment","body_b":"push_box","contact_count":98.0,"contact_point_centroid":[0.55117,0.02414,0.03465],"force_p95":7.51439,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.79799,"mean_force":3.56711,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.54801,0.03606,0.02077]},{"body_a":"world","body_b":"push_box","contact_count":3088.0,"contact_point_centroid":[0.55342,0.00057,-1e-05],"force_p95":0.863,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.02327,"mean_force":0.35885,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.5453,0.05417,0.02628]},{"body_a":"world","body_b":"push_box","contact_count":2240.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.52148,0.03617,0.1725]}],"total_contact_groups":8},"final_pose_error":0.01486,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50209,-0.15264,0.02492],"final_tcp_position":[0.41839,-0.19663,0.01764],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":63.15832,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":560.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2240.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.54616,0.07546,0.03765],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0755,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":814.0,"n_steps_budget":930.0,"object_pos_end":[0.55414,-0.00306,0.02497],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.1566,"object_to_goal_dist_start":0.16043,"object_z_max":0.0251,"peak_contact_force":5.85535,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3186.0,"raw_peak_contact_force":7.79799,"subtask_id":"contact","tcp_end":[0.54846,0.03364,0.0201],"tcp_start":[0.54616,0.07546,0.03765],"tcp_to_object_dist_end":0.03745,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54127,-0.11784,0.02642],"object_pos_start":[0.55414,-0.00306,0.02497],"object_to_goal_dist_end":0.05234,"object_to_goal_dist_start":0.1566,"object_z_max":0.02855,"peak_contact_force":30.09465,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3558.0,"raw_peak_contact_force":62.85104,"subtask_id":"push","tcp_end":[0.492,-0.11948,0.01854],"tcp_start":[0.54846,0.03364,0.0201],"tcp_to_object_dist_end":0.04993,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":334.0,"n_steps_budget":720.0,"object_pos_end":[0.50209,-0.15264,0.02492],"object_pos_start":[0.54127,-0.11784,0.02642],"object_to_goal_dist_end":0.00337,"object_to_goal_dist_start":0.05234,"object_z_max":0.03256,"peak_contact_force":0.24556,"phase_name":"push_final","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":754.0,"raw_peak_contact_force":63.15832,"subtask_id":"push","tcp_end":[0.41839,-0.19663,0.01764],"tcp_start":[0.492,-0.11948,0.01854],"tcp_to_object_dist_end":0.09484,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```