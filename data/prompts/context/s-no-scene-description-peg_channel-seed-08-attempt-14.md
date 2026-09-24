## Search State

- **Seed**: 8
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.8709 | 0.46 | ❌ rejected |
| 13 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.9092 | 0.53 | ❌ rejected |
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.8347 | 0.42 | ❌ rejected |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.3496 | 0.04 | ❌ rejected |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.9122 | 0.53 | ✅ accepted |

**Proposal policy**: task_score is 0.46 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.871) — your mutation base

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

- **Composite score**: 0.871
- **task_score** (E): 0.461
- **fitness_score**: 0.701  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1421 |
| descend_to_peg | 1.00 | 1.00 | 0.1378 |
| push_through_channel | 1.00 | 1.00 | 0.1966 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.162, 0.168) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.538 | 3.526 |
| descend_to_peg | descend | 1.00 / force_exceeded | (0.513, 0.162, 0.168)→(0.500, 0.159, 0.031) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 69.971 | 69.971 |
| push_through_channel | push | 1.00 / time_limit | (0.500, 0.159, 0.031)→(0.495, -0.037, 0.037) | (0.503, 0.080, 0.034)→(0.504, -0.065, 0.037) | 0.160→0.022 | 1.00 / 2.667 | 120.241 | 225.343 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.936
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.737
- phase_score: 0.772
- phase_breakdown.push_through_channel_score: 0.751
- phase_breakdown.approach_peg_score: 0.820

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.758
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.737
- **Median Q (composite search score)**: 0.868
- **K-run variance**: 0.0021
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.367


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45902,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.15876,"descend_to_peg.contact_force":9.05597,"descend_to_peg.descend_speed":0.04455,"push_through_channel.push_distance":0.23495,"push_through_channel.push_speed":0.13811,"push_through_channel.push_timeout":4.8173},"optimized_scores":{"best_composite_score":0.92788,"best_fitness_score":0.75788,"best_task_score":0.73682},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":865.0,"contact_point_centroid":[0.54632,0.09015,0.05994],"force_p95":239.54125,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":334.90516,"mean_force":185.42391,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49305,0.12241,0.0338]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52501,0.0031,0.06],"force_p95":179.12374,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":182.93591,"mean_force":104.3362,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5007,0.00288,0.0367]},{"body_a":"peg","body_b":"channel_base_body","contact_count":854.0,"contact_point_centroid":[0.49797,0.07263,0.0095],"force_p95":3.30098,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.95888,"mean_force":1.27998,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49251,0.12649,0.03365]},{"body_a":"attachment","body_b":"peg","contact_count":151.0,"contact_point_centroid":[0.4998,0.064,0.0396],"force_p95":27.53026,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.86038,"mean_force":4.48588,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49806,0.07552,0.03637]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54791,0.11997,0.05997],"force_p95":58.01876,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":58.01876,"mean_force":58.01876,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49102,0.19738,0.02624]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":113.0,"contact_point_centroid":[0.47469,0.01468,0.04451],"force_p95":1.08361,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.93851,"mean_force":0.79163,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49915,0.04983,0.03653]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":63.0,"contact_point_centroid":[0.52537,0.04993,0.04302],"force_p95":3.14152,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.33901,"mean_force":0.85978,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49819,0.08364,0.03643]},{"body_a":"peg","body_b":"channel_base_body","contact_count":342.0,"contact_point_centroid":[0.4964,0.11915,0.00938],"force_p95":0.62209,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56501,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49153,0.19852,0.23108]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4994,0.19957,0.29734]},{"body_a":"peg","body_b":"channel_base_body","contact_count":879.0,"contact_point_centroid":[0.49608,0.11905,0.00944],"force_p95":0.60597,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65483,"mean_force":0.54074,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48677,0.19718,0.09414]}],"total_contact_groups":10},"final_pose_error":0.03805,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49594,-0.03077,0.0361],"final_tcp_position":[0.5006,0.0002,0.03666],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":334.90516,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":367.0,"n_steps_budget":600.0,"object_pos_end":[0.49605,0.11898,0.03391],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19911,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.53731,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":366.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_peg","tcp_end":[0.48489,0.19796,0.16977],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15755,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":879.0,"n_steps_budget":1000.0,"object_pos_end":[0.49595,0.11899,0.03393],"object_pos_start":[0.49605,0.11898,0.03391],"object_to_goal_dist_end":0.19912,"object_to_goal_dist_start":0.19911,"object_z_max":0.03418,"peak_contact_force":58.01876,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":880.0,"raw_peak_contact_force":58.01876,"tcp_end":[0.49105,0.19739,0.02611],"tcp_start":[0.48489,0.19796,0.16977],"tcp_to_object_dist_end":0.07894,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49594,-0.03077,0.0361],"object_pos_start":[0.49595,0.11899,0.03393],"object_to_goal_dist_end":0.04955,"object_to_goal_dist_start":0.19912,"object_z_max":0.04076,"peak_contact_force":190.55739,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2050.0,"raw_peak_contact_force":334.90516,"subtask_id":"push_through_channel","tcp_end":[0.5006,0.0002,0.03666],"tcp_start":[0.49105,0.19739,0.02611],"tcp_to_object_dist_end":0.03132,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46364,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.1348,"descend_to_peg.contact_force":9.85197,"descend_to_peg.descend_speed":0.05618,"push_through_channel.push_distance":0.23194,"push_through_channel.push_speed":0.12918,"push_through_channel.push_timeout":4.67539},"optimized_scores":{"best_composite_score":0.868,"best_fitness_score":0.698,"best_task_score":0.38562},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":573.0,"contact_point_centroid":[0.54578,0.06686,0.05998],"force_p95":129.20408,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":157.78272,"mean_force":89.38271,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49992,0.07211,0.03602]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":62.0,"contact_point_centroid":[0.52504,0.11486,0.05998],"force_p95":131.97056,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":155.3411,"mean_force":80.72777,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50143,0.11665,0.03559]},{"body_a":"attachment","body_b":"peg","contact_count":329.0,"contact_point_centroid":[0.50117,-0.01051,0.04148],"force_p95":52.89359,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.80774,"mean_force":13.14073,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49605,0.00062,0.03713]},{"body_a":"peg","body_b":"channel_base_body","contact_count":58.0,"contact_point_centroid":[0.50739,-0.10064,0.05925],"force_p95":80.00079,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.93313,"mean_force":43.42086,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4923,-0.05308,0.03743]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55458,0.12,0.05995],"force_p95":70.72724,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.72724,"mean_force":70.72724,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50433,0.14241,0.03368]},{"body_a":"peg","body_b":"channel_base_body","contact_count":742.0,"contact_point_centroid":[0.5036,0.01475,0.00951],"force_p95":14.64954,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.33108,"mean_force":2.75469,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49941,0.06373,0.03615]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":257.0,"contact_point_centroid":[0.52525,-0.04347,0.03169],"force_p95":11.51649,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.7187,"mean_force":3.24019,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49504,-0.01599,0.03727]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.47452,0.03148,0.0379],"force_p95":2.76672,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.15339,"mean_force":0.89174,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50009,0.0633,0.03668]},{"body_a":"peg","body_b":"channel_base_body","contact_count":419.0,"contact_point_centroid":[0.5057,0.06303,0.00935],"force_p95":0.58063,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57885,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51171,0.17218,0.22903]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50011,0.19838,0.29614]},{"body_a":"peg","body_b":"channel_base_body","contact_count":655.0,"contact_point_centroid":[0.50593,0.06292,0.00938],"force_p95":0.55142,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54658,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51305,0.14442,0.09888]}],"total_contact_groups":11},"final_pose_error":0.03369,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50756,-0.08186,0.03715],"final_tcp_position":[0.49208,-0.05609,0.03742],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":157.78272,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":447.0,"n_steps_budget":720.0,"object_pos_end":[0.50601,0.06295,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54682,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":453.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach_peg","tcp_end":[0.52408,0.14714,0.16687],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15849,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":655.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.06303,0.0338],"object_pos_start":[0.50601,0.06295,0.03381],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14321,"object_z_max":0.03381,"peak_contact_force":70.72724,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":656.0,"raw_peak_contact_force":70.72724,"tcp_end":[0.50432,0.14241,0.03353],"tcp_start":[0.52408,0.14714,0.16687],"tcp_to_object_dist_end":0.0794,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50756,-0.08186,0.03715],"object_pos_start":[0.50595,0.06303,0.0338],"object_to_goal_dist_end":0.00829,"object_to_goal_dist_start":0.14329,"object_z_max":0.03887,"peak_contact_force":85.80774,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2056.0,"raw_peak_contact_force":157.78272,"subtask_id":"push_through_channel","tcp_end":[0.49208,-0.05609,0.03742],"tcp_start":[0.50432,0.14241,0.03353],"tcp_to_object_dist_end":0.03007,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34641,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.12501,"descend_to_peg.contact_force":5.67659,"descend_to_peg.descend_speed":0.0311,"push_through_channel.push_distance":0.21838,"push_through_channel.push_speed":0.12497,"push_through_channel.push_timeout":4.41178},"optimized_scores":{"best_composite_score":0.8167,"best_fitness_score":0.6467,"best_task_score":0.2608},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":527.0,"contact_point_centroid":[0.54623,0.07075,0.05998],"force_p95":138.53604,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":183.34086,"mean_force":86.80381,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50069,0.07494,0.03602]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":134.0,"contact_point_centroid":[0.52502,0.11037,0.05999],"force_p95":156.02983,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":164.43628,"mean_force":95.45266,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50169,0.1127,0.03563]},{"body_a":"attachment","body_b":"peg","contact_count":343.0,"contact_point_centroid":[0.50034,-0.01993,0.0418],"force_p95":56.20496,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.86937,"mean_force":12.34251,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49599,-0.00865,0.03721]},{"body_a":"peg","body_b":"channel_base_body","contact_count":62.0,"contact_point_centroid":[0.50718,-0.10067,0.0595],"force_p95":79.61784,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.04082,"mean_force":44.79746,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49261,-0.0535,0.03747]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55383,0.12,0.05993],"force_p95":81.16817,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":81.16817,"mean_force":81.16817,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50538,0.13617,0.03396]},{"body_a":"peg","body_b":"channel_base_body","contact_count":743.0,"contact_point_centroid":[0.50359,0.01236,0.00954],"force_p95":11.64568,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.92432,"mean_force":2.49416,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4999,0.06208,0.03623]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":176.0,"contact_point_centroid":[0.47475,-0.00162,0.02888],"force_p95":2.11421,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.15456,"mean_force":0.82103,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4989,0.02845,0.03702]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":171.0,"contact_point_centroid":[0.52512,-0.04858,0.03444],"force_p95":7.33867,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.58547,"mean_force":2.28505,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49489,-0.02099,0.03724]},{"body_a":"peg","body_b":"channel_base_body","contact_count":443.0,"contact_point_centroid":[0.50585,0.0566,0.00935],"force_p95":0.60156,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.58247,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51498,0.16908,0.22871]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50026,0.19817,0.29587]},{"body_a":"peg","body_b":"channel_base_body","contact_count":647.0,"contact_point_centroid":[0.5061,0.05664,0.00937],"force_p95":0.60098,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65255,"mean_force":0.54652,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51682,0.13833,0.09902]}],"total_contact_groups":11},"final_pose_error":0.02628,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50741,-0.08239,0.03709],"final_tcp_position":[0.4923,-0.05647,0.03742],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":183.34086,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":472.0,"n_steps_budget":810.0,"object_pos_end":[0.50614,0.0566,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.53006,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":480.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach_peg","tcp_end":[0.53041,0.14116,0.16624],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":647.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05661,0.03378],"object_pos_start":[0.50614,0.0566,0.03377],"object_to_goal_dist_end":0.13689,"object_to_goal_dist_start":0.13688,"object_z_max":0.03381,"peak_contact_force":81.16817,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":648.0,"raw_peak_contact_force":81.16817,"tcp_end":[0.50536,0.13617,0.0338],"tcp_start":[0.53041,0.14116,0.16624],"tcp_to_object_dist_end":0.07956,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50741,-0.08239,0.03709],"object_pos_start":[0.50613,0.05661,0.03378],"object_to_goal_dist_end":0.00832,"object_to_goal_dist_start":0.13689,"object_z_max":0.0389,"peak_contact_force":84.35682,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2156.0,"raw_peak_contact_force":183.34086,"subtask_id":"push_through_channel","tcp_end":[0.4923,-0.05647,0.03742],"tcp_start":[0.50536,0.13617,0.0338],"tcp_to_object_dist_end":0.03,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```