## Search State

- **Seed**: 5
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → approach | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.2300 | 0.00 | ❌ rejected |
| 3 | approach → descend → descend | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.1800 | 0.00 | ❌ rejected |
| 2 | approach → descend | linear_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 2 | 0.7786 | 0.88 | ✅ accepted |
| 1 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 3 | 0.7283 | 0.88 | ✅ accepted |
| 0 | approach → descend | arc_cartesian | linear_cartesian | force_threshold_switch | position_control | pose_tolerance | pose_tolerance | 2 | -0.1000 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `35b656cc89b57a5f115ac5b9cfa690565debfcfd5af880d0b6438b747265b590`
- Frozen task target: [0.730500292374538, 0.030794078973649372, 0.15]
- Goal object position: (0.730500292374538, 0.030794078973649372, 0.15)
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
  frozen_task_target: [0.7305, 0.0308, 0.15]
  frozen_obstacle_position: [0.5, 0, 0.15]
  frozen_targets: {'task_goal': [0.730500292374538, 0.030794078973649372, 0.15]}
  frozen_obstacles: {'obstacle_block': [0.5, 0.0, 0.15]}
  goal_tolerance_m: 0.02
  force_limit_n: 5
  obstacle_height_m: 0.3
  force_scale_n: 5
  realized_scene_sha256: 35b656cc89b57a5f115ac5b9cfa690565debfcfd5af880d0b6438b747265b590

## Current Skill (Q=-0.230) — your mutation base

