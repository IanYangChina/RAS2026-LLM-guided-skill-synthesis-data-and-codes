## Search State

- **Seed**: 1
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → approach → approach → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.2875 | 0.30 | ❌ rejected |
| 6 | approach → approach → descend | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.3800 | 0.00 | ❌ rejected |
| 5 | approach → approach → descend | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.3732 | 0.80 | ✅ accepted |
| 4 | approach → approach → approach → descend | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.5100 | 0.00 | ❌ rejected |
| 3 | approach → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.2800 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `46c72c16be0fa319940ad2424e6763e117e5dc5f0c6b9e34d827f50eec225036`
- Frozen task target: [0.7011821624700256, 0.045046369632593536, 0.15]
- Goal object position: (0.7011821624700256, 0.045046369632593536, 0.15)
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
  frozen_task_target: [0.7012, 0.045, 0.15]
  frozen_obstacle_position: [0.5, 0, 0.15]
  frozen_targets: {'task_goal': [0.7011821624700256, 0.045046369632593536, 0.15]}
  frozen_obstacles: {'obstacle_block': [0.5, 0.0, 0.15]}
  goal_tolerance_m: 0.02
  force_limit_n: 5
  obstacle_height_m: 0.3
  force_scale_n: 5
  realized_scene_sha256: 46c72c16be0fa319940ad2424e6763e117e5dc5f0c6b9e34d827f50eec225036

## Current Skill (Q=-0.288) — your mutation base

