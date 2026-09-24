## Search State

- **Seed**: 6
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → approach → align → approach → descend | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | admittance_control | admittance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 14 | 0.2092 | 0.93 | ✅ accepted |
| 2 | approach → approach → align → descend | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | admittance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.0146 | 0.65 | ✅ accepted |
| 1 | approach → descend | arc_cartesian | linear_cartesian | admittance_control | admittance_control | pose_tolerance | pose_tolerance | 5 | -0.2500 | 0.00 | ✅ accepted |
| 0 | approach → descend | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | pose_tolerance | pose_tolerance | 3 | -0.1500 | 0.00 | ✅ accepted |

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

- Task name: obstacle_reach
- Frozen realised-scene SHA-256: `bd4f35ed59709260e094776b661704e90745f7a52d08ebc05c5947cbc49435ce`
- Frozen task target: [0.7038164351471943, -0.015672913018666156, 0.15]
- Goal object position: (0.7038164351471943, -0.015672913018666156, 0.15)
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
  frozen_task_target: [0.7038, -0.0157, 0.15]
  frozen_obstacle_position: [0.5, 0, 0.15]
  frozen_targets: {'task_goal': [0.7038164351471943, -0.015672913018666156, 0.15]}
  frozen_obstacles: {'obstacle_block': [0.5, 0.0, 0.15]}
  goal_tolerance_m: 0.02
  force_limit_n: 5
  obstacle_height_m: 0.3
  force_scale_n: 5
  realized_scene_sha256: bd4f35ed59709260e094776b661704e90745f7a52d08ebc05c5947cbc49435ce

## Current Skill (Q=0.209) — your mutation base

