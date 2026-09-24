## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → approach → align → approach → descend | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | admittance_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 16 | -0.2445 | 0.65 | ❌ rejected |
| 13 | approach → approach → align → approach → descend | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | admittance_control | admittance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 17 | -0.6699 | 0.27 | ❌ rejected |
| 12 | approach → approach → align → approach → descend | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | admittance_control | admittance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 14 | -0.1447 | 0.65 | ❌ rejected |
| 11 | approach → approach → align → descend | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | admittance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 14 | -0.4909 | 0.27 | ❌ rejected |
| 10 | approach → approach → approach → descend | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | admittance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.0147 | 0.65 | ❌ rejected |

**Proposal policy**: task_score is 0.65 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.245) — your mutation base

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

- **Composite score**: -0.245
- **task_score** (E): 0.645
- **fitness_score**: 0.645  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.890

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| lift_and_side_move | 0.67 | 0.00 | 0.3123 |
| arc_above_goal | 1.00 | 0.00 | 0.3701 |
| side_align_to_goal_xy | 1.00 | 0.00 | 0.1669 |
| lateral_to_goal_y | 1.00 | 0.00 | 0.1071 |
| descend_to_goal | 1.00 | 0.33 | 0.2297 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force | Obstacle/contact |
|---|---|---|---|---|---|---|---|---|---|
| lift_and_side_move | approach | 0.67 / step_budget | (0.350, -0.000, 0.321)→(0.350, 0.236, 0.525) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| arc_above_goal | approach | 1.00 / step_budget | (0.350, 0.236, 0.525)→(0.699, 0.303, 0.427) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| side_align_to_goal_xy | align | 1.00 / step_budget | (0.699, 0.303, 0.427)→(0.700, 0.136, 0.427) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| lateral_to_goal_y | approach | 1.00 / step_budget | (0.700, 0.136, 0.427)→(0.699, 0.038, 0.385) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| descend_to_goal | descend | 1.00 / step_budget | (0.699, 0.038, 0.385)→(0.699, 0.025, 0.156) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.717→0.717 | 0.33 / 0.333 | 44.953 | 53.927 | link5 ↔ obstacle_block/obstacle_block_geom |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.841
- path_efficiency: 0.287
- arc_smoothness: 0.997
- collision_factor: 1.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 0.000 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.005
- min_tcp_distance: 0.005
- tcp_proximity_score: 0.968
- goal_reached_rate: 1.000
- peak_obstacle_counterbody: None
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: None
- peak_obstacle_obstacle_geom: None

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.968
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.968
- **Median Q (composite search score)**: 0.078
- **K-run variance**: 0.2083
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 4.7
- **Parameters at lower bound**: descend_to_goal.descend_tolerance
- **Final σ (mean)**: 0.303


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97285,"average_solve_count":221.0,"average_success_count":221.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_above_goal.arc_height":0.16947,"arc_above_goal.arc_speed":0.27164,"arc_above_goal.arc_tolerance":0.02743,"arc_above_goal.arc_y_offset":0.31721,"descend_to_goal.descend_speed":0.04377,"descend_to_goal.descend_tolerance":0.00501,"lateral_to_goal_y.lateral_speed":0.21195,"lateral_to_goal_y.lateral_tolerance":0.01291,"lateral_to_goal_y.lateral_z_offset":0.24178,"lift_and_side_move.clearance_z":0.22048,"lift_and_side_move.lateral_y":0.28646,"lift_and_side_move.lift_speed":0.18275,"lift_and_side_move.lift_tolerance":0.0114,"side_align_to_goal_xy.side_align_speed":0.1686,"side_align_to_goal_xy.side_align_tolerance":0.00974,"side_align_to_goal_xy.side_align_z_offset":0.26745},"optimized_scores":{"best_composite_score":0.07823,"best_fitness_score":0.96823,"best_task_score":0.96823},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.00484,"key_states":{"actual_goal_position":[0.70382,-0.01567,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.70052,-0.01514,0.15351],"realised_goal_position":[0.70382,-0.01567,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lift_and_side_move","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.35019,0.23664,0.49954],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.65435,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":673.0,"n_steps_budget":870.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"arc_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.70308,0.30107,0.42669],"tcp_start":[0.35019,0.23664,0.49954],"tcp_to_object_dist_end":0.8758,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":752.0,"n_steps_budget":810.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"side_align_to_goal_xy","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.70367,0.09448,0.409],"tcp_start":[0.70308,0.30107,0.42669],"tcp_to_object_dist_end":0.81937,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":374.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lateral_to_goal_y","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.70328,-0.00504,0.38468],"tcp_start":[0.70367,0.09448,0.409],"tcp_to_object_dist_end":0.80163,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":851.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.70052,-0.01514,0.15351],"tcp_start":[0.70328,-0.00504,0.38468],"tcp_to_object_dist_end":0.7173,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.46452,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_above_goal.arc_height":0.27435,"arc_above_goal.arc_speed":0.29601,"arc_above_goal.arc_tolerance":0.02366,"arc_above_goal.arc_y_offset":0.2193,"descend_to_goal.descend_speed":0.08599,"descend_to_goal.descend_tolerance":0.005,"lateral_to_goal_y.lateral_speed":0.22604,"lateral_to_goal_y.lateral_tolerance":0.01476,"lateral_to_goal_y.lateral_z_offset":0.22226,"lift_and_side_move.clearance_z":0.23289,"lift_and_side_move.lateral_y":0.23892,"lift_and_side_move.lift_speed":0.20832,"lift_and_side_move.lift_tolerance":0.01273,"side_align_to_goal_xy.side_align_speed":0.25218,"side_align_to_goal_xy.side_align_tolerance":0.01735,"side_align_to_goal_xy.side_align_z_offset":0.28827},"optimized_scores":{"best_composite_score":0.07823,"best_fitness_score":0.96823,"best_task_score":0.96823},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.00484,"key_states":{"actual_goal_position":[0.71251,0.03972,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.70924,0.04026,0.15353],"realised_goal_position":[0.71251,0.03972,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":961.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lift_and_side_move","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.35038,0.22966,0.5412],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.6844,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":687.0,"n_steps_budget":840.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"arc_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.70845,0.25843,0.42318],"tcp_start":[0.35038,0.22966,0.5412],"tcp_to_object_dist_end":0.86474,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":337.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"side_align_to_goal_xy","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.71233,0.15294,0.4273],"tcp_start":[0.70845,0.25843,0.42318],"tcp_to_object_dist_end":0.84463,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":296.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lateral_to_goal_y","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.71199,0.05417,0.37036],"tcp_start":[0.71233,0.15294,0.4273],"tcp_to_object_dist_end":0.80438,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":726.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.70924,0.04026,0.15353],"tcp_start":[0.71199,0.05417,0.37036],"tcp_to_object_dist_end":0.72678,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94737,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_above_goal.arc_height":0.17035,"arc_above_goal.arc_speed":0.41742,"arc_above_goal.arc_tolerance":0.03008,"arc_above_goal.arc_y_offset":0.29915,"descend_to_goal.descend_speed":0.0564,"descend_to_goal.descend_tolerance":0.01018,"lateral_to_goal_y.lateral_speed":0.19557,"lateral_to_goal_y.lateral_tolerance":0.01778,"lateral_to_goal_y.lateral_z_offset":0.25272,"lift_and_side_move.clearance_z":0.23914,"lift_and_side_move.lateral_y":0.26644,"lift_and_side_move.lift_speed":0.18609,"lift_and_side_move.lift_tolerance":0.01514,"side_align_to_goal_xy.side_align_speed":0.20131,"side_align_to_goal_xy.side_align_tolerance":0.00823,"side_align_to_goal_xy.side_align_z_offset":0.30614},"optimized_scores":{"best_composite_score":-0.89,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link5","contact_count":168.0,"contact_point_centroid":[0.53996,0.13149,0.29998],"force_p95":159.41023,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":161.78094,"mean_force":137.16996,"phase_index":4.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.68394,0.04972,0.16965]}],"total_contact_groups":1},"final_pose_error":0.01203,"key_states":{"actual_goal_position":[0.6827,0.04873,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.68616,0.04887,0.16152],"realised_goal_position":[0.6827,0.04873,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":161.78094,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lift_and_side_move","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.35037,0.24142,0.53399],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.68278,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":525.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"arc_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.68466,0.34806,0.42973],"tcp_start":[0.35037,0.24142,0.53399],"tcp_to_object_dist_end":0.8801,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":601.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"side_align_to_goal_xy","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.68325,0.1609,0.44588],"tcp_start":[0.68466,0.34806,0.42973],"tcp_to_object_dist_end":0.83158,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":242.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lateral_to_goal_y","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.68263,0.06611,0.40115],"tcp_start":[0.68325,0.1609,0.44588],"tcp_to_object_dist_end":0.79453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":777.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":134.85757,"phase_name":"descend_to_goal","phase_peak_obstacle_force":161.78094,"phase_type":"descend","raw_contact_event_count":168.0,"raw_peak_contact_force":161.78094,"tcp_end":[0.68616,0.04887,0.16152],"tcp_start":[0.68263,0.06611,0.40115],"tcp_to_object_dist_end":0.70661,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```