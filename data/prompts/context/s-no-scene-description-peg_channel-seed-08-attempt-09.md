## Search State

- **Seed**: 8
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.1620 | 0.01 | ❌ rejected |
| 8 | approach → rotate → descend → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.0530 | 0.01 | ❌ rejected |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 8 | -0.3289 | 0.01 | ❌ rejected |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 8 | -0.3898 | 0.00 | ❌ rejected |
| 5 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | 0.1968 | 0.11 | ❌ rejected |

**Proposal policy**: task_score is 0.01 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.162) — your mutation base

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

- **Composite score**: 0.162
- **task_score** (E): 0.008
- **fitness_score**: 0.159  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1421 |
| descend_to_peg | 1.00 | 1.00 | 0.1234 |
| push_through_channel | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.162, 0.168) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.544 | 3.526 |
| descend_to_peg | descend | 1.00 / force_exceeded | (0.513, 0.162, 0.168)→(0.500, 0.105, 0.060) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 19.613 | 19.613 |
| push_through_channel | push | 0.00 / guard_failure | (0.499, 0.100, 0.059)→(0.499, 0.100, 0.059) | (0.503, 0.080, 0.034)→(0.502, 0.077, 0.033) | 0.160→0.157 | 1.00 / 2.000 | 45.230 | 61.321 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.020
- alignment_error: None
- force_efficiency: 0.056
- terminal_score: 0.005
- phase_score: 0.263
- phase_breakdown.push_through_channel_score: 0.023
- phase_breakdown.approach_peg_score: 0.822

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.160
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.013
- **Median Q (composite search score)**: 0.162
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.325


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17949,"average_solve_count":78.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.13587,"descend_to_peg.contact_force":9.78228,"descend_to_peg.descend_speed":0.05191,"push_through_channel.push_distance":0.21599,"push_through_channel.push_speed":0.10189,"push_through_channel.push_timeout":5.09093},"optimized_scores":{"best_composite_score":0.16148,"best_fitness_score":0.15815,"best_task_score":0.01258},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":39.0,"contact_point_centroid":[0.49376,0.11325,0.00941],"force_p95":40.9566,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.16078,"mean_force":31.85226,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49074,0.14162,0.05942]},{"body_a":"attachment","body_b":"peg","contact_count":39.0,"contact_point_centroid":[0.50068,0.13511,0.05841],"force_p95":40.54347,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.63016,"mean_force":31.41983,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49074,0.14162,0.05942]},{"body_a":"peg","body_b":"channel_base_body","contact_count":740.0,"contact_point_centroid":[0.49603,0.11913,0.00949],"force_p95":0.59746,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.76345,"mean_force":0.56077,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48695,0.17033,0.11249]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50067,0.13657,0.05893],"force_p95":18.25831,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.25831,"mean_force":18.25831,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49132,0.14395,0.06031]},{"body_a":"peg","body_b":"channel_base_body","contact_count":354.0,"contact_point_centroid":[0.49631,0.11912,0.0094],"force_p95":0.63666,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56232,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49165,0.19853,0.23126]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49949,0.19956,0.29753]}],"total_contact_groups":6},"final_pose_error":0.21147,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49525,0.11651,0.03368],"final_tcp_position":[0.49042,0.1393,0.05903],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":69.16078,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":379.0,"n_steps_budget":660.0,"object_pos_end":[0.49603,0.1193,0.03394],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19943,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52535,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":378.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_peg","tcp_end":[0.48501,0.19799,0.16966],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15727,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":740.0,"n_steps_budget":1000.0,"object_pos_end":[0.49606,0.11909,0.034],"object_pos_start":[0.49603,0.1193,0.03394],"object_to_goal_dist_end":0.19922,"object_to_goal_dist_start":0.19943,"object_z_max":0.03425,"peak_contact_force":18.76345,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":741.0,"raw_peak_contact_force":18.76345,"tcp_end":[0.49133,0.14389,0.0602],"tcp_start":[0.48501,0.19799,0.16966],"tcp_to_object_dist_end":0.03638,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":39.0,"n_steps_budget":1000.0,"object_pos_end":[0.49521,0.11665,0.03366],"object_pos_start":[0.49606,0.11909,0.034],"object_to_goal_dist_end":0.19681,"object_to_goal_dist_start":0.19922,"object_z_max":0.034,"peak_contact_force":48.6368,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":78.0,"raw_peak_contact_force":69.16078,"subtask_id":"push_through_channel","tcp_end":[0.49042,0.1393,0.05903],"tcp_start":[0.49042,0.13937,0.05904],"tcp_to_object_dist_end":0.03435,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.61644,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.14201,"descend_to_peg.contact_force":14.41959,"descend_to_peg.descend_speed":0.01058,"push_through_channel.push_distance":0.20273,"push_through_channel.push_speed":0.10412,"push_through_channel.push_timeout":2.20762},"optimized_scores":{"best_composite_score":0.1616,"best_fitness_score":0.15826,"best_task_score":0.00635},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":40.0,"contact_point_centroid":[0.50485,0.05847,0.00938],"force_p95":40.09198,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.58918,"mean_force":33.23283,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50329,0.08618,0.05909]},{"body_a":"attachment","body_b":"peg","contact_count":40.0,"contact_point_centroid":[0.51228,0.0784,0.05825],"force_p95":39.53245,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.14423,"mean_force":32.80634,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50329,0.08618,0.05909]},{"body_a":"peg","body_b":"channel_base_body","contact_count":694.0,"contact_point_centroid":[0.50592,0.06293,0.00938],"force_p95":0.55176,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.68982,"mean_force":0.56696,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51286,0.11773,0.1116]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5122,0.07986,0.05876],"force_p95":14.26736,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.26736,"mean_force":14.26736,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50402,0.08854,0.05997]},{"body_a":"peg","body_b":"channel_base_body","contact_count":410.0,"contact_point_centroid":[0.50572,0.06301,0.00935],"force_p95":0.58104,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57954,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51183,0.17218,0.22905]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50021,0.19836,0.29609]}],"total_contact_groups":6},"final_pose_error":0.19803,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50509,0.06025,0.0335],"final_tcp_position":[0.50284,0.08375,0.05872],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":67.58918,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":438.0,"n_steps_budget":690.0,"object_pos_end":[0.50598,0.06294,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54686,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":444.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach_peg","tcp_end":[0.52415,0.14713,0.16693],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15855,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":694.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.06302,0.0338],"object_pos_start":[0.50598,0.06294,0.03381],"object_to_goal_dist_end":0.14327,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":14.68982,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":695.0,"raw_peak_contact_force":14.68982,"tcp_end":[0.504,0.08846,0.05983],"tcp_start":[0.52415,0.14713,0.16693],"tcp_to_object_dist_end":0.03645,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":40.0,"n_steps_budget":1000.0,"object_pos_end":[0.50507,0.06041,0.0335],"object_pos_start":[0.50595,0.06302,0.0338],"object_to_goal_dist_end":0.14066,"object_to_goal_dist_start":0.14327,"object_z_max":0.03398,"peak_contact_force":39.83852,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":80.0,"raw_peak_contact_force":67.58918,"subtask_id":"push_through_channel","tcp_end":[0.50284,0.08375,0.05872],"tcp_start":[0.50284,0.08382,0.05874],"tcp_to_object_dist_end":0.03443,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20879,"average_solve_count":91.0,"average_success_count":91.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.11487,"descend_to_peg.contact_force":15.66591,"descend_to_peg.descend_speed":0.04839,"push_through_channel.push_distance":0.18737,"push_through_channel.push_speed":0.06177,"push_through_channel.push_timeout":3.8192},"optimized_scores":{"best_composite_score":0.163,"best_fitness_score":0.15966,"best_task_score":0.00538},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":57.0,"contact_point_centroid":[0.50573,0.05381,0.00929],"force_p95":39.08836,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.2132,"mean_force":31.63132,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50385,0.07999,0.05881]},{"body_a":"attachment","body_b":"peg","contact_count":57.0,"contact_point_centroid":[0.51237,0.0717,0.05805],"force_p95":38.64225,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.6433,"mean_force":31.18461,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50385,0.07999,0.05881]},{"body_a":"peg","body_b":"channel_base_body","contact_count":635.0,"contact_point_centroid":[0.50615,0.05664,0.00938],"force_p95":0.55756,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.38497,"mean_force":0.58578,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.5165,0.11173,0.11138]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51266,0.07339,0.05878],"force_p95":24.92416,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.92416,"mean_force":24.92416,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50481,0.08239,0.05999]},{"body_a":"peg","body_b":"channel_base_body","contact_count":447.0,"contact_point_centroid":[0.50582,0.05662,0.00935],"force_p95":0.60155,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.58218,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51504,0.16906,0.2287]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50032,0.19816,0.29587]}],"total_contact_groups":6},"final_pose_error":0.18252,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5051,0.0534,0.03325],"final_tcp_position":[0.50339,0.07743,0.05843],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":47.2132,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":476.0,"n_steps_budget":870.0,"object_pos_end":[0.50614,0.05665,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13693,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.55945,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":484.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach_peg","tcp_end":[0.53051,0.14114,0.16628],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":635.0,"n_steps_budget":1000.0,"object_pos_end":[0.50616,0.05658,0.03379],"object_pos_start":[0.50614,0.05665,0.03377],"object_to_goal_dist_end":0.13686,"object_to_goal_dist_start":0.13693,"object_z_max":0.03379,"peak_contact_force":25.38497,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":636.0,"raw_peak_contact_force":25.38497,"tcp_end":[0.50478,0.0823,0.05984],"tcp_start":[0.53051,0.14114,0.16628],"tcp_to_object_dist_end":0.03663,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":57.0,"n_steps_budget":1000.0,"object_pos_end":[0.50509,0.05351,0.03328],"object_pos_start":[0.50616,0.05658,0.03379],"object_to_goal_dist_end":0.13378,"object_to_goal_dist_start":0.13686,"object_z_max":0.03388,"peak_contact_force":47.2132,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":114.0,"raw_peak_contact_force":47.2132,"subtask_id":"push_through_channel","tcp_end":[0.50339,0.07743,0.05843],"tcp_start":[0.5034,0.07748,0.05845],"tcp_to_object_dist_end":0.03475,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```