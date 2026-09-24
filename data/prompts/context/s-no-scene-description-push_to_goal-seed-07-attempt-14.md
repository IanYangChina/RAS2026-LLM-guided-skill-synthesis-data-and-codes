## Search State

- **Seed**: 7
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | release → approach → push | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | 5 | 0.5782 | 0.95 | ❌ rejected |
| 13 | release → approach → push | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | 5 | 0.5435 | 0.92 | ❌ rejected |
| 12 | release → approach → push | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | 5 | 0.5439 | 0.91 | ❌ rejected |
| 11 | release → approach → push | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | 5 | 0.5662 | 0.95 | ❌ rejected |
| 10 | release → approach → push | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | 5 | 0.5504 | 0.92 | ❌ rejected |

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

## Current Skill (Q=0.578) — your mutation base

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

- **Composite score**: 0.578
- **task_score** (E): 0.955
- **fitness_score**: 0.858  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| release_1 | 1.00 | 1.00 | 0.0085 |
| approach_behind | 1.00 | 1.00 | 0.2639 |
| push_to_goal | 1.00 | 1.00 | 0.1783 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| release_1 | release | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, -0.000, 0.293) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| approach_behind | approach | 1.00 / step_budget | (0.496, -0.000, 0.293)→(0.513, 0.066, 0.043) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 3.667 | 4.357 | 118.760 |
| push_to_goal | push | 1.00 / step_budget | (0.513, 0.066, 0.043)→(0.500, -0.108, 0.022) | (0.513, 0.027, 0.025)→(0.506, -0.151, 0.025) | 0.180→0.008 | 1.00 / 3.000 | 13.698 | 62.167 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.977
- lateral_force_integral: None
- approach_alignment: 0.673
- goal_progress: 0.973
- terminal_score: 0.973
- phase_score: 0.797
- phase_breakdown.contact_object_score: 0.386
- phase_breakdown.reach_goal_score: 0.973

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.867
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.973
- **Median Q (composite search score)**: 0.581
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.282


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92771,"average_solve_count":83.0,"average_success_count":83.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.behind_distance":0.04209,"approach_behind.speed":0.12968,"push_to_goal.behind_goal_offset":0.02243,"push_to_goal.speed":0.11896,"release_1.max_time":0.3138},"optimized_scores":{"best_composite_score":0.56596,"best_fitness_score":0.84596,"best_task_score":0.93725},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":38.0,"contact_point_centroid":[0.52309,0.07407,0.04737],"force_p95":257.50986,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":267.81716,"mean_force":179.80251,"phase_index":1.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51548,0.08137,0.04887]},{"body_a":"world","body_b":"push_box","contact_count":2032.0,"contact_point_centroid":[0.51516,0.04845,-3e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":255.42766,"mean_force":3.62834,"phase_index":1.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50406,0.03991,0.16854]},{"body_a":"attachment","body_b":"push_box","contact_count":244.0,"contact_point_centroid":[0.5145,-0.01686,0.04466],"force_p95":46.02528,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.05667,"mean_force":7.49086,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50813,-0.0052,0.03134]},{"body_a":"world","body_b":"push_box","contact_count":517.0,"contact_point_centroid":[0.51696,-0.05325,-0.00026],"force_p95":24.26937,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":60.82193,"mean_force":5.01672,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50827,-0.00519,0.03152]},{"body_a":"push_box","body_b":"link7","contact_count":35.0,"contact_point_centroid":[0.54394,-0.10157,0.05212],"force_p95":38.23806,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.68484,"mean_force":14.00646,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50207,-0.07913,0.02438]},{"body_a":"world","body_b":"push_box","contact_count":800.0,"contact_point_centroid":[0.51501,0.04767,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49754,-3e-05,0.29537]}],"total_contact_groups":6},"final_pose_error":0.01968,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51036,-0.15688,0.02492],"final_tcp_position":[0.49971,-0.10836,0.02167],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":267.81716,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49646,-4e-05,0.29284],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.2727,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":524.0,"n_steps_budget":1000.0,"object_pos_end":[0.51674,0.0481,0.02417],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19881,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":12.36605,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2070.0,"raw_peak_contact_force":267.81716,"subtask_id":"contact_object","tcp_end":[0.51878,0.08515,0.04409],"tcp_start":[0.49646,-4e-05,0.29284],"tcp_to_object_dist_end":0.04212,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":466.0,"n_steps_budget":1000.0,"object_pos_end":[0.51036,-0.15688,0.02492],"object_pos_start":[0.51674,0.0481,0.02417],"object_to_goal_dist_end":0.01244,"object_to_goal_dist_start":0.19881,"object_z_max":0.02982,"peak_contact_force":0.98817,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":796.0,"raw_peak_contact_force":65.05667,"subtask_id":"reach_goal","tcp_end":[0.49971,-0.10836,0.02167],"tcp_start":[0.51878,0.08515,0.04409],"tcp_to_object_dist_end":0.04979,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94017,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.behind_distance":0.05391,"approach_behind.speed":0.08033,"push_to_goal.behind_goal_offset":0.03007,"push_to_goal.speed":0.10692,"release_1.max_time":0.2384},"optimized_scores":{"best_composite_score":0.58749,"best_fitness_score":0.86749,"best_task_score":0.97315},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":306.0,"contact_point_centroid":[0.49037,-0.01443,0.0428],"force_p95":47.68825,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.57173,"mean_force":10.57917,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48079,-0.00336,0.02968]},{"body_a":"push_box","body_b":"link7","contact_count":97.0,"contact_point_centroid":[0.51971,-0.02192,0.0547],"force_p95":33.37317,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.40546,"mean_force":9.23933,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48152,-0.00986,0.02914]},{"body_a":"world","body_b":"push_box","contact_count":594.0,"contact_point_centroid":[0.4965,-0.03772,-0.00011],"force_p95":30.03688,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.72211,"mean_force":7.29888,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47974,0.00835,0.03091]},{"body_a":"world","body_b":"push_box","contact_count":800.0,"contact_point_centroid":[0.47924,0.05847,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49754,-3e-05,0.29537]},{"body_a":"world","body_b":"push_box","contact_count":2172.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48398,0.05026,0.16776]}],"total_contact_groups":5},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50244,-0.14498,0.02431],"final_tcp_position":[0.49157,-0.10142,0.02167],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":60.57173,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49646,-4e-05,0.29284],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.27471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_object","tcp_end":[0.4723,0.10236,0.04201],"tcp_start":[0.49646,-4e-05,0.29284],"tcp_to_object_dist_end":0.04758,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":514.0,"n_steps_budget":1000.0,"object_pos_end":[0.50244,-0.14498,0.02431],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.00562,"object_to_goal_dist_start":0.2095,"object_z_max":0.02976,"peak_contact_force":37.4592,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":997.0,"raw_peak_contact_force":60.57173,"subtask_id":"reach_goal","tcp_end":[0.49157,-0.10142,0.02167],"tcp_start":[0.4723,0.10236,0.04201],"tcp_to_object_dist_end":0.04498,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92208,"average_solve_count":77.0,"average_success_count":77.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.behind_distance":0.04023,"approach_behind.speed":0.10388,"push_to_goal.behind_goal_offset":0.01795,"push_to_goal.speed":0.14057,"release_1.max_time":0.30795},"optimized_scores":{"best_composite_score":0.58108,"best_fitness_score":0.86108,"best_task_score":0.9541},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":5.0,"contact_point_centroid":[0.54853,-0.00085,0.04973],"force_p95":87.2,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":88.21758,"mean_force":52.62307,"phase_index":1.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.54745,0.0108,0.04994]},{"body_a":"attachment","body_b":"push_box","contact_count":194.0,"contact_point_centroid":[0.52853,-0.06604,0.0418],"force_p95":21.48348,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.87373,"mean_force":4.37179,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52582,-0.05456,0.02968]},{"body_a":"world","body_b":"push_box","contact_count":1997.0,"contact_point_centroid":[0.54429,-0.02575,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.76422,"mean_force":0.37882,"phase_index":1.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52142,0.00535,0.16962]},{"body_a":"world","body_b":"push_box","contact_count":399.0,"contact_point_centroid":[0.52377,-0.08589,-0.00032],"force_p95":11.86155,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.73789,"mean_force":2.55123,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52799,-0.04781,0.0307]},{"body_a":"world","body_b":"push_box","contact_count":800.0,"contact_point_centroid":[0.54443,-0.02558,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49754,-3e-05,0.29537]}],"total_contact_groups":5},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.506,-0.15079,0.0247],"final_tcp_position":[0.50778,-0.11363,0.02207],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":88.21758,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49646,-4e-05,0.29284],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.27331,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":503.0,"n_steps_budget":1000.0,"object_pos_end":[0.5442,-0.02619,0.02494],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13147,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.45883,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2002.0,"raw_peak_contact_force":88.21758,"subtask_id":"contact_object","tcp_end":[0.5492,0.01141,0.04272],"tcp_start":[0.49646,-4e-05,0.29284],"tcp_to_object_dist_end":0.04189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":298.0,"n_steps_budget":690.0,"object_pos_end":[0.506,-0.15079,0.0247],"object_pos_start":[0.5442,-0.02619,0.02494],"object_to_goal_dist_end":0.00606,"object_to_goal_dist_start":0.13147,"object_z_max":0.02793,"peak_contact_force":2.64752,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":593.0,"raw_peak_contact_force":60.87373,"subtask_id":"reach_goal","tcp_end":[0.50778,-0.11363,0.02207],"tcp_start":[0.5492,0.01141,0.04272],"tcp_to_object_dist_end":0.0373,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```