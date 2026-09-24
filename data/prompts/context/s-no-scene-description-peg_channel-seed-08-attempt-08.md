## Search State

- **Seed**: 8
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → rotate → descend → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.0530 | 0.01 | ❌ rejected |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 8 | -0.3289 | 0.01 | ❌ rejected |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 8 | -0.3898 | 0.00 | ❌ rejected |
| 5 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | 0.1968 | 0.11 | ❌ rejected |
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 6 | -0.1816 | 0.00 | ❌ rejected |

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

## Current Skill (Q=-0.053) — your mutation base

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

- **Composite score**: -0.053
- **task_score** (E): 0.007
- **fitness_score**: 0.157  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1420 |
| rotate_to_channel | 1.00 | 1.00 | 0.0251 |
| descend_to_peg | 1.00 | 1.00 | 0.1289 |
| push_through_channel | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.162, 0.168) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.534 | 3.526 |
| rotate_to_channel | rotate | 1.00 / step_budget | (0.513, 0.162, 0.168)→(0.502, 0.184, 0.162) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.559 | 0.606 |
| descend_to_peg | descend | 1.00 / force_exceeded | (0.502, 0.184, 0.162)→(0.499, 0.105, 0.061) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 15.120 | 15.120 |
| push_through_channel | push | 0.00 / guard_failure | (0.498, 0.102, 0.060)→(0.498, 0.102, 0.060) | (0.503, 0.080, 0.034)→(0.502, 0.077, 0.034) | 0.160→0.157 | 1.00 / 2.000 | 41.334 | 47.540 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.016
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.006
- phase_score: 0.258
- phase_breakdown.push_through_channel_score: 0.018
- phase_breakdown.approach_peg_score: 0.819

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.157
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.011
- **Median Q (composite search score)**: -0.053
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.338


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24359,"average_solve_count":78.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.1642,"descend_to_peg.contact_force":2.76759,"descend_to_peg.descend_speed":0.05168,"push_through_channel.force_limit":37.98012,"push_through_channel.push_distance":0.2003,"push_through_channel.push_speed":0.06686,"push_through_channel.push_timeout":3.53387,"rotate_to_channel.rotate_speed":0.31607},"optimized_scores":{"best_composite_score":-0.05314,"best_fitness_score":0.15686,"best_task_score":0.01137},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":41.0,"contact_point_centroid":[0.48918,0.11546,0.00947],"force_p95":38.60441,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.75391,"mean_force":31.25934,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48581,0.14137,0.06134]},{"body_a":"attachment","body_b":"peg","contact_count":41.0,"contact_point_centroid":[0.49593,0.13599,0.05847],"force_p95":38.02296,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.22518,"mean_force":30.82105,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48581,0.14137,0.06134]},{"body_a":"peg","body_b":"channel_base_body","contact_count":943.0,"contact_point_centroid":[0.49607,0.11901,0.00944],"force_p95":0.59839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.75597,"mean_force":0.55412,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.47854,0.17851,0.10903]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49621,0.13713,0.05898],"force_p95":12.27951,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.27951,"mean_force":12.27951,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48633,0.14314,0.0622]},{"body_a":"peg","body_b":"channel_base_body","contact_count":342.0,"contact_point_centroid":[0.4964,0.11915,0.00938],"force_p95":0.62209,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56501,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49153,0.19852,0.23108]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4994,0.19957,0.29734]},{"body_a":"peg","body_b":"channel_base_body","contact_count":311.0,"contact_point_centroid":[0.49601,0.11914,0.00943],"force_p95":0.61682,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65483,"mean_force":0.5412,"phase_index":1.0,"phase_name":"rotate_to_channel","phase_type":"rotate","tcp_position_centroid":[0.47732,0.20873,0.16529]}],"total_contact_groups":7},"final_pose_error":0.19681,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49533,0.11674,0.03356],"final_tcp_position":[0.48537,0.13952,0.06081],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":42.75391,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":367.0,"n_steps_budget":600.0,"object_pos_end":[0.49605,0.11898,0.03391],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19911,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.53731,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":366.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_peg","tcp_end":[0.48489,0.19796,0.16977],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15755,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":311.0,"n_steps_budget":600.0,"object_pos_end":[0.49607,0.11902,0.03395],"object_pos_start":[0.49605,0.11898,0.03391],"object_to_goal_dist_end":0.19915,"object_to_goal_dist_start":0.19911,"object_z_max":0.03401,"peak_contact_force":0.59055,"phase_name":"rotate_to_channel","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":311.0,"raw_peak_contact_force":0.65483,"tcp_end":[0.47262,0.21824,0.16461],"tcp_start":[0.48489,0.19796,0.16977],"tcp_to_object_dist_end":0.16573,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":943.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11906,0.03405],"object_pos_start":[0.49607,0.11902,0.03395],"object_to_goal_dist_end":0.19919,"object_to_goal_dist_start":0.19915,"object_z_max":0.03418,"peak_contact_force":12.75597,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":944.0,"raw_peak_contact_force":12.75597,"tcp_end":[0.48635,0.14307,0.06212],"tcp_start":[0.47262,0.21824,0.16461],"tcp_to_object_dist_end":0.03818,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":41.0,"n_steps_budget":1000.0,"object_pos_end":[0.49533,0.11683,0.03359],"object_pos_start":[0.49602,0.11906,0.03405],"object_to_goal_dist_end":0.19699,"object_to_goal_dist_start":0.19919,"object_z_max":0.03418,"peak_contact_force":42.75391,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":82.0,"raw_peak_contact_force":42.75391,"subtask_id":"push_through_channel","tcp_end":[0.48537,0.13952,0.06081],"tcp_start":[0.48539,0.13956,0.06084],"tcp_to_object_dist_end":0.03681,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31111,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.16706,"descend_to_peg.contact_force":11.99875,"descend_to_peg.descend_speed":0.04222,"push_through_channel.force_limit":37.87408,"push_through_channel.push_distance":0.24579,"push_through_channel.push_speed":0.05973,"push_through_channel.push_timeout":2.95889,"rotate_to_channel.rotate_speed":0.26727},"optimized_scores":{"best_composite_score":-0.05275,"best_fitness_score":0.15725,"best_task_score":0.00612},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":43.0,"contact_point_centroid":[0.50197,0.05973,0.00936],"force_p95":36.92646,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.94653,"mean_force":31.73126,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50339,0.08745,0.06]},{"body_a":"attachment","body_b":"peg","contact_count":43.0,"contact_point_centroid":[0.51114,0.07866,0.05826],"force_p95":36.51323,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.40621,"mean_force":31.29955,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50339,0.08745,0.06]},{"body_a":"peg","body_b":"channel_base_body","contact_count":832.0,"contact_point_centroid":[0.50603,0.06293,0.00938],"force_p95":0.5526,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.66775,"mean_force":0.56714,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.5075,0.12848,0.10813]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51147,0.07996,0.05884],"force_p95":17.24363,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.24363,"mean_force":17.24363,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50409,0.08917,0.06094]},{"body_a":"peg","body_b":"channel_base_body","contact_count":390.0,"contact_point_centroid":[0.50571,0.06301,0.00935],"force_p95":0.5833,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.58125,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51181,0.17214,0.22892]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50021,0.19824,0.29566]},{"body_a":"peg","body_b":"channel_base_body","contact_count":318.0,"contact_point_centroid":[0.50589,0.06305,0.00938],"force_p95":0.5514,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54657,"phase_index":1.0,"phase_name":"rotate_to_channel","phase_type":"rotate","tcp_position_centroid":[0.51752,0.15933,0.16226]}],"total_contact_groups":7},"final_pose_error":0.24238,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50486,0.06031,0.03342],"final_tcp_position":[0.5029,0.08566,0.05951],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":51.94653,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":418.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.06294,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54237,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":424.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach_peg","tcp_end":[0.52405,0.14723,0.16709],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15873,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":318.0,"n_steps_budget":600.0,"object_pos_end":[0.50603,0.06298,0.03381],"object_pos_start":[0.50599,0.06294,0.03381],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":0.54147,"phase_name":"rotate_to_channel","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":318.0,"raw_peak_contact_force":0.55501,"tcp_end":[0.51375,0.16982,0.16151],"tcp_start":[0.52405,0.14723,0.16709],"tcp_to_object_dist_end":0.16669,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":832.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.0629,0.03383],"object_pos_start":[0.50603,0.06298,0.03381],"object_to_goal_dist_end":0.14316,"object_to_goal_dist_start":0.14324,"object_z_max":0.03383,"peak_contact_force":17.66775,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":833.0,"raw_peak_contact_force":17.66775,"tcp_end":[0.50409,0.08909,0.06083],"tcp_start":[0.51375,0.16982,0.16151],"tcp_to_object_dist_end":0.03766,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":43.0,"n_steps_budget":1000.0,"object_pos_end":[0.50486,0.06041,0.03344],"object_pos_start":[0.50594,0.0629,0.03383],"object_to_goal_dist_end":0.14065,"object_to_goal_dist_start":0.14316,"object_z_max":0.03398,"peak_contact_force":33.33118,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":86.0,"raw_peak_contact_force":51.94653,"subtask_id":"push_through_channel","tcp_end":[0.5029,0.08566,0.05951],"tcp_start":[0.50291,0.0857,0.05954],"tcp_to_object_dist_end":0.03635,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.375,"average_solve_count":80.0,"average_success_count":80.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.17494,"descend_to_peg.contact_force":10.61051,"descend_to_peg.descend_speed":0.05037,"push_through_channel.force_limit":37.74882,"push_through_channel.push_distance":0.19425,"push_through_channel.push_speed":0.0722,"push_through_channel.push_timeout":4.09521,"rotate_to_channel.rotate_speed":0.31215},"optimized_scores":{"best_composite_score":-0.05311,"best_fitness_score":0.15689,"best_task_score":0.00417},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":39.0,"contact_point_centroid":[0.50303,0.05235,0.00937],"force_p95":37.89418,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.91835,"mean_force":31.37557,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50514,0.08135,0.05982]},{"body_a":"attachment","body_b":"peg","contact_count":39.0,"contact_point_centroid":[0.51231,0.07203,0.05828],"force_p95":37.45382,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.36155,"mean_force":30.94737,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50514,0.08135,0.05982]},{"body_a":"peg","body_b":"channel_base_body","contact_count":801.0,"contact_point_centroid":[0.50615,0.05659,0.00938],"force_p95":0.55649,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.93515,"mean_force":0.56455,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51168,0.12271,0.10771]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51263,0.07333,0.0588],"force_p95":14.47888,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.47888,"mean_force":14.47888,"phase_index":2.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50583,0.08302,0.0607]},{"body_a":"peg","body_b":"channel_base_body","contact_count":406.0,"contact_point_centroid":[0.50582,0.05657,0.00934],"force_p95":0.60208,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.58568,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51518,0.16891,0.2283]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50044,0.19792,0.2952]},{"body_a":"peg","body_b":"channel_base_body","contact_count":312.0,"contact_point_centroid":[0.50611,0.05671,0.00938],"force_p95":0.59881,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60886,"mean_force":0.54658,"phase_index":1.0,"phase_name":"rotate_to_channel","phase_type":"rotate","tcp_position_centroid":[0.52405,0.15335,0.16131]}],"total_contact_groups":7},"final_pose_error":0.19099,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50513,0.05412,0.03347],"final_tcp_position":[0.50466,0.07966,0.05936],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":47.91835,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":435.0,"n_steps_budget":600.0,"object_pos_end":[0.50613,0.05661,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13689,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.52325,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":443.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach_peg","tcp_end":[0.53044,0.14113,0.1662],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15896,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":312.0,"n_steps_budget":600.0,"object_pos_end":[0.50614,0.0566,0.03378],"object_pos_start":[0.50613,0.05661,0.03377],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.13689,"object_z_max":0.03378,"peak_contact_force":0.54606,"phase_name":"rotate_to_channel","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":312.0,"raw_peak_contact_force":0.60886,"tcp_end":[0.52038,0.16405,0.16054],"tcp_start":[0.53044,0.14113,0.1662],"tcp_to_object_dist_end":0.16678,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":801.0,"n_steps_budget":1000.0,"object_pos_end":[0.50612,0.05656,0.0338],"object_pos_start":[0.50614,0.0566,0.03378],"object_to_goal_dist_end":0.13684,"object_to_goal_dist_start":0.13688,"object_z_max":0.03379,"peak_contact_force":14.93515,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":802.0,"raw_peak_contact_force":14.93515,"tcp_end":[0.50582,0.08294,0.06061],"tcp_start":[0.52038,0.16405,0.16054],"tcp_to_object_dist_end":0.03761,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":39.0,"n_steps_budget":1000.0,"object_pos_end":[0.50513,0.05426,0.0335],"object_pos_start":[0.50612,0.05656,0.0338],"object_to_goal_dist_end":0.13452,"object_to_goal_dist_start":0.13684,"object_z_max":0.03395,"peak_contact_force":47.91835,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":78.0,"raw_peak_contact_force":47.91835,"subtask_id":"push_through_channel","tcp_end":[0.50466,0.07966,0.05936],"tcp_start":[0.50467,0.07972,0.05938],"tcp_to_object_dist_end":0.03625,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```