## Search State

- **Seed**: 3
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | -0.0765 | 0.00 | ❌ rejected |
| 6 | approach → descend → align → push | linear_cartesian | linear_cartesian | joint_interpolation | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | time_limit | 7 | 0.0312 | 0.00 | ❌ rejected |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.4965 | 0.10 | ✅ accepted |
| 4 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | -0.1168 | 0.09 | ❌ rejected |
| 3 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | -0.1168 | 0.09 | ❌ rejected |

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

- Task name: peg_channel
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

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

## Current Skill (Q=-0.077) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_above_peg
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: contact_peg
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.5
phases:
- id: approach_peg
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_above_peg
- id: descend_contact
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_below_contact
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  subtask_id: contact_peg
- id: push_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    max_push_time:
      type: scalar
      range:
      - 0.5
      - 3.0
      default: 1.5
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.15
      - 0.25
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_contact** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_below_contact, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
- **push_channel** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.2, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - max_push_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]

## Design Metrics

- **Composite score**: -0.077
- **task_score** (E): 0.004
- **fitness_score**: 0.123  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.200

**⚠ Warning**: CMA-ES stagnated + low fitness_score → structure may be fundamentally incompatible with task

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| lateral_approach | 1.00 | 1.00 | 0.2565 |
| push_through | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| lateral_approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.506, 0.119, 0.059) | (0.509, 0.081, 0.040)→(0.502, 0.082, 0.034) | 0.165→0.162 | 1.00 / 1.667 | 331.623 | 375.109 |
| push_through | push | 0.00 / guard_failure | (0.505, 0.115, 0.057)→(0.505, 0.115, 0.057) | (0.502, 0.082, 0.034)→(0.502, 0.080, 0.035) | 0.162→0.160 | 1.00 / 2.333 | 109.877 | 131.016 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.025
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.013
- phase_score: 0.218
- phase_breakdown.reach_behind_peg_score: 0.675
- phase_breakdown.push_through_channel_score: 0.022

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.136
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.013
- **Median Q (composite search score)**: -0.082
- **K-run variance**: 0.0001
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 5.3
- **Final σ (mean)**: 0.324


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `cc7283febf3c95cef1fde4c5a16cbcb134186cb6faf3a169717a9aa53375931d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `178d67757a065da6e29d31070e25f6065dc7e42bdbf58dfbff0deec513214033`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.86364,"average_solve_count":22.0,"average_success_count":22.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lateral_approach.approach_speed":0.39631,"push_through.max_push_time":1.95246,"push_through.push_distance":0.1868,"push_through.push_speed":0.12008},"optimized_scores":{"best_composite_score":-0.08207,"best_fitness_score":0.11793,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":12.0,"contact_point_centroid":[0.4749,0.08909,0.05919],"force_p95":540.28923,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":541.58395,"mean_force":455.38428,"phase_index":0.0,"phase_name":"lateral_approach","phase_type":"approach","tcp_position_centroid":[0.4675,0.0985,0.05942]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47488,0.08834,0.05903],"force_p95":159.14803,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":159.93213,"mean_force":152.0912,"phase_index":1.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.46809,0.09819,0.059]},{"body_a":"peg","body_b":"channel_base_body","contact_count":401.0,"contact_point_centroid":[0.49443,0.05887,0.00934],"force_p95":0.5959,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.5827,"phase_index":0.0,"phase_name":"lateral_approach","phase_type":"approach","tcp_position_centroid":[0.48194,0.14529,0.16929]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"lateral_approach","phase_type":"approach","tcp_position_centroid":[0.49867,0.19669,0.29217]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.51174,0.05967,0.00939],"force_p95":0.54724,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54735,"mean_force":0.54629,"phase_index":1.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.46809,0.09819,0.059]}],"total_contact_groups":5},"final_pose_error":0.36686,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49421,0.05903,0.03386],"final_tcp_position":[0.46818,0.09818,0.05908],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":541.58395,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":430.0,"n_steps_budget":600.0,"object_pos_end":[0.49423,0.05894,0.03386],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13919,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":505.13596,"phase_name":"lateral_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":448.0,"raw_peak_contact_force":541.58395,"subtask_id":"reach_behind_peg","tcp_end":[0.46805,0.0982,0.05897],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.49423,0.05898,0.03386],"object_pos_start":[0.49423,0.05894,0.03386],"object_to_goal_dist_end":0.13924,"object_to_goal_dist_start":0.13919,"object_z_max":0.03386,"peak_contact_force":159.93213,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":159.93213,"subtask_id":"push_through_channel","tcp_end":[0.46818,0.09818,0.05908],"tcp_start":[0.46813,0.09819,0.05903],"tcp_to_object_dist_end":0.0534,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.45455,"average_solve_count":22.0,"average_success_count":22.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lateral_approach.approach_speed":0.3916,"push_through.max_push_time":1.64256,"push_through.push_distance":0.19928,"push_through.push_speed":0.05894},"optimized_scores":{"best_composite_score":-0.08335,"best_fitness_score":0.11665,"best_task_score":7e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.54133,0.11819,0.05912],"force_p95":578.17274,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":580.41119,"mean_force":487.49527,"phase_index":0.0,"phase_name":"lateral_approach","phase_type":"approach","tcp_position_centroid":[0.52946,0.11887,0.05985]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.54216,0.118,0.05902],"force_p95":103.72036,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":104.87346,"mean_force":93.34242,"phase_index":1.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.53028,0.11867,0.05964]},{"body_a":"peg","body_b":"channel_base_body","contact_count":401.0,"contact_point_centroid":[0.50557,0.08086,0.00935],"force_p95":0.56155,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.58481,"phase_index":0.0,"phase_name":"lateral_approach","phase_type":"approach","tcp_position_centroid":[0.51503,0.15606,0.16921]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"lateral_approach","phase_type":"approach","tcp_position_centroid":[0.50069,0.19732,0.29211]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.51406,0.0947,0.00938],"force_p95":0.54982,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55009,"mean_force":0.54736,"phase_index":1.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.53028,0.11867,0.05964]}],"total_contact_groups":5},"final_pose_error":0.3996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50599,0.08087,0.03378],"final_tcp_position":[0.53041,0.11867,0.05976],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":580.41119,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":430.0,"n_steps_budget":600.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":489.15923,"phase_name":"lateral_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":451.0,"raw_peak_contact_force":580.41119,"subtask_id":"reach_behind_peg","tcp_end":[0.53023,0.11866,0.0596],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":104.87346,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":104.87346,"subtask_id":"push_through_channel","tcp_end":[0.53041,0.11867,0.05976],"tcp_start":[0.53033,0.11867,0.05968],"tcp_to_object_dist_end":0.05195,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.48276,"average_solve_count":29.0,"average_success_count":29.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lateral_approach.approach_speed":0.24261,"push_through.max_push_time":2.92747,"push_through.push_distance":0.19441,"push_through.push_speed":0.1313},"optimized_scores":{"best_composite_score":-0.06413,"best_fitness_score":0.13587,"best_task_score":0.01307},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.5251,0.11991,0.05999],"force_p95":106.37295,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":128.24286,"mean_force":50.82364,"phase_index":1.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.51518,0.1279,0.05315]},{"body_a":"peg","body_b":"channel_base_body","contact_count":87.0,"contact_point_centroid":[0.50488,0.09879,0.00944],"force_p95":5.04933,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.1987,"mean_force":0.90126,"phase_index":1.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.51628,0.13406,0.05436]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.51163,0.12071,0.05415],"force_p95":6.58376,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.87766,"mean_force":3.45646,"phase_index":1.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.51563,0.13194,0.05361]},{"body_a":"peg","body_b":"channel_base_body","contact_count":399.0,"contact_point_centroid":[0.50544,0.10468,0.00937],"force_p95":0.58008,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57469,"phase_index":0.0,"phase_name":"lateral_approach","phase_type":"approach","tcp_position_centroid":[0.50951,0.16814,0.17207]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"lateral_approach","phase_type":"approach","tcp_position_centroid":[0.50029,0.19825,0.29354]}],"total_contact_groups":5},"final_pose_error":0.40256,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50652,0.10065,0.03701],"final_tcp_position":[0.5151,0.12765,0.05312],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":128.24286,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":426.0,"n_steps_budget":720.0,"object_pos_end":[0.50598,0.10471,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.57506,"phase_name":"lateral_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":431.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_behind_peg","tcp_end":[0.51909,0.13962,0.05829],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0446,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":87.0,"n_steps_budget":1000.0,"object_pos_end":[0.50646,0.1007,0.03695],"object_pos_start":[0.50598,0.10471,0.03383],"object_to_goal_dist_end":0.18084,"object_to_goal_dist_start":0.18491,"object_z_max":0.03695,"peak_contact_force":64.82689,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":103.0,"raw_peak_contact_force":128.24286,"subtask_id":"push_through_channel","tcp_end":[0.5151,0.12765,0.05312],"tcp_start":[0.51513,0.12766,0.05313],"tcp_to_object_dist_end":0.0326,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```