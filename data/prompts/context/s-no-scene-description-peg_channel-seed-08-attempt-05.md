## Search State

- **Seed**: 8
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | 0.1968 | 0.11 | ❌ rejected |
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 6 | -0.1816 | 0.00 | ❌ rejected |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.8850 | 0.51 | ✅ accepted |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.3492 | 0.39 | ✅ accepted |
| 1 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | 0.2633 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.11 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.197) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.08
  - 0.12
  weight: 0.3
- id: push_through_channel
  target_entity: object
  metric: goal_progress
  weight: 0.7
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
    - 0.08
    - 0.12
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
  subtask_id: approach_peg
- id: descend_to_peg
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.08
    - -0.015
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
- id: push_through_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
  parameters:
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
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    push_timeout:
      type: scalar
      range:
      - 1.0
      - 5.0
      default: 3.0
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: push_through_channel

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.08, 0.12]
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.08, -0.015]
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_through_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_timeout: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.197
- **task_score** (E): 0.108
- **fitness_score**: 0.397  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.200

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2575 |
| push_peg | 1.00 | 1.00 | 0.1437 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.160, 0.048) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.537 | 3.526 |
| push_peg | push | 1.00 / time_limit | (0.513, 0.160, 0.048)→(0.501, 0.017, 0.048) | (0.503, 0.080, 0.034)→(0.499, 0.009, 0.033) | 0.160→0.090 | 1.00 / 2.667 | 65.436 | 191.106 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.622
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.160
- phase_score: 0.739
- phase_breakdown.push_through_channel_score: 0.704
- phase_breakdown.approach_peg_score: 0.822

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.508
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.160
- **Median Q (composite search score)**: 0.299
- **K-run variance**: 0.0228
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.349


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a8ce855c7f52ba2d198de8387bdd2f3b869655c206850d620daaec6ac6f298cd`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `79b30dd7102e96fb2fa0880d3932c959e04a6f943c7e87b878f77a0e54f87a94`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75385,"average_solve_count":65.0,"average_success_count":65.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.19827,"push_peg.push_distance":0.20009,"push_peg.push_speed":0.03958,"push_peg.push_timeout":1.61281},"optimized_scores":{"best_composite_score":-0.01666,"best_fitness_score":0.18334,"best_task_score":0.03572},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47494,0.11991,0.04765],"force_p95":35.7357,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":36.64242,"mean_force":25.77778,"phase_index":1.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.48107,0.13006,0.04677]},{"body_a":"peg","body_b":"channel_base_body","contact_count":979.0,"contact_point_centroid":[0.49802,0.11457,0.00955],"force_p95":2.64722,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.25955,"mean_force":0.82413,"phase_index":1.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.48059,0.16266,0.04576]},{"body_a":"attachment","body_b":"peg","contact_count":197.0,"contact_point_centroid":[0.48853,0.12812,0.05075],"force_p95":2.6999,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.87535,"mean_force":1.57265,"phase_index":1.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.48093,0.13784,0.04648]},{"body_a":"peg","body_b":"channel_base_body","contact_count":643.0,"contact_point_centroid":[0.49623,0.11911,0.00943],"force_p95":0.61668,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55238,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4908,0.19832,0.16946]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49958,0.19959,0.29674]}],"total_contact_groups":5},"final_pose_error":0.1327,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50148,0.10941,0.03679],"final_tcp_position":[0.48106,0.12996,0.04679],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":36.64242,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":668.0,"n_steps_budget":840.0,"object_pos_end":[0.49605,0.11922,0.03388],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19935,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52067,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":667.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_peg","tcp_end":[0.48345,0.19765,0.04925],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08091,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50148,0.10941,0.03679],"object_pos_start":[0.49605,0.11922,0.03388],"object_to_goal_dist_end":0.18944,"object_to_goal_dist_start":0.19935,"object_z_max":0.03687,"peak_contact_force":36.64242,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1187.0,"raw_peak_contact_force":36.64242,"subtask_id":"push_through_channel","tcp_end":[0.48106,0.12996,0.04679],"tcp_start":[0.48345,0.19765,0.04925],"tcp_to_object_dist_end":0.03065,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92771,"average_solve_count":83.0,"average_success_count":83.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.11711,"push_peg.push_distance":0.18402,"push_peg.push_speed":0.10521,"push_peg.push_timeout":3.6535},"optimized_scores":{"best_composite_score":0.29931,"best_fitness_score":0.49931,"best_task_score":0.12886},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":766.0,"contact_point_centroid":[0.52503,0.06856,0.05999],"force_p95":172.05659,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":213.90067,"mean_force":123.71972,"phase_index":1.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.51252,0.07181,0.04584]},{"body_a":"attachment","body_b":"peg","contact_count":494.0,"contact_point_centroid":[0.50343,0.01999,0.04731],"force_p95":32.48595,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.36721,"mean_force":18.03508,"phase_index":1.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.51067,0.02915,0.04621]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":476.0,"contact_point_centroid":[0.47425,0.00272,0.05076],"force_p95":32.15504,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.08612,"mean_force":17.18684,"phase_index":1.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.51071,0.0254,0.0464]},{"body_a":"peg","body_b":"channel_base_body","contact_count":707.0,"contact_point_centroid":[0.50009,0.03738,0.00957],"force_p95":10.52339,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.6435,"mean_force":3.00916,"phase_index":1.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.51401,0.09033,0.04577]},{"body_a":"peg","body_b":"channel_base_body","contact_count":762.0,"contact_point_centroid":[0.50583,0.06295,0.00936],"force_p95":0.55663,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56432,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51166,0.17129,0.169]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49989,0.19889,0.29604]}],"total_contact_groups":6},"final_pose_error":0.02109,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49249,-0.03985,0.03951],"final_tcp_position":[0.51118,-0.0197,0.04916],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":213.90067,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":790.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.06297,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.5435,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":796.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach_peg","tcp_end":[0.52429,0.14485,0.04817],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08514,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49249,-0.03985,0.03951],"object_pos_start":[0.50594,0.06297,0.03381],"object_to_goal_dist_end":0.04085,"object_to_goal_dist_start":0.14323,"object_z_max":0.03957,"peak_contact_force":16.2558,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2443.0,"raw_peak_contact_force":213.90067,"subtask_id":"push_through_channel","tcp_end":[0.51118,-0.0197,0.04916],"tcp_start":[0.52429,0.14485,0.04817],"tcp_to_object_dist_end":0.02913,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93333,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.07949,"push_peg.push_distance":0.22313,"push_peg.push_speed":0.13407,"push_peg.push_timeout":4.40645},"optimized_scores":{"best_composite_score":0.30764,"best_fitness_score":0.50764,"best_task_score":0.16004},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":807.0,"contact_point_centroid":[0.52556,0.06261,0.05999],"force_p95":222.3525,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":322.77506,"mean_force":174.40256,"phase_index":1.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.51515,0.068,0.0462]},{"body_a":"peg","body_b":"channel_base_body","contact_count":946.0,"contact_point_centroid":[0.50196,0.02052,0.00929],"force_p95":21.58877,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.5898,"mean_force":4.11772,"phase_index":1.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.51562,0.0678,0.04618]},{"body_a":"attachment","body_b":"peg","contact_count":214.0,"contact_point_centroid":[0.50318,-0.00154,0.0456],"force_p95":37.38728,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.58297,"mean_force":21.81061,"phase_index":1.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.50982,0.00783,0.04416]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":211.0,"contact_point_centroid":[0.47475,-0.00989,0.03002],"force_p95":21.65726,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.96256,"mean_force":12.94085,"phase_index":1.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.50978,0.00776,0.04403]},{"body_a":"peg","body_b":"channel_base_body","contact_count":807.0,"contact_point_centroid":[0.50593,0.05658,0.00936],"force_p95":0.5995,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56625,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51497,0.16813,0.16853]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49997,0.19876,0.29577]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52526,-0.00099,0.05858],"force_p95":0.9825,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.12358,"mean_force":0.3041,"phase_index":1.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.50948,0.03841,0.04238]}],"total_contact_groups":7},"final_pose_error":0.02961,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50433,-0.04292,0.02415],"final_tcp_position":[0.51045,-0.05849,0.04663],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":322.77506,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":836.0,"n_steps_budget":1000.0,"object_pos_end":[0.50609,0.05667,0.03382],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13694,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54534,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":844.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach_peg","tcp_end":[0.53081,0.1388,0.04767],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08688,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50433,-0.04292,0.02415],"object_pos_start":[0.50609,0.05667,0.03382],"object_to_goal_dist_end":0.04056,"object_to_goal_dist_start":0.13694,"object_z_max":0.04042,"peak_contact_force":143.41098,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2192.0,"raw_peak_contact_force":322.77506,"subtask_id":"push_through_channel","tcp_end":[0.51045,-0.05849,0.04663],"tcp_start":[0.53081,0.1388,0.04767],"tcp_to_object_dist_end":0.02802,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```