## Search State

- **Seed**: 0
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.2621 | 0.29 | ❌ rejected |
| 1 | approach → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.0372 | 0.29 | ❌ rejected |
| 0 | approach → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.8457 | 0.88 | ✅ accepted |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: obstacle_reach
- Frozen realised-scene SHA-256: `47501b1aab9bfa0e6b563b161626f42def695cce7ac7b19bb24da49f0ff9be1e`
- Frozen task target: [0.7136961687321454, -0.02302132862361297, 0.15]
- Goal object position: (0.7136961687321454, -0.02302132862361297, 0.15)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.5
- Force limit: 5.0 N
- Obstacle body: obstacle_block (contact = collision penalty)
- Robot initial TCP position: (0.35, 0.0, 0.32)
- Primary evaluation target: **TCP distance to goal position (Gaussian proximity kernel)**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.35, 0, 0.32]
objects:
  - name: obstacle_block
    role: obstacle
    dynamics: static
    geometry: box
    dimensions_m: [0.08, 0.3, 0.3]
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_task_target: [0.7137, -0.023, 0.15]
  frozen_obstacle_position: [0.5, 0, 0.15]
  frozen_targets: {'task_goal': [0.7136961687321454, -0.02302132862361297, 0.15]}
  frozen_obstacles: {'obstacle_block': [0.5, 0.0, 0.15]}
  goal_tolerance_m: 0.02
  force_limit_n: 5
  obstacle_height_m: 0.3
  force_scale_n: 5
  realized_scene_sha256: 47501b1aab9bfa0e6b563b161626f42def695cce7ac7b19bb24da49f0ff9be1e

## Current Skill (Q=0.262) — your mutation base

