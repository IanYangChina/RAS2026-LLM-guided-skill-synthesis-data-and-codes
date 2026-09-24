## Search State

- **Seed**: 4
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | push → align → insert → release | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.3276 | 0.94 | ❌ rejected |
| 12 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.1391 | 0.96 | ❌ rejected |
| 11 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.1391 | 0.96 | ❌ rejected |
| 10 | approach → grasp → lift → approach → align → insert → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | — | position_control | position_control | impedance_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.0341 | 0.88 | ❌ rejected |
| 9 | push → align → release → insert | linear_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | force_exceeded | 6 | 0.1595 | 0.86 | ❌ rejected |

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

## Current Skill (Q=0.328) — your mutation base

```yaml
skill: peg_insert
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0

```

## Design Metrics

- **Composite score**: 0.328
- **task_score** (E): 0.936
- **fitness_score**: 0.604  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| push_1 | 0.00 | 1.00 | 0.2453 |
| align_1 | 0.33 | 1.00 | 0.0194 |
| insert_1 | 1.00 | 1.00 | 0.0001 |
| release_1 | 1.00 | 0.00 | 0.0798 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| push_1 | push | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.515, 0.003, 0.056) | (0.504, -0.000, 0.340)→(0.531, 0.003, 0.093) | 0.260→0.036 | 1.00 / 1.000 | 282.655 | 457.185 |
| align_1 | align | 0.33 / step_budget | (0.515, 0.003, 0.056)→(0.514, 0.003, 0.075) | (0.531, 0.003, 0.093)→(0.537, 0.007, 0.096) | 0.036→0.042 | 1.00 / 1.333 | 404.116 | 268.506 |
| insert_1 | insert | 1.00 / step_budget | (0.514, 0.003, 0.075)→(0.514, 0.003, 0.075) | (0.537, 0.007, 0.096)→(0.537, 0.007, 0.096) | 0.042→0.042 | 1.00 / 1.333 | 438.644 | 250.747 |
| release_1 | release | 1.00 / step_budget | (0.514, 0.003, 0.075)→(0.514, 0.004, 0.155) | (0.537, 0.007, 0.096)→(0.538, 0.008, 0.175) | 0.042→0.104 | 0.00 / 0.000 | 0.000 | 307.023 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.965
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.965
- phase_score: 0.392
- phase_breakdown.pre_insert_score: 0.704
- phase_breakdown.insert_depth_score: 0.184

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.621
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.965
- **Median Q (composite search score)**: 0.237
- **K-run variance**: 0.0168
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.358


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `1c06d48834291abac995c6cc1d2cd84f840e8dd85a042a042b29bb3e8b43f340`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a5dd99a2832e295b96a2d483dc6e44525a65c5240d3c756ec4d63dfbfe5237b3`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":40.0,"average_failure_rate":0.23529,"average_mean_iterations":49.77647,"average_solve_count":170.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00144,"align_1.lateral_offset_y":-0.00999,"insert_1.insertion_depth":0.07742,"insert_1.insertion_force":19.95412,"push_1.push_distance":0.19736,"push_1.push_speed":0.01224},"optimized_scores":{"best_composite_score":0.23479,"best_fitness_score":0.59479,"best_task_score":0.92218},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":496.0,"contact_point_centroid":[0.53736,0.00064,0.04989],"force_p95":301.25718,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":456.85044,"mean_force":293.63784,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52335,0.00056,0.05513]},{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.50509,0.00223,0.07858],"force_p95":396.6517,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":403.40874,"mean_force":199.72434,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5183,0.00048,0.07418]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.53873,0.00069,0.04996],"force_p95":75.01578,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.02953,"mean_force":55.43115,"phase_index":3.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52494,0.00057,0.05582]}],"total_contact_groups":3},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.53102,0.00078,0.16054],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":456.85044,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54065,0.00058,0.09255],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.04254,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":282.47377,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":509.0,"raw_peak_contact_force":456.85044,"subtask_id":"pre_insert","tcp_end":[0.5249,0.00057,0.05578],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":0.0,"n_steps_budget":600.0,"object_pos_end":[0.54065,0.00058,0.09255],"object_pos_start":[0.54065,0.00058,0.09255],"object_to_goal_dist_end":0.04254,"object_to_goal_dist_start":0.04254,"peak_contact_force":282.41335,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_insert","tcp_end":[0.5249,0.00057,0.05578],"tcp_start":[0.5249,0.00057,0.05578],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":0.0,"n_steps_budget":600.0,"object_pos_end":[0.54065,0.00058,0.09255],"object_pos_start":[0.54065,0.00058,0.09255],"object_to_goal_dist_end":0.04254,"object_to_goal_dist_start":0.04254,"peak_contact_force":282.41335,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_depth","tcp_end":[0.5249,0.00057,0.05578],"tcp_start":[0.5249,0.00057,0.05578],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":341.0,"n_steps_budget":780.0,"object_pos_end":[0.54435,0.00071,0.19148],"object_pos_start":[0.54065,0.00058,0.09255],"object_to_goal_dist_end":0.11998,"object_to_goal_dist_start":0.04254,"object_z_max":0.19736,"peak_contact_force":0.0,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4.0,"raw_peak_contact_force":79.02953,"tcp_end":[0.52765,0.00069,0.15513],"tcp_start":[0.5249,0.00057,0.05578],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `82356f74d11e1888d903e80aabfa97b50f0a1f9374ab8997097863e47a04dcc6`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":40.0,"average_failure_rate":0.24845,"average_mean_iterations":52.45963,"average_solve_count":161.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00542,"align_1.lateral_offset_y":0.00032,"insert_1.insertion_depth":0.05127,"insert_1.insertion_force":14.7315,"push_1.push_distance":0.19849,"push_1.push_speed":0.06937},"optimized_scores":{"best_composite_score":0.23701,"best_fitness_score":0.59701,"best_task_score":0.91945},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":507.0,"contact_point_centroid":[0.52877,0.0164,0.04989],"force_p95":299.87283,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":462.15953,"mean_force":292.62176,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51489,0.01638,0.05545]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.53011,0.01675,0.04997],"force_p95":81.13375,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.52908,"mean_force":57.44019,"phase_index":3.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51649,0.01671,0.05621]}],"total_contact_groups":2},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.52029,0.02354,0.16074],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":462.15953,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53321,0.01683,0.0925],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.03927,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":281.30446,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":507.0,"raw_peak_contact_force":462.15953,"subtask_id":"pre_insert","tcp_end":[0.51645,0.01671,0.05618],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":0.0,"n_steps_budget":600.0,"object_pos_end":[0.53321,0.01683,0.0925],"object_pos_start":[0.53321,0.01683,0.0925],"object_to_goal_dist_end":0.03927,"object_to_goal_dist_start":0.03927,"peak_contact_force":281.27808,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_insert","tcp_end":[0.51645,0.01671,0.05618],"tcp_start":[0.51645,0.01671,0.05618],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":0.0,"n_steps_budget":600.0,"object_pos_end":[0.53321,0.01683,0.0925],"object_pos_start":[0.53321,0.01683,0.0925],"object_to_goal_dist_end":0.03927,"object_to_goal_dist_start":0.03927,"peak_contact_force":281.27808,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_depth","tcp_end":[0.51645,0.01671,0.05618],"tcp_start":[0.51645,0.01671,0.05618],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":338.0,"n_steps_budget":780.0,"object_pos_end":[0.53464,0.0235,0.19138],"object_pos_start":[0.53321,0.01683,0.0925],"object_to_goal_dist_end":0.11898,"object_to_goal_dist_start":0.03927,"object_z_max":0.1971,"peak_contact_force":0.0,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4.0,"raw_peak_contact_force":86.52908,"tcp_end":[0.51696,0.02333,0.1555],"tcp_start":[0.51645,0.01671,0.05618],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `4fedbe547233117d2a5522e0e6da389f32d172824e1a5c898bb2e8c1e5f99b78`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":14.0,"average_failure_rate":0.09524,"average_mean_iterations":22.87075,"average_solve_count":147.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00551,"align_1.lateral_offset_y":-0.00387,"insert_1.insertion_depth":0.13504,"insert_1.insertion_force":15.46493,"push_1.push_distance":0.18906,"push_1.push_speed":0.04202},"optimized_scores":{"best_composite_score":0.5111,"best_fitness_score":0.6211,"best_task_score":0.965},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":68.0,"contact_point_centroid":[0.54382,0.00203,0.07972],"force_p95":684.51641,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":805.51941,"mean_force":372.59208,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51178,-0.01045,0.08686]},{"body_a":"peg_socket","body_b":"link7","contact_count":68.0,"contact_point_centroid":[0.56299,0.03127,0.07563],"force_p95":384.6625,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":755.50915,"mean_force":123.60259,"phase_index":3.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50075,-0.00913,0.11893]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5627,0.03264,0.06977],"force_p95":752.2417,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":752.2417,"mean_force":752.2417,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50122,-0.00792,0.11441]},{"body_a":"peg_socket","body_b":"link7","contact_count":60.0,"contact_point_centroid":[0.5625,0.04611,0.07422],"force_p95":671.47665,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":690.82039,"mean_force":475.29306,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51319,-0.01416,0.11036]},{"body_a":"attachment","body_b":"peg_socket","contact_count":5.0,"contact_point_centroid":[0.563,0.01183,0.07984],"force_p95":641.89029,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":674.75407,"mean_force":371.10559,"phase_index":3.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50076,-0.00774,0.1144]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.56296,0.01246,0.0797],"force_p95":665.21023,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":665.21023,"mean_force":665.21023,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50122,-0.00792,0.11441]},{"body_a":"attachment","body_b":"peg_socket","contact_count":506.0,"contact_point_centroid":[0.51467,-0.00868,0.04989],"force_p95":298.61724,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":452.54594,"mean_force":293.52977,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50091,-0.00864,0.05573]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.51593,-0.00887,0.04996],"force_p95":338.73605,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":338.75833,"mean_force":338.53548,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50238,-0.00879,0.05637]}],"total_contact_groups":8},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.50079,-0.01158,0.16037],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":805.51941,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5195,-0.00888,0.09246],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02478,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":284.18573,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":506.0,"raw_peak_contact_force":452.54594,"subtask_id":"pre_insert","tcp_end":[0.50234,-0.00881,0.05633],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":180.0,"n_steps_budget":600.0,"object_pos_end":[0.53784,0.00337,0.10295],"object_pos_start":[0.5195,-0.00888,0.09246],"object_to_goal_dist_end":0.04438,"object_to_goal_dist_start":0.02478,"object_z_max":0.10375,"peak_contact_force":648.65558,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":130.0,"raw_peak_contact_force":805.51941,"subtask_id":"pre_insert","tcp_end":[0.50122,-0.00792,0.11441],"tcp_start":[0.50234,-0.00881,0.05633],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":750.0,"object_pos_end":[0.53768,0.00325,0.103],"object_pos_start":[0.53784,0.00337,0.10295],"object_to_goal_dist_end":0.04426,"object_to_goal_dist_start":0.04438,"object_z_max":0.10295,"peak_contact_force":752.2417,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":752.2417,"subtask_id":"insert_depth","tcp_end":[0.50098,-0.00783,0.1144],"tcp_start":[0.50122,-0.00792,0.11441],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":211.0,"n_steps_budget":600.0,"object_pos_end":[0.53501,-0.00037,0.14248],"object_pos_start":[0.53768,0.00325,0.103],"object_to_goal_dist_end":0.07163,"object_to_goal_dist_start":0.04426,"object_z_max":0.14885,"peak_contact_force":0.0,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":73.0,"raw_peak_contact_force":755.50915,"tcp_end":[0.49861,-0.01156,0.15472],"tcp_start":[0.50098,-0.00783,0.1144],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```