## Search State

- **Seed**: 3
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → push → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 9 | 0.4250 | 0.39 | ✅ accepted |
| 13 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.4964 | 0.10 | ✅ accepted |
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.4934 | 0.09 | ❌ rejected |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | -0.1396 | 0.00 | ❌ rejected |
| 10 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | -0.0766 | 0.00 | ❌ rejected |

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

## Current Skill (Q=0.425) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_above_peg
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.25
  weight: 0.2
- id: contact_peg
  anchor: object
  offset:
  - 0.0
  - 0.02
  - -0.02
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.5
phases:
- id: approach_peg
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.25
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
    arc_height:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: reach_above_peg
- id: align_peg
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - -0.02
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact_peg
- id: engage_peg
  type: push
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 25.0
      default: 12.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_push_distance:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    contact_push_speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_below_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  subtask_id: push_to_goal
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
      - 1.0
      - 3.5
      default: 2.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.15
      - 0.28
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.25], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **align_peg** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, -0.02], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **engage_peg** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.05, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - contact_push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_below_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
- **push_channel** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.2, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - max_push_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]

## Design Metrics

- **Composite score**: 0.425
- **task_score** (E): 0.389
- **fitness_score**: 0.602  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1053 |
| align_peg | 1.00 | 1.00 | 0.2671 |
| engage_peg | 1.00 | 1.00 | 0.0194 |
| push_channel | 1.00 | 1.00 | 0.1538 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.098, 0.298) | (0.509, 0.081, 0.040)→(0.502, 0.082, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.548 | 3.954 |
| align_peg | descend | 1.00 / step_budget | (0.505, 0.098, 0.298)→(0.506, 0.103, 0.032) | (0.502, 0.082, 0.034)→(0.492, 0.067, 0.038) | 0.162→0.147 | 1.00 / 1.000 | 0.412 | 359.347 |
| engage_peg | push | 1.00 / force_exceeded | (0.506, 0.103, 0.032)→(0.502, 0.085, 0.029) | (0.492, 0.067, 0.038)→(0.494, 0.057, 0.035) | 0.147→0.137 | 1.00 / 2.667 | 1473.637 | 4.678 |
| push_channel | push | 1.00 / time_limit | (0.502, 0.085, 0.029)→(0.502, -0.068, 0.029) | (0.494, 0.057, 0.035)→(0.502, -0.093, 0.036) | 0.137→0.015 | 1.00 / 3.667 | 109.517 | 147.964 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.507
- phase_score: 0.808
- phase_breakdown.contact_peg_score: 0.691
- phase_breakdown.push_to_goal_score: 0.931
- phase_breakdown.reach_above_peg_score: 0.674

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.688
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.507
- **Median Q (composite search score)**: 0.403
- **K-run variance**: 0.0040
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.297


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.42424,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_peg.descend_speed":0.16764,"approach_peg.approach_speed":0.15372,"approach_peg.arc_height":0.10457,"engage_peg.contact_force_threshold":5.9008,"engage_peg.contact_push_distance":0.05609,"engage_peg.contact_push_speed":0.10613,"push_channel.max_push_time":1.86,"push_channel.push_distance":0.25716,"push_channel.push_speed":0.08501},"optimized_scores":{"best_composite_score":0.36145,"best_fitness_score":0.53811,"best_task_score":0.34604},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":657.0,"contact_point_centroid":[0.49613,0.06051,0.00914],"force_p95":215.949,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":256.23115,"mean_force":27.77806,"phase_index":1.0,"phase_name":"align_peg","phase_type":"descend","tcp_position_centroid":[0.48026,0.07528,0.1612]},{"body_a":"attachment","body_b":"peg","contact_count":99.0,"contact_point_centroid":[0.50422,0.07232,0.05223],"force_p95":252.0877,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":255.80075,"mean_force":180.72782,"phase_index":1.0,"phase_name":"align_peg","phase_type":"descend","tcp_position_centroid":[0.49645,0.07927,0.0499]},{"body_a":"peg","body_b":"channel_base_body","contact_count":224.0,"contact_point_centroid":[0.49405,-0.10394,0.04346],"force_p95":86.33734,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":112.49556,"mean_force":39.83425,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49475,-0.06236,0.02669]},{"body_a":"attachment","body_b":"peg","contact_count":797.0,"contact_point_centroid":[0.49523,-0.02755,0.0403],"force_p95":68.18488,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":112.00802,"mean_force":13.77904,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49419,-0.01586,0.02548]},{"body_a":"channel_base_body","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.52229,-0.1,0.06499],"force_p95":76.28722,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.78789,"mean_force":52.13716,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4939,-0.0606,0.02576]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":323.0,"contact_point_centroid":[0.47478,-0.0262,0.03602],"force_p95":34.82964,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.43289,"mean_force":6.05755,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49446,0.00247,0.02525]},{"body_a":"peg","body_b":"channel_base_body","contact_count":669.0,"contact_point_centroid":[0.49461,-0.04722,0.0099],"force_p95":10.09598,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.22811,"mean_force":2.55592,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49408,-0.00622,0.02525]},{"body_a":"attachment","body_b":"peg","contact_count":15.0,"contact_point_centroid":[0.49801,0.04539,0.05832],"force_p95":3.5055,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.5319,"mean_force":0.87256,"phase_index":2.0,"phase_name":"engage_peg","phase_type":"push","tcp_position_centroid":[0.49724,0.05658,0.02751]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":48.0,"contact_point_centroid":[0.47429,0.02028,0.04601],"force_p95":0.59022,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.88322,"mean_force":0.4168,"phase_index":2.0,"phase_name":"engage_peg","phase_type":"push","tcp_position_centroid":[0.49858,0.07405,0.02826]},{"body_a":"peg","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.50876,-0.10546,0.0669],"force_p95":3.7144,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.643,"mean_force":0.9286,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49613,-0.07562,0.02801]},{"body_a":"peg","body_b":"channel_base_body","contact_count":302.0,"contact_point_centroid":[0.49465,0.05885,0.00933],"force_p95":0.63176,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.59462,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48379,0.13519,0.32664]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49817,0.19563,0.30408]},{"body_a":"peg","body_b":"channel_base_body","contact_count":149.0,"contact_point_centroid":[0.49718,0.01747,0.00968],"force_p95":0.92814,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.28692,"mean_force":0.57501,"phase_index":2.0,"phase_name":"engage_peg","phase_type":"push","tcp_position_centroid":[0.49772,0.06787,0.02755]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.47387,0.04506,0.02425],"force_p95":2.67129,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.07683,"mean_force":0.97357,"phase_index":1.0,"phase_name":"align_peg","phase_type":"descend","tcp_position_centroid":[0.50295,0.08086,0.03459]}],"total_contact_groups":14},"final_pose_error":0.25938,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49308,-0.10318,0.03735],"final_tcp_position":[0.49606,-0.07809,0.02803],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":256.23115,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":331.0,"n_steps_budget":600.0,"object_pos_end":[0.4942,0.05902,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13928,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.5462,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":337.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_above_peg","tcp_end":[0.469,0.0721,0.30482],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.27246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":668.0,"n_steps_budget":1000.0,"object_pos_end":[0.48993,0.04386,0.03958],"object_pos_start":[0.4942,0.05902,0.03385],"object_to_goal_dist_end":0.12427,"object_to_goal_dist_start":0.13928,"object_z_max":0.03938,"peak_contact_force":0.37559,"phase_name":"align_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":769.0,"raw_peak_contact_force":256.23115,"subtask_id":"contact_peg","tcp_end":[0.50116,0.08054,0.03108],"tcp_start":[0.469,0.0721,0.30482],"tcp_to_object_dist_end":0.03929,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":171.0,"n_steps_budget":1000.0,"object_pos_end":[0.49344,0.02653,0.03402],"object_pos_start":[0.48993,0.04386,0.03958],"object_to_goal_dist_end":0.1069,"object_to_goal_dist_start":0.12427,"object_z_max":0.04031,"peak_contact_force":9.5319,"phase_name":"engage_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":212.0,"raw_peak_contact_force":9.5319,"subtask_id":"push_to_goal","tcp_end":[0.49723,0.05538,0.02755],"tcp_start":[0.50116,0.08054,0.03108],"tcp_to_object_dist_end":0.02981,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49308,-0.10318,0.03735],"object_pos_start":[0.49344,0.02653,0.03402],"object_to_goal_dist_end":0.02434,"object_to_goal_dist_start":0.1069,"object_z_max":0.04087,"peak_contact_force":12.79521,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2026.0,"raw_peak_contact_force":112.49556,"subtask_id":"push_to_goal","tcp_end":[0.49606,-0.07809,0.02803],"tcp_start":[0.49723,0.05538,0.02755],"tcp_to_object_dist_end":0.02694,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.96992,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_peg.descend_speed":0.07732,"approach_peg.approach_speed":0.36936,"approach_peg.arc_height":0.15415,"engage_peg.contact_force_threshold":9.73345,"engage_peg.contact_push_distance":0.04779,"engage_peg.contact_push_speed":0.08239,"push_channel.max_push_time":1.81992,"push_channel.push_distance":0.22535,"push_channel.push_speed":0.1379},"optimized_scores":{"best_composite_score":0.40256,"best_fitness_score":0.57923,"best_task_score":0.31303},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":157.0,"contact_point_centroid":[0.52515,0.1021,0.05998],"force_p95":456.39574,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":553.60754,"mean_force":344.4296,"phase_index":1.0,"phase_name":"align_peg","phase_type":"descend","tcp_position_centroid":[0.51184,0.10218,0.04939]},{"body_a":"attachment","body_b":"peg","contact_count":207.0,"contact_point_centroid":[0.51782,0.09293,0.0529],"force_p95":173.37488,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":208.63909,"mean_force":153.67378,"phase_index":1.0,"phase_name":"align_peg","phase_type":"descend","tcp_position_centroid":[0.51114,0.10181,0.0506]},{"body_a":"peg","body_b":"channel_base_body","contact_count":778.0,"contact_point_centroid":[0.50834,0.08309,0.009],"force_p95":171.68765,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":187.82148,"mean_force":40.92314,"phase_index":1.0,"phase_name":"align_peg","phase_type":"descend","tcp_position_centroid":[0.51557,0.09955,0.14203]},{"body_a":"attachment","body_b":"peg","contact_count":762.0,"contact_point_centroid":[0.50354,-0.01687,0.04435],"force_p95":159.86612,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":163.42336,"mean_force":51.07321,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50188,-0.00584,0.03082]},{"body_a":"peg","body_b":"channel_base_body","contact_count":284.0,"contact_point_centroid":[0.50723,-0.10242,0.0598],"force_p95":157.78283,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":158.64551,"mean_force":130.41758,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5018,-0.06136,0.03099]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":67.0,"contact_point_centroid":[0.52529,0.08224,0.05662],"force_p95":33.32725,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.86939,"mean_force":13.42401,"phase_index":1.0,"phase_name":"align_peg","phase_type":"descend","tcp_position_centroid":[0.51088,0.10136,0.05173]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":295.0,"contact_point_centroid":[0.5253,-0.07731,0.05291],"force_p95":16.05832,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.26274,"mean_force":8.39043,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50185,-0.0513,0.0309]},{"body_a":"peg","body_b":"channel_base_body","contact_count":732.0,"contact_point_centroid":[0.50267,-0.04118,0.00983],"force_p95":7.21942,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.68201,"mean_force":3.05465,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50192,-0.00206,0.03077]},{"body_a":"peg","body_b":"channel_base_body","contact_count":230.0,"contact_point_centroid":[0.5054,0.08094,0.00933],"force_p95":0.65926,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.6131,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51469,0.14545,0.3087]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50056,0.19467,0.30182]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":41.0,"contact_point_centroid":[0.47476,0.06598,0.03783],"force_p95":2.8148,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.67882,"mean_force":1.23891,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50409,0.09383,0.03096]},{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.48424,0.06628,0.009],"force_p95":0.42888,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43389,"mean_force":0.40697,"phase_index":2.0,"phase_name":"engage_peg","phase_type":"push","tcp_position_centroid":[0.50803,0.10276,0.03552]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.07221,0.05817],"force_p95":0.14562,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14562,"mean_force":0.14562,"phase_index":2.0,"phase_name":"engage_peg","phase_type":"push","tcp_position_centroid":[0.50701,0.10219,0.03421]}],"total_contact_groups":13},"final_pose_error":0.242,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50722,-0.08788,0.03533],"final_tcp_position":[0.50661,-0.06359,0.03133],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":553.60754,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":259.0,"n_steps_budget":600.0,"object_pos_end":[0.50598,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54611,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":266.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_above_peg","tcp_end":[0.52878,0.09806,0.29695],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.26472,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":778.0,"n_steps_budget":1000.0,"object_pos_end":[0.4968,0.07352,0.03472],"object_pos_start":[0.50598,0.08086,0.03378],"object_to_goal_dist_end":0.15364,"object_to_goal_dist_start":0.16109,"object_z_max":0.03454,"peak_contact_force":0.44996,"phase_name":"align_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1209.0,"raw_peak_contact_force":553.60754,"subtask_id":"contact_peg","tcp_end":[0.50919,0.10321,0.03734],"tcp_start":[0.52878,0.09806,0.29695],"tcp_to_object_dist_end":0.03228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":9.0,"n_steps_budget":1000.0,"object_pos_end":[0.49611,0.07381,0.03594],"object_pos_start":[0.4968,0.07352,0.03472],"object_to_goal_dist_end":0.15392,"object_to_goal_dist_start":0.15364,"object_z_max":0.03584,"peak_contact_force":496.57228,"phase_name":"engage_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":10.0,"raw_peak_contact_force":0.43389,"subtask_id":"push_to_goal","tcp_end":[0.50686,0.10203,0.03408],"tcp_start":[0.50919,0.10321,0.03734],"tcp_to_object_dist_end":0.03025,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50722,-0.08788,0.03533],"object_pos_start":[0.49611,0.07381,0.03594],"object_to_goal_dist_end":0.01166,"object_to_goal_dist_start":0.15392,"object_z_max":0.03722,"peak_contact_force":154.54905,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2114.0,"raw_peak_contact_force":163.42336,"subtask_id":"push_to_goal","tcp_end":[0.50661,-0.06359,0.03133],"tcp_start":[0.50686,0.10203,0.03408],"tcp_to_object_dist_end":0.02462,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.22772,"average_solve_count":101.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_peg.descend_speed":0.15998,"approach_peg.approach_speed":0.25502,"approach_peg.arc_height":0.17625,"engage_peg.contact_force_threshold":14.32666,"engage_peg.contact_push_distance":0.05952,"engage_peg.contact_push_speed":0.08369,"push_channel.max_push_time":2.29353,"push_channel.push_distance":0.21014,"push_channel.push_speed":0.12939},"optimized_scores":{"best_composite_score":0.51087,"best_fitness_score":0.68753,"best_task_score":0.50704},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52506,0.11995,0.05999],"force_p95":260.52087,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":268.20318,"mean_force":174.16062,"phase_index":1.0,"phase_name":"align_peg","phase_type":"descend","tcp_position_centroid":[0.51386,0.12713,0.0468]},{"body_a":"attachment","body_b":"peg","contact_count":84.0,"contact_point_centroid":[0.51757,0.11861,0.05316],"force_p95":233.23776,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":241.64695,"mean_force":161.10076,"phase_index":1.0,"phase_name":"align_peg","phase_type":"descend","tcp_position_centroid":[0.50991,0.12572,0.0511]},{"body_a":"peg","body_b":"channel_base_body","contact_count":595.0,"contact_point_centroid":[0.50723,0.10599,0.00921],"force_p95":197.91504,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":232.915,"mean_force":22.09779,"phase_index":1.0,"phase_name":"align_peg","phase_type":"descend","tcp_position_centroid":[0.51091,0.12342,0.15773]},{"body_a":"peg","body_b":"channel_base_body","contact_count":254.0,"contact_point_centroid":[0.50543,-0.10216,0.06049],"force_p95":159.73,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":167.97451,"mean_force":118.65515,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49973,-0.06008,0.02689]},{"body_a":"attachment","body_b":"peg","contact_count":764.0,"contact_point_centroid":[0.50197,-0.01553,0.04256],"force_p95":158.55101,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":166.74864,"mean_force":40.12714,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5,-0.00426,0.02548]},{"body_a":"channel_base_body","body_b":"link7","contact_count":145.0,"contact_point_centroid":[0.5508,-0.1,0.065],"force_p95":87.27837,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":141.14617,"mean_force":48.96765,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50023,-0.06174,0.02712]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":271.0,"contact_point_centroid":[0.53686,0.07174,0.05998],"force_p95":80.04941,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":87.78681,"mean_force":60.47101,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50148,0.0653,0.02444]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":69.0,"contact_point_centroid":[0.52541,0.10645,0.05646],"force_p95":48.89863,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.78776,"mean_force":23.88424,"phase_index":1.0,"phase_name":"align_peg","phase_type":"descend","tcp_position_centroid":[0.50998,0.12563,0.05109]},{"body_a":"peg","body_b":"channel_base_body","contact_count":630.0,"contact_point_centroid":[0.50007,-0.01287,0.00979],"force_p95":3.87673,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.39837,"mean_force":1.60802,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50062,0.02163,0.02509]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":33.0,"contact_point_centroid":[0.52509,-0.08829,0.05983],"force_p95":9.18622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.76733,"mean_force":4.07602,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50209,-0.06359,0.02773]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":98.0,"contact_point_centroid":[0.4749,0.06377,0.03696],"force_p95":3.7581,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.91423,"mean_force":0.74644,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5024,0.09233,0.02435]},{"body_a":"attachment","body_b":"peg","contact_count":26.0,"contact_point_centroid":[0.49933,0.08961,0.02526],"force_p95":3.22094,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.06947,"mean_force":1.2452,"phase_index":2.0,"phase_name":"engage_peg","phase_type":"push","tcp_position_centroid":[0.50343,0.10081,0.02475]},{"body_a":"peg","body_b":"channel_base_body","contact_count":166.0,"contact_point_centroid":[0.50488,0.10478,0.00933],"force_p95":0.78698,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.61462,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50937,0.15736,0.30081]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":90.0,"contact_point_centroid":[0.47477,0.07382,0.04617],"force_p95":1.50717,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.75551,"mean_force":0.41074,"phase_index":2.0,"phase_name":"engage_peg","phase_type":"push","tcp_position_centroid":[0.5047,0.11367,0.02526]},{"body_a":"peg","body_b":"channel_base_body","contact_count":193.0,"contact_point_centroid":[0.49623,0.07078,0.00954],"force_p95":1.33026,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.37567,"mean_force":0.67312,"phase_index":2.0,"phase_name":"engage_peg","phase_type":"push","tcp_position_centroid":[0.50431,0.11248,0.02487]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50039,0.19524,0.30049]}],"total_contact_groups":17},"final_pose_error":0.22685,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50582,-0.08758,0.03601],"final_tcp_position":[0.50265,-0.06364,0.02784],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":3914.80545,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":193.0,"n_steps_budget":600.0,"object_pos_end":[0.506,0.10469,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18489,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55139,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":198.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_above_peg","tcp_end":[0.51806,0.12297,0.29355],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.26063,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":617.0,"n_steps_budget":1000.0,"object_pos_end":[0.48997,0.08274,0.03829],"object_pos_start":[0.506,0.10469,0.03384],"object_to_goal_dist_end":0.16306,"object_to_goal_dist_start":0.18489,"object_z_max":0.03923,"peak_contact_force":0.40936,"phase_name":"align_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":774.0,"raw_peak_contact_force":268.20318,"subtask_id":"contact_peg","tcp_end":[0.50811,0.1264,0.0285],"tcp_start":[0.51806,0.12297,0.29355],"tcp_to_object_dist_end":0.04828,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":205.0,"n_steps_budget":1000.0,"object_pos_end":[0.49324,0.07052,0.03528],"object_pos_start":[0.48997,0.08274,0.03829],"object_to_goal_dist_end":0.15074,"object_to_goal_dist_start":0.16306,"object_z_max":0.03829,"peak_contact_force":3914.80545,"phase_name":"engage_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":309.0,"raw_peak_contact_force":4.06947,"subtask_id":"push_to_goal","tcp_end":[0.50338,0.09871,0.02485],"tcp_start":[0.50811,0.1264,0.0285],"tcp_to_object_dist_end":0.03172,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50582,-0.08758,0.03601],"object_pos_start":[0.49324,0.07052,0.03528],"object_to_goal_dist_end":0.01036,"object_to_goal_dist_start":0.15074,"object_z_max":0.03675,"peak_contact_force":161.20678,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2195.0,"raw_peak_contact_force":167.97451,"subtask_id":"push_to_goal","tcp_end":[0.50265,-0.06364,0.02784],"tcp_start":[0.50338,0.09871,0.02485],"tcp_to_object_dist_end":0.0255,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```