```yaml
skill: obstacle_reach
dsl_version: 2
phases:
- id: approach_via
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.0
    - 0.4
    tolerance: 0.05
    orientation:
      mode: keep_current
- id: approach_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.05
    orientation:
      mode: keep_current
- id: descend_goal
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_via** (`approach`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.0, 0.4], tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings: none
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.2], tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.262
- **task_score** (E): 0.292
- **fitness_score**: 0.292  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.333
- **Complexity Penalty**: 0.030

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_via | 1.00 | 0.00 | 0.1198 |
| approach_goal | 1.00 | 0.00 | 0.1934 |
| descend_goal | 1.00 | 0.67 | 0.1872 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force | Obstacle/contact |
|---|---|---|---|---|---|---|---|---|---|
| approach_via | approach | 1.00 / step_budget | (0.350, -0.000, 0.321)→(0.458, 0.000, 0.374) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.714→0.714 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| approach_goal | approach | 1.00 / step_budget | (0.458, 0.000, 0.374)→(0.648, 0.001, 0.350) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.714→0.714 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| descend_goal | descend | 1.00 / step_budget | (0.648, 0.001, 0.350)→(0.695, 0.001, 0.169) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.714→0.714 | 0.67 / 0.667 | 110.192 | 163.787 | link5 ↔ obstacle_block/obstacle_block_geom |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.616
- path_efficiency: 0.750
- arc_smoothness: 0.995
- collision_factor: 1.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 0.000 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.020
- min_tcp_distance: 0.020
- tcp_proximity_score: 0.876
- goal_reached_rate: 1.000
- peak_obstacle_counterbody: None
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: None
- peak_obstacle_obstacle_geom: None

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.292
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.292
- **Median Q (composite search score)**: 0.262
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: no_parameters
- **Mean generations**: 0.0
- **Final σ (mean)**: 0.000


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `30565d16bb12c763ef96950bff0806542e706772a2f5d6530b71a1e799295889`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `93ed75540af82fc2f732261ad21f1d84d6fc60a0bcf806dd0394bfdc69d4362f`; realized-scene SHA-256: `47501b1aab9bfa0e6b563b161626f42def695cce7ac7b19bb24da49f0ff9be1e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.7137,-0.02302,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.7137,-0.02302,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9313,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{},"optimized_scores":{"best_composite_score":0.84632,"best_fitness_score":0.87632,"best_task_score":0.87632},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.7137,-0.02302,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.70481,-0.02244,0.16769],"realised_goal_position":[0.7137,-0.02302,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":129.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72965,"object_to_goal_dist_start":0.72965,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_via","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.45773,1e-05,0.3738],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.59096,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":206.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72965,"object_to_goal_dist_start":0.72965,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.66456,-0.01841,0.34948],"tcp_start":[0.45773,1e-05,0.3738],"tcp_to_object_dist_end":0.75108,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":323.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72965,"object_to_goal_dist_start":0.72965,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.70481,-0.02244,0.16769],"tcp_start":[0.66456,-0.01841,0.34948],"tcp_to_object_dist_end":0.72483,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e2f42f3fbbcca284b57f515aa7c9c12d3405e5434d2b225f750641c72d8a7bd9`; realized-scene SHA-256: `46c72c16be0fa319940ad2424e6763e117e5dc5f0c6b9e34d827f50eec225036`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.70118,0.04505,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.70118,0.04505,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93023,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{},"optimized_scores":{"best_composite_score":-0.03,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link5","contact_count":78.0,"contact_point_centroid":[0.53997,0.13325,0.29999],"force_p95":202.51522,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":207.17806,"mean_force":164.07168,"phase_index":2.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.69189,0.04287,0.18982]}],"total_contact_groups":1},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.70118,0.04505,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.69937,0.04399,0.16984],"realised_goal_position":[0.70118,0.04505,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":207.17806,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":129.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71846,"object_to_goal_dist_start":0.71846,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_via","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.45773,1e-05,0.3738],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.59096,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":197.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71846,"object_to_goal_dist_start":0.71846,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.65225,0.03548,0.34991],"tcp_start":[0.45773,1e-05,0.3738],"tcp_to_object_dist_end":0.74103,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71846,"object_to_goal_dist_start":0.71846,"object_z_max":0.0,"peak_contact_force":147.87741,"phase_name":"descend_goal","phase_peak_obstacle_force":207.17806,"phase_type":"descend","raw_contact_event_count":78.0,"raw_peak_contact_force":207.17806,"tcp_end":[0.69937,0.04399,0.16984],"tcp_start":[0.65225,0.03548,0.34991],"tcp_to_object_dist_end":0.72104,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `6daafe4988ca0b57abfa37034ad4d1d5846eda9319b3f27d8d423c2e135ec43b`; realized-scene SHA-256: `91e4de206df15f80750cdb645e4a7fbeecac222f6e7e3c9e7aabeca93992a5f5`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.67616,-0.02015,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.67616,-0.02015,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92742,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{},"optimized_scores":{"best_composite_score":-0.03,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link6","contact_count":106.0,"contact_point_centroid":[0.53995,-0.01784,0.29996],"force_p95":274.68851,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":284.18268,"mean_force":211.29374,"phase_index":2.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.66449,-0.01879,0.2156]},{"body_a":"obstacle_block","body_b":"link5","contact_count":201.0,"contact_point_centroid":[0.53997,0.04802,0.29999],"force_p95":266.48371,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":269.78903,"mean_force":225.1127,"phase_index":2.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.67599,-0.01937,0.19274]}],"total_contact_groups":2},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.67616,-0.02015,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.68005,-0.01958,0.16958],"realised_goal_position":[0.67616,-0.02015,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":284.18268,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":129.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.69289,"object_to_goal_dist_start":0.69289,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_via","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.45773,1e-05,0.3738],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.59096,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":171.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.69289,"object_to_goal_dist_start":0.69289,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.62734,-0.01541,0.35107],"tcp_start":[0.45773,1e-05,0.3738],"tcp_to_object_dist_end":0.71905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":569.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.69289,"object_to_goal_dist_start":0.69289,"object_z_max":0.0,"peak_contact_force":182.69965,"phase_name":"descend_goal","phase_peak_obstacle_force":284.18268,"phase_type":"descend","raw_contact_event_count":307.0,"raw_peak_contact_force":284.18268,"tcp_end":[0.68005,-0.01958,0.16958],"tcp_start":[0.62734,-0.01541,0.35107],"tcp_to_object_dist_end":0.70115,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```