```yaml
skill: obstacle_reach
dsl_version: 2
phases:
- id: approach_over_obstacle
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
    - 0.25
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_to_goal
  type: descend
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
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_over_obstacle** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.25], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.230
- **task_score** (E): 0.000
- **fitness_score**: 0.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

**⚠ Warning**: CMA-ES stagnated + low fitness_score → structure may be fundamentally incompatible with task

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| move_around_obstacle | 1.00 | 0.00 | 0.4409 |
| descend_to_lateral_z | 1.00 | 0.00 | 0.2618 |
| move_to_goal | 0.00 | 1.00 | 0.1620 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force | Obstacle/contact |
|---|---|---|---|---|---|---|---|---|---|
| move_around_obstacle | approach | 1.00 / step_budget | (0.350, -0.000, 0.321)→(0.693, 0.250, 0.440) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.732→0.732 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| descend_to_lateral_z | descend | 1.00 / step_budget | (0.693, 0.250, 0.440)→(0.711, 0.265, 0.179) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.732→0.732 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| move_to_goal | approach | 0.00 / step_budget | (0.711, 0.265, 0.179)→(0.710, 0.105, 0.155) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.732→0.732 | 1.00 / 1.000 | 206.513 | 228.906 | link5 ↔ obstacle_block/obstacle_block_geom |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.421
- path_efficiency: 0.402
- arc_smoothness: 0.993
- collision_factor: 0.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 214.855 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.081
- min_tcp_distance: 0.081
- tcp_proximity_score: 0.582
- goal_reached_rate: 0.000
- peak_obstacle_counterbody: link5
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: obstacle_block
- peak_obstacle_obstacle_geom: obstacle_block_geom

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.230
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.342


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `f3b9025bd026eb63e7a6b7b9dcbae30ae5fd727c3f404b5eea2986d705494aa6`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `016b297ed5457e75e60006ae43546f9e20e6368637b147588ecc5457d8da87e0`; realized-scene SHA-256: `35b656cc89b57a5f115ac5b9cfa690565debfcfd5af880d0b6438b747265b590`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.7305,0.03079,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.7305,0.03079,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.3835,"average_solve_count":206.0,"average_success_count":206.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_lateral_z.descend_speed":0.0978,"move_around_obstacle.approach_speed":0.10778,"move_around_obstacle.arc_height":0.2842,"move_to_goal.final_speed":0.09305},"optimized_scores":{"best_composite_score":-0.23,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link5","contact_count":448.0,"contact_point_centroid":[0.53517,0.14995,0.29996],"force_p95":204.81138,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":214.8554,"mean_force":194.12832,"phase_index":2.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.72411,0.1141,0.15166]}],"total_contact_groups":1},"final_pose_error":0.0811,"key_states":{"actual_goal_position":[0.7305,0.03079,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.72393,0.11157,0.15302],"realised_goal_position":[0.7305,0.03079,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":214.8554,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":580.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.74638,"object_to_goal_dist_start":0.74638,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"move_around_obstacle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.70892,0.2634,0.44133],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.87563,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":312.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.74638,"object_to_goal_dist_start":0.74638,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_lateral_z","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.72625,0.2778,0.17887],"tcp_start":[0.70892,0.2634,0.44133],"tcp_to_object_dist_end":0.79788,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":850.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.74638,"object_to_goal_dist_start":0.74638,"object_z_max":0.0,"peak_contact_force":191.98259,"phase_name":"move_to_goal","phase_peak_obstacle_force":214.8554,"phase_type":"approach","raw_contact_event_count":448.0,"raw_peak_contact_force":214.8554,"tcp_end":[0.72393,0.11157,0.15302],"tcp_start":[0.72625,0.2778,0.17887],"tcp_to_object_dist_end":0.74829,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `91da6d91b20aa8f1968f3c6d7ec8aa818a9ddb55695f45bcb9bfaacd3acccdac`; realized-scene SHA-256: `bd4f35ed59709260e094776b661704e90745f7a52d08ebc05c5947cbc49435ce`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.70382,-0.01567,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.70382,-0.01567,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.29448,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_lateral_z.descend_speed":0.13016,"move_around_obstacle.approach_speed":0.15233,"move_around_obstacle.arc_height":0.3093,"move_to_goal.final_speed":0.08257},"optimized_scores":{"best_composite_score":-0.23,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link5","contact_count":682.0,"contact_point_centroid":[0.53313,0.14996,0.29997],"force_p95":239.39338,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":270.19105,"mean_force":196.13157,"phase_index":2.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.69759,0.09974,0.15693]}],"total_contact_groups":1},"final_pose_error":0.11319,"key_states":{"actual_goal_position":[0.70382,-0.01567,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.6993,0.09705,0.15933],"realised_goal_position":[0.70382,-0.01567,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":270.19105,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"move_around_obstacle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.67467,0.2137,0.43409],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.83023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":311.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_lateral_z","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.6984,0.23088,0.17872],"tcp_start":[0.67467,0.2137,0.43409],"tcp_to_object_dist_end":0.75697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":242.89367,"phase_name":"move_to_goal","phase_peak_obstacle_force":270.19105,"phase_type":"approach","raw_contact_event_count":682.0,"raw_peak_contact_force":270.19105,"tcp_end":[0.6993,0.09705,0.15933],"tcp_start":[0.6984,0.23088,0.17872],"tcp_to_object_dist_end":0.72376,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fc3e8abaaf02ca668222d0cd4e885164ebd20230be343b2ee428dfce1066794d`; realized-scene SHA-256: `f5f2ee542fad8ea5b5618e39465af4fd2d024325ca55c46b8aecfe9ce333bfb2`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.71251,0.03972,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.71251,0.03972,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.775,"average_solve_count":240.0,"average_success_count":240.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_lateral_z.descend_speed":0.1317,"move_around_obstacle.approach_speed":0.09655,"move_around_obstacle.arc_height":0.25102,"move_to_goal.final_speed":0.05238},"optimized_scores":{"best_composite_score":-0.23,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link5","contact_count":539.0,"contact_point_centroid":[0.53242,0.14996,0.29997],"force_p95":193.2508,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":201.67143,"mean_force":186.1115,"phase_index":2.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.70677,0.1083,0.15023]}],"total_contact_groups":1},"final_pose_error":0.06699,"key_states":{"actual_goal_position":[0.71251,0.03972,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.70652,0.10643,0.15136],"realised_goal_position":[0.71251,0.03972,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":201.67143,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":611.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"move_around_obstacle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.69505,0.27417,0.44345],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.86886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":312.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_lateral_z","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.70878,0.2869,0.17923],"tcp_start":[0.69505,0.27417,0.44345],"tcp_to_object_dist_end":0.78537,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":184.66306,"phase_name":"move_to_goal","phase_peak_obstacle_force":201.67143,"phase_type":"approach","raw_contact_event_count":539.0,"raw_peak_contact_force":201.67143,"tcp_end":[0.70652,0.10643,0.15136],"tcp_start":[0.70878,0.2869,0.17923],"tcp_to_object_dist_end":0.73035,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```