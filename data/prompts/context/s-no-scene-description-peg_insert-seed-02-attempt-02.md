## Search State

- **Seed**: 2
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 8 | 0.8506 | 0.92 | ✅ accepted |
| 1 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 6 | 1.1003 | 0.90 | ✅ accepted |
| 0 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.0712 | 0.10 | ✅ accepted |

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

- Task name: peg_insert
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.851) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: insertion
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    lateral_x_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_y_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  subtask_id: pre_contact
- id: insert_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: negative
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insertion_force_threshold:
      type: scalar
      range:
      - 10.0
      - 40.0
      default: 30.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    insertion_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: insertion

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - lateral_x_offset: status=consumed; consumers=target.offset.x (add)
    - lateral_y_offset: status=consumed; consumers=target.offset.y (add)
- **insert_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=negative}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insertion_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - insertion_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.851
- **task_score** (E): 0.917
- **fitness_score**: 0.917  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.67 | 1.00 | 0.1894 |
| insert_1 | 1.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.67 / step_budget | (0.500, -0.000, 0.301)→(0.480, -0.008, 0.113) | (0.504, -0.000, 0.340)→(0.519, -0.008, 0.107) | 0.260→0.037 | 1.00 / 1.333 | 267.913 | 4709.545 |
| insert_1 | push | 1.00 / force_exceeded | (0.480, -0.008, 0.113)→(0.480, -0.008, 0.113) | (0.519, -0.008, 0.107)→(0.519, -0.008, 0.107) | 0.037→0.037 | 1.00 / 1.667 | 356.373 | 272.433 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.901
- alignment_error: None
- force_efficiency: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.957
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.957
- **Median Q (composite search score)**: 0.994
- **K-run variance**: 0.0432
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.458


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6921a9025d4eafab3a26182307d104597a59aa3c28d9e7087cf253b6e9b1c7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `d09be956b809b9acd01354eeb5f0494d5058516cbca42b9f2b0bee8c1b6b25a7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.17391,"average_solve_count":23.0,"average_success_count":23.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05908,"approach_1.approach_speed":0.32627,"approach_1.approach_tolerance":0.0296,"approach_1.lateral_x_offset":0.01918,"approach_1.lateral_y_offset":0.00555,"insert_1.insertion_depth":0.07045,"insert_1.insertion_force_threshold":26.7899,"insert_1.insertion_speed":0.09607},"optimized_scores":{"best_composite_score":1.00135,"best_fitness_score":0.90135,"best_task_score":0.90135},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":72.0,"contact_point_centroid":[0.5298,-0.00347,0.07934],"force_p95":10769.45986,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":11529.86064,"mean_force":2445.5024,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46248,-0.00354,0.10022]},{"body_a":"peg_socket","body_b":"link7","contact_count":390.0,"contact_point_centroid":[0.54045,-0.00753,0.06638],"force_p95":3035.27231,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6806.66628,"mean_force":586.87259,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46718,-0.00324,0.10891]},{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.45003,0.00403,0.07982],"force_p95":4701.73707,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4875.51015,"mean_force":3938.19943,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44958,-0.0029,0.07787]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54083,-0.00902,0.06406],"force_p95":454.04285,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":472.34328,"mean_force":253.8941,"phase_index":1.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.47167,-0.0051,0.1149]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.54091,-0.00473,0.07992],"force_p95":252.82973,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":252.82973,"mean_force":252.82973,"phase_index":1.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.47182,-0.00486,0.11487]}],"total_contact_groups":5},"final_pose_error":0.10632,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.47175,-0.00475,0.11486],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":11529.86064,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.51004,-0.00511,0.10425],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02674,"object_to_goal_dist_start":0.26034,"object_z_max":0.34495,"peak_contact_force":326.72445,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":475.0,"raw_peak_contact_force":11529.86064,"subtask_id":"pre_contact","tcp_end":[0.47149,-0.00522,0.11491],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":5.0,"n_steps_budget":720.0,"object_pos_end":[0.51023,-0.00474,0.10395],"object_pos_start":[0.51004,-0.00511,0.10425],"object_to_goal_dist_end":0.02647,"object_to_goal_dist_start":0.02674,"object_z_max":0.10425,"peak_contact_force":472.34328,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":472.34328,"subtask_id":"insertion","tcp_end":[0.47175,-0.00475,0.11486],"tcp_start":[0.47149,-0.00522,0.11491],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7c892e828ea48eee928c80191ad243a972830b09953cba6358be1d4656816d00`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.09524,"average_solve_count":21.0,"average_success_count":21.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05027,"approach_1.approach_speed":0.21219,"approach_1.approach_tolerance":0.0296,"approach_1.lateral_x_offset":0.01992,"approach_1.lateral_y_offset":-0.00352,"insert_1.insertion_depth":0.07302,"insert_1.insertion_force_threshold":24.01047,"insert_1.insertion_speed":0.12168},"optimized_scores":{"best_composite_score":0.99383,"best_fitness_score":0.89383,"best_task_score":0.89383},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.49704,-0.00618,0.07951],"force_p95":1071.97157,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1079.28129,"mean_force":855.76751,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46293,-0.00604,0.08238]},{"body_a":"peg_socket","body_b":"link7","contact_count":386.0,"contact_point_centroid":[0.52644,-0.01241,0.06726],"force_p95":358.42494,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":862.2687,"mean_force":319.70211,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45879,-0.00718,0.11893]},{"body_a":"world","body_b":"link6","contact_count":93.0,"contact_point_centroid":[0.67831,-0.00999,-9e-05],"force_p95":298.02033,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":365.34455,"mean_force":137.30103,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46278,-0.00766,0.12325]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.67856,-0.01224,-6e-05],"force_p95":344.95558,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":344.95558,"mean_force":344.95558,"phase_index":1.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.46282,-0.00816,0.12291]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5268,-0.01278,0.06578],"force_p95":192.52386,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":192.52386,"mean_force":192.52386,"phase_index":1.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.46282,-0.00816,0.12291]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.43619,-0.01009,0.07982],"force_p95":186.03189,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":190.54794,"mean_force":87.74721,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43488,-0.00632,0.09353]}],"total_contact_groups":6},"final_pose_error":0.11672,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46284,-0.0081,0.12292],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":1079.28129,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.50019,-0.00925,0.10867],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.03013,"object_to_goal_dist_start":0.26034,"object_z_max":0.34486,"peak_contact_force":225.70302,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":489.0,"raw_peak_contact_force":1079.28129,"subtask_id":"pre_contact","tcp_end":[0.46282,-0.00816,0.12291],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":630.0,"object_pos_end":[0.50021,-0.0092,0.10869],"object_pos_start":[0.50019,-0.00925,0.10867],"object_to_goal_dist_end":0.03013,"object_to_goal_dist_start":0.03013,"object_z_max":0.10867,"peak_contact_force":344.95558,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":344.95558,"subtask_id":"insertion","tcp_end":[0.46284,-0.0081,0.12292],"tcp_start":[0.46282,-0.00816,0.12291],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `65c1f23a0338c26bf257d85b07ab64c0180da795e8d67e7d51a2ed2fb2a4d0db`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":20.0,"average_failure_rate":0.5,"average_mean_iterations":104.275,"average_solve_count":40.0,"average_success_count":20.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19606,"approach_1.approach_speed":0.23698,"approach_1.approach_tolerance":0.02792,"approach_1.lateral_x_offset":0.0155,"approach_1.lateral_y_offset":-0.01156,"insert_1.insertion_depth":0.06562,"insert_1.insertion_force_threshold":23.273,"insert_1.insertion_speed":0.14415},"optimized_scores":{"best_composite_score":0.55668,"best_fitness_score":0.95668,"best_task_score":0.95668},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":49.0,"contact_point_centroid":[0.59392,-0.0134,0.07804],"force_p95":1043.738,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1519.49331,"mean_force":386.18224,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50158,-0.00934,0.09242]},{"body_a":"attachment","body_b":"peg_socket","contact_count":24.0,"contact_point_centroid":[0.5026,-0.01611,0.07915],"force_p95":891.30239,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1058.5891,"mean_force":361.46829,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4976,-0.00877,0.08607]}],"total_contact_groups":2},"final_pose_error":0.09294,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.5066,-0.00989,0.10207],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1519.49331,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":143.0,"n_steps_budget":600.0,"object_pos_end":[0.54614,-0.00997,0.10812],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.05495,"object_to_goal_dist_start":0.26034,"object_z_max":0.34744,"peak_contact_force":251.31073,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":73.0,"raw_peak_contact_force":1519.49331,"subtask_id":"pre_contact","tcp_end":[0.5066,-0.00989,0.10207],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":0.0,"n_steps_budget":600.0,"object_pos_end":[0.54614,-0.00997,0.10812],"object_pos_start":[0.54614,-0.00997,0.10812],"object_to_goal_dist_end":0.05495,"object_to_goal_dist_start":0.05495,"peak_contact_force":251.82038,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion","tcp_end":[0.5066,-0.00989,0.10207],"tcp_start":[0.5066,-0.00989,0.10207],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```