## Search State

- **Seed**: 8
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.3496 | 0.04 | ❌ rejected |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.9122 | 0.53 | ✅ accepted |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.1620 | 0.01 | ❌ rejected |
| 8 | approach → rotate → descend → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.0530 | 0.01 | ❌ rejected |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 8 | -0.3289 | 0.01 | ❌ rejected |

**Proposal policy**: task_score is 0.04 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.350) — your mutation base

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

- **Composite score**: 0.350
- **task_score** (E): 0.039
- **fitness_score**: 0.180  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1794 |
| descend_to_peg | 1.00 | 1.00 | 0.1023 |
| push_through_channel | 1.00 | 1.00 | 0.0433 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.514, 0.087, 0.164) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.536 | 3.526 |
| descend_to_peg | descend | 1.00 / force_exceeded | (0.514, 0.087, 0.164)→(0.503, 0.082, 0.063) | (0.503, 0.080, 0.034)→(0.503, 0.079, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 21.973 | 21.973 |
| push_through_channel | push | 1.00 / time_limit | (0.503, 0.082, 0.063)→(0.519, 0.066, 0.088) | (0.503, 0.079, 0.034)→(0.494, 0.073, 0.033) | 0.160→0.153 | 1.00 / 2.333 | 254.380 | 473.400 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.135
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.114
- phase_score: 0.322
- phase_breakdown.push_through_channel_score: 0.108
- phase_breakdown.approach_peg_score: 0.821

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.239
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.114
- **Median Q (composite search score)**: 0.322
- **K-run variance**: 0.0018
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.317


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17742,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.16971,"descend_to_peg.contact_force":7.88415,"descend_to_peg.descend_speed":0.0412,"push_through_channel.push_distance":0.16665,"push_through_channel.push_speed":0.02029,"push_through_channel.push_timeout":2.81269},"optimized_scores":{"best_composite_score":0.40885,"best_fitness_score":0.23885,"best_task_score":0.11431},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":1000.0,"contact_point_centroid":[0.49091,0.10202,0.05383],"force_p95":218.13245,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":259.63557,"mean_force":105.24623,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48997,0.09428,0.06337]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.48989,0.09749,0.00815],"force_p95":146.30687,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":259.12154,"mean_force":96.59811,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48997,0.09428,0.06337]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":486.0,"contact_point_centroid":[0.46044,0.11996,0.059],"force_p95":192.14424,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":212.25965,"mean_force":133.33054,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49024,0.08029,0.06526]},{"body_a":"peg","body_b":"world","contact_count":109.0,"contact_point_centroid":[0.49272,0.13183,-0.00165],"force_p95":137.14227,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":154.06812,"mean_force":88.55778,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48971,0.13401,0.05228]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":223.0,"contact_point_centroid":[0.47486,0.11462,0.03232],"force_p95":58.07471,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":86.36115,"mean_force":16.87568,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48913,0.11743,0.05944]},{"body_a":"peg","body_b":"channel_base_body","contact_count":628.0,"contact_point_centroid":[0.496,0.11915,0.00946],"force_p95":0.60213,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.89479,"mean_force":0.57342,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48506,0.12263,0.11362]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49899,0.12103,0.05881],"force_p95":21.38113,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.38113,"mean_force":21.38113,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.4881,0.12066,0.06382]},{"body_a":"peg","body_b":"channel_base_body","contact_count":403.0,"contact_point_centroid":[0.4963,0.11915,0.00939],"force_p95":0.61715,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56048,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4913,0.16109,0.2297]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49933,0.19842,0.29745]}],"total_contact_groups":9},"final_pose_error":0.12673,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49449,0.09738,0.03206],"final_tcp_position":[0.49093,0.08079,0.06517],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":259.63557,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":428.0,"n_steps_budget":630.0,"object_pos_end":[0.49604,0.1195,0.03419],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19962,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52183,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":427.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_peg","tcp_end":[0.48454,0.12529,0.16738],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":628.0,"n_steps_budget":1000.0,"object_pos_end":[0.49608,0.11898,0.03383],"object_pos_start":[0.49604,0.1195,0.03419],"object_to_goal_dist_end":0.19911,"object_to_goal_dist_start":0.19962,"object_z_max":0.03419,"peak_contact_force":21.89479,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":629.0,"raw_peak_contact_force":21.89479,"tcp_end":[0.48811,0.12066,0.06368],"tcp_start":[0.48454,0.12529,0.16738],"tcp_to_object_dist_end":0.03094,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49449,0.09738,0.03206],"object_pos_start":[0.49608,0.11898,0.03383],"object_to_goal_dist_end":0.17764,"object_to_goal_dist_start":0.19911,"object_z_max":0.03485,"peak_contact_force":191.70767,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2818.0,"raw_peak_contact_force":259.63557,"subtask_id":"push_through_channel","tcp_end":[0.49093,0.08079,0.06517],"tcp_start":[0.48811,0.12066,0.06368],"tcp_to_object_dist_end":0.0372,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59542,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.09816,"descend_to_peg.contact_force":6.1559,"descend_to_peg.descend_speed":0.04093,"push_through_channel.push_distance":0.20469,"push_through_channel.push_speed":0.10681,"push_through_channel.push_timeout":1.58636},"optimized_scores":{"best_composite_score":0.31798,"best_fitness_score":0.14798,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":930.0,"contact_point_centroid":[0.52527,0.1165,0.05993],"force_p95":319.36822,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":645.66212,"mean_force":285.35653,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.52663,0.05676,0.10026]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52554,0.05876,0.05975],"force_p95":355.2376,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":374.87948,"mean_force":191.70811,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51394,0.05854,0.06181]},{"body_a":"attachment","body_b":"peg","contact_count":63.0,"contact_point_centroid":[0.51505,0.06759,0.05628],"force_p95":224.26041,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":302.6704,"mean_force":159.71208,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50661,0.06359,0.06229]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49527,0.0665,0.00926],"force_p95":92.12634,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":249.90804,"mean_force":10.41372,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.52545,0.05717,0.098]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52596,0.05934,0.05795],"force_p95":127.1456,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":131.98475,"mean_force":24.20659,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51353,0.05937,0.06189]},{"body_a":"peg","body_b":"channel_base_body","contact_count":501.0,"contact_point_centroid":[0.50599,0.06295,0.00938],"force_p95":0.55154,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.08425,"mean_force":0.58957,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51576,0.06791,0.11259]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51994,0.06536,0.05873],"force_p95":21.60699,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.60699,"mean_force":21.60699,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50892,0.06531,0.0634]},{"body_a":"peg","body_b":"channel_base_body","contact_count":630.0,"contact_point_centroid":[0.50582,0.063,0.00936],"force_p95":0.56085,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56803,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51196,0.13267,0.22706]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49988,0.19736,0.29681]}],"total_contact_groups":9},"final_pose_error":0.19294,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49471,0.06639,0.03377],"final_tcp_position":[0.53158,0.04912,0.10131],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":645.66212,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":658.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.06294,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54291,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":664.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach_peg","tcp_end":[0.52474,0.07082,0.16317],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13095,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":501.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.06293,0.0338],"object_pos_start":[0.50598,0.06294,0.03381],"object_to_goal_dist_end":0.14319,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":22.08425,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":502.0,"raw_peak_contact_force":22.08425,"tcp_end":[0.5089,0.0653,0.06321],"tcp_start":[0.52474,0.07082,0.16317],"tcp_to_object_dist_end":0.02965,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49471,0.06639,0.03377],"object_pos_start":[0.50596,0.06293,0.0338],"object_to_goal_dist_end":0.14662,"object_to_goal_dist_start":0.14319,"object_z_max":0.03455,"peak_contact_force":308.24946,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2023.0,"raw_peak_contact_force":645.66212,"subtask_id":"push_through_channel","tcp_end":[0.53158,0.04912,0.10131],"tcp_start":[0.5089,0.0653,0.06321],"tcp_to_object_dist_end":0.07886,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.00565,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.06065,"descend_to_peg.contact_force":6.56437,"descend_to_peg.descend_speed":0.03111,"push_through_channel.push_distance":0.19467,"push_through_channel.push_speed":0.04901,"push_through_channel.push_timeout":3.06901},"optimized_scores":{"best_composite_score":0.32204,"best_fitness_score":0.15204,"best_task_score":0.00126},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52553,0.055,0.05976],"force_p95":487.00153,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":514.90355,"mean_force":252.93741,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51396,0.05489,0.06192]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":934.0,"contact_point_centroid":[0.5263,0.11994,0.05994],"force_p95":296.1747,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":479.95343,"mean_force":269.23808,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.52925,0.06676,0.09712]},{"body_a":"attachment","body_b":"peg","contact_count":75.0,"contact_point_centroid":[0.51469,0.06958,0.05619],"force_p95":220.61682,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":286.17169,"mean_force":151.46075,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50789,0.0645,0.06219]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49437,0.05578,0.00932],"force_p95":128.02446,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":221.7935,"mean_force":11.78871,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.52789,0.06657,0.09486]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52542,0.05425,0.05834],"force_p95":126.28548,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":137.86863,"mean_force":22.961,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51385,0.05554,0.06207]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":230.0,"contact_point_centroid":[0.47484,0.0558,0.04933],"force_p95":35.75467,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.20265,"mean_force":3.22402,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.52459,0.06666,0.09094]},{"body_a":"peg","body_b":"channel_base_body","contact_count":491.0,"contact_point_centroid":[0.50614,0.05658,0.00938],"force_p95":0.55241,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.94144,"mean_force":0.59021,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.52036,0.06169,0.11261]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.52245,0.0589,0.05877],"force_p95":21.44528,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.44528,"mean_force":21.44528,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51141,0.05905,0.06345]},{"body_a":"peg","body_b":"channel_base_body","contact_count":724.0,"contact_point_centroid":[0.50596,0.05663,0.00936],"force_p95":0.60087,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56852,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51527,0.12949,0.22687]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49989,0.19743,0.29689]}],"total_contact_groups":10},"final_pose_error":0.20734,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4931,0.05524,0.03383],"final_tcp_position":[0.53332,0.06812,0.09864],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":514.90355,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":753.0,"n_steps_budget":1000.0,"object_pos_end":[0.50614,0.05659,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54277,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":761.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach_peg","tcp_end":[0.53123,0.06459,0.16275],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13162,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":491.0,"n_steps_budget":1000.0,"object_pos_end":[0.50614,0.05658,0.03378],"object_pos_start":[0.50614,0.05659,0.03378],"object_to_goal_dist_end":0.13686,"object_to_goal_dist_start":0.13687,"object_z_max":0.03378,"peak_contact_force":21.94144,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":492.0,"raw_peak_contact_force":21.94144,"tcp_end":[0.51139,0.05905,0.06327],"tcp_start":[0.53123,0.06459,0.16275],"tcp_to_object_dist_end":0.03005,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4931,0.05524,0.03383],"object_pos_start":[0.50614,0.05658,0.03378],"object_to_goal_dist_end":0.13556,"object_to_goal_dist_start":0.13686,"object_z_max":0.03704,"peak_contact_force":263.18415,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2261.0,"raw_peak_contact_force":514.90355,"subtask_id":"push_through_channel","tcp_end":[0.53332,0.06812,0.09864],"tcp_start":[0.51139,0.05905,0.06327],"tcp_to_object_dist_end":0.07735,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```