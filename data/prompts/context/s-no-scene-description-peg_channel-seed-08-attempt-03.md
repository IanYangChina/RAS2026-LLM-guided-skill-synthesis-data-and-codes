## Search State

- **Seed**: 8
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.8850 | 0.51 | ✅ accepted |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.3492 | 0.39 | ✅ accepted |
| 1 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | 0.2633 | 0.00 | ❌ rejected |
| 0 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | 0.2633 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.51 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.885) — your mutation base

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

- **Composite score**: 0.885
- **task_score** (E): 0.509
- **fitness_score**: 0.715  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1420 |
| descend_to_peg | 1.00 | 1.00 | 0.1378 |
| push_through_channel | 1.00 | 1.00 | 0.2000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.162, 0.168) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.537 | 3.526 |
| descend_to_peg | descend | 1.00 / force_exceeded | (0.513, 0.162, 0.168)→(0.500, 0.159, 0.031) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 77.237 | 77.237 |
| push_through_channel | push | 1.00 / time_limit | (0.500, 0.159, 0.031)→(0.495, -0.041, 0.037) | (0.503, 0.080, 0.034)→(0.503, -0.065, 0.032) | 0.160→0.024 | 1.00 / 3.333 | 102.239 | 231.838 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.923
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.870
- phase_score: 0.754
- phase_breakdown.push_through_channel_score: 0.726
- phase_breakdown.approach_peg_score: 0.819

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.800
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.870
- **Median Q (composite search score)**: 0.868
- **K-run variance**: 0.0041
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.431


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71287,"average_solve_count":101.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.12898,"descend_to_peg.contact_force":8.73935,"descend_to_peg.descend_speed":0.06923,"push_through_channel.push_distance":0.22212,"push_through_channel.push_speed":0.13588,"push_through_channel.push_timeout":2.13941},"optimized_scores":{"best_composite_score":0.97034,"best_fitness_score":0.80034,"best_task_score":0.87001},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":723.0,"contact_point_centroid":[0.54668,0.10059,0.05994],"force_p95":242.39807,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":336.17149,"mean_force":175.6042,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49174,0.13867,0.03327]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":74.0,"contact_point_centroid":[0.525,0.01345,0.06],"force_p95":145.78974,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":154.96105,"mean_force":94.06684,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50071,0.01326,0.03675]},{"body_a":"attachment","body_b":"peg","contact_count":510.0,"contact_point_centroid":[0.49896,0.04922,0.03776],"force_p95":117.45074,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":125.22911,"mean_force":50.17403,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49888,0.06009,0.03653]},{"body_a":"peg","body_b":"channel_base_body","contact_count":969.0,"contact_point_centroid":[0.49597,0.0713,0.00941],"force_p95":97.98184,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":111.12463,"mean_force":23.45102,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49331,0.11837,0.03403]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":256.0,"contact_point_centroid":[0.47469,0.00731,0.02423],"force_p95":61.2569,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.88767,"mean_force":34.78046,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50036,0.02742,0.03673]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54795,0.11998,0.05998],"force_p95":69.95605,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.95605,"mean_force":69.95605,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49102,0.19739,0.02627]},{"body_a":"peg","body_b":"channel_base_body","contact_count":355.0,"contact_point_centroid":[0.49627,0.11908,0.00939],"force_p95":0.63218,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56405,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49153,0.19851,0.23131]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49941,0.19957,0.29754]},{"body_a":"peg","body_b":"channel_base_body","contact_count":826.0,"contact_point_centroid":[0.49605,0.11917,0.00944],"force_p95":0.5926,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63497,"mean_force":0.54076,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48678,0.1972,0.09441]}],"total_contact_groups":9},"final_pose_error":0.0201,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49234,-0.02872,0.02271],"final_tcp_position":[0.50063,-0.00557,0.03669],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":336.17149,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":380.0,"n_steps_budget":690.0,"object_pos_end":[0.49605,0.11899,0.03386],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19912,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.51971,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":379.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_peg","tcp_end":[0.4849,0.19797,0.16985],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15765,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":826.0,"n_steps_budget":1000.0,"object_pos_end":[0.49612,0.11933,0.03404],"object_pos_start":[0.49605,0.11899,0.03386],"object_to_goal_dist_end":0.19945,"object_to_goal_dist_start":0.19912,"object_z_max":0.03409,"peak_contact_force":69.95605,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":827.0,"raw_peak_contact_force":69.95605,"tcp_end":[0.49106,0.19741,0.02614],"tcp_start":[0.4849,0.19797,0.16985],"tcp_to_object_dist_end":0.07864,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.49234,-0.02872,0.02271],"object_pos_start":[0.49612,0.11933,0.03404],"object_to_goal_dist_end":0.05466,"object_to_goal_dist_start":0.19945,"object_z_max":0.04106,"peak_contact_force":108.43708,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2532.0,"raw_peak_contact_force":336.17149,"subtask_id":"push_through_channel","tcp_end":[0.50063,-0.00557,0.03669],"tcp_start":[0.49106,0.19741,0.02614],"tcp_to_object_dist_end":0.02828,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55752,"average_solve_count":113.0,"average_success_count":113.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.11415,"descend_to_peg.contact_force":4.27769,"descend_to_peg.descend_speed":0.05454,"push_through_channel.push_distance":0.21829,"push_through_channel.push_speed":0.14201,"push_through_channel.push_timeout":3.65703},"optimized_scores":{"best_composite_score":0.86839,"best_fitness_score":0.69839,"best_task_score":0.39015},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":498.0,"contact_point_centroid":[0.54586,0.06807,0.05998],"force_p95":134.10155,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":167.72742,"mean_force":91.75963,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49996,0.0734,0.036]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":50.0,"contact_point_centroid":[0.52502,0.11455,0.05999],"force_p95":155.97016,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":160.98075,"mean_force":83.45367,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50141,0.11644,0.03559]},{"body_a":"attachment","body_b":"peg","contact_count":371.0,"contact_point_centroid":[0.50192,-0.0121,0.04194],"force_p95":73.8037,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":88.45888,"mean_force":16.43724,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49595,-0.00099,0.0372]},{"body_a":"peg","body_b":"channel_base_body","contact_count":66.0,"contact_point_centroid":[0.50749,-0.10075,0.05951],"force_p95":82.50078,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.68572,"mean_force":51.98344,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49221,-0.05389,0.03749]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55459,0.12,0.05999],"force_p95":71.58035,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.58035,"mean_force":71.58035,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50434,0.14242,0.03376]},{"body_a":"peg","body_b":"channel_base_body","contact_count":672.0,"contact_point_centroid":[0.50483,0.01529,0.00961],"force_p95":19.23854,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.87702,"mean_force":3.9761,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49947,0.06514,0.03615]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":315.0,"contact_point_centroid":[0.52512,-0.02922,0.02516],"force_p95":11.82041,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.49854,"mean_force":3.69026,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49579,-0.00264,0.03719]},{"body_a":"peg","body_b":"channel_base_body","contact_count":429.0,"contact_point_centroid":[0.50571,0.06303,0.00935],"force_p95":0.58041,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57809,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51165,0.17226,0.22924]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5001,0.19841,0.2962]},{"body_a":"peg","body_b":"channel_base_body","contact_count":656.0,"contact_point_centroid":[0.50592,0.06293,0.00938],"force_p95":0.55142,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54658,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51303,0.14443,0.09894]}],"total_contact_groups":10},"final_pose_error":0.01912,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50766,-0.08284,0.03694],"final_tcp_position":[0.4919,-0.05752,0.03743],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":167.72742,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":457.0,"n_steps_budget":870.0,"object_pos_end":[0.50601,0.06295,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54805,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":463.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach_peg","tcp_end":[0.52404,0.14716,0.16691],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15853,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":656.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.06304,0.03381],"object_pos_start":[0.50601,0.06295,0.03381],"object_to_goal_dist_end":0.1433,"object_to_goal_dist_start":0.14321,"object_z_max":0.03381,"peak_contact_force":71.58035,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":657.0,"raw_peak_contact_force":71.58035,"tcp_end":[0.50433,0.14241,0.0336],"tcp_start":[0.52404,0.14716,0.16691],"tcp_to_object_dist_end":0.07939,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":931.0,"n_steps_budget":960.0,"object_pos_end":[0.50766,-0.08284,0.03694],"object_pos_start":[0.50598,0.06304,0.03381],"object_to_goal_dist_end":0.00872,"object_to_goal_dist_start":0.1433,"object_z_max":0.04016,"peak_contact_force":88.45888,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1972.0,"raw_peak_contact_force":167.72742,"subtask_id":"push_through_channel","tcp_end":[0.4919,-0.05752,0.03743],"tcp_start":[0.50433,0.14241,0.0336],"tcp_to_object_dist_end":0.02983,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04848,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.13197,"descend_to_peg.contact_force":9.9987,"descend_to_peg.descend_speed":0.02597,"push_through_channel.push_distance":0.21629,"push_through_channel.push_speed":0.14793,"push_through_channel.push_timeout":3.54889},"optimized_scores":{"best_composite_score":0.81637,"best_fitness_score":0.64637,"best_task_score":0.26661},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":424.0,"contact_point_centroid":[0.54638,0.07343,0.05998],"force_p95":148.37252,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":191.61588,"mean_force":92.94311,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50081,0.07766,0.03597]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":102.0,"contact_point_centroid":[0.52506,0.11168,0.05997],"force_p95":157.04906,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":159.80171,"mean_force":110.92129,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50183,0.11422,0.03556]},{"body_a":"attachment","body_b":"peg","contact_count":389.0,"contact_point_centroid":[0.50238,-0.01598,0.04249],"force_p95":102.10459,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":109.81986,"mean_force":21.44325,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49616,-0.00495,0.03723]},{"body_a":"peg","body_b":"channel_base_body","contact_count":84.0,"contact_point_centroid":[0.50751,-0.10098,0.05957],"force_p95":104.03975,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":105.39469,"mean_force":65.46063,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4924,-0.05472,0.03755]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55384,0.12,0.06],"force_p95":90.175,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.175,"mean_force":90.175,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50539,0.1362,0.03408]},{"body_a":"peg","body_b":"channel_base_body","contact_count":642.0,"contact_point_centroid":[0.50552,0.00919,0.00959],"force_p95":19.95489,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.38935,"mean_force":4.30143,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49971,0.06003,0.03627]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":346.0,"contact_point_centroid":[0.52517,-0.03495,0.03351],"force_p95":14.47076,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.77566,"mean_force":4.51713,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49601,-0.00754,0.03726]},{"body_a":"peg","body_b":"channel_base_body","contact_count":439.0,"contact_point_centroid":[0.50577,0.0566,0.00935],"force_p95":0.60142,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.58272,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51502,0.16905,0.22862]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50027,0.19814,0.29581]},{"body_a":"peg","body_b":"channel_base_body","contact_count":669.0,"contact_point_centroid":[0.50618,0.05663,0.00938],"force_p95":0.55035,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55839,"mean_force":0.54672,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51682,0.13835,0.09904]}],"total_contact_groups":10},"final_pose_error":0.02141,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50764,-0.08392,0.03675],"final_tcp_position":[0.49195,-0.05953,0.03743],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":191.61588,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":468.0,"n_steps_budget":750.0,"object_pos_end":[0.50613,0.05663,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54349,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":476.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach_peg","tcp_end":[0.53043,0.14116,0.16626],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15902,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":669.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05659,0.03378],"object_pos_start":[0.50613,0.05663,0.03378],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.13691,"object_z_max":0.03378,"peak_contact_force":90.175,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":670.0,"raw_peak_contact_force":90.175,"tcp_end":[0.50537,0.1362,0.03392],"tcp_start":[0.53043,0.14116,0.16626],"tcp_to_object_dist_end":0.07961,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":901.0,"n_steps_budget":930.0,"object_pos_end":[0.50764,-0.08392,0.03675],"object_pos_start":[0.50613,0.05659,0.03378],"object_to_goal_dist_end":0.00918,"object_to_goal_dist_start":0.13687,"object_z_max":0.03916,"peak_contact_force":109.81986,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1987.0,"raw_peak_contact_force":191.61588,"subtask_id":"push_through_channel","tcp_end":[0.49195,-0.05953,0.03743],"tcp_start":[0.50537,0.1362,0.03392],"tcp_to_object_dist_end":0.02901,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```