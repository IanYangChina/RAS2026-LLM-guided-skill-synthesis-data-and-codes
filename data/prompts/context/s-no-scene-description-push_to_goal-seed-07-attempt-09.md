## Search State

- **Seed**: 7
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | release → approach → push | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | 5 | 0.5495 | 0.93 | ❌ rejected |
| 8 | release → approach → push | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | 5 | 0.5791 | 0.96 | ✅ accepted |
| 7 | release → approach → push | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | 5 | 0.4847 | 0.85 | ❌ rejected |
| 6 | release → approach → push | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | 5 | 0.5618 | 0.93 | ❌ rejected |
| 5 | release → approach → push | — | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | time_limit | force_exceeded | pose_tolerance | 6 | -0.1749 | 0.12 | ❌ rejected |

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

## Current Skill (Q=0.549) — your mutation base

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

- **Composite score**: 0.549
- **task_score** (E): 0.929
- **fitness_score**: 0.829  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| release_1 | 1.00 | 1.00 | 0.0085 |
| approach_behind | 1.00 | 1.00 | 0.2648 |
| push_to_goal | 1.00 | 1.00 | 0.1851 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| release_1 | release | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, -0.000, 0.293) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| approach_behind | approach | 1.00 / step_budget | (0.496, -0.000, 0.293)→(0.516, 0.072, 0.043) | (0.513, 0.027, 0.025)→(0.514, 0.027, 0.025) | 0.180→0.181 | 1.00 / 3.667 | 0.587 | 88.518 |
| push_to_goal | push | 1.00 / step_budget | (0.516, 0.072, 0.043)→(0.502, -0.109, 0.022) | (0.514, 0.027, 0.025)→(0.508, -0.146, 0.025) | 0.181→0.011 | 1.00 / 3.000 | 16.132 | 68.275 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.695
- goal_progress: 0.986
- terminal_score: 0.986
- phase_score: 0.807
- phase_breakdown.contact_object_score: 0.390
- phase_breakdown.reach_goal_score: 0.986

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.878
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.986
- **Median Q (composite search score)**: 0.584
- **K-run variance**: 0.0035
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.269


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.19565,"average_solve_count":92.0,"average_success_count":92.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.behind_distance":0.04172,"approach_behind.speed":0.08686,"push_to_goal.behind_goal_offset":0.01959,"push_to_goal.speed":0.18436,"release_1.max_time":0.41548},"optimized_scores":{"best_composite_score":0.58373,"best_fitness_score":0.86373,"best_task_score":0.96029},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":42.0,"contact_point_centroid":[0.52399,0.07461,0.04697],"force_p95":263.55359,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":265.06298,"mean_force":198.65599,"phase_index":1.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51574,0.08143,0.04871]},{"body_a":"world","body_b":"push_box","contact_count":2099.0,"contact_point_centroid":[0.51515,0.04853,-3e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":244.47983,"mean_force":4.2498,"phase_index":1.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.504,0.03974,0.16857]},{"body_a":"attachment","body_b":"push_box","contact_count":260.0,"contact_point_centroid":[0.51175,-0.02752,0.03932],"force_p95":45.3751,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.21101,"mean_force":8.15205,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50788,-0.01573,0.03066]},{"body_a":"world","body_b":"push_box","contact_count":482.0,"contact_point_centroid":[0.51088,-0.05282,-0.00021],"force_p95":26.28113,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.24032,"mean_force":5.09583,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50883,-0.00594,0.03174]},{"body_a":"push_box","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53495,-0.11863,0.05152],"force_p95":32.11152,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.25828,"mean_force":25.03893,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50033,-0.10539,0.02232]},{"body_a":"world","body_b":"push_box","contact_count":800.0,"contact_point_centroid":[0.51501,0.04767,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49754,-3e-05,0.29537]}],"total_contact_groups":6},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5073,-0.14707,0.02488],"final_tcp_position":[0.49989,-0.11085,0.02188],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":265.06298,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49646,-4e-05,0.29284],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.2727,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":543.0,"n_steps_budget":1000.0,"object_pos_end":[0.51765,0.04929,0.02484],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.20007,"object_to_goal_dist_start":0.19823,"object_z_max":0.02535,"peak_contact_force":1.27067,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2141.0,"raw_peak_contact_force":265.06298,"subtask_id":"contact_object","tcp_end":[0.51974,0.08577,0.0444],"tcp_start":[0.49646,-4e-05,0.29284],"tcp_to_object_dist_end":0.04145,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":436.0,"n_steps_budget":750.0,"object_pos_end":[0.5073,-0.14707,0.02488],"object_pos_start":[0.51765,0.04929,0.02484],"object_to_goal_dist_end":0.00787,"object_to_goal_dist_start":0.20007,"object_z_max":0.03006,"peak_contact_force":46.66077,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":745.0,"raw_peak_contact_force":77.21101,"subtask_id":"reach_goal","tcp_end":[0.49989,-0.11085,0.02188],"tcp_start":[0.51974,0.08577,0.0444],"tcp_to_object_dist_end":0.03709,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.375,"average_solve_count":80.0,"average_success_count":80.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.behind_distance":0.05334,"approach_behind.speed":0.16606,"push_to_goal.behind_goal_offset":0.01555,"push_to_goal.speed":0.11599,"release_1.max_time":0.28575},"optimized_scores":{"best_composite_score":0.59831,"best_fitness_score":0.87831,"best_task_score":0.98552},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":302.0,"contact_point_centroid":[0.49142,-0.02241,0.04333],"force_p95":48.50902,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.64146,"mean_force":10.19747,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48154,-0.01134,0.02954]},{"body_a":"world","body_b":"push_box","contact_count":569.0,"contact_point_centroid":[0.49716,-0.04902,-0.00011],"force_p95":26.01371,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.54124,"mean_force":6.35955,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48051,0.00031,0.03071]},{"body_a":"push_box","body_b":"link7","contact_count":66.0,"contact_point_centroid":[0.52057,-0.0553,0.05412],"force_p95":32.80686,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.15202,"mean_force":3.83978,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48497,-0.04283,0.0271]},{"body_a":"world","body_b":"push_box","contact_count":800.0,"contact_point_centroid":[0.47924,0.05847,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49754,-3e-05,0.29537]},{"body_a":"world","body_b":"push_box","contact_count":2004.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48411,0.05009,0.16757]}],"total_contact_groups":5},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49927,-0.15291,0.02458],"final_tcp_position":[0.49292,-0.11577,0.02141],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":59.64146,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49646,-4e-05,0.29284],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.27471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":501.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2004.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_object","tcp_end":[0.47241,0.10184,0.04205],"tcp_start":[0.49646,-4e-05,0.29284],"tcp_to_object_dist_end":0.0471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":545.0,"n_steps_budget":1000.0,"object_pos_end":[0.49927,-0.15291,0.02458],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.00303,"object_to_goal_dist_start":0.2095,"object_z_max":0.02995,"peak_contact_force":1.69726,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":937.0,"raw_peak_contact_force":59.64146,"subtask_id":"reach_goal","tcp_end":[0.49292,-0.11577,0.02141],"tcp_start":[0.47241,0.10184,0.04205],"tcp_to_object_dist_end":0.03781,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0625,"average_solve_count":64.0,"average_success_count":64.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.behind_distance":0.05959,"approach_behind.speed":0.13626,"push_to_goal.behind_goal_offset":0.03115,"push_to_goal.speed":0.15005,"release_1.max_time":0.41306},"optimized_scores":{"best_composite_score":0.4664,"best_fitness_score":0.7464,"best_task_score":0.83995},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":174.0,"contact_point_centroid":[0.53502,-0.05547,0.04355],"force_p95":43.63768,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.97285,"mean_force":6.80058,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52984,-0.04373,0.02877]},{"body_a":"world","body_b":"push_box","contact_count":451.0,"contact_point_centroid":[0.53522,-0.06499,-0.00012],"force_p95":17.98168,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.71188,"mean_force":3.04518,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53796,-0.01841,0.03243]},{"body_a":"world","body_b":"push_box","contact_count":800.0,"contact_point_centroid":[0.54443,-0.02558,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49754,-3e-05,0.29537]},{"body_a":"world","body_b":"push_box","contact_count":1996.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52462,0.01351,0.16841]}],"total_contact_groups":4},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51728,-0.13784,0.02586],"final_tcp_position":[0.51246,-0.10099,0.02208],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":67.97285,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49646,-4e-05,0.29284],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.27331,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":499.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1996.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_object","tcp_end":[0.55502,0.02766,0.04216],"tcp_start":[0.49646,-4e-05,0.29284],"tcp_to_object_dist_end":0.05694,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":301.0,"n_steps_budget":660.0,"object_pos_end":[0.51728,-0.13784,0.02586],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.02114,"object_to_goal_dist_start":0.13211,"object_z_max":0.02687,"peak_contact_force":0.0371,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":625.0,"raw_peak_contact_force":67.97285,"subtask_id":"reach_goal","tcp_end":[0.51246,-0.10099,0.02208],"tcp_start":[0.55502,0.02766,0.04216],"tcp_to_object_dist_end":0.03736,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```