```yaml
skill: obstacle_reach
dsl_version: 2
phases:
- id: rise_above_obstacle
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    rise_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    rise_z:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
- id: arc_approach
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.05
    - 0.15
    - 0.4
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.1
      - 0.6
      default: 0.3
      binds_to:
      - path: generator.arc_height
        mode: replace
    arc_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    arc_x_offset:
      type: scalar
      range:
      - -0.1
      - 0.2
      default: 0.05
      binds_to:
      - path: target.offset.x
        mode: replace
    arc_y_offset:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.y
        mode: replace
    arc_z_offset:
      type: scalar
      range:
      - 0.25
      - 0.5
      default: 0.4
      binds_to:
      - path: target.offset.z
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
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **rise_above_obstacle** (`approach`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - rise_speed: status=consumed; consumers=generator.speed (replace)
    - rise_z: status=consumed; consumers=target.offset.z (replace)
- **arc_approach** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.05, 0.15, 0.4], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - arc_speed: status=consumed; consumers=generator.speed (replace)
    - arc_x_offset: status=consumed; consumers=target.offset.x (replace)
    - arc_y_offset: status=consumed; consumers=target.offset.y (replace)
    - arc_z_offset: status=consumed; consumers=target.offset.z (replace)
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.288
- **task_score** (E): 0.302
- **fitness_score**: 0.302  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.590

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rise_above_obstacle | 1.00 | 0.00 | 0.2560 |
| lateral_clear | 1.00 | 0.00 | 0.2044 |
| forward_approach | 1.00 | 0.00 | 0.2783 |
| lateral_recenter | 1.00 | 0.00 | 0.1789 |
| vertical_descend | 0.67 | 0.67 | 0.3664 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force | Obstacle/contact |
|---|---|---|---|---|---|---|---|---|---|
| rise_above_obstacle | approach | 1.00 / step_budget | (0.350, -0.000, 0.321)→(0.353, 0.000, 0.577) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.696→0.696 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| lateral_clear | approach | 1.00 / step_budget | (0.353, 0.000, 0.577)→(0.356, 0.204, 0.574) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.696→0.696 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| forward_approach | approach | 1.00 / step_budget | (0.356, 0.204, 0.574)→(0.630, 0.219, 0.570) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.696→0.696 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| lateral_recenter | approach | 1.00 / step_budget | (0.630, 0.219, 0.570)→(0.671, 0.048, 0.541) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.696→0.696 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| vertical_descend | descend | 0.67 / step_budget | (0.671, 0.048, 0.541)→(0.680, 0.002, 0.178) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.696→0.696 | 0.67 / 0.667 | 117.588 | 145.221 | link5 ↔ obstacle_block/obstacle_block_geom |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.822
- path_efficiency: 0.300
- arc_smoothness: 0.997
- collision_factor: 1.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 0.000 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.015
- min_tcp_distance: 0.015
- tcp_proximity_score: 0.907
- goal_reached_rate: 1.000
- peak_obstacle_counterbody: None
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: None
- peak_obstacle_obstacle_geom: None

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.907
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.907
- **Median Q (composite search score)**: -0.590
- **K-run variance**: 0.1830
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 3.7
- **Final σ (mean)**: 0.318


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `478db1dab52eb01481055efd6f2fff61413c9177072131767e0a0a25f54d7566`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ab453d7ac328d553824b415fbc509c66751d415382130335c8aeb3bef634620b`; realized-scene SHA-256: `46c72c16be0fa319940ad2424e6763e117e5dc5f0c6b9e34d827f50eec225036`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.70118,0.04505,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.70118,0.04505,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24575,"average_solve_count":529.0,"average_success_count":529.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"forward_approach.forward_speed":0.05715,"forward_approach.forward_y":0.23179,"forward_approach.forward_z":0.41312,"lateral_clear.lateral_speed":0.05395,"lateral_clear.lateral_y":0.26065,"lateral_recenter.recenter_speed":0.03825,"lateral_recenter.recenter_z":0.3779,"rise_above_obstacle.rise_speed":0.07307,"rise_above_obstacle.rise_z":0.25319,"vertical_descend.descend_speed":0.04931},"optimized_scores":{"best_composite_score":0.31744,"best_fitness_score":0.90744,"best_task_score":0.90744},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.01457,"key_states":{"actual_goal_position":[0.70118,0.04505,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.69793,0.04771,0.16395],"realised_goal_position":[0.70118,0.04505,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":224.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71846,"object_to_goal_dist_start":0.71846,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"rise_above_obstacle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.3528,4e-05,0.52477],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.63233,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":226.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71846,"object_to_goal_dist_start":0.71846,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lateral_clear","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.35536,0.21106,0.52198],"tcp_start":[0.3528,4e-05,0.52477],"tcp_to_object_dist_end":0.6658,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":310.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71846,"object_to_goal_dist_start":0.71846,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"forward_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.65364,0.27027,0.55295],"tcp_start":[0.35536,0.21106,0.52198],"tcp_to_object_dist_end":0.8978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":198.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71846,"object_to_goal_dist_start":0.71846,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lateral_recenter","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.69369,0.0942,0.52493],"tcp_start":[0.65364,0.27027,0.55295],"tcp_to_object_dist_end":0.875,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":751.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71846,"object_to_goal_dist_start":0.71846,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"vertical_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.69793,0.04771,0.16395],"tcp_start":[0.69369,0.0942,0.52493],"tcp_to_object_dist_end":0.71851,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4563dbe78b318e3606cd01905d6b3a9462728e64a716c0768d4fdd05025d3340`; realized-scene SHA-256: `91e4de206df15f80750cdb645e4a7fbeecac222f6e7e3c9e7aabeca93992a5f5`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.67616,-0.02015,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.67616,-0.02015,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20442,"average_solve_count":543.0,"average_success_count":543.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"forward_approach.forward_speed":0.05146,"forward_approach.forward_y":0.24657,"forward_approach.forward_z":0.4528,"lateral_clear.lateral_speed":0.03942,"lateral_clear.lateral_y":0.2643,"lateral_recenter.recenter_speed":0.08316,"lateral_recenter.recenter_z":0.39709,"rise_above_obstacle.rise_speed":0.05648,"rise_above_obstacle.rise_z":0.34255,"vertical_descend.descend_speed":0.06257},"optimized_scores":{"best_composite_score":-0.59,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link5","contact_count":17.0,"contact_point_centroid":[0.53999,0.06623,0.3],"force_p95":157.48745,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":158.01766,"mean_force":130.94285,"phase_index":4.0,"phase_name":"vertical_descend","phase_type":"descend","tcp_position_centroid":[0.67367,-0.01713,0.16881]}],"total_contact_groups":1},"final_pose_error":0.01489,"key_states":{"actual_goal_position":[0.67616,-0.02015,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.67452,-0.01789,0.16462],"realised_goal_position":[0.67616,-0.02015,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":158.01766,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.69289,"object_to_goal_dist_start":0.69289,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"rise_above_obstacle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.35294,5e-05,0.61388],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.7081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":231.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.69289,"object_to_goal_dist_start":0.69289,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lateral_clear","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.35584,0.21461,0.61123],"tcp_start":[0.35294,5e-05,0.61388],"tcp_to_object_dist_end":0.73911,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":277.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.69289,"object_to_goal_dist_start":0.69289,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"forward_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.62633,0.22698,0.60093],"tcp_start":[0.35584,0.21461,0.61123],"tcp_to_object_dist_end":0.89718,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.69289,"object_to_goal_dist_start":0.69289,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lateral_recenter","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.66954,0.0283,0.54997],"tcp_start":[0.62633,0.22698,0.60093],"tcp_to_object_dist_end":0.86692,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":827.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.69289,"object_to_goal_dist_start":0.69289,"object_z_max":0.0,"peak_contact_force":108.74876,"phase_name":"vertical_descend","phase_peak_obstacle_force":158.01766,"phase_type":"descend","raw_contact_event_count":17.0,"raw_peak_contact_force":158.01766,"tcp_end":[0.67452,-0.01789,0.16462],"tcp_start":[0.66954,0.0283,0.54997],"tcp_to_object_dist_end":0.69455,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `78d10c6222d4f3052d259f9f421271029a9d205b1f94de5e9c7c2e42d26cca24`; realized-scene SHA-256: `09b1e5e25d1c1085fb3b7b529543c8c0ed19e559c3b72845a3b8c8c62899d8b5`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.65856,-0.02632,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.65856,-0.02632,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30943,"average_solve_count":488.0,"average_success_count":488.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"forward_approach.forward_speed":0.05421,"forward_approach.forward_y":0.17949,"forward_approach.forward_z":0.40194,"lateral_clear.lateral_speed":0.0326,"lateral_clear.lateral_y":0.237,"lateral_recenter.recenter_speed":0.06308,"lateral_recenter.recenter_z":0.40518,"rise_above_obstacle.rise_speed":0.08549,"rise_above_obstacle.rise_z":0.32062,"vertical_descend.descend_speed":0.03178},"optimized_scores":{"best_composite_score":-0.59,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link6","contact_count":277.0,"contact_point_centroid":[0.53992,-0.04569,0.29995],"force_p95":265.06238,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":277.64578,"mean_force":230.92369,"phase_index":4.0,"phase_name":"vertical_descend","phase_type":"descend","tcp_position_centroid":[0.66295,-0.02068,0.21069]}],"total_contact_groups":1},"final_pose_error":0.05485,"key_states":{"actual_goal_position":[0.65856,-0.02632,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.66754,-0.0224,0.20397],"realised_goal_position":[0.65856,-0.02632,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":277.64578,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":292.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.67594,"object_to_goal_dist_start":0.67594,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"rise_above_obstacle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.353,5e-05,0.59201],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.68926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":206.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.67594,"object_to_goal_dist_start":0.67594,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lateral_clear","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.35582,0.18745,0.58944],"tcp_start":[0.353,5e-05,0.59201],"tcp_to_object_dist_end":0.71357,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":267.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.67594,"object_to_goal_dist_start":0.67594,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"forward_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.61025,0.16069,0.55477],"tcp_start":[0.35582,0.18745,0.58944],"tcp_to_object_dist_end":0.84023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":154.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.67594,"object_to_goal_dist_start":0.67594,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lateral_recenter","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.64908,0.02175,0.54787],"tcp_start":[0.61025,0.16069,0.55477],"tcp_to_object_dist_end":0.84967,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.67594,"object_to_goal_dist_start":0.67594,"object_z_max":0.0,"peak_contact_force":244.01668,"phase_name":"vertical_descend","phase_peak_obstacle_force":277.64578,"phase_type":"descend","raw_contact_event_count":277.0,"raw_peak_contact_force":277.64578,"tcp_end":[0.66754,-0.0224,0.20397],"tcp_start":[0.64908,0.02175,0.54787],"tcp_to_object_dist_end":0.69836,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```