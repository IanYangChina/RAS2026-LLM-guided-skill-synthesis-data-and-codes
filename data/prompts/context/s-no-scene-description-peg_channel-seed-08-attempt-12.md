## Search State

- **Seed**: 8
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.8347 | 0.42 | ❌ rejected |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.3496 | 0.04 | ❌ rejected |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.9122 | 0.53 | ✅ accepted |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.1620 | 0.01 | ❌ rejected |
| 8 | approach → rotate → descend → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.0530 | 0.01 | ❌ rejected |

**Proposal policy**: task_score is 0.42 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.835) — your mutation base

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

- **Composite score**: 0.835
- **task_score** (E): 0.416
- **fitness_score**: 0.665  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1420 |
| descend_to_peg | 1.00 | 1.00 | 0.1378 |
| push_through_channel | 1.00 | 1.00 | 0.1854 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.162, 0.168) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.543 | 3.526 |
| descend_to_peg | descend | 1.00 / force_exceeded | (0.513, 0.162, 0.168)→(0.500, 0.159, 0.031) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 43.301 | 43.023 |
| push_through_channel | push | 1.00 / time_limit | (0.500, 0.159, 0.031)→(0.495, -0.026, 0.037) | (0.503, 0.080, 0.034)→(0.504, -0.056, 0.037) | 0.160→0.031 | 1.00 / 3.000 | 34.768 | 224.177 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.912
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.389
- phase_score: 0.903
- phase_breakdown.push_through_channel_score: 0.939
- phase_breakdown.approach_peg_score: 0.819

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.698
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.602
- **Median Q (composite search score)**: 0.820
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.364


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42105,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.10896,"descend_to_peg.contact_force":5.55162,"descend_to_peg.descend_speed":0.05181,"push_through_channel.push_distance":0.18949,"push_through_channel.push_speed":0.1375,"push_through_channel.push_timeout":3.65756},"optimized_scores":{"best_composite_score":0.81975,"best_fitness_score":0.64975,"best_task_score":0.60202},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":697.0,"contact_point_centroid":[0.54661,0.10446,0.05994],"force_p95":242.90598,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":334.36266,"mean_force":179.74833,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49139,0.14377,0.03313]},{"body_a":"attachment","body_b":"peg","contact_count":361.0,"contact_point_centroid":[0.49952,0.06728,0.03666],"force_p95":78.94788,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":104.84121,"mean_force":25.53718,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49819,0.0788,0.03647]},{"body_a":"peg","body_b":"channel_base_body","contact_count":820.0,"contact_point_centroid":[0.49684,0.08451,0.00964],"force_p95":74.54,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.69933,"mean_force":11.37951,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49195,0.13727,0.03353]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54767,0.11998,0.05998],"force_p95":46.65468,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":46.65468,"mean_force":46.65468,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49101,0.19746,0.02621]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":30.0,"contact_point_centroid":[0.47498,0.01657,0.02529],"force_p95":38.32612,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.32086,"mean_force":18.93802,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50006,0.03804,0.03674]},{"body_a":"peg","body_b":"channel_base_body","contact_count":363.0,"contact_point_centroid":[0.49635,0.11908,0.00942],"force_p95":0.62652,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56095,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49151,0.19851,0.23124]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52508,0.09081,0.05937],"force_p95":0.93217,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.97085,"mean_force":0.63459,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49334,0.13522,0.03516]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49941,0.19957,0.2975]},{"body_a":"peg","body_b":"channel_base_body","contact_count":875.0,"contact_point_centroid":[0.49601,0.11914,0.00944],"force_p95":0.61346,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66003,"mean_force":0.54115,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48676,0.19723,0.0941]}],"total_contact_groups":9},"final_pose_error":0.02703,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49617,-0.00479,0.03812],"final_tcp_position":[0.50025,0.03416,0.03675],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":334.36266,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":388.0,"n_steps_budget":810.0,"object_pos_end":[0.49603,0.11907,0.034],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1992,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.5576,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":387.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_peg","tcp_end":[0.48488,0.19797,0.1697],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15738,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":875.0,"n_steps_budget":1000.0,"object_pos_end":[0.49595,0.11898,0.03382],"object_pos_start":[0.49603,0.11907,0.034],"object_to_goal_dist_end":0.19912,"object_to_goal_dist_start":0.1992,"object_z_max":0.03412,"peak_contact_force":46.65468,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":876.0,"raw_peak_contact_force":46.65468,"tcp_end":[0.49103,0.19747,0.02609],"tcp_start":[0.48488,0.19797,0.1697],"tcp_to_object_dist_end":0.07902,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":841.0,"n_steps_budget":870.0,"object_pos_end":[0.49617,-0.00479,0.03812],"object_pos_start":[0.49595,0.11898,0.03382],"object_to_goal_dist_end":0.07533,"object_to_goal_dist_start":0.19912,"object_z_max":0.04106,"peak_contact_force":104.28516,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1913.0,"raw_peak_contact_force":334.36266,"subtask_id":"push_through_channel","tcp_end":[0.50025,0.03416,0.03675],"tcp_start":[0.49103,0.19747,0.02609],"tcp_to_object_dist_end":0.03918,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57391,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.18737,"descend_to_peg.contact_force":1.00061,"descend_to_peg.descend_speed":0.04756,"push_through_channel.push_distance":0.22307,"push_through_channel.push_speed":0.13203,"push_through_channel.push_timeout":3.71633},"optimized_scores":{"best_composite_score":0.86756,"best_fitness_score":0.69756,"best_task_score":0.38911},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":543.0,"contact_point_centroid":[0.54576,0.06838,0.05998],"force_p95":124.29643,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":151.16909,"mean_force":87.21109,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49989,0.07361,0.03603]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":48.0,"contact_point_centroid":[0.52502,0.11595,0.05999],"force_p95":132.65578,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":147.17383,"mean_force":85.14986,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50141,0.11789,0.03555]},{"body_a":"attachment","body_b":"peg","contact_count":352.0,"contact_point_centroid":[0.50109,-0.01803,0.04305],"force_p95":74.58071,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":105.06168,"mean_force":16.7787,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49539,-0.00688,0.03726]},{"body_a":"peg","body_b":"channel_base_body","contact_count":73.0,"contact_point_centroid":[0.5075,-0.10077,0.0595],"force_p95":96.83174,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":101.75536,"mean_force":53.59485,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49196,-0.05419,0.03754]},{"body_a":"peg","body_b":"channel_base_body","contact_count":744.0,"contact_point_centroid":[0.50315,0.0145,0.00953],"force_p95":16.8527,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.29522,"mean_force":2.89242,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49925,0.06285,0.03621]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":229.0,"contact_point_centroid":[0.52523,-0.04795,0.03438],"force_p95":14.4796,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.24147,"mean_force":4.50417,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49443,-0.02103,0.03736]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":19.0,"contact_point_centroid":[0.47455,0.00751,0.03699],"force_p95":12.86717,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.31918,"mean_force":2.76518,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49858,0.03738,0.03702]},{"body_a":"peg","body_b":"channel_base_body","contact_count":390.0,"contact_point_centroid":[0.50571,0.06301,0.00935],"force_p95":0.5833,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.58125,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51181,0.17214,0.22892]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50021,0.19824,0.29566]},{"body_a":"peg","body_b":"channel_base_body","contact_count":658.0,"contact_point_centroid":[0.50594,0.06301,0.00938],"force_p95":0.55169,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54657,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51304,0.14447,0.09914]}],"total_contact_groups":10},"final_pose_error":0.02333,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50759,-0.08296,0.03692],"final_tcp_position":[0.49164,-0.05792,0.03746],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":151.16909,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":418.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.06294,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54237,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":424.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach_peg","tcp_end":[0.52405,0.14723,0.16709],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15873,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":658.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.06297,0.03381],"object_pos_start":[0.50599,0.06294,0.03381],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":1.39103,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":658.0,"raw_peak_contact_force":0.55501,"tcp_end":[0.50434,0.14242,0.03376],"tcp_start":[0.52405,0.14723,0.16709],"tcp_to_object_dist_end":0.07947,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50759,-0.08296,0.03692],"object_pos_start":[0.50603,0.06297,0.03381],"object_to_goal_dist_end":0.00871,"object_to_goal_dist_start":0.14324,"object_z_max":0.03906,"peak_contact_force":0.01145,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2008.0,"raw_peak_contact_force":151.16909,"subtask_id":"push_through_channel","tcp_end":[0.49164,-0.05792,0.03746],"tcp_start":[0.50434,0.14242,0.03376],"tcp_to_object_dist_end":0.02969,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46154,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.12415,"descend_to_peg.contact_force":7.98377,"descend_to_peg.descend_speed":0.05212,"push_through_channel.push_distance":0.20798,"push_through_channel.push_speed":0.12423,"push_through_channel.push_timeout":3.24109},"optimized_scores":{"best_composite_score":0.81666,"best_fitness_score":0.64666,"best_task_score":0.25756},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":536.0,"contact_point_centroid":[0.5463,0.07163,0.05998],"force_p95":137.17567,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":186.99992,"mean_force":87.77006,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50077,0.07591,0.03602]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":125.0,"contact_point_centroid":[0.52503,0.11104,0.05999],"force_p95":154.8297,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":165.59914,"mean_force":100.38968,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5017,0.1134,0.03562]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55383,0.12,0.05994],"force_p95":81.85822,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":81.85822,"mean_force":81.85822,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50539,0.13617,0.03397]},{"body_a":"attachment","body_b":"peg","contact_count":333.0,"contact_point_centroid":[0.50105,-0.01508,0.04109],"force_p95":37.44007,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.66932,"mean_force":9.69037,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4963,-0.00392,0.03722]},{"body_a":"peg","body_b":"channel_base_body","contact_count":45.0,"contact_point_centroid":[0.50729,-0.10051,0.05905],"force_p95":60.15676,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.23115,"mean_force":33.87429,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49277,-0.05196,0.03758]},{"body_a":"peg","body_b":"channel_base_body","contact_count":762.0,"contact_point_centroid":[0.50418,0.01167,0.00955],"force_p95":15.15979,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.47504,"mean_force":2.58306,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49986,0.06158,0.03625]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":220.0,"contact_point_centroid":[0.52515,-0.04641,0.02573],"force_p95":9.63423,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.63705,"mean_force":2.94948,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49525,-0.01974,0.03735]},{"body_a":"peg","body_b":"channel_base_body","contact_count":443.0,"contact_point_centroid":[0.50585,0.0566,0.00935],"force_p95":0.60156,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.58247,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51498,0.16908,0.22871]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50026,0.19817,0.29587]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":81.0,"contact_point_centroid":[0.47471,0.0221,0.02707],"force_p95":1.05944,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33492,"mean_force":0.456,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50022,0.05195,0.03677]},{"body_a":"peg","body_b":"channel_base_body","contact_count":636.0,"contact_point_centroid":[0.50613,0.05664,0.00937],"force_p95":0.60102,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65255,"mean_force":0.54656,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51682,0.13833,0.09899]}],"total_contact_groups":11},"final_pose_error":0.01801,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50741,-0.08071,0.03731],"final_tcp_position":[0.49236,-0.05474,0.03742],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":186.99992,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":472.0,"n_steps_budget":810.0,"object_pos_end":[0.50614,0.0566,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.53006,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":480.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach_peg","tcp_end":[0.53041,0.14116,0.16624],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":636.0,"n_steps_budget":1000.0,"object_pos_end":[0.50615,0.05663,0.03378],"object_pos_start":[0.50614,0.0566,0.03377],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.13688,"object_z_max":0.03381,"peak_contact_force":81.85822,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":637.0,"raw_peak_contact_force":81.85822,"tcp_end":[0.50537,0.13617,0.0338],"tcp_start":[0.53041,0.14116,0.16624],"tcp_to_object_dist_end":0.07954,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50741,-0.08071,0.03731],"object_pos_start":[0.50615,0.05663,0.03378],"object_to_goal_dist_end":0.00791,"object_to_goal_dist_start":0.13691,"object_z_max":0.03901,"peak_contact_force":0.00592,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2102.0,"raw_peak_contact_force":186.99992,"subtask_id":"push_through_channel","tcp_end":[0.49236,-0.05474,0.03742],"tcp_start":[0.50537,0.13617,0.0338],"tcp_to_object_dist_end":0.03001,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```