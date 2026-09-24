## Search State

- **Seed**: 9
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → push | linear_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | time_limit | 6 | 0.5291 | 0.94 | ✅ accepted |
| 10 | approach → push | linear_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | time_limit | 6 | 0.5291 | 0.94 | ✅ accepted |
| 9 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | time_limit | time_limit | 6 | 0.3986 | 0.78 | ❌ rejected |
| 8 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 6 | 0.3855 | 0.75 | ❌ rejected |
| 7 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 7 | -0.2475 | 0.07 | ❌ rejected |

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

## Current Skill (Q=0.529) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  weight: 0.2
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.8
phases:
- id: approach_from_behind
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
      distance: 0.15
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_behind_distance:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.03
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    approach_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.025
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: approach_pose_check
    when: after_phase
    predicate: pose_within_tolerance
    threshold: 0.025
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: reach_object
- id: push_to_goal_phase
  type: push
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: none
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    push_time:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 8.0
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_from_behind** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=replace_offset_projection, sign=negative}, tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - approach_z_offset: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=approach_pose_check, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.025
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **push_to_goal_phase** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_time: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.529
- **task_score** (E): 0.936
- **fitness_score**: 0.829  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_from_behind | 1.00 | 1.00 | 0.2929 |
| push_to_goal_phase | 1.00 | 1.00 | 0.2604 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_from_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.536, 0.126, 0.056) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_to_goal_phase | push | 1.00 / time_limit | (0.536, 0.126, 0.056)→(0.501, -0.117, 0.024) | (0.518, -0.020, 0.025)→(0.492, -0.149, 0.025) | 0.139→0.008 | 1.00 / 3.333 | 7.176 | 47.848 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.678
- goal_progress: 0.989
- terminal_score: 0.989
- phase_score: 0.799
- phase_breakdown.reach_object_score: 0.037
- phase_breakdown.push_to_goal_score: 0.989

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.875
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.989
- **Median Q (composite search score)**: 0.530
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.263


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `327b95871eb659cd41b4cf66bc0b4dfb3b240662e8501854b46ee2b8b86a04c5`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5ffd2bb280d1d50ec9ffd23c1ed75abf73d645c1d10372a9b5bb6e9fac6e0bf8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.32184,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_from_behind.approach_behind_distance":0.18218,"approach_from_behind.approach_speed":0.12583,"approach_from_behind.approach_tolerance":0.01832,"approach_from_behind.approach_z_offset":0.01528,"push_to_goal_phase.push_speed":0.17014,"push_to_goal_phase.push_time":13.65504},"optimized_scores":{"best_composite_score":0.48248,"best_fitness_score":0.78248,"best_task_score":0.88465},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":302.0,"contact_point_centroid":[0.53017,-0.05368,0.03043],"force_p95":29.73156,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.49431,"mean_force":7.3532,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.53158,-0.04204,0.02976]},{"body_a":"world","body_b":"push_box","contact_count":2871.0,"contact_point_centroid":[0.536,-0.04605,-6e-05],"force_p95":6.56264,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.68443,"mean_force":1.05514,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.55801,0.03678,0.03693]},{"body_a":"world","body_b":"push_box","contact_count":2412.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_from_behind","phase_type":"approach","tcp_position_centroid":[0.54602,0.06641,0.17632]}],"total_contact_groups":3},"final_pose_error":0.03267,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48499,-0.14735,0.02501],"final_tcp_position":[0.50638,-0.11803,0.02284],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":39.49431,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":603.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_from_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2412.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.59455,0.13485,0.05192],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17022,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48499,-0.14735,0.02501],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.01524,"object_to_goal_dist_start":0.13211,"object_z_max":0.02633,"peak_contact_force":2.0,"phase_name":"push_to_goal_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3173.0,"raw_peak_contact_force":39.49431,"subtask_id":"push_to_goal","tcp_end":[0.50638,-0.11803,0.02284],"tcp_start":[0.59455,0.13485,0.05192],"tcp_to_object_dist_end":0.03636,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e094d2c5a71c8b89ef1fa30d7ce553b9c4ed64cd3fbca90620c3ede94e719cec`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.12222,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_from_behind.approach_behind_distance":0.1468,"approach_from_behind.approach_speed":0.11359,"approach_from_behind.approach_tolerance":0.01704,"approach_from_behind.approach_z_offset":0.01615,"push_to_goal_phase.push_speed":0.14536,"push_to_goal_phase.push_time":8.02909},"optimized_scores":{"best_composite_score":0.52991,"best_fitness_score":0.82991,"best_task_score":0.93436},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":288.0,"contact_point_centroid":[0.53792,-0.06024,0.03268],"force_p95":28.88754,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.56998,"mean_force":7.49836,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.5401,-0.04868,0.03176]},{"body_a":"world","body_b":"push_box","contact_count":2836.0,"contact_point_centroid":[0.54348,-0.05782,-7e-05],"force_p95":6.24296,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.39082,"mean_force":1.04993,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.56533,0.00807,0.03851]},{"body_a":"world","body_b":"push_box","contact_count":2284.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_from_behind","phase_type":"approach","tcp_position_centroid":[0.55111,0.0439,0.17787]}],"total_contact_groups":3},"final_pose_error":0.03452,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49182,-0.14836,0.02461],"final_tcp_position":[0.51006,-0.11701,0.02374],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":34.56998,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":571.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_from_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2284.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.60516,0.08942,0.05428],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13748,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49182,-0.14836,0.02461],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.00835,"object_to_goal_dist_start":0.12728,"object_z_max":0.02623,"peak_contact_force":19.43019,"phase_name":"push_to_goal_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3124.0,"raw_peak_contact_force":34.56998,"subtask_id":"push_to_goal","tcp_end":[0.51006,-0.11701,0.02374],"tcp_start":[0.60516,0.08942,0.05428],"tcp_to_object_dist_end":0.03628,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0fd7d18e656259f06515eb57b82afa0c0febd9395a43c1a5f926ddaec3767c64`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.33735,"average_solve_count":83.0,"average_success_count":83.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_from_behind.approach_behind_distance":0.17468,"approach_from_behind.approach_speed":0.13769,"approach_from_behind.approach_tolerance":0.01588,"approach_from_behind.approach_z_offset":0.02296,"push_to_goal_phase.push_speed":0.17844,"push_to_goal_phase.push_time":12.03655},"optimized_scores":{"best_composite_score":0.57496,"best_fitness_score":0.87496,"best_task_score":0.98927},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":310.0,"contact_point_centroid":[0.47442,-0.05392,0.04782],"force_p95":46.41866,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.4792,"mean_force":13.16048,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.46464,-0.04229,0.03398]},{"body_a":"world","body_b":"push_box","contact_count":2458.0,"contact_point_centroid":[0.46247,-0.02222,-3e-05],"force_p95":14.42651,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.72355,"mean_force":2.00612,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.43281,0.06452,0.04774]},{"body_a":"push_box","body_b":"link7","contact_count":26.0,"contact_point_centroid":[0.51551,-0.09643,0.05378],"force_p95":4.49829,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.89064,"mean_force":1.72695,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.47659,-0.08232,0.02878]},{"body_a":"world","body_b":"push_box","contact_count":2308.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_from_behind","phase_type":"approach","tcp_position_centroid":[0.45457,0.07624,0.18099]}],"total_contact_groups":4},"final_pose_error":0.03737,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49964,-0.1509,0.02637],"final_tcp_position":[0.48683,-0.11503,0.02461],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":69.4792,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":577.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_from_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2308.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.40956,0.15419,0.06247],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.16525,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49964,-0.1509,0.02637],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.00168,"object_to_goal_dist_start":0.1564,"object_z_max":0.02826,"peak_contact_force":0.09697,"phase_name":"push_to_goal_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2794.0,"raw_peak_contact_force":69.4792,"subtask_id":"push_to_goal","tcp_end":[0.48683,-0.11503,0.02461],"tcp_start":[0.40956,0.15419,0.06247],"tcp_to_object_dist_end":0.03813,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```