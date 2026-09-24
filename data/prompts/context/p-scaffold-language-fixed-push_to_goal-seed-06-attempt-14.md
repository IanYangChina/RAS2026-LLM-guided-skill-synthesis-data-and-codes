## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | time_limit | force_exceeded | time_limit | time_limit | 8 | 0.8176 | 0.28 | ❌ rejected |
| 13 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.5941 | 0.95 | ✅ accepted |
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.5692 | 0.95 | ❌ rejected |
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3752 | 0.94 | ❌ rejected |
| 10 | approach → descend → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.4797 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.28 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`
- Frozen object start: [0.5045797221766332, -0.01880749562239939, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5045797221766332, -0.01880749562239939, 0.025)
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
  frozen_object_start: [0.5046, -0.0188, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5045797221766332, -0.01880749562239939, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0046, -0.1312, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7

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

## Current Skill (Q=0.818) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
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
  offset:
  - 0.0
  - 0.03
  - 0.0
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
    - 0.05
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
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
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
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
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.08, 0.05], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.03, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.818
- **task_score** (E): 0.276
- **fitness_score**: 0.278  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 1.000
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1843 |
| contact_1 | 1.00 | 1.00 | 0.0922 |
| push_1 | 1.00 | 1.00 | 0.0806 |
| retract_1 | 1.00 | 1.00 | 0.0835 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.497, 0.078, 0.135) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.497, 0.078, 0.135)→(0.495, 0.062, 0.046) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.179 | 1.00 / 4.667 | 38.297 | 6.497 |
| push_1 | push | 1.00 / time_limit | (0.495, 0.062, 0.046)→(0.494, -0.019, 0.045) | (0.500, 0.029, 0.025)→(0.503, -0.016, 0.028) | 0.179→0.135 | 1.00 / 3.333 | 49.988 | 53.989 |
| retract_1 | retract | 1.00 / time_limit | (0.494, -0.019, 0.045)→(0.497, -0.023, 0.127) | (0.503, -0.016, 0.028)→(0.503, -0.014, 0.025) | 0.135→0.137 | 1.00 / 4.000 | 0.245 | 51.824 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.549
- lateral_force_integral: None
- approach_alignment: 0.761
- goal_progress: 0.546
- terminal_score: 0.546
- phase_score: 0.403
- phase_breakdown.push_score: 0.280
- phase_breakdown.approach_score: 0.175
- phase_breakdown.contact_score: 0.758

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.460
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.546
- **Median Q (composite search score)**: 0.736
- **K-run variance**: 0.0167
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.447


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `acf3715aaa310bcc73047d49f01e71bc863ef036ae437b7dc851a0f6d3fe40ae`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec1d0331416d42e6883eeb3b72499fac99c0735b785eb70ece69dc94e8044fc3`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3815,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07572,"approach_1.speed":0.0966,"contact_1.contact_force":17.53865,"contact_1.speed":0.0318,"push_1.push_depth":0.18139,"push_1.speed":0.04791,"retract_1.retract_height":0.1297,"retract_1.speed":0.0848},"optimized_scores":{"best_composite_score":0.99993,"best_fitness_score":0.45993,"best_task_score":0.54577},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.53092,-0.08012,0.05586],"force_p95":16.51416,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.81932,"mean_force":4.28267,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49303,-0.06223,0.0285]},{"body_a":"world","body_b":"push_box","contact_count":1462.0,"contact_point_centroid":[0.51574,-0.07536,-6e-05],"force_p95":13.89466,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.59353,"mean_force":4.46165,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49486,-0.02119,0.02764]},{"body_a":"world","body_b":"push_box","contact_count":3092.0,"contact_point_centroid":[0.50996,-0.09529,-3e-05],"force_p95":0.47573,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.80583,"mean_force":0.33121,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50021,-0.07973,0.09517]},{"body_a":"attachment","body_b":"push_box","contact_count":17.0,"contact_point_centroid":[0.49989,0.00576,0.03318],"force_p95":16.04588,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.99905,"mean_force":10.96221,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49983,0.01771,0.03306]},{"body_a":"attachment","body_b":"push_box","contact_count":926.0,"contact_point_centroid":[0.50587,-0.03481,0.04623],"force_p95":11.27186,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.38234,"mean_force":4.56775,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49465,-0.02351,0.0275]},{"body_a":"push_box","body_b":"link7","contact_count":268.0,"contact_point_centroid":[0.52936,-0.06056,0.05575],"force_p95":14.19974,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.60174,"mean_force":7.62121,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49374,-0.04981,0.02748]},{"body_a":"attachment","body_b":"push_box","contact_count":205.0,"contact_point_centroid":[0.50687,-0.07569,0.05595],"force_p95":3.13363,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.05496,"mean_force":0.86097,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49308,-0.06617,0.0424]},{"body_a":"world","body_b":"push_box","contact_count":2548.0,"contact_point_centroid":[0.50446,-0.01895,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.78799,"mean_force":0.31851,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49875,0.03589,0.0691]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49936,0.02816,0.20335]}],"total_contact_groups":9},"final_pose_error":0.01128,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50695,-0.09078,0.02499],"final_tcp_position":[0.508,-0.09341,0.14886],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":26.81932,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.50062,0.05583,0.11192],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11465,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":643.0,"n_steps_budget":1000.0,"object_pos_end":[0.50454,-0.01958,0.02496],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.1305,"object_to_goal_dist_start":0.13127,"object_z_max":0.02501,"peak_contact_force":18.99905,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2565.0,"raw_peak_contact_force":18.99905,"subtask_id":"contact","tcp_end":[0.49994,0.01724,0.03191],"tcp_start":[0.50062,0.05583,0.11192],"tcp_to_object_dist_end":0.03775,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51192,-0.0952,0.02959],"object_pos_start":[0.50454,-0.01958,0.02496],"object_to_goal_dist_end":0.05627,"object_to_goal_dist_start":0.1305,"object_z_max":0.02958,"peak_contact_force":16.34932,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2656.0,"raw_peak_contact_force":24.59353,"subtask_id":"push","tcp_end":[0.4938,-0.0618,0.02794],"tcp_start":[0.49994,0.01724,0.03191],"tcp_to_object_dist_end":0.03803,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":962.0,"n_steps_budget":1000.0,"object_pos_end":[0.50695,-0.09078,0.02499],"object_pos_start":[0.51192,-0.0952,0.02959],"object_to_goal_dist_end":0.05963,"object_to_goal_dist_start":0.05627,"object_z_max":0.0305,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3330.0,"raw_peak_contact_force":26.81932,"tcp_end":[0.508,-0.09341,0.14886],"tcp_start":[0.4938,-0.0618,0.02794],"tcp_to_object_dist_end":0.1239,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `589e611c6c27578474525e3fd29be4fb5907d8bbd5d1ca44922bfd811e342c78`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04819,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07399,"approach_1.speed":0.09635,"contact_1.contact_force":14.32792,"contact_1.speed":0.04173,"push_1.push_depth":0.2054,"push_1.speed":0.04988,"retract_1.retract_height":0.17271,"retract_1.speed":0.01669},"optimized_scores":{"best_composite_score":0.73555,"best_fitness_score":0.19555,"best_task_score":0.16079},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":1000.0,"contact_point_centroid":[0.51678,0.04148,0.04923],"force_p95":69.07339,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.11603,"mean_force":61.76772,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50586,0.04111,0.05283]},{"body_a":"attachment","body_b":"push_box","contact_count":73.0,"contact_point_centroid":[0.513,0.0025,0.05063],"force_p95":32.39952,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.91356,"mean_force":12.88191,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50261,-0.00166,0.0545]},{"body_a":"world","body_b":"push_box","contact_count":3795.0,"contact_point_centroid":[0.51642,0.015,-3e-05],"force_p95":0.28044,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.13284,"mean_force":0.50702,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50136,0.00132,0.07288]},{"body_a":"world","body_b":"push_box","contact_count":3244.0,"contact_point_centroid":[0.51369,0.03061,-0.00024],"force_p95":36.42081,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.57417,"mean_force":19.34597,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50617,0.0466,0.05277]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50265,0.04464,0.22498]},{"body_a":"world","body_b":"push_box","contact_count":2436.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50672,0.08357,0.10264]}],"total_contact_groups":6},"final_pose_error":0.10972,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51685,0.01551,0.02499],"final_tcp_position":[0.50256,0.00403,0.09239],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":70.11603,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.50712,0.0879,0.15581],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1371,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":609.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":51.02028,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2436.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.50901,0.07962,0.05316],"tcp_start":[0.50712,0.0879,0.15581],"tcp_to_object_dist_end":0.04302,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51266,0.01842,0.02798],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.16892,"object_to_goal_dist_start":0.19823,"object_z_max":0.02795,"peak_contact_force":68.60162,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4244.0,"raw_peak_contact_force":70.11603,"subtask_id":"push","tcp_end":[0.50358,-0.0019,0.05351],"tcp_start":[0.50901,0.07962,0.05316],"tcp_to_object_dist_end":0.03386,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51685,0.01551,0.02499],"object_pos_start":[0.51266,0.01842,0.02798],"object_to_goal_dist_end":0.16636,"object_to_goal_dist_start":0.16892,"object_z_max":0.02802,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3868.0,"raw_peak_contact_force":67.91356,"tcp_end":[0.50256,0.00403,0.09239],"tcp_start":[0.50358,-0.0019,0.05351],"tcp_to_object_dist_end":0.06985,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f2c9c63f0d9eca1b3ff8bf951759f6a3adee73f9f65e1cd3613c5e9d1203ebcc`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20667,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0383,"approach_1.speed":0.09976,"contact_1.contact_force":2.31506,"contact_1.speed":0.04994,"push_1.push_depth":0.10764,"push_1.speed":0.05,"retract_1.retract_height":0.19975,"retract_1.speed":0.05446},"optimized_scores":{"best_composite_score":0.71732,"best_fitness_score":0.17732,"best_task_score":0.12081},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":1000.0,"contact_point_centroid":[0.49094,0.05097,0.04919],"force_p95":64.59006,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.25621,"mean_force":59.69938,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48013,0.05022,0.05343]},{"body_a":"world","body_b":"push_box","contact_count":3091.0,"contact_point_centroid":[0.48067,0.04032,-0.00023],"force_p95":52.70759,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.01937,"mean_force":19.65964,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47946,0.05629,0.0534]},{"body_a":"attachment","body_b":"push_box","contact_count":48.0,"contact_point_centroid":[0.49422,0.01207,0.05041],"force_p95":32.86896,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.7399,"mean_force":14.25807,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48389,0.00814,0.05466]},{"body_a":"world","body_b":"push_box","contact_count":3852.0,"contact_point_centroid":[0.48373,0.03281,-2e-05],"force_p95":0.24869,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.5879,"mean_force":0.43307,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48105,0.01379,0.09554]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49037,0.04612,0.21657]},{"body_a":"world","body_b":"push_box","contact_count":1908.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47848,0.08966,0.09549]}],"total_contact_groups":6},"final_pose_error":0.08978,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48397,0.03349,0.02499],"final_tcp_position":[0.48108,0.01924,0.13836],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":67.25621,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.48297,0.09112,0.13873],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11839,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":477.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":44.87122,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1908.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.47651,0.08856,0.0541],"tcp_start":[0.48297,0.09112,0.13873],"tcp_to_object_dist_end":0.04196,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48401,0.03015,0.02767],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.18088,"object_to_goal_dist_start":0.2095,"object_z_max":0.02765,"peak_contact_force":65.01176,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4091.0,"raw_peak_contact_force":67.25621,"subtask_id":"push","tcp_end":[0.48466,0.00811,0.05373],"tcp_start":[0.47651,0.08856,0.0541],"tcp_to_object_dist_end":0.03414,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48397,0.03349,0.02499],"object_pos_start":[0.48401,0.03015,0.02767],"object_to_goal_dist_end":0.18419,"object_to_goal_dist_start":0.18088,"object_z_max":0.02775,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3900.0,"raw_peak_contact_force":60.7399,"tcp_end":[0.48108,0.01924,0.13836],"tcp_start":[0.48466,0.00811,0.05373],"tcp_to_object_dist_end":0.1143,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```