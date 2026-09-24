## Search State

- **Seed**: 2
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → contact → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | contact_lost | pose_tolerance | 7 | 0.4842 | 0.87 | ❌ rejected |
| 12 | approach → contact → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | contact_lost | pose_tolerance | 7 | 0.5297 | 0.95 | ✅ accepted |
| 11 | approach → contact → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | contact_lost | pose_tolerance | 7 | 0.3586 | 0.93 | ✅ accepted |
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.4861 | 0.65 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.5646 | 0.69 | ❌ rejected |

**Proposal policy**: task_score is 0.87 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.484) — your mutation base

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

- **Composite score**: 0.484
- **task_score** (E): 0.873
- **fitness_score**: 0.644  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2742 |
| contact | 1.00 | 1.00 | 0.0417 |
| push | 0.00 | 1.00 | 0.1352 |
| push_final | 1.00 | 1.00 | 0.0935 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.489, 0.058, 0.036) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact | contact | 1.00 / force_exceeded | (0.489, 0.058, 0.036)→(0.487, 0.019, 0.022) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 5.000 | 26.461 | 0.245 |
| push | push | 0.00 / step_budget | (0.487, 0.019, 0.022)→(0.498, -0.110, 0.019) | (0.492, -0.018, 0.025)→(0.517, -0.139, 0.025) | 0.139→0.028 | 1.00 / 2.667 | 7.173 | 35.117 |
| push_final | push | 1.00 / step_budget | (0.498, -0.110, 0.019)→(0.449, -0.108, 0.019) | (0.517, -0.139, 0.025)→(0.497, -0.144, 0.025) | 0.028→0.019 | 1.00 / 4.000 | 0.245 | 22.577 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.633
- goal_progress: 0.880
- terminal_score: 0.880
- phase_score: 0.585
- phase_breakdown.push_score: 0.407
- phase_breakdown.contact_score: 0.774
- phase_breakdown.approach_score: 0.747

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.703
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.980
- **Median Q (composite search score)**: 0.496
- **K-run variance**: 0.0029
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77895,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.94013,"contact.contact_force_threshold":11.35763,"contact.contact_speed":0.21226,"push.push_depth":0.20999,"push.push_speed":0.02118,"push_final.final_push_depth":0.02102,"push_final.final_push_speed":0.11077},"optimized_scores":{"best_composite_score":0.54323,"best_fitness_score":0.70323,"best_task_score":0.88043},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":882.0,"contact_point_centroid":[0.4841,-0.0686,0.03465],"force_p95":15.4587,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.43647,"mean_force":3.81352,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47998,-0.0567,0.01917]},{"body_a":"world","body_b":"push_box","contact_count":1294.0,"contact_point_centroid":[0.48639,-0.10705,-4e-05],"force_p95":8.28192,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.14246,"mean_force":2.98408,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47868,-0.05049,0.01934]},{"body_a":"world","body_b":"push_box","contact_count":531.0,"contact_point_centroid":[0.50427,-0.16581,-4e-05],"force_p95":0.41475,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.22558,"mean_force":0.26651,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.48738,-0.10634,0.01679]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.50494,-0.13983,0.05111],"force_p95":1.15415,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.24452,"mean_force":0.55322,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.49638,-0.12799,0.01872]},{"body_a":"world","body_b":"push_box","contact_count":2232.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48477,0.02489,0.17266]},{"body_a":"world","body_b":"push_box","contact_count":1872.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.46701,0.03182,0.02915]}],"total_contact_groups":6},"final_pose_error":0.0148,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50421,-0.16484,0.02499],"final_tcp_position":[0.4805,-0.08533,0.01703],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":26.43647,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":558.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2232.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.46986,0.05174,0.03893],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":468.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":26.05682,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1872.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.4673,0.01282,0.02304],"tcp_start":[0.46986,0.05174,0.03893],"tcp_to_object_dist_end":0.03727,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50414,-0.16413,0.02556],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.01473,"object_to_goal_dist_start":0.12903,"object_z_max":0.02571,"peak_contact_force":1.61561,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2176.0,"raw_peak_contact_force":26.43647,"subtask_id":"push","tcp_end":[0.4964,-0.12784,0.01875],"tcp_start":[0.4673,0.01282,0.02304],"tcp_to_object_dist_end":0.03772,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":142.0,"n_steps_budget":600.0,"object_pos_end":[0.50421,-0.16484,0.02499],"object_pos_start":[0.50414,-0.16413,0.02556],"object_to_goal_dist_end":0.01543,"object_to_goal_dist_start":0.01473,"object_z_max":0.02558,"peak_contact_force":0.24525,"phase_name":"push_final","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":535.0,"raw_peak_contact_force":2.22558,"subtask_id":"push","tcp_end":[0.4805,-0.08533,0.01703],"tcp_start":[0.4964,-0.12784,0.01875],"tcp_to_object_dist_end":0.08336,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9604,"average_solve_count":101.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.55735,"contact.contact_force_threshold":10.16242,"contact.contact_speed":0.08402,"push.push_depth":0.16105,"push.push_speed":0.02352,"push_final.final_push_depth":0.08331,"push_final.final_push_speed":0.09134},"optimized_scores":{"best_composite_score":0.49599,"best_fitness_score":0.65599,"best_task_score":0.97975},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":891.0,"contact_point_centroid":[0.47135,-0.0657,0.03305],"force_p95":12.75776,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.6785,"mean_force":3.79796,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.46828,-0.05376,0.01968]},{"body_a":"world","body_b":"push_box","contact_count":1741.0,"contact_point_centroid":[0.47399,-0.09999,-4e-05],"force_p95":6.60651,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.85135,"mean_force":2.24487,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.46818,-0.05353,0.01968]},{"body_a":"world","body_b":"push_box","contact_count":1054.0,"contact_point_centroid":[0.50108,-0.15262,-2e-05],"force_p95":0.24924,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.39009,"mean_force":0.25228,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.46517,-0.07534,0.01845]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.50079,-0.1268,0.05],"force_p95":1.51344,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.59084,"mean_force":1.03155,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.4938,-0.11485,0.01904]},{"body_a":"world","body_b":"push_box","contact_count":2232.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47529,0.02164,0.17252]},{"body_a":"world","body_b":"push_box","contact_count":1880.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.44691,0.02472,0.02954]}],"total_contact_groups":6},"final_pose_error":0.01488,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50112,-0.15235,0.02499],"final_tcp_position":[0.43902,-0.03589,0.02112],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":24.99587,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":558.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2232.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.45028,0.04491,0.0391],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":470.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":24.99587,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1880.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.44659,0.0054,0.02338],"tcp_start":[0.45028,0.04491,0.0391],"tcp_to_object_dist_end":0.0372,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5009,-0.15158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.00182,"object_to_goal_dist_start":0.12843,"object_z_max":0.02525,"peak_contact_force":0.00045,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2632.0,"raw_peak_contact_force":22.6785,"subtask_id":"push","tcp_end":[0.49379,-0.11476,0.01906],"tcp_start":[0.44659,0.0054,0.02338],"tcp_to_object_dist_end":0.03796,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":270.0,"n_steps_budget":780.0,"object_pos_end":[0.50112,-0.15235,0.02499],"object_pos_start":[0.5009,-0.15158,0.02499],"object_to_goal_dist_end":0.0026,"object_to_goal_dist_start":0.00182,"object_z_max":0.02508,"peak_contact_force":0.24525,"phase_name":"push_final","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1057.0,"raw_peak_contact_force":2.39009,"subtask_id":"push","tcp_end":[0.43902,-0.03589,0.02112],"tcp_start":[0.49379,-0.11476,0.01906],"tcp_to_object_dist_end":0.13204,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.00833,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.191,"contact.contact_force_threshold":10.37109,"contact.contact_speed":0.15882,"push.push_depth":0.1386,"push.push_speed":0.02315,"push_final.final_push_depth":0.04103,"push_final.final_push_speed":0.09663},"optimized_scores":{"best_composite_score":0.41341,"best_fitness_score":0.57341,"best_task_score":0.75833},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1128.0,"contact_point_centroid":[0.50335,-0.11871,-0.00019],"force_p95":54.6875,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.11431,"mean_force":10.24935,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.45992,-0.15291,0.01834]},{"body_a":"push_box","body_b":"link7","contact_count":265.0,"contact_point_centroid":[0.5181,-0.10701,0.05144],"force_p95":58.30862,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.40078,"mean_force":41.86574,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.48225,-0.11768,0.01808]},{"body_a":"push_box","body_b":"link7","contact_count":905.0,"contact_point_centroid":[0.55965,-0.03402,0.05212],"force_p95":54.38981,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.23716,"mean_force":34.12926,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52442,-0.02303,0.01838]},{"body_a":"world","body_b":"push_box","contact_count":1873.0,"contact_point_centroid":[0.5601,-0.07045,-0.00014],"force_p95":37.58023,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.76621,"mean_force":20.59391,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52375,-0.0253,0.01848]},{"body_a":"attachment","body_b":"push_box","contact_count":891.0,"contact_point_centroid":[0.54189,-0.02419,0.05355],"force_p95":27.56957,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.72605,"mean_force":16.05064,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52697,-0.01581,0.01845]},{"body_a":"attachment","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.46403,-0.14212,0.03952],"force_p95":0.14429,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32064,"mean_force":0.02672,"phase_index":3.0,"phase_name":"push_final","phase_type":"push","tcp_position_centroid":[0.4591,-0.15378,0.01802]},{"body_a":"world","body_b":"push_box","contact_count":3336.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.52255,0.03855,0.16424]},{"body_a":"world","body_b":"push_box","contact_count":1864.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.54547,0.05722,0.0234]}],"total_contact_groups":8},"final_pose_error":0.01479,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48669,-0.11359,0.02499],"final_tcp_position":[0.42829,-0.20407,0.01978],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":63.11431,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":834.0,"n_steps_budget":960.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3336.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.5467,0.07723,0.03117],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":466.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":28.33042,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1864.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.54769,0.03831,0.02029],"tcp_start":[0.5467,0.07723,0.03117],"tcp_to_object_dist_end":0.03765,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54603,-0.10274,0.02521],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.06597,"object_to_goal_dist_start":0.16043,"object_z_max":0.02836,"peak_contact_force":19.90396,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3669.0,"raw_peak_contact_force":56.23716,"subtask_id":"push","tcp_end":[0.50249,-0.08645,0.0177],"tcp_start":[0.54769,0.03831,0.02029],"tcp_to_object_dist_end":0.04709,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":469.0,"n_steps_budget":990.0,"object_pos_end":[0.48669,-0.11359,0.02499],"object_pos_start":[0.54603,-0.10274,0.02521],"object_to_goal_dist_end":0.03877,"object_to_goal_dist_start":0.06597,"object_z_max":0.02888,"peak_contact_force":0.24525,"phase_name":"push_final","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1405.0,"raw_peak_contact_force":63.11431,"subtask_id":"push","tcp_end":[0.42829,-0.20407,0.01978],"tcp_start":[0.50249,-0.08645,0.0177],"tcp_to_object_dist_end":0.10782,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```