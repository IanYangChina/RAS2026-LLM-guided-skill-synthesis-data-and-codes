## Search State

- **Seed**: 7
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | release → approach → push | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | 5 | 0.5791 | 0.96 | ✅ accepted |
| 7 | release → approach → push | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | 5 | 0.4847 | 0.85 | ❌ rejected |
| 6 | release → approach → push | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | 5 | 0.5618 | 0.93 | ❌ rejected |
| 5 | release → approach → push | — | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | time_limit | force_exceeded | pose_tolerance | 6 | -0.1749 | 0.12 | ❌ rejected |
| 4 | release → approach → push | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | 6 | 0.4733 | 0.89 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.96). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.579) — your mutation base

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
    tolerance: 0.02
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
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.02
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    behind_goal_offset:
      type: scalar
      range:
      - 0.005
      - 0.05
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.02, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.02, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - behind_goal_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.579
- **task_score** (E): 0.957
- **fitness_score**: 0.859  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| release_1 | 1.00 | 1.00 | 0.0085 |
| approach_behind | 1.00 | 1.00 | 0.2634 |
| push_to_goal | 1.00 | 0.67 | 0.1807 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| release_1 | release | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, -0.000, 0.293) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| approach_behind | approach | 1.00 / step_budget | (0.496, -0.000, 0.293)→(0.514, 0.067, 0.043) | (0.513, 0.027, 0.025)→(0.512, 0.026, 0.025) | 0.180→0.179 | 1.00 / 2.667 | 0.596 | 138.733 |
| push_to_goal | push | 1.00 / step_budget | (0.514, 0.067, 0.043)→(0.500, -0.110, 0.022) | (0.512, 0.026, 0.025)→(0.506, -0.147, 0.025) | 0.179→0.007 | 0.67 / 1.667 | 9.765 | 71.569 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.994
- lateral_force_integral: None
- approach_alignment: 0.690
- goal_progress: 0.994
- terminal_score: 0.994
- phase_score: 0.821
- phase_breakdown.contact_object_score: 0.419
- phase_breakdown.reach_goal_score: 0.994

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.890
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.994
- **Median Q (composite search score)**: 0.566
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.223


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.84848,"average_solve_count":66.0,"average_success_count":66.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.behind_distance":0.04453,"approach_behind.speed":0.16175,"push_to_goal.behind_goal_offset":0.02489,"push_to_goal.speed":0.15531,"release_1.max_time":0.25473},"optimized_scores":{"best_composite_score":0.5662,"best_fitness_score":0.8462,"best_task_score":0.93734},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":21.0,"contact_point_centroid":[0.51947,0.07287,0.0486],"force_p95":264.81148,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":266.65197,"mean_force":139.91367,"phase_index":1.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.5138,0.08199,0.04997]},{"body_a":"world","body_b":"push_box","contact_count":1952.0,"contact_point_centroid":[0.51512,0.04789,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":246.1561,"mean_force":1.76442,"phase_index":1.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.5041,0.04081,0.16897]},{"body_a":"attachment","body_b":"push_box","contact_count":255.0,"contact_point_centroid":[0.51451,-0.02198,0.04638],"force_p95":59.34358,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.81326,"mean_force":11.31758,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50584,-0.01051,0.03047]},{"body_a":"world","body_b":"push_box","contact_count":438.0,"contact_point_centroid":[0.51843,-0.05442,-0.00017],"force_p95":30.13875,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.50162,"mean_force":7.29613,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50636,-0.00329,0.03119]},{"body_a":"push_box","body_b":"link7","contact_count":38.0,"contact_point_centroid":[0.53913,-0.07101,0.05404],"force_p95":7.65002,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.61399,"mean_force":2.90088,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50241,-0.05834,0.0259]},{"body_a":"world","body_b":"push_box","contact_count":800.0,"contact_point_centroid":[0.51501,0.04767,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49754,-3e-05,0.29537]}],"total_contact_groups":6},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51004,-0.1427,0.0254],"final_tcp_position":[0.49934,-0.10579,0.02172],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":266.65197,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49646,-4e-05,0.29284],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.2727,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":496.0,"n_steps_budget":1000.0,"object_pos_end":[0.51409,0.0461,0.02534],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.1966,"object_to_goal_dist_start":0.19823,"object_z_max":0.02523,"peak_contact_force":1.12291,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1973.0,"raw_peak_contact_force":266.65197,"subtask_id":"contact_object","tcp_end":[0.51549,0.08539,0.04333],"tcp_start":[0.49646,-4e-05,0.29284],"tcp_to_object_dist_end":0.04324,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":440.0,"n_steps_budget":870.0,"object_pos_end":[0.51004,-0.1427,0.0254],"object_pos_start":[0.51409,0.0461,0.02534],"object_to_goal_dist_end":0.01242,"object_to_goal_dist_start":0.1966,"object_z_max":0.02833,"peak_contact_force":0.0,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":731.0,"raw_peak_contact_force":79.81326,"subtask_id":"reach_goal","tcp_end":[0.49934,-0.10579,0.02172],"tcp_start":[0.51549,0.08539,0.04333],"tcp_to_object_dist_end":0.03861,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94309,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.behind_distance":0.0478,"approach_behind.speed":0.07234,"push_to_goal.behind_goal_offset":0.01894,"push_to_goal.speed":0.11342,"release_1.max_time":0.24026},"optimized_scores":{"best_composite_score":0.61015,"best_fitness_score":0.89015,"best_task_score":0.99363},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":14.0,"contact_point_centroid":[0.47862,0.08343,0.04932],"force_p95":146.69517,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":149.3022,"mean_force":107.27824,"phase_index":1.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.47409,0.09367,0.05111]},{"body_a":"world","body_b":"push_box","contact_count":2137.0,"contact_point_centroid":[0.47923,0.05846,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":101.1489,"mean_force":0.95314,"phase_index":1.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48437,0.04718,0.16875]},{"body_a":"attachment","body_b":"push_box","contact_count":299.0,"contact_point_centroid":[0.49098,-0.03007,0.04239],"force_p95":58.30096,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":73.3062,"mean_force":11.40454,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48294,-0.01867,0.02955]},{"body_a":"world","body_b":"push_box","contact_count":632.0,"contact_point_centroid":[0.49394,-0.04663,-0.00016],"force_p95":28.94468,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.09552,"mean_force":6.1561,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48109,-1e-05,0.03125]},{"body_a":"push_box","body_b":"link7","contact_count":57.0,"contact_point_centroid":[0.52511,-0.08208,0.0516],"force_p95":19.65215,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.47864,"mean_force":4.02199,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48795,-0.06705,0.02541]},{"body_a":"world","body_b":"push_box","contact_count":800.0,"contact_point_centroid":[0.47924,0.05847,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49754,-3e-05,0.29537]}],"total_contact_groups":6},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50007,-0.14867,0.02511],"final_tcp_position":[0.49274,-0.11249,0.02159],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":149.3022,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49646,-4e-05,0.29284],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.27471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":539.0,"n_steps_budget":1000.0,"object_pos_end":[0.47891,0.05774,0.02471],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20881,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.42129,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2151.0,"raw_peak_contact_force":149.3022,"subtask_id":"contact_object","tcp_end":[0.47395,0.09769,0.04312],"tcp_start":[0.49646,-4e-05,0.29284],"tcp_to_object_dist_end":0.04427,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":528.0,"n_steps_budget":1000.0,"object_pos_end":[0.50007,-0.14867,0.02511],"object_pos_start":[0.47891,0.05774,0.02471],"object_to_goal_dist_end":0.00133,"object_to_goal_dist_start":0.20881,"object_z_max":0.02843,"peak_contact_force":0.0,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":988.0,"raw_peak_contact_force":73.3062,"subtask_id":"reach_goal","tcp_end":[0.49274,-0.11249,0.02159],"tcp_start":[0.47395,0.09769,0.04312],"tcp_to_object_dist_end":0.03709,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93258,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.behind_distance":0.04768,"approach_behind.speed":0.09953,"push_to_goal.behind_goal_offset":0.02067,"push_to_goal.speed":0.10245,"release_1.max_time":0.36599},"optimized_scores":{"best_composite_score":0.56088,"best_fitness_score":0.84088,"best_task_score":0.93966},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":228.0,"contact_point_centroid":[0.52967,-0.06302,0.0406],"force_p95":40.14805,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.58734,"mean_force":5.31779,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52686,-0.05136,0.02936]},{"body_a":"world","body_b":"push_box","contact_count":449.0,"contact_point_centroid":[0.52871,-0.07529,-0.00018],"force_p95":16.11504,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.02072,"mean_force":3.09545,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53126,-0.03789,0.03144]},{"body_a":"world","body_b":"push_box","contact_count":800.0,"contact_point_centroid":[0.54443,-0.02558,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49754,-3e-05,0.29537]},{"body_a":"world","body_b":"push_box","contact_count":2028.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.5227,0.00849,0.16879]}],"total_contact_groups":4},"final_pose_error":0.01964,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50779,-0.14838,0.02451],"final_tcp_position":[0.50867,-0.11119,0.02201],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":61.58734,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49646,-4e-05,0.29284],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.27331,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":507.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2028.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_object","tcp_end":[0.55121,0.01743,0.04259],"tcp_start":[0.49646,-4e-05,0.29284],"tcp_to_object_dist_end":0.04697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":318.0,"n_steps_budget":960.0,"object_pos_end":[0.50779,-0.14838,0.02451],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.00797,"object_to_goal_dist_start":0.13211,"object_z_max":0.02726,"peak_contact_force":29.29441,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":677.0,"raw_peak_contact_force":61.58734,"subtask_id":"reach_goal","tcp_end":[0.50867,-0.11119,0.02201],"tcp_start":[0.55121,0.01743,0.04259],"tcp_to_object_dist_end":0.03728,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```