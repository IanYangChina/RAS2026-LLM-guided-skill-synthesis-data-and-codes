## Search State

- **Seed**: 3
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.5745 | 0.92 | ❌ rejected |
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.6353 | 0.95 | ✅ accepted |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.5356 | 0.86 | ✅ accepted |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.6631 | 0.79 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.5157 | 0.61 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.92). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.574) — your mutation base

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

- **Composite score**: 0.574
- **task_score** (E): 0.922
- **fitness_score**: 0.784  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2589 |
| contact_approach | 1.00 | 1.00 | 0.0196 |
| push_to_goal | 1.00 | 0.67 | 0.1725 |
| retract_up | 0.67 | 1.00 | 0.1075 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.512, 0.056, 0.057) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_approach | contact | 1.00 / force_exceeded | (0.512, 0.056, 0.057)→(0.509, 0.039, 0.049) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 5.000 | 75893.537 | 0.245 |
| push_to_goal | push | 1.00 / step_budget | (0.509, 0.039, 0.049)→(0.501, -0.123, 0.023) | (0.513, 0.002, 0.025)→(0.506, -0.159, 0.027) | 0.160→0.012 | 0.67 / 2.333 | 32.181 | 81.011 |
| retract_up | retract | 0.67 / step_budget | (0.501, -0.123, 0.023)→(0.497, -0.122, 0.130) | (0.506, -0.159, 0.027)→(0.502, -0.161, 0.025) | 0.012→0.013 | 1.00 / 4.000 | 0.245 | 22.204 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.808
- goal_progress: 0.928
- terminal_score: 0.928
- phase_score: 0.734
- phase_breakdown.approach_score: 0.443
- phase_breakdown.push_score: 0.929
- phase_breakdown.contact_score: 0.603

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.812
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.946
- **Median Q (composite search score)**: 0.569
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.245


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05042,"average_solve_count":238.0,"average_success_count":238.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.08461,"contact_approach.contact_force_threshold":6.06187,"contact_approach.contact_speed":0.0291,"push_to_goal.push_lateral_y":0.02264,"push_to_goal.push_speed":0.02424,"push_to_goal.push_tolerance":0.01081,"retract_up.retract_height":0.1526,"retract_up.retract_speed":0.0699},"optimized_scores":{"best_composite_score":0.55246,"best_fitness_score":0.76246,"best_task_score":0.94649},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":3958.0,"contact_point_centroid":[0.50047,-0.15695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.97334,"mean_force":0.27212,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.4894,-0.11937,0.07945]},{"body_a":"push_box","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.5264,-0.13451,0.05011],"force_p95":39.40738,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.80435,"mean_force":24.70684,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49295,-0.1201,0.02137]},{"body_a":"attachment","body_b":"push_box","contact_count":679.0,"contact_point_centroid":[0.47121,-0.07446,0.04617],"force_p95":21.74105,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.43474,"mean_force":8.71786,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.46302,-0.06245,0.03363]},{"body_a":"world","body_b":"push_box","contact_count":1640.0,"contact_point_centroid":[0.47648,-0.10455,-6e-05],"force_p95":11.45716,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.64778,"mean_force":4.1003,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.46013,-0.05676,0.03489]},{"body_a":"push_box","body_b":"link7","contact_count":64.0,"contact_point_centroid":[0.52371,-0.12141,0.05037],"force_p95":10.59393,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.79784,"mean_force":3.46504,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48664,-0.10828,0.02382]},{"body_a":"attachment","body_b":"push_box","contact_count":5.0,"contact_point_centroid":[0.50077,-0.13209,0.03864],"force_p95":0.55072,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.58232,"mean_force":0.29673,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49293,-0.12012,0.02139]},{"body_a":"world","body_b":"push_box","contact_count":3136.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.46327,0.01097,0.17968]},{"body_a":"world","body_b":"push_box","contact_count":1420.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_approach","phase_type":"contact","tcp_position_centroid":[0.42806,0.0129,0.0538]}],"total_contact_groups":8},"final_pose_error":0.03744,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50063,-0.15684,0.02499],"final_tcp_position":[0.48972,-0.11939,0.13669],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":784.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3136.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.42742,0.02225,0.05964],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06798,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":355.0,"n_steps_budget":870.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_approach","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1420.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.4309,0.00517,0.0512],"tcp_start":[0.42742,0.02225,0.05964],"tcp_to_object_dist_end":0.04913,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":961.0,"n_steps_budget":1000.0,"object_pos_end":[0.50116,-0.15703,0.02517],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.00713,"object_to_goal_dist_start":0.12843,"object_z_max":0.02663,"peak_contact_force":1.28413,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2383.0,"raw_peak_contact_force":40.43474,"subtask_id":"push","tcp_end":[0.49298,-0.12001,0.02138],"tcp_start":[0.4309,0.00517,0.0512],"tcp_to_object_dist_end":0.0381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50063,-0.15684,0.02499],"object_pos_start":[0.50116,-0.15703,0.02517],"object_to_goal_dist_end":0.00687,"object_to_goal_dist_start":0.00713,"object_z_max":0.02522,"peak_contact_force":0.24525,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3967.0,"raw_peak_contact_force":40.97334,"tcp_end":[0.48972,-0.11939,0.13669],"tcp_start":[0.49298,-0.12001,0.02138],"tcp_to_object_dist_end":0.11832,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04706,"average_solve_count":255.0,"average_success_count":255.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.06078,"contact_approach.contact_force_threshold":6.37775,"contact_approach.contact_speed":0.03634,"push_to_goal.push_lateral_y":-0.00085,"push_to_goal.push_speed":0.03879,"push_to_goal.push_tolerance":0.02967,"retract_up.retract_height":0.15193,"retract_up.retract_speed":0.04049},"optimized_scores":{"best_composite_score":0.56912,"best_fitness_score":0.77912,"best_task_score":0.89017},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":163.0,"contact_point_centroid":[0.53163,-0.06033,0.04032],"force_p95":63.15728,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.36988,"mean_force":9.91684,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52852,-0.04861,0.03231]},{"body_a":"world","body_b":"push_box","contact_count":330.0,"contact_point_centroid":[0.52683,-0.08432,-0.0002],"force_p95":21.27471,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.41035,"mean_force":5.41423,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53074,-0.04159,0.0332]},{"body_a":"world","body_b":"push_box","contact_count":3920.0,"contact_point_centroid":[0.49592,-0.16722,-2e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.8964,"mean_force":0.2511,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50146,-0.12131,0.06625]},{"body_a":"world","body_b":"push_box","contact_count":3800.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.53165,0.02724,0.17684]},{"body_a":"world","body_b":"push_box","contact_count":964.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_approach","phase_type":"contact","tcp_position_centroid":[0.56055,0.04595,0.04931]}],"total_contact_groups":5},"final_pose_error":0.06606,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49595,-0.16715,0.02499],"final_tcp_position":[0.5017,-0.12127,0.109],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":950.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3800.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.56551,0.0548,0.05565],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":241.0,"n_steps_budget":630.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_approach","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":964.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.55852,0.03837,0.04703],"tcp_start":[0.56551,0.0548,0.05565],"tcp_to_object_dist_end":0.04341,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":293.0,"n_steps_budget":1000.0,"object_pos_end":[0.50138,-0.15875,0.02654],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.00899,"object_to_goal_dist_start":0.16043,"object_z_max":0.0279,"peak_contact_force":0.0,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":493.0,"raw_peak_contact_force":85.36988,"subtask_id":"push","tcp_end":[0.50527,-0.12193,0.02303],"tcp_start":[0.55852,0.03837,0.04703],"tcp_to_object_dist_end":0.03719,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49595,-0.16715,0.02499],"object_pos_start":[0.50138,-0.15875,0.02654],"object_to_goal_dist_end":0.01762,"object_to_goal_dist_start":0.00899,"object_z_max":0.02676,"peak_contact_force":0.24525,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3920.0,"raw_peak_contact_force":2.8964,"tcp_end":[0.5017,-0.12127,0.109],"tcp_start":[0.50527,-0.12193,0.02303],"tcp_to_object_dist_end":0.0959,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22047,"average_solve_count":254.0,"average_success_count":254.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.06851,"contact_approach.contact_force_threshold":6.8783,"contact_approach.contact_speed":0.0247,"push_to_goal.push_lateral_y":-0.00654,"push_to_goal.push_speed":0.02742,"push_to_goal.push_tolerance":0.03117,"retract_up.retract_height":0.13114,"retract_up.retract_speed":0.0762},"optimized_scores":{"best_composite_score":0.60183,"best_fitness_score":0.81183,"best_task_score":0.92845},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":204.0,"contact_point_centroid":[0.52795,-0.0352,0.04839],"force_p95":96.30573,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":117.22869,"mean_force":21.80253,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51861,-0.02441,0.03369]},{"body_a":"push_box","body_b":"link7","contact_count":63.0,"contact_point_centroid":[0.54044,-0.11327,0.05611],"force_p95":92.88032,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":98.28518,"mean_force":27.07354,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50719,-0.09633,0.02648]},{"body_a":"world","body_b":"push_box","contact_count":371.0,"contact_point_centroid":[0.53107,-0.0744,-0.00042],"force_p95":66.29812,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":89.57098,"mean_force":16.10321,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51842,-0.02474,0.0335]},{"body_a":"push_box","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.53039,-0.14408,0.05691],"force_p95":22.36888,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.74209,"mean_force":12.97541,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50252,-0.12711,0.02507]},{"body_a":"attachment","body_b":"push_box","contact_count":159.0,"contact_point_centroid":[0.51376,-0.13554,0.05293],"force_p95":13.6389,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.3694,"mean_force":1.77293,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50023,-0.12581,0.03877]},{"body_a":"world","body_b":"push_box","contact_count":3359.0,"contact_point_centroid":[0.51263,-0.16179,-2e-05],"force_p95":0.50509,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.37959,"mean_force":0.31591,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49989,-0.12541,0.0918]},{"body_a":"world","body_b":"push_box","contact_count":3784.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51995,0.0452,0.17665]},{"body_a":"world","body_b":"push_box","contact_count":1336.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_approach","phase_type":"contact","tcp_position_centroid":[0.53783,0.08116,0.04923]}],"total_contact_groups":8},"final_pose_error":0.01063,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51069,-0.15846,0.02499],"final_tcp_position":[0.50028,-0.12542,0.14548],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":946.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3784.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.5419,0.09078,0.05569],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06219,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":334.0,"n_steps_budget":900.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_approach","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1336.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.53695,0.07393,0.04731],"tcp_start":[0.5419,0.09078,0.05569],"tcp_to_object_dist_end":0.04319,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":348.0,"n_steps_budget":1000.0,"object_pos_end":[0.51423,-0.16253,0.02937],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.01946,"object_to_goal_dist_start":0.1905,"object_z_max":0.03066,"peak_contact_force":95.25995,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":638.0,"raw_peak_contact_force":117.22869,"subtask_id":"push","tcp_end":[0.50347,-0.12606,0.02445],"tcp_start":[0.53695,0.07393,0.04731],"tcp_to_object_dist_end":0.03835,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":978.0,"n_steps_budget":1000.0,"object_pos_end":[0.51069,-0.15846,0.02499],"object_pos_start":[0.51423,-0.16253,0.02937],"object_to_goal_dist_end":0.01363,"object_to_goal_dist_start":0.01946,"object_z_max":0.0301,"peak_contact_force":0.24525,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3538.0,"raw_peak_contact_force":22.74209,"tcp_end":[0.50028,-0.12542,0.14548],"tcp_start":[0.50347,-0.12606,0.02445],"tcp_to_object_dist_end":0.12537,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```