```yaml
skill: obstacle_reach
dsl_version: 2
phases:
- id: lift_and_side_move
  type: approach
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.25
    - 0.15
  parameters:
    clearance_z:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.25
      binds_to:
      - path: target.offset.z
        mode: replace
    lateral_y:
      type: scalar
      range:
      - 0.15
      - 0.35
      default: 0.25
      binds_to:
      - path: target.offset.y
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    lift_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
- id: arc_above_goal
  type: approach
  generator: arc_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.25
    - 0.25
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.35
      default: 0.2
      binds_to:
      - path: generator.arc_height
        mode: replace
    arc_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
    arc_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    arc_y_offset:
      type: scalar
      range:
      - 0.15
      - 0.35
      default: 0.25
      binds_to:
      - path: target.offset.y
        mode: replace
- id: side_align_to_goal_xy
  type: align
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.1
    - 0.25
  parameters:
    side_align_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    side_align_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
- id: lateral_to_goal_y
  type: approach
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.25
  parameters:
    lateral_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
    lateral_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
- id: descend_to_goal
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 1.0
      - 5.0
      default: 4.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: descend_contact_guard
    when: during_phase
    predicate: force_below
    threshold: 5.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.03
    - 0.0

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **lift_and_side_move** (`approach`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.25, 0.15]
  - parameter_bindings:
    - clearance_z: status=consumed; consumers=target.offset.z (replace)
    - lateral_y: status=consumed; consumers=target.offset.y (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
    - lift_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **arc_above_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.25, 0.25]
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - arc_speed: status=consumed; consumers=generator.speed (replace)
    - arc_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - arc_y_offset: status=consumed; consumers=target.offset.y (replace)
- **side_align_to_goal_xy** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.1, 0.25]
  - parameter_bindings:
    - side_align_speed: status=consumed; consumers=generator.speed (replace)
    - side_align_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **lateral_to_goal_y** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.25]
  - parameter_bindings:
    - lateral_speed: status=consumed; consumers=generator.speed (replace)
    - lateral_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=descend_contact_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=5.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.03, 0.0]

## Design Metrics

- **Composite score**: 0.209
- **task_score** (E): 0.933
- **fitness_score**: 0.933  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.067
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.790

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| lift_and_side_move | 1.00 | 0.00 | 0.3763 |
| arc_above_goal | 1.00 | 0.00 | 0.4115 |
| side_align_to_goal_xy | 1.00 | 0.00 | 0.1621 |
| lateral_to_goal_y | 1.00 | 0.00 | 0.1049 |
| descend_to_goal | 0.33 | 0.33 | 0.2312 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| lift_and_side_move | approach | 1.00 / step_budget | (0.350, -0.000, 0.321)→(0.351, 0.242, 0.605) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 0.00 / 0.000 | 0.000 | 0.000 |
| arc_above_goal | approach | 1.00 / step_budget | (0.351, 0.242, 0.605)→(0.710, 0.294, 0.429) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 0.00 / 0.000 | 0.000 | 0.000 |
| side_align_to_goal_xy | align | 1.00 / step_budget | (0.710, 0.294, 0.429)→(0.700, 0.137, 0.394) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 0.00 / 0.000 | 0.000 | 0.000 |
| lateral_to_goal_y | approach | 1.00 / step_budget | (0.700, 0.137, 0.394)→(0.699, 0.033, 0.391) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_goal | descend | 0.33 / step_budget | (0.699, 0.033, 0.391)→(0.696, 0.025, 0.160) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 0.33 / 0.333 | 76.085 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.863
- path_efficiency: 0.225
- arc_smoothness: 0.997
- collision_factor: 1.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 0.000 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.022
- min_tcp_distance: 0.022
- tcp_proximity_score: 0.861
- goal_reached_rate: 0.000
- peak_obstacle_counterbody: None
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: None
- peak_obstacle_obstacle_geom: None

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.968
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.968
- **Median Q (composite search score)**: 0.178
- **K-run variance**: 0.0019
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.254


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `89af5e6373a217810de823e85ed206d27eafc89c151e748b39ede2d750fe7c5e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6b4e4a3a850359b999c84710456096c65c7b37ffa6a27fd54ebaec8821f1dcd2`; realized-scene SHA-256: `bd4f35ed59709260e094776b661704e90745f7a52d08ebc05c5947cbc49435ce`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.70382,-0.01567,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.70382,-0.01567,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.58784,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_above_goal.arc_height":0.20282,"arc_above_goal.arc_speed":0.42217,"arc_above_goal.arc_tolerance":0.03114,"arc_above_goal.arc_y_offset":0.25592,"descend_to_goal.descend_force_threshold":4.01388,"descend_to_goal.descend_speed":0.0986,"lateral_to_goal_y.lateral_speed":0.24171,"lateral_to_goal_y.lateral_tolerance":0.01332,"lift_and_side_move.clearance_z":0.35117,"lift_and_side_move.lateral_y":0.24399,"lift_and_side_move.lift_speed":0.24127,"lift_and_side_move.lift_tolerance":0.01582,"side_align_to_goal_xy.side_align_speed":0.17357,"side_align_to_goal_xy.side_align_tolerance":0.01491},"optimized_scores":{"best_composite_score":0.17839,"best_fitness_score":0.96839,"best_task_score":0.96839},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.00482,"key_states":{"actual_goal_position":[0.70382,-0.01567,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.70052,-0.01522,0.15349],"realised_goal_position":[0.70382,-0.01567,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lift_and_side_move","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.35104,0.22531,0.64148],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.76518,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":584.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"arc_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.71775,0.24119,0.42717],"tcp_start":[0.35104,0.22531,0.64148],"tcp_to_object_dist_end":0.86937,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"side_align_to_goal_xy","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.70484,0.09763,0.3934],"tcp_start":[0.71775,0.24119,0.42717],"tcp_to_object_dist_end":0.81308,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":425.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lateral_to_goal_y","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.70344,-0.00621,0.39065],"tcp_start":[0.70484,0.09763,0.3934],"tcp_to_object_dist_end":0.80465,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":792.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.70052,-0.01522,0.15349],"tcp_start":[0.70344,-0.00621,0.39065],"tcp_to_object_dist_end":0.7173,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3dbedbccfafbb480e6b8853d24674113c48a7d6ac70107463f0222214d243e47`; realized-scene SHA-256: `f5f2ee542fad8ea5b5618e39465af4fd2d024325ca55c46b8aecfe9ce333bfb2`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.71251,0.03972,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.71251,0.03972,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.53529,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_above_goal.arc_height":0.20138,"arc_above_goal.arc_speed":0.23254,"arc_above_goal.arc_tolerance":0.03961,"arc_above_goal.arc_y_offset":0.22338,"descend_to_goal.descend_force_threshold":2.80485,"descend_to_goal.descend_speed":0.09089,"lateral_to_goal_y.lateral_speed":0.19482,"lateral_to_goal_y.lateral_tolerance":0.01005,"lift_and_side_move.clearance_z":0.20257,"lift_and_side_move.lateral_y":0.25217,"lift_and_side_move.lift_speed":0.16161,"lift_and_side_move.lift_tolerance":0.0168,"side_align_to_goal_xy.side_align_speed":0.1628,"side_align_to_goal_xy.side_align_tolerance":0.01547},"optimized_scores":{"best_composite_score":0.17842,"best_fitness_score":0.96842,"best_task_score":0.96842},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.00481,"key_states":{"actual_goal_position":[0.71251,0.03972,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.70924,0.03985,0.15353],"realised_goal_position":[0.71251,0.03972,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":884.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lift_and_side_move","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.35025,0.24112,0.51105],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.66483,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":520.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"arc_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.71237,0.26297,0.43856],"tcp_start":[0.35025,0.24112,0.51105],"tcp_to_object_dist_end":0.87691,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":324.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"side_align_to_goal_xy","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.71244,0.15422,0.3953],"tcp_start":[0.71237,0.26297,0.43856],"tcp_to_object_dist_end":0.82923,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":521.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lateral_to_goal_y","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.71208,0.0475,0.39066],"tcp_start":[0.71244,0.15422,0.3953],"tcp_to_object_dist_end":0.8136,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":787.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.70924,0.03985,0.15353],"tcp_start":[0.71208,0.0475,0.39066],"tcp_to_object_dist_end":0.72676,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `71285845baf1b8f9da7d5ce873550759a4c17d69a356cdc4cf82cc31badfb976`; realized-scene SHA-256: `4d99f589f09839c4f3a4e389174672e239f050e8ccee110af89dc738cbe9e683`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.6827,0.04873,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.6827,0.04873,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.42932,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_above_goal.arc_height":0.22207,"arc_above_goal.arc_speed":0.31102,"arc_above_goal.arc_tolerance":0.02774,"arc_above_goal.arc_y_offset":0.32375,"descend_to_goal.descend_force_threshold":2.78034,"descend_to_goal.descend_speed":0.06886,"lateral_to_goal_y.lateral_speed":0.18876,"lateral_to_goal_y.lateral_tolerance":0.00909,"lift_and_side_move.clearance_z":0.36047,"lift_and_side_move.lateral_y":0.27207,"lift_and_side_move.lift_speed":0.19165,"lift_and_side_move.lift_tolerance":0.02209,"side_align_to_goal_xy.side_align_speed":0.19744,"side_align_to_goal_xy.side_align_tolerance":0.01401},"optimized_scores":{"best_composite_score":0.27081,"best_fitness_score":0.86081,"best_task_score":0.86081},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.02248,"key_states":{"actual_goal_position":[0.6827,0.04873,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.67963,0.04937,0.17226],"realised_goal_position":[0.6827,0.04873,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":228.25425,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":935.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lift_and_side_move","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.35125,0.26101,0.66244],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.79394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":738.0,"n_steps_budget":900.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"arc_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.69896,0.37902,0.42113],"tcp_start":[0.35125,0.26101,0.66244],"tcp_to_object_dist_end":0.89975,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":684.0,"n_steps_budget":750.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"side_align_to_goal_xy","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.68335,0.16029,0.39242],"tcp_start":[0.69896,0.37902,0.42113],"tcp_to_object_dist_end":0.80415,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":527.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lateral_to_goal_y","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.68221,0.05626,0.39112],"tcp_start":[0.68335,0.16029,0.39242],"tcp_to_object_dist_end":0.78838,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":793.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":228.25425,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.67963,0.04937,0.17226],"tcp_start":[0.68221,0.05626,0.39112],"tcp_to_object_dist_end":0.70285,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```