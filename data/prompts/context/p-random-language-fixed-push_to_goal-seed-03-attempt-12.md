## Search State

- **Seed**: 3
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.6353 | 0.95 | ✅ accepted |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.5356 | 0.86 | ✅ accepted |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.6631 | 0.79 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.5157 | 0.61 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.6154 | 0.85 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`
- Frozen object start: [0.45027790005723495, -0.03158273920846803, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.45027790005723495, -0.03158273920846803, 0.025)
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
  frozen_object_start: [0.4503, -0.0316, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.45027790005723495, -0.03158273920846803, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0497, -0.1184, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be

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

## Current Skill (Q=0.635) — your mutation base

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
- id: approach_behind
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.025
    offset_along_axis:
      distance: 0.08
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: contact_approach
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.025
    offset_along_axis:
      distance: 0.02
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 3.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: contact
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    push_lateral_y:
      type: scalar
      range:
      - -0.03
      - 0.05
      default: 0.01
      binds_to:
      - path: target.offset.y
        mode: add
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: contact_maintained
    when: during_phase
    predicate: contact_detected
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: push
- id: retract_up
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
    - 0.2
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=0.08, mode=add_to_offset, sign=negative}
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_approach** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=0.02, mode=add_to_offset, sign=negative}
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - push_lateral_y: status=consumed; consumers=target.offset.y (add)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=contact_maintained, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.5
  - retries: max_attempts=3, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **retract_up** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2]
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.635
- **task_score** (E): 0.948
- **fitness_score**: 0.795  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2655 |
| contact_approach | 1.00 | 1.00 | 0.0376 |
| push_to_goal | 1.00 | 1.00 | 0.1695 |
| retract_up | 1.00 | 1.00 | 0.1627 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.513, 0.074, 0.056) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_approach | contact | 1.00 / force_exceeded | (0.513, 0.074, 0.056)→(0.509, 0.039, 0.047) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 5.000 | 75893.537 | 0.245 |
| push_to_goal | push | 1.00 / step_budget | (0.509, 0.039, 0.047)→(0.500, -0.119, 0.022) | (0.513, 0.002, 0.025)→(0.505, -0.158, 0.025) | 0.160→0.009 | 1.00 / 2.667 | 7.293 | 54.338 |
| retract_up | retract | 1.00 / step_budget | (0.500, -0.119, 0.022)→(0.497, -0.119, 0.185) | (0.505, -0.158, 0.025)→(0.505, -0.157, 0.025) | 0.009→0.008 | 1.00 / 4.000 | 0.245 | 2.215 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.853
- goal_progress: 0.956
- terminal_score: 0.956
- phase_score: 0.734
- phase_breakdown.approach_score: 0.525
- phase_breakdown.push_score: 0.888
- phase_breakdown.contact_score: 0.616

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.823
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.956
- **Median Q (composite search score)**: 0.641
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.223


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `01fea9f27a58d64b0f9b0ff0cae1096a52b0da1ad311c77058a75ddb9aab77d2`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c53c9bf1992485fcf877d50f4ee23d3483b4b9e63e5a19adda2461c26d89c46e`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.98712,"average_solve_count":233.0,"average_success_count":233.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.12199,"contact_approach.contact_force_threshold":7.02906,"contact_approach.contact_speed":0.02758,"push_to_goal.push_lateral_y":0.02426,"push_to_goal.push_speed":0.01915,"push_to_goal.push_tolerance":0.01134,"retract_up.retract_height":0.17865},"optimized_scores":{"best_composite_score":0.60177,"best_fitness_score":0.76177,"best_task_score":0.95215},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1467.0,"contact_point_centroid":[0.48218,-0.10553,-7e-05],"force_p95":13.34277,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.34265,"mean_force":4.39911,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.46083,-0.0573,0.03372]},{"body_a":"attachment","body_b":"push_box","contact_count":586.0,"contact_point_centroid":[0.47212,-0.07078,0.05017],"force_p95":21.56912,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.09725,"mean_force":9.3561,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.46159,-0.05876,0.0334]},{"body_a":"push_box","body_b":"link7","contact_count":54.0,"contact_point_centroid":[0.52374,-0.1264,0.05038],"force_p95":11.33655,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.9166,"mean_force":7.32937,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48653,-0.10587,0.0239]},{"body_a":"world","body_b":"push_box","contact_count":3960.0,"contact_point_centroid":[0.50253,-0.15578,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.53522,"mean_force":0.2472,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48953,-0.11704,0.10322]},{"body_a":"attachment","body_b":"push_box","contact_count":17.0,"contact_point_centroid":[0.50641,-0.12918,0.04973],"force_p95":1.59385,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.95748,"mean_force":0.755,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49139,-0.11756,0.02411]},{"body_a":"push_box","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.5251,-0.143,0.05088],"force_p95":0.8757,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.03023,"mean_force":0.25756,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.4923,-0.11775,0.02183]},{"body_a":"world","body_b":"push_box","contact_count":3088.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.45959,0.01958,0.17943]},{"body_a":"world","body_b":"push_box","contact_count":3136.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_approach","phase_type":"contact","tcp_position_centroid":[0.42413,0.02155,0.05272]}],"total_contact_groups":8},"final_pose_error":0.01551,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50254,-0.15559,0.02499],"final_tcp_position":[0.48997,-0.11707,0.18502],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":772.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3088.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.42003,0.03964,0.05944],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0847,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":784.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_approach","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3136.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.4308,0.0054,0.04952],"tcp_start":[0.42003,0.03964,0.05944],"tcp_to_object_dist_end":0.04847,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":879.0,"n_steps_budget":1000.0,"object_pos_end":[0.5026,-0.15567,0.02478],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.00624,"object_to_goal_dist_start":0.12843,"object_z_max":0.02634,"peak_contact_force":19.28768,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2107.0,"raw_peak_contact_force":27.34265,"subtask_id":"push","tcp_end":[0.49286,-0.11763,0.0216],"tcp_start":[0.4308,0.0054,0.04952],"tcp_to_object_dist_end":0.03939,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50254,-0.15559,0.02499],"object_pos_start":[0.5026,-0.15567,0.02478],"object_to_goal_dist_end":0.00614,"object_to_goal_dist_start":0.00624,"object_z_max":0.02546,"peak_contact_force":0.24525,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3981.0,"raw_peak_contact_force":2.53522,"tcp_end":[0.48997,-0.11707,0.18502],"tcp_start":[0.49286,-0.11763,0.0216],"tcp_to_object_dist_end":0.16508,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `234a0edc218dcf63b67654ddcfd8b0f12da84040687f62c4c4845001a50f549a`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26877,"average_solve_count":253.0,"average_success_count":253.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.09059,"contact_approach.contact_force_threshold":7.44317,"contact_approach.contact_speed":0.02322,"push_to_goal.push_lateral_y":0.0017,"push_to_goal.push_speed":0.02497,"push_to_goal.push_tolerance":0.02876,"retract_up.retract_height":0.20848},"optimized_scores":{"best_composite_score":0.6413,"best_fitness_score":0.8013,"best_task_score":0.93547},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":162.0,"contact_point_centroid":[0.53685,-0.04398,0.04499],"force_p95":29.21424,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.65235,"mean_force":5.1857,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53381,-0.03281,0.03321]},{"body_a":"world","body_b":"push_box","contact_count":326.0,"contact_point_centroid":[0.52769,-0.08191,-0.00052],"force_p95":15.26531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.40578,"mean_force":3.10289,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5323,-0.03746,0.03266]},{"body_a":"attachment","body_b":"push_box","contact_count":55.0,"contact_point_centroid":[0.50181,-0.13254,0.02993],"force_p95":1.05576,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.84605,"mean_force":0.78283,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50212,-0.12056,0.02978]},{"body_a":"world","body_b":"push_box","contact_count":3789.0,"contact_point_centroid":[0.5074,-0.15855,-2e-05],"force_p95":0.3395,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79035,"mean_force":0.25368,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50169,-0.11975,0.10637]},{"body_a":"world","body_b":"push_box","contact_count":3728.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.53504,0.03635,0.17604]},{"body_a":"world","body_b":"push_box","contact_count":3344.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_approach","phase_type":"contact","tcp_position_centroid":[0.56361,0.0541,0.04729]}],"total_contact_groups":6},"final_pose_error":0.04643,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50743,-0.15721,0.02499],"final_tcp_position":[0.50226,-0.11977,0.18478],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":932.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3728.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.572,0.07289,0.05475],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07973,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":836.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_approach","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3344.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.55969,0.03833,0.04562],"tcp_start":[0.572,0.07289,0.05475],"tcp_to_object_dist_end":0.04284,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.50761,-0.15918,0.02418],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.01196,"object_to_goal_dist_start":0.16043,"object_z_max":0.03104,"peak_contact_force":0.946,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":488.0,"raw_peak_contact_force":72.65235,"subtask_id":"push","tcp_end":[0.50511,-0.12033,0.02264],"tcp_start":[0.55969,0.03833,0.04562],"tcp_to_object_dist_end":0.03897,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50743,-0.15721,0.02499],"object_pos_start":[0.50761,-0.15918,0.02418],"object_to_goal_dist_end":0.01035,"object_to_goal_dist_start":0.01196,"object_z_max":0.02569,"peak_contact_force":0.24525,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3844.0,"raw_peak_contact_force":1.84605,"tcp_end":[0.50226,-0.11977,0.18478],"tcp_start":[0.50511,-0.12033,0.02264],"tcp_to_object_dist_end":0.1642,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `107d1233d3b0a09f0fa34aa18231b315c9a1d92237bb254399d486ed8004836a`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37349,"average_solve_count":249.0,"average_success_count":249.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.08454,"contact_approach.contact_force_threshold":6.9041,"contact_approach.contact_speed":0.03398,"push_to_goal.push_lateral_y":0.00543,"push_to_goal.push_speed":0.02135,"push_to_goal.push_tolerance":0.02517,"retract_up.retract_height":0.18778},"optimized_scores":{"best_composite_score":0.66275,"best_fitness_score":0.82275,"best_task_score":0.95621},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":66.0,"contact_point_centroid":[0.53668,-0.09818,0.05707],"force_p95":55.9259,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.01775,"mean_force":9.2526,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50721,-0.08268,0.02598]},{"body_a":"attachment","body_b":"push_box","contact_count":225.0,"contact_point_centroid":[0.52739,-0.03278,0.04472],"force_p95":45.29354,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.4807,"mean_force":8.91481,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51816,-0.02173,0.03235]},{"body_a":"world","body_b":"push_box","contact_count":321.0,"contact_point_centroid":[0.53588,-0.07018,-0.00011],"force_p95":33.1198,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.71666,"mean_force":8.77742,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51937,-0.01532,0.03312]},{"body_a":"world","body_b":"push_box","contact_count":3778.0,"contact_point_centroid":[0.50508,-0.15827,-1e-05],"force_p95":0.36079,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.26418,"mean_force":0.25849,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49738,-0.11913,0.10697]},{"body_a":"attachment","body_b":"push_box","contact_count":62.0,"contact_point_centroid":[0.51134,-0.1314,0.05171],"force_p95":1.20096,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.61891,"mean_force":0.64253,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.498,-0.11988,0.03022]},{"body_a":"world","body_b":"push_box","contact_count":3828.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52189,0.05473,0.17604]},{"body_a":"world","body_b":"push_box","contact_count":2368.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_approach","phase_type":"contact","tcp_position_centroid":[0.53991,0.09054,0.04796]}],"total_contact_groups":7},"final_pose_error":0.02539,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50469,-0.1569,0.02499],"final_tcp_position":[0.49786,-0.11913,0.18496],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":957.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3828.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.54566,0.10963,0.05504],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07917,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":592.0,"n_steps_budget":990.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_approach","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2368.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.53794,0.07391,0.046],"tcp_start":[0.54566,0.10963,0.05504],"tcp_to_object_dist_end":0.04253,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":405.0,"n_steps_budget":1000.0,"object_pos_end":[0.50608,-0.15782,0.02715],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.01014,"object_to_goal_dist_start":0.1905,"object_z_max":0.03077,"peak_contact_force":1.64638,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":612.0,"raw_peak_contact_force":63.01775,"subtask_id":"push","tcp_end":[0.50077,-0.11971,0.02239],"tcp_start":[0.53794,0.07391,0.046],"tcp_to_object_dist_end":0.03878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50469,-0.1569,0.02499],"object_pos_start":[0.50608,-0.15782,0.02715],"object_to_goal_dist_end":0.00834,"object_to_goal_dist_start":0.01014,"object_z_max":0.02715,"peak_contact_force":0.24525,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3840.0,"raw_peak_contact_force":2.26418,"tcp_end":[0.49786,-0.11913,0.18496],"tcp_start":[0.50077,-0.11971,0.02239],"tcp_to_object_dist_end":0.16451,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```