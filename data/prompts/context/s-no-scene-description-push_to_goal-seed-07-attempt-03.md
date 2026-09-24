## Search State

- **Seed**: 7
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | release → approach → push | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | 5 | 0.5517 | 0.94 | ✅ accepted |
| 2 | release → approach → push | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | 4 | -0.0730 | 0.00 | ✅ accepted |
| 1 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.3400 | 0.00 | ❌ rejected |
| 0 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.3400 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.94). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Primary evaluation target: **object displacement ratio toward goal_object_position**

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
| `fixture` | offset from fixture pose | targets near fixture |

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

## Current Skill (Q=0.552) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: contact_object
  anchor: object
  weight: 0.3
- id: reach_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    max_time:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: duration.max_time
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
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
    - 0.0
    offset_along_axis:
      distance: 0.02
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.005
    orientation:
      mode: none
  parameters:
    behind_distance:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.02
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: contact_object
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.3
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    distance:
      type: scalar
      range:
      - 0.1
      - 0.45
      default: 0.3
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (replace)
  - retries: max_attempts=0, strategy=repeat
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.02, mode=add_to_offset, sign=negative}, tolerance=0.005
  - orientation: mode=none
  - parameter_bindings:
    - behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.3, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.552
- **task_score** (E): 0.936
- **fitness_score**: 0.832  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| release_1 | 1.00 | 1.00 | 0.0085 |
| approach_behind | 1.00 | 1.00 | 0.2713 |
| push_to_goal | 1.00 | 1.00 | 0.2288 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| release_1 | release | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, -0.000, 0.293) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| approach_behind | approach | 1.00 / step_budget | (0.496, -0.000, 0.293)→(0.511, 0.076, 0.038) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_to_goal | push | 1.00 / step_budget | (0.511, 0.076, 0.038)→(0.483, -0.148, 0.034) | (0.513, 0.027, 0.025)→(0.509, -0.150, 0.028) | 0.180→0.011 | 1.00 / 3.000 | 32.506 | 84.284 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.983
- lateral_force_integral: None
- approach_alignment: 0.690
- goal_progress: 0.977
- terminal_score: 0.977
- phase_score: 0.800
- phase_breakdown.contact_object_score: 0.388
- phase_breakdown.reach_goal_score: 0.977

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.871
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.977
- **Median Q (composite search score)**: 0.539
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.341


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `75e2389a1a667086aa2b9c0de482ff37adf5571150b90a83772692baadf8b52e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `154c216c563de6b8ee153943e5b668ca6d0c7dfd9253696b060f91a67dca06ec`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.86364,"average_solve_count":66.0,"average_success_count":66.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.behind_distance":0.06298,"approach_behind.speed":0.18085,"push_to_goal.distance":0.2467,"push_to_goal.speed":0.16154,"release_1.max_time":0.44388},"optimized_scores":{"best_composite_score":0.53896,"best_fitness_score":0.81896,"best_task_score":0.92986},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":371.0,"contact_point_centroid":[0.51342,-0.03876,0.04517],"force_p95":57.78953,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.17705,"mean_force":15.04111,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50137,-0.02799,0.02561]},{"body_a":"world","body_b":"push_box","contact_count":662.0,"contact_point_centroid":[0.52131,-0.03858,-9e-05],"force_p95":44.71995,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.79576,"mean_force":11.36119,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50478,0.01134,0.02626]},{"body_a":"push_box","body_b":"link7","contact_count":185.0,"contact_point_centroid":[0.53108,-0.08482,0.05577],"force_p95":44.55821,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.7775,"mean_force":14.77202,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49842,-0.07009,0.02581]},{"body_a":"world","body_b":"push_box","contact_count":800.0,"contact_point_centroid":[0.51501,0.04767,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49754,-3e-05,0.29537]},{"body_a":"world","body_b":"push_box","contact_count":3924.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50451,0.05133,0.1627]}],"total_contact_groups":5},"final_pose_error":0.0197,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51172,-0.15516,0.03041],"final_tcp_position":[0.49594,-0.12109,0.02701],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":85.17705,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49646,-4e-05,0.29284],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.2727,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":981.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3924.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_object","tcp_end":[0.51468,0.10542,0.0299],"tcp_start":[0.49646,-4e-05,0.29284],"tcp_to_object_dist_end":0.05796,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":527.0,"n_steps_budget":960.0,"object_pos_end":[0.51172,-0.15516,0.03041],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.0139,"object_to_goal_dist_start":0.19823,"object_z_max":0.03051,"peak_contact_force":69.41588,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1218.0,"raw_peak_contact_force":85.17705,"subtask_id":"reach_goal","tcp_end":[0.49594,-0.12109,0.02701],"tcp_start":[0.51468,0.10542,0.0299],"tcp_to_object_dist_end":0.0377,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.24468,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.behind_distance":0.05184,"approach_behind.speed":0.19985,"push_to_goal.distance":0.235,"push_to_goal.speed":0.07682,"release_1.max_time":0.18447},"optimized_scores":{"best_composite_score":0.5911,"best_fitness_score":0.8711,"best_task_score":0.97714},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":386.0,"contact_point_centroid":[0.48843,-0.02082,0.0405],"force_p95":32.57053,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.16442,"mean_force":6.28165,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47907,-0.00953,0.02742]},{"body_a":"push_box","body_b":"link7","contact_count":83.0,"contact_point_centroid":[0.51807,-0.05347,0.05384],"force_p95":36.90381,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.93297,"mean_force":6.3966,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.4822,-0.04127,0.02726]},{"body_a":"world","body_b":"push_box","contact_count":567.0,"contact_point_centroid":[0.49317,-0.03314,-6e-05],"force_p95":22.14993,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.89593,"mean_force":5.55877,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47671,0.01863,0.02806]},{"body_a":"world","body_b":"push_box","contact_count":800.0,"contact_point_centroid":[0.47924,0.05847,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49754,-3e-05,0.29537]},{"body_a":"world","body_b":"push_box","contact_count":3576.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48334,0.05067,0.16424]}],"total_contact_groups":5},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50238,-0.1461,0.02643],"final_tcp_position":[0.48889,-0.11074,0.0268],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":48.16442,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49646,-4e-05,0.29284],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.27471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":894.0,"n_steps_budget":930.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3576.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_object","tcp_end":[0.47106,0.10462,0.03164],"tcp_start":[0.49646,-4e-05,0.29284],"tcp_to_object_dist_end":0.04734,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":558.0,"n_steps_budget":1000.0,"object_pos_end":[0.50238,-0.1461,0.02643],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.00479,"object_to_goal_dist_start":0.2095,"object_z_max":0.02852,"peak_contact_force":27.74146,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1036.0,"raw_peak_contact_force":48.16442,"subtask_id":"reach_goal","tcp_end":[0.48889,-0.11074,0.0268],"tcp_start":[0.47106,0.10462,0.03164],"tcp_to_object_dist_end":0.03784,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.60563,"average_solve_count":71.0,"average_success_count":71.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.behind_distance":0.04735,"approach_behind.speed":0.15215,"push_to_goal.distance":0.26207,"push_to_goal.speed":0.15347,"release_1.max_time":0.24866},"optimized_scores":{"best_composite_score":0.52519,"best_fitness_score":0.80519,"best_task_score":0.90092},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":854.0,"contact_point_centroid":[0.52334,-0.10902,-0.00034],"force_p95":111.20194,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":119.50981,"mean_force":38.49196,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51012,-0.08812,0.04983]},{"body_a":"attachment","body_b":"push_box","contact_count":468.0,"contact_point_centroid":[0.51567,-0.09777,0.04862],"force_p95":112.94579,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":118.49856,"mean_force":69.04282,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50835,-0.0951,0.05068]},{"body_a":"world","body_b":"push_box","contact_count":800.0,"contact_point_centroid":[0.54443,-0.02558,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49754,-3e-05,0.29537]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52102,0.00804,0.17285]}],"total_contact_groups":4},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5128,-0.14921,0.02763],"final_tcp_position":[0.46437,-0.21136,0.0474],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":119.50981,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49646,-4e-05,0.29284],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.27331,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_object","tcp_end":[0.54852,0.01652,0.05137],"tcp_start":[0.49646,-4e-05,0.29284],"tcp_to_object_dist_end":0.04985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":611.0,"n_steps_budget":1000.0,"object_pos_end":[0.5128,-0.14921,0.02763],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.01309,"object_to_goal_dist_start":0.13211,"object_z_max":0.03475,"peak_contact_force":0.36159,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1322.0,"raw_peak_contact_force":119.50981,"subtask_id":"reach_goal","tcp_end":[0.46437,-0.21136,0.0474],"tcp_start":[0.54852,0.01652,0.05137],"tcp_to_object_dist_end":0.08123,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```