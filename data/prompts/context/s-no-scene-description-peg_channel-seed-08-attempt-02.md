## Search State

- **Seed**: 8
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.3492 | 0.39 | ✅ accepted |
| 1 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | 0.2633 | 0.00 | ❌ rejected |
| 0 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | 0.2633 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.39 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.349) — your mutation base

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
    - 0.0
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.08, 0.0]
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

- **Composite score**: 0.349
- **task_score** (E): 0.389
- **fitness_score**: 0.679  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1421 |
| descend_to_peg | 0.00 | 1.00 | 0.1323 |
| push_through_channel | 1.00 | 1.00 | 0.2095 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.162, 0.168) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.547 | 3.526 |
| descend_to_peg | descend | 0.00 / step_budget | (0.513, 0.162, 0.168)→(0.499, 0.159, 0.037) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.545 | 0.590 |
| push_through_channel | push | 1.00 / time_limit | (0.499, 0.159, 0.037)→(0.489, -0.051, 0.040) | (0.503, 0.080, 0.034)→(0.509, -0.068, 0.039) | 0.160→0.018 | 1.00 / 4.333 | 107.246 | 143.348 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.868
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.440
- phase_score: 0.889
- phase_breakdown.push_through_channel_score: 0.918
- phase_breakdown.approach_peg_score: 0.820

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.709
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.447
- **Median Q (composite search score)**: 0.347
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.516


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40441,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.16988,"descend_to_peg.contact_force":9.82005,"descend_to_peg.descend_speed":0.0341,"push_through_channel.push_distance":0.23342,"push_through_channel.push_speed":0.13863,"push_through_channel.push_timeout":3.21424},"optimized_scores":{"best_composite_score":0.34737,"best_fitness_score":0.67737,"best_task_score":0.44726},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":467.0,"contact_point_centroid":[0.54197,0.09163,0.05999],"force_p95":100.37553,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":121.51949,"mean_force":76.32535,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49105,0.11081,0.03581]},{"body_a":"attachment","body_b":"peg","contact_count":431.0,"contact_point_centroid":[0.49945,0.04706,0.04119],"force_p95":31.65781,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.83508,"mean_force":9.29194,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49214,0.05766,0.03718]},{"body_a":"peg","body_b":"channel_base_body","contact_count":728.0,"contact_point_centroid":[0.5015,0.06192,0.00964],"force_p95":26.44158,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.26335,"mean_force":5.38582,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49101,0.10825,0.03569]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":328.0,"contact_point_centroid":[0.5251,0.02309,0.02827],"force_p95":12.50549,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.21312,"mean_force":3.49744,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49225,0.04803,0.03735]},{"body_a":"peg","body_b":"channel_base_body","contact_count":342.0,"contact_point_centroid":[0.4964,0.11915,0.00938],"force_p95":0.62209,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56501,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49153,0.19852,0.23108]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4994,0.19957,0.29734]},{"body_a":"peg","body_b":"channel_base_body","contact_count":831.0,"contact_point_centroid":[0.49606,0.11903,0.00944],"force_p95":0.60673,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65483,"mean_force":0.54075,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48699,0.19721,0.09909]}],"total_contact_groups":7},"final_pose_error":0.0155,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50725,-0.04806,0.03809],"final_tcp_position":[0.49236,-0.02154,0.03767],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":121.51949,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":367.0,"n_steps_budget":600.0,"object_pos_end":[0.49605,0.11898,0.03391],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19911,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.53731,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":366.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_peg","tcp_end":[0.48489,0.19796,0.16977],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15755,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":831.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11901,0.03383],"object_pos_start":[0.49605,0.11898,0.03391],"object_to_goal_dist_end":0.19915,"object_to_goal_dist_start":0.19911,"object_z_max":0.03418,"peak_contact_force":0.54591,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":831.0,"raw_peak_contact_force":0.65483,"tcp_end":[0.49148,0.19743,0.03513],"tcp_start":[0.48489,0.19796,0.16977],"tcp_to_object_dist_end":0.07856,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50725,-0.04806,0.03809],"object_pos_start":[0.49602,0.11901,0.03383],"object_to_goal_dist_end":0.03281,"object_to_goal_dist_start":0.19915,"object_z_max":0.04018,"peak_contact_force":17.2852,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1954.0,"raw_peak_contact_force":121.51949,"subtask_id":"push_through_channel","tcp_end":[0.49236,-0.02154,0.03767],"tcp_start":[0.49148,0.19743,0.03513],"tcp_to_object_dist_end":0.03041,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.82407,"average_solve_count":216.0,"average_success_count":216.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.05016,"descend_to_peg.contact_force":3.24187,"descend_to_peg.descend_speed":0.01024,"push_through_channel.push_distance":0.23816,"push_through_channel.push_speed":0.14933,"push_through_channel.push_timeout":3.72947},"optimized_scores":{"best_composite_score":0.37901,"best_fitness_score":0.70901,"best_task_score":0.43972},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":600.0,"contact_point_centroid":[0.49983,-0.01117,0.04077],"force_p95":147.64463,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":170.93282,"mean_force":45.22166,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49273,-0.00204,0.03952]},{"body_a":"peg","body_b":"channel_base_body","contact_count":161.0,"contact_point_centroid":[0.50921,-0.10133,0.0493],"force_p95":127.24446,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":146.61691,"mean_force":79.09107,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48865,-0.05524,0.04136]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":516.0,"contact_point_centroid":[0.52547,-0.03012,0.02862],"force_p95":64.74695,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":99.39292,"mean_force":22.29452,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49229,-0.00978,0.03982]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":16.0,"contact_point_centroid":[0.47497,-0.066,0.04682],"force_p95":91.98775,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.57284,"mean_force":78.52435,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48558,-0.06592,0.04125]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":134.0,"contact_point_centroid":[0.54453,0.10563,0.05999],"force_p95":78.4838,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.24172,"mean_force":57.25818,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4988,0.10909,0.03592]},{"body_a":"peg","body_b":"channel_base_body","contact_count":780.0,"contact_point_centroid":[0.50703,-0.00637,0.00958],"force_p95":64.00869,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":77.63579,"mean_force":19.36298,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49473,0.03377,0.03847]},{"body_a":"peg","body_b":"link7","contact_count":52.0,"contact_point_centroid":[0.52296,-0.07788,0.06711],"force_p95":28.71361,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.12662,"mean_force":20.62072,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48589,-0.06435,0.0411]},{"body_a":"peg","body_b":"channel_base_body","contact_count":476.0,"contact_point_centroid":[0.50564,0.06301,0.00935],"force_p95":0.5787,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57498,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51152,0.17241,0.22961]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49996,0.19859,0.29669]},{"body_a":"peg","body_b":"channel_base_body","contact_count":673.0,"contact_point_centroid":[0.50605,0.06301,0.00938],"force_p95":0.55194,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54657,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51248,0.14436,0.10124]}],"total_contact_groups":10},"final_pose_error":0.02928,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.51102,-0.07593,0.03923],"final_tcp_position":[0.48559,-0.06797,0.04152],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":170.93282,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":504.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.06303,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.55142,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":510.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach_peg","tcp_end":[0.52402,0.1472,0.16698],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15857,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":673.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.06295,0.03381],"object_pos_start":[0.50602,0.06303,0.03381],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14329,"object_z_max":0.03381,"peak_contact_force":0.54379,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":673.0,"raw_peak_contact_force":0.55501,"tcp_end":[0.50316,0.14222,0.03769],"tcp_start":[0.52402,0.1472,0.16698],"tcp_to_object_dist_end":0.07941,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":961.0,"n_steps_budget":990.0,"object_pos_end":[0.51102,-0.07593,0.03923],"object_pos_start":[0.50602,0.06295,0.03381],"object_to_goal_dist_end":0.01177,"object_to_goal_dist_start":0.14321,"object_z_max":0.04019,"peak_contact_force":166.86137,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2259.0,"raw_peak_contact_force":170.93282,"subtask_id":"push_through_channel","tcp_end":[0.48559,-0.06797,0.04152],"tcp_start":[0.50316,0.14222,0.03769],"tcp_to_object_dist_end":0.02675,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45865,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.14151,"descend_to_peg.contact_force":2.94218,"descend_to_peg.descend_speed":0.03535,"push_through_channel.push_distance":0.22133,"push_through_channel.push_speed":0.14968,"push_through_channel.push_timeout":1.02585},"optimized_scores":{"best_composite_score":0.32136,"best_fitness_score":0.65136,"best_task_score":0.28075},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":526.0,"contact_point_centroid":[0.50014,-0.00992,0.041],"force_p95":126.61039,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":137.59142,"mean_force":28.29781,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49369,0.00017,0.0396]},{"body_a":"peg","body_b":"channel_base_body","contact_count":110.0,"contact_point_centroid":[0.50827,-0.10104,0.05508],"force_p95":103.70533,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":113.44058,"mean_force":65.0012,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49032,-0.05417,0.0416]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":109.0,"contact_point_centroid":[0.54473,0.10601,0.05999],"force_p95":73.48737,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.45301,"mean_force":53.6118,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49949,0.10763,0.03599]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":405.0,"contact_point_centroid":[0.52527,-0.03376,0.02724],"force_p95":41.83556,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.23002,"mean_force":13.23534,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49308,-0.01143,0.04008]},{"body_a":"peg","body_b":"channel_base_body","contact_count":666.0,"contact_point_centroid":[0.5066,-0.00541,0.00964],"force_p95":36.18511,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.00804,"mean_force":10.85998,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49587,0.03881,0.03845]},{"body_a":"peg","body_b":"channel_base_body","contact_count":436.0,"contact_point_centroid":[0.50582,0.05665,0.00935],"force_p95":0.60143,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.58301,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51504,0.16902,0.22856]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5003,0.19811,0.29573]},{"body_a":"peg","body_b":"channel_base_body","contact_count":619.0,"contact_point_centroid":[0.50612,0.05655,0.00938],"force_p95":0.55294,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56022,"mean_force":0.54662,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51613,0.13819,0.10129]}],"total_contact_groups":8},"final_pose_error":0.02454,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50929,-0.07959,0.03835],"final_tcp_position":[0.48869,-0.06216,0.04089],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":137.59142,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":465.0,"n_steps_budget":720.0,"object_pos_end":[0.50614,0.0566,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.5531,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":473.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach_peg","tcp_end":[0.53044,0.14114,0.16621],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15898,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":619.0,"n_steps_budget":1000.0,"object_pos_end":[0.50609,0.05662,0.0338],"object_pos_start":[0.50614,0.0566,0.03378],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.13688,"object_z_max":0.0338,"peak_contact_force":0.54382,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":619.0,"raw_peak_contact_force":0.56022,"tcp_end":[0.50381,0.13588,0.03809],"tcp_start":[0.53044,0.14114,0.16621],"tcp_to_object_dist_end":0.0794,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":901.0,"n_steps_budget":930.0,"object_pos_end":[0.50929,-0.07959,0.03835],"object_pos_start":[0.50609,0.05662,0.0338],"object_to_goal_dist_end":0.00945,"object_to_goal_dist_start":0.1369,"object_z_max":0.04013,"peak_contact_force":137.59142,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1816.0,"raw_peak_contact_force":137.59142,"subtask_id":"push_through_channel","tcp_end":[0.48869,-0.06216,0.04089],"tcp_start":[0.50381,0.13588,0.03809],"tcp_to_object_dist_end":0.02711,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```